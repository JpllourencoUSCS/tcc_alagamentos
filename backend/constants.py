"""
Vocabulário compartilhado entre o schema do banco (backend/db/models.py,
backend/db/schema.sql) e a camada de API (backend/api/schemas.py).

backend/db/schema.sql é DDL puro (não importa Python) — os valores abaixo
precisam ser mantidos manualmente em sincronia com os CHECK constraints
definidos lá. models.py, por outro lado, gera seus CHECK constraints a partir
destes enums, então não há duplicação entre modelo ORM e schema Pydantic.
"""

from enum import Enum


class NivelRisco(str, Enum):
    BAIXO = "Baixo"
    MEDIO = "Médio"
    ALTO = "Alto"


# Área monitorada (escopo do projeto desde 03/09/2026): retângulo aproximado de São Caetano
# do Sul, com folga nas bordas — o mesmo do app (AreaBusca.SAO_CAETANO_DO_SUL, Localizacao.kt).
# O app confere a cidade pelo geocodificador; a API só garante este limite (07/10/2026).
AREA_SAO_CAETANO_DO_SUL = {"lat_min": -23.650, "lon_min": -46.600, "lat_max": -23.595, "lon_max": -46.535}


def dentro_de_sao_caetano(latitude: float, longitude: float) -> bool:
    a = AREA_SAO_CAETANO_DO_SUL
    return a["lat_min"] <= latitude <= a["lat_max"] and a["lon_min"] <= longitude <= a["lon_max"]


class FonteDado(str, Enum):
    USUARIO = "usuario"
    OPENWEATHER = "openweather"
    ANA = "ana"
    # Até 07/10/2026 era CPTEC = "cptec"; o CPTEC foi substituído pelo INMET em 06/10/2026
    # (bancos existentes: backend/db/migracao_2026-10-07_fonte_inmet.sql)
    INMET = "inmet"
