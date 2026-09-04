"""
Fixtures compartilhadas de backend/tests/ (Semana 10 — João).

`db_session`: sessão SQLAlchemy real contra o Postgres/PostGIS apontado por
DATABASE_URL, isolada por teste com o padrão "sessão dentro de uma transação
externa" (recomendado pela própria documentação do SQLAlchemy para suítes de
teste): abre uma conexão, inicia uma transação e um SAVEPOINT, entrega a
sessão ao teste e, ao final, dá rollback na transação externa inteira —
nenhuma escrita sobrevive, incluindo os `db.commit()` que
`OcorrenciaRepository.criar()` faz internamente (cada commit fecha só o
SAVEPOINT atual; o listener abaixo reabre um novo na hora).

Isso resolve o problema de testar contra um banco que pode estar vazio (ou,
sendo compartilhado com o time via Tailscale, com dados de outra pessoa):
cada teste cria os próprios dados e não deixa rastro, então o estado inicial
do banco nunca importa.

Pula automaticamente (skip, não falha) se DATABASE_URL não estiver definida —
mesmo critério já usado no resto do projeto para "sem Postgres disponível"
(ver docs/CRONOGRAMA_STATUS.md).
"""

import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
from sqlalchemy import event

from db.session import SessionLocal, engine


@pytest.fixture()
def db_session():
    if "DATABASE_URL" not in os.environ:
        pytest.skip(
            "DATABASE_URL não definida — sem Postgres/PostGIS disponível nesta máquina "
            "(ver docs/CRONOGRAMA_STATUS.md, seção 'Ambiente de desenvolvimento')"
        )

    conexao = engine.connect()
    transacao_externa = conexao.begin()
    sessao = SessionLocal(bind=conexao)

    savepoint = conexao.begin_nested()

    @event.listens_for(sessao, "after_transaction_end")
    def _reabrir_savepoint(sessao_evento, transacao_evento):
        nonlocal savepoint
        if not savepoint.is_active:
            savepoint = conexao.begin_nested()

    try:
        yield sessao
    finally:
        sessao.close()
        transacao_externa.rollback()
        conexao.close()
