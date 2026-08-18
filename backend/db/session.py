"""
Engine e sessão do SQLAlchemy contra o PostgreSQL/PostGIS de produção.

A URL de conexão fica fora do código (variável de ambiente DATABASE_URL), pelo
mesmo motivo das credenciais da ANA em fusao_climatica.py — nunca commitar
segredo de conexão de banco no repositório.

Wiring estrutural feito na Semana 3 para os endpoints poderem declarar a
dependência; a conexão real contra um Postgres/PostGIS vivo (aplicar
schema.sql, testar leitura/escrita ponta a ponta) é o objeto da Semana 5.
"""

import os
from collections.abc import Generator

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

DATABASE_URL = os.environ.get(
    "DATABASE_URL", "postgresql+psycopg2://localhost/alagamentos"
)

engine = create_engine(DATABASE_URL, pool_pre_ping=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


def get_db() -> Generator[Session, None, None]:
    """Dependency do FastAPI: uma sessão por requisição, sempre fechada ao final."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
