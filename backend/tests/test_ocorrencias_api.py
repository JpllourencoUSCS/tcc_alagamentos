"""
Testes da API de ocorrências (Semana 3 — Henrique).

Usa um repositório fake em memória no lugar do SQLAlchemy real, via
dependency_override do FastAPI — testa contrato HTTP (rotas, validação,
filtros, códigos de status), não a integração com Postgres/PostGIS em si
(isso é objeto da Semana 5, contra um banco de verdade).

Rodar a partir de backend/: pytest tests/test_ocorrencias_api.py -v
"""

import sys
from datetime import datetime, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from fastapi.testclient import TestClient

from api.ocorrencias import get_classificador_risco, get_ocorrencia_repository
from db.models import Ocorrencia
from db.repository import FiltrosOcorrencia
from main import app


class FakeOcorrenciaRepository:
    """Implementa o mesmo contrato de OcorrenciaRepositoryProtocol, sobre uma
    lista Python — nenhuma dependência de banco."""

    def __init__(self):
        self._dados: list[Ocorrencia] = []
        self._proximo_id = 1

    def criar(self, dados: dict) -> Ocorrencia:
        ocorrencia = Ocorrencia(**dados)
        ocorrencia.id = self._proximo_id
        ocorrencia.data_hora = datetime.now(timezone.utc)
        self._proximo_id += 1
        self._dados.append(ocorrencia)
        return ocorrencia

    def listar(self, filtros: FiltrosOcorrencia) -> list[Ocorrencia]:
        resultado = self._dados
        if filtros.fonte is not None:
            resultado = [o for o in resultado if o.fonte == filtros.fonte]
        if filtros.nivel_risco is not None:
            resultado = [o for o in resultado if o.nivel_risco == filtros.nivel_risco]
        if filtros.data_inicio is not None:
            resultado = [o for o in resultado if o.data_hora >= filtros.data_inicio]
        if filtros.data_fim is not None:
            resultado = [o for o in resultado if o.data_hora <= filtros.data_fim]
        if filtros.bbox is not None:
            lat_min, lon_min, lat_max, lon_max = filtros.bbox
            resultado = [
                o for o in resultado
                if lat_min <= o.latitude <= lat_max and lon_min <= o.longitude <= lon_max
            ]
        resultado = sorted(resultado, key=lambda o: o.data_hora, reverse=True)
        return resultado[filtros.skip : filtros.skip + filtros.limit]

    def obter(self, id: int) -> Ocorrencia | None:
        return next((o for o in self._dados if o.id == id), None)


class FakeClassificadorRisco:
    """Fake de ClassificadorRiscoProtocol — nunca faz chamada HTTP real.
    Conta quantas vezes foi chamado, para provar que o override manual de
    nivel_risco (reporte de usuário) pula o cálculo automático."""

    def __init__(self, classificacao="Alto", chuva_mm=12.3):
        self.classificacao = classificacao
        self.chuva_mm = chuva_mm
        self.chamadas = 0

    def classificar(self, lat: float, lon: float) -> dict:
        self.chamadas += 1
        return {"classificacao": self.classificacao, "chuva_mm": self.chuva_mm}


def _cliente(classificador: FakeClassificadorRisco | None = None):
    fake_repo = FakeOcorrenciaRepository()
    fake_classificador = classificador or FakeClassificadorRisco()
    app.dependency_overrides[get_ocorrencia_repository] = lambda: fake_repo
    app.dependency_overrides[get_classificador_risco] = lambda: fake_classificador
    return TestClient(app), fake_repo, fake_classificador


PAYLOAD_BASE = {
    "latitude": -23.6639,
    "longitude": -46.5383,
    "descricao": "Alagamento na Av. Industrial",
    "nivel_risco": "Alto",
    "fonte": "usuario",
}


def test_criar_ocorrencia():
    client, _, _ = _cliente()
    resp = client.post("/ocorrencias", json=PAYLOAD_BASE)
    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["id"] == 1
    assert corpo["nivel_risco"] == "Alto"
    assert corpo["fonte"] == "usuario"


def test_criar_ocorrencia_rejeita_nivel_risco_invalido():
    client, _, _ = _cliente()
    payload = {**PAYLOAD_BASE, "nivel_risco": "Altíssimo"}
    resp = client.post("/ocorrencias", json=payload)
    assert resp.status_code == 422


def test_listar_ocorrencias_vazio():
    client, _, _ = _cliente()
    resp = client.get("/ocorrencias")
    assert resp.status_code == 200
    assert resp.json() == []


def test_listar_ocorrencias_filtra_por_fonte():
    client, _, _ = _cliente()
    client.post("/ocorrencias", json=PAYLOAD_BASE)
    client.post("/ocorrencias", json={**PAYLOAD_BASE, "fonte": "openweather", "nivel_risco": "Baixo"})

    resp = client.get("/ocorrencias", params={"fonte": "openweather"})
    assert resp.status_code == 200
    corpo = resp.json()
    assert len(corpo) == 1
    assert corpo[0]["fonte"] == "openweather"


def test_listar_ocorrencias_filtra_por_regiao_bbox():
    client, _, _ = _cliente()
    client.post("/ocorrencias", json=PAYLOAD_BASE)  # Santo André (~ -23.66, -46.54)
    client.post("/ocorrencias", json={**PAYLOAD_BASE, "latitude": -3.7319, "longitude": -38.5267})  # Fortaleza

    resp = client.get(
        "/ocorrencias",
        params={"lat_min": -24, "lon_min": -47, "lat_max": -23, "lon_max": -46},
    )
    assert resp.status_code == 200
    corpo = resp.json()
    assert len(corpo) == 1
    assert corpo[0]["latitude"] == PAYLOAD_BASE["latitude"]


def test_listar_ocorrencias_bbox_incompleto_e_422():
    client, _, _ = _cliente()
    resp = client.get("/ocorrencias", params={"lat_min": -24})
    assert resp.status_code == 422


def test_listar_ocorrencias_fonte_invalida_e_422():
    # Revisão de código (Semana 6): antes, fonte era `str` solto no endpoint —
    # um valor fora do vocabulário devolvia lista vazia (200) em vez de 422.
    client, _, _ = _cliente()
    resp = client.get("/ocorrencias", params={"fonte": "cemaden"})
    assert resp.status_code == 422


def test_obter_ocorrencia_existente():
    client, _, _ = _cliente()
    criada = client.post("/ocorrencias", json=PAYLOAD_BASE).json()
    resp = client.get(f"/ocorrencias/{criada['id']}")
    assert resp.status_code == 200
    assert resp.json()["id"] == criada["id"]


def test_obter_ocorrencia_inexistente_e_404():
    client, _, _ = _cliente()
    resp = client.get("/ocorrencias/999")
    assert resp.status_code == 404


# ---------- Semana 5: classificação automática de risco ----------

def test_criar_ocorrencia_sem_nivel_risco_calcula_automaticamente():
    fake_classificador = FakeClassificadorRisco(classificacao="Médio", chuva_mm=5.5)
    client, _, classificador = _cliente(fake_classificador)

    payload = {k: v for k, v in PAYLOAD_BASE.items() if k != "nivel_risco"}
    resp = client.post("/ocorrencias", json=payload)

    assert resp.status_code == 201
    corpo = resp.json()
    assert corpo["nivel_risco"] == "Médio"
    assert corpo["chuva_mm"] == 5.5
    assert classificador.chamadas == 1


def test_criar_ocorrencia_com_nivel_risco_nao_chama_classificador():
    client, _, classificador = _cliente()
    resp = client.post("/ocorrencias", json=PAYLOAD_BASE)

    assert resp.status_code == 201
    assert resp.json()["nivel_risco"] == PAYLOAD_BASE["nivel_risco"]
    assert classificador.chamadas == 0
