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


class FonteDado(str, Enum):
    USUARIO = "usuario"
    OPENWEATHER = "openweather"
    ANA = "ana"
    CPTEC = "cptec"
