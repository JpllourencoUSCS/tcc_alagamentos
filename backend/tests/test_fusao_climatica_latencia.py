"""
Teste da paralelização das 4 chamadas externas em obter_dados_consolidados
(achado de revisão de latência, 03/09/2026 — ver docs/CRONOGRAMA_STATUS.md).

Antes, as chamadas a OpenWeather (atual/previsão), ANA e CPTEC eram
sequenciais: no pior caso (uma fonte lenta), o tempo de resposta ao usuário
somava os timeouts das 4. Agora rodam em paralelo via ThreadPoolExecutor —
o tempo total fica limitado ao ramo mais lento, não à soma de todos.

Mocka as 4 funções de busca (`_buscar_*`) com `time.sleep` para não depender
de rede/credenciais reais, e mede o tempo de parede: se ainda fosse
sequencial, 4 chamadas de ~0.2s levariam >=0.8s; em paralelo, pouco mais que
0.2s (o tempo do ramo mais lento).
"""

import sys
import time
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import fusao_climatica as fc

ATRASO_POR_CHAMADA_S = 0.2
MARGEM_SEQUENCIAL_S = ATRASO_POR_CHAMADA_S * 4 * 0.75  # limiar bem abaixo da soma sequencial


def _openweather_atual_lento(lat, lon):
    time.sleep(ATRASO_POR_CHAMADA_S)
    return {"rain": {"1h": 5.0}}


def _openweather_previsao_lenta(lat, lon):
    time.sleep(ATRASO_POR_CHAMADA_S)
    return {"list": [{"rain": {"3h": 8.0}}]}


def _ana_lenta(codigo_estacao):
    time.sleep(ATRASO_POR_CHAMADA_S)
    return 3.5


def _cptec_lento(id_cidade):
    time.sleep(ATRASO_POR_CHAMADA_S)
    return "Chuvoso"


def test_obter_dados_consolidados_roda_fontes_em_paralelo():
    with patch.object(fc, "_buscar_openweather_atual", side_effect=_openweather_atual_lento), \
         patch.object(fc, "_buscar_openweather_previsao", side_effect=_openweather_previsao_lenta), \
         patch.object(fc, "_buscar_ana", side_effect=_ana_lenta), \
         patch.object(fc, "_buscar_cptec_previsao", side_effect=_cptec_lento):
        inicio = time.monotonic()
        dados = fc.obter_dados_consolidados(-23.6, -46.5)
        duracao = time.monotonic() - inicio

    assert duracao < MARGEM_SEQUENCIAL_S, (
        f"levou {duracao:.2f}s — esperado bem menos que a soma sequencial "
        f"({ATRASO_POR_CHAMADA_S * 4:.2f}s), indicando que as chamadas não "
        "estão rodando em paralelo"
    )
    assert dados.precipitacao_atual_mm_h == 5.0
    assert dados.pico_previsto_mm_3h == 8.0
    assert dados.pluviometro_local_mm_h == 3.5
    assert dados.fonte_pluviometro_local == "ANA"
    assert dados.validacao_cptec == "Chuvoso"


def test_obter_dados_consolidados_ana_indisponivel_mantem_fail_safe():
    # ANA retornando None (fail-safe já existente) continua funcionando igual
    # depois da paralelização — só muda o agendamento das chamadas.
    with patch.object(fc, "_buscar_openweather_atual", return_value={"rain": {"1h": 1.0}}), \
         patch.object(fc, "_buscar_openweather_previsao", return_value={"list": []}), \
         patch.object(fc, "_buscar_ana", return_value=None), \
         patch.object(fc, "_buscar_cptec_previsao", return_value=None):
        dados = fc.obter_dados_consolidados(-23.6, -46.5)

    assert dados.pluviometro_local_mm_h is None
    assert dados.fonte_pluviometro_local is None


def test_obter_dados_consolidados_propaga_erro_do_openweather():
    # Comportamento pré-existente preservado: falha do OpenWeather (fonte
    # principal, sem fail-safe interno) ainda derruba a chamada, mesmo com
    # as outras 3 fontes rodando em paralelo e bem-sucedidas.
    with patch.object(fc, "_buscar_openweather_atual", side_effect=RuntimeError("timeout")), \
         patch.object(fc, "_buscar_openweather_previsao", return_value={"list": []}), \
         patch.object(fc, "_buscar_ana", return_value=None), \
         patch.object(fc, "_buscar_cptec_previsao", return_value=None):
        try:
            fc.obter_dados_consolidados(-23.6, -46.5)
            assert False, "deveria ter propagado o RuntimeError do OpenWeather"
        except RuntimeError:
            pass
