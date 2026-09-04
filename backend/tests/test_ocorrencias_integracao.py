"""
Testes de integração da API de ocorrências contra Postgres/PostGIS real
(Semana 10 — João).

Complementa test_ocorrencias_api.py (que usa um repositório fake em memória
para testar só o contrato HTTP): aqui o router usa `OcorrenciaRepository` de
verdade, ligado à sessão transacional de `db_session` (conftest.py) — cada
teste cria seus próprios dados via chamadas HTTP normais e tudo é desfeito no
rollback ao final da fixture, então o teste não depende de o banco já ter
dados (nem deixa dado nenhum para trás).

Precondição: `schema.sql` já aplicado no banco apontado por DATABASE_URL (ver
docs/CRONOGRAMA_STATUS.md, seção "Ambiente de desenvolvimento"). Sem
DATABASE_URL definida, toda a suíte é pulada (skip), não falha — mesmo
critério dos demais testes que dependem de Postgres no projeto.

Rodar a partir de backend/, com Postgres disponível:
    $env:DATABASE_URL = "postgresql+psycopg2://alagamentos:<senha>@localhost:5432/alagamentos"
    pytest tests/test_ocorrencias_integracao.py -v
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from fastapi.testclient import TestClient

from api.ocorrencias import get_classificador_risco
from db.session import get_db
from main import app
from test_ocorrencias_api import FakeClassificadorRisco, PAYLOAD_BASE


@pytest.fixture()
def client(db_session):
    app.dependency_overrides[get_db] = lambda: db_session
    app.dependency_overrides[get_classificador_risco] = lambda: FakeClassificadorRisco()
    yield TestClient(app)
    app.dependency_overrides.clear()


def test_criar_e_obter_ocorrencia(client):
    resp = client.post("/ocorrencias", json=PAYLOAD_BASE)
    assert resp.status_code == 201
    criada = resp.json()

    resp = client.get(f"/ocorrencias/{criada['id']}")
    assert resp.status_code == 200
    assert resp.json()["latitude"] == PAYLOAD_BASE["latitude"]


def test_listar_filtra_por_regiao_bbox_usando_indice_geoespacial(client):
    # Exercita o caminho real de db/repository.py (ST_MakeEnvelope + geom &&),
    # não a versão em Python puro do fake — prova que o filtro compila e
    # retorna certo contra o PostGIS de verdade.
    client.post("/ocorrencias", json=PAYLOAD_BASE)  # Santo André (~ -23.66, -46.54)
    client.post(
        "/ocorrencias",
        json={**PAYLOAD_BASE, "latitude": -3.7319, "longitude": -38.5267},  # Fortaleza
    )

    resp = client.get(
        "/ocorrencias",
        params={"lat_min": -24, "lon_min": -47, "lat_max": -23, "lon_max": -46},
    )
    assert resp.status_code == 200
    corpo = resp.json()
    assert len(corpo) == 1
    assert corpo[0]["latitude"] == PAYLOAD_BASE["latitude"]


def test_listar_ocorrencias_comeca_vazio(client):
    # Prova de que o isolamento funciona: se um teste anterior desta suíte
    # tivesse deixado dado para trás, esta lista não estaria vazia.
    resp = client.get("/ocorrencias")
    assert resp.status_code == 200
    assert resp.json() == []
