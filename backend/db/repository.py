"""
Camada de acesso a dados para `ocorrencias` (Semana 3 — Henrique).

Isola os endpoints (backend/api/ocorrencias.py) do SQLAlchemy: o router chama
`OcorrenciaRepository`, não `Session` diretamente. Isso é o que permite os testes
da API (backend/tests/test_ocorrencias_api.py) trocarem a implementação real por
uma fake em memória via dependency_override do FastAPI, sem precisar de um
Postgres/PostGIS de verdade rodando neste ambiente de desenvolvimento.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import Protocol

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from db.models import Ocorrencia


@dataclass
class FiltrosOcorrencia:
    fonte: str | None = None
    nivel_risco: str | None = None
    data_inicio: datetime | None = None
    data_fim: datetime | None = None
    # bbox = (lat_min, lon_min, lat_max, lon_max) — filtro de região.
    bbox: tuple[float, float, float, float] | None = None
    skip: int = 0
    limit: int = 100


class OcorrenciaRepositoryProtocol(Protocol):
    """Contrato que a implementação real (SQLAlchemy) e a fake de teste
    precisam cumprir igualmente."""

    def criar(self, dados: dict) -> Ocorrencia: ...
    def listar(self, filtros: FiltrosOcorrencia) -> list[Ocorrencia]: ...
    def obter(self, id: int) -> Ocorrencia | None: ...


class OcorrenciaRepository:
    """Implementação real, contra o Postgres/PostGIS via SQLAlchemy."""

    def __init__(self, db: Session):
        self.db = db

    def criar(self, dados: dict) -> Ocorrencia:
        ocorrencia = Ocorrencia(**dados)
        self.db.add(ocorrencia)
        self.db.commit()
        self.db.refresh(ocorrencia)
        return ocorrencia

    def listar(self, filtros: FiltrosOcorrencia) -> list[Ocorrencia]:
        stmt = select(Ocorrencia)
        if filtros.fonte is not None:
            stmt = stmt.where(Ocorrencia.fonte == filtros.fonte)
        if filtros.nivel_risco is not None:
            stmt = stmt.where(Ocorrencia.nivel_risco == filtros.nivel_risco)
        if filtros.data_inicio is not None:
            stmt = stmt.where(Ocorrencia.data_hora >= filtros.data_inicio)
        if filtros.data_fim is not None:
            stmt = stmt.where(Ocorrencia.data_hora <= filtros.data_fim)
        if filtros.bbox is not None:
            # Revisão de performance (Semana 6): a versão anterior filtrava com
            # BETWEEN direto em latitude/longitude, colunas sem índice — full
            # scan a cada consulta de mapa (a mais frequente do app). `.intersects()`
            # do GeoAlchemy2 compila para o operador `&&` (overlap de bounding
            # box), o mesmo que o índice GiST criado em schema.sql
            # (idx_ocorrencias_geom) resolve nativamente — ver
            # T17_indexacao_espacial_fundamentacao.md, seção 4. Para dados do
            # tipo Point (o caso de `ocorrencias`), o bounding box de um ponto é
            # o próprio ponto, então `&&` aqui já é exato, não uma aproximação
            # que precisaria de um ST_Intersects/ST_Contains exato por cima.
            lat_min, lon_min, lat_max, lon_max = filtros.bbox
            envelope = func.ST_MakeEnvelope(lon_min, lat_min, lon_max, lat_max, 4326)
            stmt = stmt.where(Ocorrencia.geom.intersects(envelope))
        stmt = stmt.order_by(Ocorrencia.data_hora.desc()).offset(filtros.skip).limit(filtros.limit)
        return list(self.db.execute(stmt).scalars().all())

    def obter(self, id: int) -> Ocorrencia | None:
        return self.db.get(Ocorrencia, id)
