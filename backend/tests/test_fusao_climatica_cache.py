"""
Testes do cache de dados climáticos e do tratamento de falha do OpenWeather
(fusao_climatica.py, 03/10/2026 — otimização da Semana 10 e correção da chave
fixa "sua_chave_aqui").
"""

import sys
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

import fusao_climatica as fc
from api.ocorrencias import get_classificador_risco, get_ocorrencia_repository
from main import app
from test_ocorrencias_api import FakeOcorrenciaRepository, PAYLOAD_BASE


@pytest.fixture(autouse=True)
def _cache_limpo():
    fc.limpar_cache()
    yield
    fc.limpar_cache()


def _dados(chuva=1.0):
    return fc.DadosClimaticosConsolidados(
        lat=-23.62, lon=-46.55, precipitacao_atual_mm_h=chuva, pico_previsto_mm_3h=0.0,
        fonte_precipitacao_atual="OpenWeather", fonte_previsao="OpenWeather",
    )


def test_segunda_consulta_na_mesma_celula_vem_do_cache():
    with patch.object(fc, "obter_dados_consolidados", return_value=_dados()) as busca:
        # ~40 m de distância, mesma célula de 0,01° (-23,62 / -46,55)
        _, do_cache_1 = fc.obter_dados_consolidados_em_cache(-23.6219, -46.5531, agora=0)
        _, do_cache_2 = fc.obter_dados_consolidados_em_cache(-23.6222, -46.5534, agora=60)
    assert (do_cache_1, do_cache_2) == (False, True)
    assert busca.call_count == 1


def test_cache_expira_depois_do_ttl():
    with patch.object(fc, "obter_dados_consolidados", return_value=_dados()) as busca:
        fc.obter_dados_consolidados_em_cache(-23.6229, -46.5548, agora=0)
        _, do_cache = fc.obter_dados_consolidados_em_cache(-23.6229, -46.5548, agora=fc.CACHE_TTL_S + 1)
    assert do_cache is False
    assert busca.call_count == 2


def test_celulas_diferentes_nao_compartilham_cache():
    with patch.object(fc, "obter_dados_consolidados", return_value=_dados()) as busca:
        fc.obter_dados_consolidados_em_cache(-23.62, -46.55, agora=0)
        fc.obter_dados_consolidados_em_cache(-23.66, -46.53, agora=1)  # Santo André
    assert busca.call_count == 2


def test_falha_nao_entra_no_cache():
    with patch.object(fc, "obter_dados_consolidados",
                      side_effect=[fc.FonteClimaticaIndisponivel("fora"), _dados()]) as busca:
        with pytest.raises(fc.FonteClimaticaIndisponivel):
            fc.obter_dados_consolidados_em_cache(-23.62, -46.55, agora=0)
        _, do_cache = fc.obter_dados_consolidados_em_cache(-23.62, -46.55, agora=1)
    assert do_cache is False
    assert busca.call_count == 2


def test_sem_chave_openweather_falha_com_erro_claro():
    with patch.object(fc, "OPENWEATHER_API_KEY", ""), \
         patch.object(fc, "_buscar_ana", return_value=None), \
         patch.object(fc, "_buscar_cptec_previsao", return_value=None):
        with pytest.raises(fc.FonteClimaticaIndisponivel, match="OPENWEATHER_API_KEY"):
            fc.obter_dados_consolidados(-23.62, -46.55)


def test_erro_de_rede_do_openweather_vira_fonte_indisponivel():
    with patch.object(fc, "_buscar_openweather_atual", side_effect=ConnectionError("sem rede")), \
         patch.object(fc, "_buscar_openweather_previsao", return_value={"list": []}), \
         patch.object(fc, "_buscar_ana", return_value=None), \
         patch.object(fc, "_buscar_cptec_previsao", return_value=None):
        with pytest.raises(fc.FonteClimaticaIndisponivel, match="sem rede"):
            fc.obter_dados_consolidados(-23.62, -46.55)


class _ClassificadorQueFalha:
    def classificar(self, lat, lon):
        raise fc.FonteClimaticaIndisponivel("OpenWeather fora do ar")


def test_post_sem_nivel_com_fonte_fora_do_ar_responde_503():
    app.dependency_overrides[get_ocorrencia_repository] = lambda: FakeOcorrenciaRepository()
    app.dependency_overrides[get_classificador_risco] = lambda: _ClassificadorQueFalha()
    try:
        payload = {k: v for k, v in PAYLOAD_BASE.items() if k != "nivel_risco"}
        resp = TestClient(app).post("/ocorrencias", json=payload)
    finally:
        app.dependency_overrides.clear()
    assert resp.status_code == 503
    assert "manualmente" in resp.json()["detail"]
