"""Contratos Pydantic da API de ocorrências (Semana 3 — Henrique)."""

from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field, model_validator

from constants import FonteDado, NivelRisco, dentro_de_sao_caetano


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

    # O sistema monitora só São Caetano do Sul: fora da área, 422 (07/10/2026). Antes só o
    # app recusava; qualquer outro cliente gravava pontos fora do escopo.
    @model_validator(mode="after")
    def dentro_da_area_monitorada(self):
        if not dentro_de_sao_caetano(self.latitude, self.longitude):
            raise ValueError("Localização fora de São Caetano do Sul (área monitorada pelo sistema).")
        return self


class ComponentesRisco(BaseModel):
    """Score 0-100 de cada componente do AHP; null = fonte sem dado (o peso
    dela foi redistribuído, ver T15 seção 6.3)."""

    precipitacao_atual: float | None
    previsao: float | None
    pluviometro_local: float | None
    colaborativo: float | None


class FontesRisco(BaseModel):
    precipitacao_atual: str | None
    previsao: str | None
    pluviometro_local: str | None


class AvisoInmetOut(BaseModel):
    """Aviso meteorológico oficial do INMET ativo para o município."""

    evento: str | None  # ex.: "Tempestade", "Chuvas Intensas"
    severidade: str | None  # "Perigo Potencial", "Perigo" ou "Grande Perigo"
    cor: str | None  # cor oficial do aviso (hex)
    inicio: str | None
    fim: str | None
    riscos: str | None


class PisoAvisoOut(BaseModel):
    """Aviso do INMET que elevou a classificação (piso: Perigo -> Médio,
    Grande Perigo -> Alto; ver T15, seção 6.5)."""

    nivel: NivelRisco
    evento: str | None
    severidade: str | None


class RiscoOut(BaseModel):
    """Risco de alagamento calculado agora para um ponto (GET /risco)."""

    latitude: float
    longitude: float
    # Classe final, já com o piso dos avisos do INMET
    classificacao: NivelRisco
    # Classe do índice AHP antes do piso; igual a `classificacao` quando nenhum aviso elevou
    classificacao_indice: NivelRisco
    piso_aviso_inmet: PisoAvisoOut | None
    score_final: float
    componentes: ComponentesRisco
    precipitacao_atual_mm_h: float
    pico_previsto_mm_3h: float
    pluviometro_local_mm_h: float | None
    reportes_colaborativos: int
    # Validação cruzada qualitativa, fora do AHP (INMET no lugar do CPTEC desde 06/10/2026)
    previsao_inmet: str | None
    avisos_inmet: list[AvisoInmetOut]
    fontes: FontesRisco
    dados_em_cache: bool


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
