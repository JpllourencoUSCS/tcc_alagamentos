"""Testes da análise de sensibilidade dos pesos do AHP (03/10/2026)."""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest

import algoritmo_risco
from analise_sensibilidade import analisar, pesos_perturbados
from algoritmo_risco import PESOS


def test_pesos_perturbados_somam_1_e_mantem_proporcao_dos_demais():
    novos = pesos_perturbados(PESOS, "precipitacao_atual", 0.20)
    assert sum(novos.values()) == pytest.approx(1.0)
    assert novos["precipitacao_atual"] == pytest.approx(PESOS["precipitacao_atual"] * 1.2)
    # os outros dois mantêm a razão entre si
    assert novos["colaborativo"] / novos["previsao"] == pytest.approx(
        PESOS["colaborativo"] / PESOS["previsao"]
    )


def test_analise_nao_altera_os_pesos_do_modelo():
    originais = dict(PESOS)
    analisar()
    assert algoritmo_risco.PESOS == originais
