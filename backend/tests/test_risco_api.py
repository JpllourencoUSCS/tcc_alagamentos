"""
Testes do GET /risco (03/10/2026): risco atual num ponto, com os componentes
do AHP separados. Contrato com classificador fake + integração com o
classificador real contra PostGIS (fontes climáticas mockadas).
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient
from sqlalchemy import func, select

from api.ocorrencias import get_classificador_risco
from db.models import Ocorrencia, ReporteColaborativoAgregado
from fusao_climatica import DadosClimaticosConsolidados, FonteClimaticaIndisponivel
from main import app
from servicos.classificacao import ClassificadorRiscoReal

LAT, LON = -23.6229, -46.5548

AVALIACAO_EXEMPLO = {
    "latitude": LAT, "longitude": LON, "classificacao": "Médio", "score_final": 42.0,
    "classificacao_indice": "Médio", "piso_aviso_inmet": None,
    "componentes": {"precipitacao_atual": 50.0, "previsao": 30.0,
                    "pluviometro_local": None, "colaborativo": None},
    "precipitacao_atual_mm_h": 7.6, "pico_previsto_mm_3h": 9.0,
    "pluviometro_local_mm_h": None, "reportes_colaborativos": 0,
    "previsao_inmet": None, "avisos_inmet": [],
    "fontes": {"precipitacao_atual": "OpenWeather", "previsao": "OpenWeather", "pluviometro_local": None},
    "dados_em_cache": False,
}


class _Fake:
    def __init__(self, avaliacao=None, erro=None):
        self.avaliacao, self.erro = avaliacao, erro

    def avaliar(self, lat, lon):
        if self.erro:
            raise self.erro
        return {**self.avaliacao, "latitude": lat, "longitude": lon}


def _get(classificador, **params):
    app.dependency_overrides[get_classificador_risco] = lambda: classificador
    try:
        return TestClient(app).get("/risco", params=params)
    finally:
        app.dependency_overrides.clear()


def test_risco_devolve_classificacao_e_componentes():
    resp = _get(_Fake(AVALIACAO_EXEMPLO), latitude=LAT, longitude=LON)
    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["classificacao"] == "Médio"
    assert corpo["componentes"]["pluviometro_local"] is None
    assert corpo["latitude"] == LAT


def test_risco_exige_coordenadas_validas():
    assert _get(_Fake(AVALIACAO_EXEMPLO), latitude=LAT).status_code == 422
    assert _get(_Fake(AVALIACAO_EXEMPLO), latitude=95, longitude=LON).status_code == 422


def test_risco_com_fonte_climatica_fora_do_ar_e_503():
    resp = _get(_Fake(erro=FonteClimaticaIndisponivel("fora")), latitude=LAT, longitude=LON)
    assert resp.status_code == 503


def test_risco_integrado_inclui_colaborativo_e_nao_grava_nada(db_session):
    agora = datetime.now(timezone.utc)
    for _ in range(2):
        db_session.add(Ocorrencia(
            latitude=LAT, longitude=LON, nivel_risco="Alto", fonte="usuario",
            data_hora=agora - timedelta(minutes=10),
        ))
    db_session.flush()
    chuva_moderada = DadosClimaticosConsolidados(
        lat=LAT, lon=LON, precipitacao_atual_mm_h=5.0, pico_previsto_mm_3h=12.0,
        fonte_precipitacao_atual="OpenWeather", fonte_previsao="OpenWeather",
        previsao_inmet="Muitas nuvens com pancadas de chuva e trovoadas isoladas",
        avisos_inmet=[{"evento": "Tempestade", "severidade": "Perigo Potencial", "cor": "#FFFE00",
                       "inicio": "2026-10-06 08:52", "fim": "2026-10-06 23:59",
                       "riscos": "Chuva entre 20 e 30 mm/h"}],
    )
    with patch("servicos.classificacao.obter_dados_consolidados_em_cache",
               return_value=(chuva_moderada, True)):
        resp = _get(ClassificadorRiscoReal(db_session), latitude=LAT, longitude=LON)

    assert resp.status_code == 200
    corpo = resp.json()
    assert corpo["reportes_colaborativos"] == 2
    assert corpo["componentes"]["colaborativo"] == 80.0
    assert corpo["componentes"]["pluviometro_local"] is None   # ANA sem credencial
    assert corpo["previsao_inmet"].startswith("Muitas nuvens")
    assert corpo["avisos_inmet"][0]["severidade"] == "Perigo Potencial"
    assert corpo["dados_em_cache"] is True
    # Consulta não registra agregado (só o POST de ocorrência registra)
    assert db_session.scalar(select(func.count()).select_from(ReporteColaborativoAgregado)) == 0
