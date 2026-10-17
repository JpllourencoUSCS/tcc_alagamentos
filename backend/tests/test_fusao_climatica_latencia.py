"""
Teste da paralelização das chamadas externas em obter_dados_consolidados
(achado de revisão de latência, 03/09/2026 — ver docs/CRONOGRAMA_STATUS.md).

Antes, as chamadas a OpenWeather (atual/previsão), ANA e CPTEC eram
sequenciais: no pior caso (uma fonte lenta), o tempo de resposta ao usuário
somava os timeouts de todas. Agora rodam em paralelo via ThreadPoolExecutor —
o tempo total fica limitado ao ramo mais lento, não à soma de todos.
Desde 06/10/2026 o CPTEC deu lugar à previsão e aos avisos do INMET (apiprevmet3);
desde 16/10/2026 a ANA deu lugar à Open-Meteo — continuam 5 chamadas.

Mocka as funções de busca (`_buscar_*`) com `time.sleep` para não depender
de rede/credenciais reais, e mede o tempo de parede: se ainda fosse
sequencial, 5 chamadas de ~0.2s levariam >=1.0s; em paralelo, pouco mais que
0.2s (o tempo do ramo mais lento).
"""

import sys
import time
from contextlib import ExitStack
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

import fusao_climatica as fc

ATRASO_POR_CHAMADA_S = 0.2
N_CHAMADAS = 5
MARGEM_SEQUENCIAL_S = ATRASO_POR_CHAMADA_S * N_CHAMADAS * 0.6  # limiar bem abaixo da soma sequencial

AVISO = {"evento": "Tempestade", "severidade": "Perigo Potencial", "cor": "#FFFE00",
         "inicio": "2026-10-06 08:52", "fim": "2026-10-06 23:59", "riscos": "Chuva entre 20 e 30 mm/h"}

# Open-Meteo: 0,5 mm nos últimos 15 min (= 2,0 mm/h); próximas horas com 1 mm/h (blocos de 3 mm)
OPEN_METEO = {
    "current": {"time": "2026-10-16T10:15", "interval": 900, "precipitation": 0.5},
    "hourly": {
        "time": [f"2026-10-16T{h:02d}:00" for h in range(24)] + [f"2026-10-17T{h:02d}:00" for h in range(24)],
        "precipitation": [1.0] * 48,
    },
}


def _lento(valor):
    def f(*_args, **_kwargs):
        time.sleep(ATRASO_POR_CHAMADA_S)
        return valor
    return f


def _fontes(**substituicoes):
    """Patches das 5 buscas externas; cada uma pode ser trocada por keyword."""
    padrao = {
        "_buscar_openweather_atual": {"return_value": {"rain": {"1h": 1.0}}},
        "_buscar_openweather_previsao": {"return_value": {"list": []}},
        "_buscar_open_meteo": {"return_value": None},
        "_buscar_inmet_previsao": {"return_value": None},
        "_buscar_inmet_avisos": {"return_value": None},
    }
    padrao.update(substituicoes)
    pilha = ExitStack()
    for nome, kwargs in padrao.items():
        pilha.enter_context(patch.object(fc, nome, **kwargs))
    return pilha


def test_obter_dados_consolidados_roda_fontes_em_paralelo():
    with _fontes(
        _buscar_openweather_atual={"side_effect": _lento({"rain": {"1h": 5.0}})},
        _buscar_openweather_previsao={"side_effect": _lento({"list": [{"rain": {"3h": 8.0}}]})},
        _buscar_open_meteo={"side_effect": _lento(OPEN_METEO)},
        _buscar_inmet_previsao={"side_effect": _lento("Muitas nuvens com pancadas de chuva")},
        _buscar_inmet_avisos={"side_effect": _lento([AVISO])},
    ):
        inicio = time.monotonic()
        dados = fc.obter_dados_consolidados(-23.6, -46.5)
        duracao = time.monotonic() - inicio

    assert duracao < MARGEM_SEQUENCIAL_S, (
        f"levou {duracao:.2f}s — esperado bem menos que a soma sequencial "
        f"({ATRASO_POR_CHAMADA_S * N_CHAMADAS:.2f}s), indicando que as chamadas não "
        "estão rodando em paralelo"
    )
    # Fusão: vale o maior valor; 5,0 (moderada) × 2,0 (leve) estão em faixas diferentes
    assert dados.precipitacao_atual_mm_h == 5.0
    assert dados.fonte_precipitacao_atual == "OpenWeather"
    assert dados.fusao_precipitacao["open_meteo"] == pytest.approx(2.0)
    assert dados.fusao_precipitacao["divergente"] is True
    assert dados.pico_previsto_mm_3h == 8.0
    assert dados.fusao_previsao["open_meteo"] == pytest.approx(3.0)
    assert dados.previsao_inmet == "Muitas nuvens com pancadas de chuva"
    assert dados.avisos_inmet == [AVISO]


def test_open_meteo_e_inmet_indisponiveis_mantem_fail_safe():
    # Open-Meteo e INMET retornando None (fail-safe) não derrubam a consolidação
    with _fontes():
        dados = fc.obter_dados_consolidados(-23.6, -46.5)

    assert dados.precipitacao_atual_mm_h == 1.0
    assert dados.fonte_precipitacao_atual == "OpenWeather"
    assert dados.fusao_precipitacao["open_meteo"] is None
    assert dados.fusao_precipitacao["divergente"] is False
    assert dados.previsao_inmet is None
    assert dados.avisos_inmet == []


def test_openweather_fora_do_ar_usa_so_a_open_meteo():
    # 16/10/2026: a falha do OpenWeather deixou de derrubar o cálculo
    with _fontes(
        _buscar_openweather_atual={"side_effect": RuntimeError("timeout")},
        _buscar_openweather_previsao={"side_effect": RuntimeError("timeout")},
        _buscar_open_meteo={"return_value": OPEN_METEO},
    ):
        dados = fc.obter_dados_consolidados(-23.6, -46.5)

    assert dados.precipitacao_atual_mm_h == pytest.approx(2.0)
    assert dados.fonte_precipitacao_atual == "Open-Meteo"
    assert dados.fusao_precipitacao["openweather"] is None
    assert dados.pico_previsto_mm_3h == pytest.approx(3.0)


def test_sem_nenhuma_fonte_numerica_levanta_fonte_indisponivel():
    with _fontes(_buscar_openweather_atual={"side_effect": RuntimeError("timeout")}):
        with pytest.raises(fc.FonteClimaticaIndisponivel, match="chuva atual"):
            fc.obter_dados_consolidados(-23.6, -46.5)
