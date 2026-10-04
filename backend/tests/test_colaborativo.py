"""
Testes do agregador de reportes colaborativos (servicos/colaborativo.py,
03/10/2026 — componente C4 do AHP).

Duas camadas, como no resto da suíte: a regra de cálculo é pura (sem banco) e
testada direto; a busca por raio/janela usa PostGIS de verdade via
`db_session` (pulada sem DATABASE_URL).
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import func, select

from api.ocorrencias import get_classificador_risco
from db.models import Ocorrencia, ReporteColaborativoAgregado
from db.session import get_db
from fusao_climatica import DadosClimaticosConsolidados
from main import app
from servicos.classificacao import ClassificadorRiscoReal
from servicos.colaborativo import (
    JANELA_HORAS,
    RAIO_METROS,
    ReporteProximo,
    buscar_reportes_proximos,
    calcular_score_colaborativo,
    obter_score_colaborativo,
    peso_reporte,
)

AGORA = datetime(2026, 10, 3, 15, 0, tzinfo=timezone.utc)
# Centro de São Caetano do Sul (mesmo de MapaFragment.kt)
LAT, LON = -23.6229, -46.5548


def _reporte(nivel="Alto", minutos_atras=0, distancia_m=0.0):
    return ReporteProximo(nivel, AGORA - timedelta(minutes=minutos_atras), distancia_m)


# ---------- Regra de cálculo (pura) ----------

def test_peso_maximo_para_reporte_agora_no_ponto():
    assert peso_reporte(_reporte(), AGORA) == 1.0


def test_peso_decai_com_tempo_e_distancia():
    meio_caminho = _reporte(minutos_atras=JANELA_HORAS * 30, distancia_m=RAIO_METROS / 2)
    assert peso_reporte(meio_caminho, AGORA) == pytest.approx(0.25)


def test_peso_zero_fora_da_janela_ou_do_raio():
    assert peso_reporte(_reporte(minutos_atras=JANELA_HORAS * 60 + 1), AGORA) == 0.0
    assert peso_reporte(_reporte(distancia_m=RAIO_METROS + 1), AGORA) == 0.0


def test_sem_reportes_suficientes_devolve_none_nao_zero():
    # None aciona o fail-safe 2 do AHP; 0.0 diria "reportes indicam risco zero"
    assert calcular_score_colaborativo([], AGORA) is None
    assert calcular_score_colaborativo([_reporte("Alto")], AGORA) is None


def test_reportes_iguais_dao_o_valor_do_nivel():
    resultado = calcular_score_colaborativo([_reporte("Alto"), _reporte("Alto", 30)], AGORA)
    assert resultado.score == 80.0
    assert resultado.quantidade_reportes == 2


def test_reporte_mais_recente_pesa_mais():
    # Alto agora (peso 1) e Baixo há 90 min (peso 0,5): média ponderada
    # (80*1 + 15*0,5) / 1,5 = 58,3
    resultado = calcular_score_colaborativo(
        [_reporte("Alto", 0), _reporte("Baixo", 90)], AGORA
    )
    assert resultado.score == pytest.approx(58.3)


def test_reportes_com_peso_zero_nao_contam_para_o_minimo():
    resultado = calcular_score_colaborativo(
        [_reporte("Alto"), _reporte("Alto", minutos_atras=JANELA_HORAS * 60 + 5)], AGORA
    )
    assert resultado is None


def test_score_fica_na_escala_0_100():
    resultado = calcular_score_colaborativo([_reporte("Médio"), _reporte("Baixo")], AGORA)
    assert 0 <= resultado.score <= 100


# ---------- Busca por raio/janela no PostGIS (integração) ----------

def _inserir(db, lat, lon, nivel="Alto", minutos_atras=10, fonte="usuario", referencia=AGORA):
    db.add(Ocorrencia(
        latitude=lat, longitude=lon, nivel_risco=nivel, fonte=fonte,
        data_hora=referencia - timedelta(minutes=minutos_atras),
    ))
    db.flush()


def test_busca_so_reportes_de_usuario_no_raio_e_na_janela(db_session):
    _inserir(db_session, LAT, LON)                              # entra
    _inserir(db_session, LAT + 0.005, LON)                      # ~555 m: entra
    _inserir(db_session, LAT + 0.02, LON)                       # ~2,2 km: fora do raio
    _inserir(db_session, LAT, LON, minutos_atras=JANELA_HORAS * 60 + 10)  # fora da janela
    _inserir(db_session, LAT, LON, fonte="openweather")         # não é reporte de usuário

    reportes = buscar_reportes_proximos(db_session, LAT, LON, AGORA)

    assert len(reportes) == 2
    distancias = sorted(r.distancia_m for r in reportes)
    assert distancias[0] == pytest.approx(0, abs=1)
    assert distancias[1] == pytest.approx(555, rel=0.02)


def test_obter_score_registra_agregado_na_sessao(db_session):
    _inserir(db_session, LAT, LON, "Alto")
    _inserir(db_session, LAT + 0.001, LON, "Médio")

    resultado = obter_score_colaborativo(db_session, LAT, LON, AGORA)
    db_session.flush()

    assert resultado is not None and 45 < resultado.score < 80
    registro = db_session.execute(select(ReporteColaborativoAgregado)).scalar_one()
    assert registro.quantidade_reportes == 2
    assert registro.score == resultado.score
    # A área registrada contém o ponto avaliado
    contem = db_session.execute(
        select(func.ST_Contains(registro.geom_area, func.ST_SetSRID(func.ST_MakePoint(LON, LAT), 4326)))
    ).scalar_one()
    assert contem


def test_post_sem_nivel_usa_reportes_colaborativos(db_session):
    """Ponta a ponta no backend: dois reportes 'Alto' recentes no mesmo ponto,
    clima seco (fontes mockadas) — o colaborativo entra no AHP e aparece no
    score. Prova que o componente C4 deixou de ser sempre None."""
    # O classificador usa o relógio real (não AGORA), então os reportes
    # também são relativos a ele
    agora_real = datetime.now(timezone.utc)
    _inserir(db_session, LAT, LON, "Alto", minutos_atras=5, referencia=agora_real)
    _inserir(db_session, LAT, LON, "Alto", minutos_atras=5, referencia=agora_real)
    seco = DadosClimaticosConsolidados(
        lat=LAT, lon=LON, precipitacao_atual_mm_h=0.0, pico_previsto_mm_3h=0.0,
        fonte_precipitacao_atual="OpenWeather", fonte_previsao="OpenWeather",
    )
    classificador = ClassificadorRiscoReal(db_session)
    with patch("servicos.classificacao.obter_dados_consolidados_em_cache", return_value=(seco, False)):
        resultado = classificador.classificar(LAT, LON)

    assert resultado["score_colaborativo"] is not None
    assert resultado["score_colaborativo"] > 70
    # Com chuva zero, todo o score vem do colaborativo (15% sem ANA)
    assert resultado["score_final"] > 0


def test_post_sem_nivel_integrado_grava_ocorrencia(db_session):
    seco = DadosClimaticosConsolidados(
        lat=LAT, lon=LON, precipitacao_atual_mm_h=0.0, pico_previsto_mm_3h=0.0,
        fonte_precipitacao_atual="OpenWeather", fonte_previsao="OpenWeather",
    )
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_classificador_risco] = lambda: ClassificadorRiscoReal(db_session)
    try:
        with patch("servicos.classificacao.obter_dados_consolidados_em_cache", return_value=(seco, False)):
            resp = TestClient(app).post(
                "/ocorrencias", json={"latitude": LAT, "longitude": LON, "fonte": "usuario"}
            )
    finally:
        app.dependency_overrides.clear()

    assert resp.status_code == 201
    assert resp.json()["nivel_risco"] == "Baixo"
