"""
Endpoints REST de ocorrências (Semana 3 — Henrique, reconstruído em 18/08/2026):
criar, listar (com filtro de fonte/nível/período/região) e obter uma ocorrência.

A dependência `get_ocorrencia_repository` é o ponto de troca entre a
implementação real (SQLAlchemy contra Postgres/PostGIS) e uma fake em memória
nos testes (ver backend/tests/test_ocorrencias_api.py) — os testes não
precisam de um banco vivo para validar roteamento, validação e filtros.
"""

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from api.schemas import OcorrenciaCreate, OcorrenciaOut
from constants import FonteDado, NivelRisco
from db.repository import FiltrosOcorrencia, OcorrenciaRepository
from db.session import get_db
from servicos.classificacao import ClassificadorRiscoProtocol, ClassificadorRiscoReal

router = APIRouter(prefix="/ocorrencias", tags=["ocorrencias"])


def get_ocorrencia_repository(db: Session = Depends(get_db)) -> OcorrenciaRepository:
    return OcorrenciaRepository(db)


def get_classificador_risco() -> ClassificadorRiscoProtocol:
    return ClassificadorRiscoReal()


@router.post("", response_model=OcorrenciaOut, status_code=201)
def criar_ocorrencia(
    dados: OcorrenciaCreate,
    repo: OcorrenciaRepository = Depends(get_ocorrencia_repository),
    classificador: ClassificadorRiscoProtocol = Depends(get_classificador_risco),
) -> OcorrenciaOut:
    valores = dados.model_dump()

    # nivel_risco ausente = calcular automaticamente (fusão de fontes + AHP);
    # se o cliente mandou um valor, ele decide (reporte manual do usuário
    # pode divergir do que as fontes automáticas indicam nesse instante).
    if valores["nivel_risco"] is None:
        resultado = classificador.classificar(valores["latitude"], valores["longitude"])
        valores["nivel_risco"] = resultado["classificacao"]
        if valores.get("chuva_mm") is None:
            valores["chuva_mm"] = resultado["chuva_mm"]

    ocorrencia = repo.criar(valores)
    return OcorrenciaOut.model_validate(ocorrencia)


@router.get("", response_model=list[OcorrenciaOut])
def listar_ocorrencias(
    # Tipados com os enums compartilhados (não `str`): um valor fora do
    # vocabulário vira 422 automático, em vez de silenciosamente não bater com
    # nada e devolver lista vazia (revisão de código, Semana 6).
    fonte: FonteDado | None = None,
    nivel_risco: NivelRisco | None = None,
    data_inicio: datetime | None = None,
    data_fim: datetime | None = None,
    lat_min: float | None = Query(default=None),
    lon_min: float | None = Query(default=None),
    lat_max: float | None = Query(default=None),
    lon_max: float | None = Query(default=None),
    skip: int = Query(default=0, ge=0),
    limit: int = Query(default=100, ge=1, le=500),
    repo: OcorrenciaRepository = Depends(get_ocorrencia_repository),
) -> list[OcorrenciaOut]:
    bbox = None
    coords_bbox = (lat_min, lon_min, lat_max, lon_max)
    if any(c is not None for c in coords_bbox):
        if any(c is None for c in coords_bbox):
            raise HTTPException(
                status_code=422,
                detail="Filtro de região exige lat_min, lon_min, lat_max e lon_max juntos.",
            )
        bbox = coords_bbox

    filtros = FiltrosOcorrencia(
        fonte=fonte,
        nivel_risco=nivel_risco,
        data_inicio=data_inicio,
        data_fim=data_fim,
        bbox=bbox,
        skip=skip,
        limit=limit,
    )
    ocorrencias = repo.listar(filtros)
    return [OcorrenciaOut.model_validate(o) for o in ocorrencias]


@router.get("/{id}", response_model=OcorrenciaOut)
def obter_ocorrencia(
    id: int,
    repo: OcorrenciaRepository = Depends(get_ocorrencia_repository),
) -> OcorrenciaOut:
    ocorrencia = repo.obter(id)
    if ocorrencia is None:
        raise HTTPException(status_code=404, detail="Ocorrência não encontrada.")
    return OcorrenciaOut.model_validate(ocorrencia)
