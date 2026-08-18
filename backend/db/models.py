"""
Modelos SQLAlchemy (ORM) para o schema PostgreSQL/PostGIS (Semana 2 — Henrique,
reconstruído em 18/08/2026).

Espelham backend/db/schema.sql. A coluna `geom` é gerenciada por trigger no banco
(ver trg_sync_geom em schema.sql) a partir de latitude/longitude — por isso ela é
lida aqui, mas o código da aplicação nunca deve escrevê-la diretamente; quem grava
lat/lon deixa o Postgres calcular o ponto.

Usados pelos endpoints FastAPI (Semana 3, backend/api/) e pela camada de
persistência (Semana 5).
"""

from datetime import datetime, timezone

from geoalchemy2 import Geometry
from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, String, Text
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship

from constants import FonteDado, NivelRisco


def _check_in(coluna: str, valores) -> str:
    """Monta a expressão SQL de um CHECK IN (...) a partir de um Enum, para não
    duplicar a lista de valores válidos entre models.py e constants.py."""
    lista = ", ".join(f"'{v.value}'" for v in valores)
    return f"{coluna} IN ({lista})"


class Base(DeclarativeBase):
    pass


class EstacaoReferencia(Base):
    """Estação física de medição consultada (hoje, só ANA — ver
    docs/T_arquitetura_fontes_dados_final.md sobre a saída do INMET/CEMADEN)."""

    __tablename__ = "estacoes_referencia"
    __table_args__ = (
        CheckConstraint(_check_in("fonte", [FonteDado.ANA]), name="ck_estacoes_fonte"),
        Index("idx_estacoes_geom", "geom", postgresql_using="gist"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    codigo_externo: Mapped[str] = mapped_column(String, nullable=False)
    nome: Mapped[str] = mapped_column(String, nullable=False)
    fonte: Mapped[str] = mapped_column(String, nullable=False)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    geom = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)

    ocorrencias: Mapped[list["Ocorrencia"]] = relationship(back_populates="estacao_ref")


class Ocorrencia(Base):
    """Registro de ocorrência — tanto reportes de usuário quanto leituras
    automáticas das fontes climáticas (OpenWeather/ANA/CPTEC)."""

    __tablename__ = "ocorrencias"
    __table_args__ = (
        CheckConstraint(_check_in("nivel_risco", NivelRisco), name="ck_ocorrencias_nivel_risco"),
        CheckConstraint(_check_in("fonte", FonteDado), name="ck_ocorrencias_fonte"),
        Index("idx_ocorrencias_geom", "geom", postgresql_using="gist"),
        Index("idx_ocorrencias_data_hora", "data_hora"),
        Index("idx_ocorrencias_fonte", "fonte"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    latitude: Mapped[float] = mapped_column(nullable=False)
    longitude: Mapped[float] = mapped_column(nullable=False)
    geom = mapped_column(Geometry(geometry_type="POINT", srid=4326), nullable=True)
    data_hora: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    nivel_risco: Mapped[str] = mapped_column(String, nullable=False)
    fonte: Mapped[str] = mapped_column(String, nullable=False)
    chuva_mm: Mapped[float | None] = mapped_column(nullable=True)
    descricao_clima: Mapped[str | None] = mapped_column(String, nullable=True)
    temperatura: Mapped[float | None] = mapped_column(nullable=True)
    umidade: Mapped[int | None] = mapped_column(nullable=True)
    id_usuario: Mapped[str | None] = mapped_column(String, nullable=True)
    id_estacao_ref: Mapped[int | None] = mapped_column(
        ForeignKey("estacoes_referencia.id"), nullable=True
    )

    estacao_ref: Mapped["EstacaoReferencia | None"] = relationship(back_populates="ocorrencias")


class ReporteColaborativoAgregado(Base):
    """Score 0-100 já agregado de reportes de usuários por área/janela de tempo —
    é o que alimenta o componente `reportes_colaborativos_score` de
    backend/algoritmo_risco.py. O módulo que calcula esse agregado a partir dos
    reportes brutos (Ocorrencia.fonte == 'usuario') ainda não existe (pendência
    aberta em 17/08 no CRONOGRAMA_STATUS.md); esta tabela só reserva onde o
    resultado do futuro módulo vai morar."""

    __tablename__ = "reportes_colaborativos_agregado"
    __table_args__ = (
        CheckConstraint("score BETWEEN 0 AND 100", name="ck_reportes_score_range"),
        Index("idx_reportes_geom_area", "geom_area", postgresql_using="gist"),
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    geom_area = mapped_column(Geometry(geometry_type="POLYGON", srid=4326), nullable=False)
    janela_inicio: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    janela_fim: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    score: Mapped[float] = mapped_column(nullable=False)
    quantidade_reportes: Mapped[int] = mapped_column(default=0, nullable=False)
    calculado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False
    )
