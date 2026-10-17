"""
Testes da Open-Meteo e da regra de fusão (fusao_climatica.py, 16/10/2026): conversão
da chuva atual para mm/h, pico de 3 h nas próximas 24 h e a fusão OpenWeather × Open-Meteo
(maior valor; divergência quando as fontes caem em faixas diferentes da escala da OMM).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

import fusao_climatica as fc
from algoritmo_risco import PESOS, faixa_intensidade


def _horario(inicio_dia: str, valores: list[float]) -> dict:
    return {"time": [f"{inicio_dia}T{h:02d}:00" for h in range(len(valores))], "precipitation": valores}


# ---------- Conversões da Open-Meteo ----------

def test_chuva_atual_de_15_min_vira_mm_por_hora():
    dados = {"current": {"time": "2026-10-16T22:30", "interval": 900, "precipitation": 0.5}}
    assert fc.precipitacao_atual_open_meteo(dados) == pytest.approx(2.0)


def test_chuva_atual_ausente_e_none():
    assert fc.precipitacao_atual_open_meteo(None) is None
    assert fc.precipitacao_atual_open_meteo({"current": {}}) is None


def test_pico_3h_comeca_na_hora_em_curso_e_usa_blocos_de_3_horas():
    valores = [0.0] * 24
    valores[11], valores[12], valores[13] = 9.0, 9.0, 9.0   # chuva já passada (11h-13h)
    valores[15], valores[16], valores[17] = 2.0, 3.0, 4.0   # 15:00, 16:00 e 17:00 = 9 mm
    dados = {
        "current": {"time": "2026-10-16T14:15", "interval": 900, "precipitation": 0.0},
        "hourly": _horario("2026-10-16", valores),
    }
    # Cada valor é o acumulado da hora que termina no horário; às 14:15, a hora em curso
    # termina às 15:00 — os blocos começam aí (15:00-17:00, 18:00-20:00...)
    assert fc.pico_3h_open_meteo(dados) == pytest.approx(9.0)


def test_pico_3h_sem_horas_seguintes_e_none():
    dados = {"current": {"time": "2026-10-16T23:30"}, "hourly": _horario("2026-10-16", [1.0] * 24)}
    assert fc.pico_3h_open_meteo(dados) is None


# ---------- Regra de fusão ----------

def test_fusao_usa_o_maior_valor():
    r = fc.fundir(1.0, 2.0)
    assert r["valor"] == 2.0
    assert r["fonte"] == "Open-Meteo"
    assert r["divergente"] is False  # as duas na faixa leve (< 2,5 mm/h)


def test_fusao_com_valores_iguais_cita_as_duas_fontes():
    assert fc.fundir(0.0, 0.0)["fonte"] == "OpenWeather e Open-Meteo"


def test_divergencia_quando_as_fontes_caem_em_faixas_diferentes():
    r = fc.fundir(1.0, 10.0)  # leve × forte
    assert r["divergente"] is True
    assert r["valor"] == 10.0


def test_divergencia_do_acumulado_de_3h_usa_a_intensidade_media():
    # 6 mm em 3 h = 2 mm/h (leve) × 9 mm em 3 h = 3 mm/h (moderada)
    assert fc.fundir(6.0, 9.0, horas=3)["divergente"] is True
    assert fc.fundir(3.0, 6.0, horas=3)["divergente"] is False


def test_fusao_com_uma_fonte_so_usa_a_disponivel():
    r = fc.fundir(None, 3.0)
    assert (r["valor"], r["fonte"], r["divergente"]) == (3.0, "Open-Meteo", False)


def test_fusao_sem_nenhuma_fonte_e_none():
    assert fc.fundir(None, None) is None


def test_faixas_da_omm():
    assert [faixa_intensidade(v) for v in (0.0, 2.4, 2.5, 7.6, 49.9, 50.0)] == [0, 0, 1, 2, 2, 3]


# ---------- Pesos do AHP com três critérios (16/10/2026) ----------

def test_pesos_tres_criterios_somam_1():
    assert set(PESOS) == {"precipitacao_atual", "previsao", "colaborativo"}
    assert sum(PESOS.values()) == pytest.approx(1.0)
    assert (PESOS["precipitacao_atual"], PESOS["previsao"], PESOS["colaborativo"]) == (0.54, 0.30, 0.16)
