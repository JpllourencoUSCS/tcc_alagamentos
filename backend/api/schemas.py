"""Contratos Pydantic da API de ocorrências (Semana 3 — Henrique)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from constants import FonteDado, NivelRisco


class OcorrenciaCreate(BaseModel):
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    descricao: str | None = Field(default=None, max_length=300)
    # None = calculado automaticamente pelo backend via fusao_climatica + AHP
    # (ver T14_modelo_banco_de_dados.md, seção "Notas de projeto"); se o
    # cliente enviar um valor, ele sobrescreve o cálculo automático.
    nivel_risco: NivelRisco | None = None
    fonte: FonteDado
    chuva_mm: float | None = None
    descricao_clima: str | None = None
    temperatura: float | None = None
    umidade: int | None = Field(default=None, ge=0, le=100)
    id_usuario: str | None = None
    id_estacao_ref: int | None = None


class OcorrenciaOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: int
    latitude: float
    longitude: float
    data_hora: datetime
    descricao: str | None
    nivel_risco: NivelRisco
    fonte: FonteDado
    chuva_mm: float | None
    descricao_clima: str | None
    temperatura: float | None
    umidade: int | None
    id_usuario: str | None
    id_estacao_ref: int | None
