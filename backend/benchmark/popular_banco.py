"""
Popula um banco de benchmark por escala (Semana 7 — Henrique, reconstruído em
18/08/2026): 1k/10k/100k registros sintéticos em `ocorrencias`.

Por que um banco por escala (`alagamentos_bench_1000`, `..._10000`,
`..._100000`), em vez de uma coluna extra marcando o lote dentro de um único
banco: isola completamente o volume testado (sem WHERE de lote competindo
pelo mesmo índice/cache/estatísticas do planner) e permite ao script de
benchmark (Semana 8/9) fazer DROP/CREATE INDEX em cada banco sem afetar os
outros — inclusive em paralelo, se necessário.

Não roda sozinho neste ambiente (sem Postgres/PostGIS disponível — ver
CRONOGRAMA_STATUS.md, pendência de 18/08). Pronto para rodar assim que houver
um Postgres acessível:

    export ADMIN_DATABASE_URL=postgresql+psycopg2://usuario:senha@host/postgres
    cd backend
    python -m benchmark.popular_banco --escalas 1000 10000 100000

`ADMIN_DATABASE_URL` precisa apontar para um banco de manutenção (`postgres`,
por convenção) com permissão de CREATE DATABASE — é dela que o script cria
(ou recria, com --recriar) um banco por escala.
"""

import argparse
import os
import time
from datetime import datetime
from pathlib import Path

from sqlalchemy import create_engine, insert, text
from sqlalchemy.engine import make_url

from benchmark.config import ESCALAS, SEMENTE_PADRAO, TAMANHO_LOTE
from benchmark.gerar_dados import gerar_ocorrencias_sinteticas
from db.models import Ocorrencia

SCHEMA_PATH = Path(__file__).resolve().parent.parent / "db" / "schema.sql"


def nome_banco_escala(escala: int) -> str:
    """Compartilhada com medir_consultas.py (Semanas 8-9) — mesma convenção
    de nome de banco por escala em todo o pacote benchmark."""
    return f"alagamentos_bench_{escala}"


def url_para_banco(url_admin: str, nome_banco: str) -> str:
    return str(make_url(url_admin).set(database=nome_banco))


def _banco_existe(url_admin: str, nome_banco: str) -> bool:
    engine = create_engine(url_admin, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as conn:
            resultado = conn.execute(
                text("SELECT 1 FROM pg_database WHERE datname = :nome"),
                {"nome": nome_banco},
            )
            return resultado.first() is not None
    finally:
        engine.dispose()


def _derrubar_banco(url_admin: str, nome_banco: str) -> None:
    engine = create_engine(url_admin, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as conn:
            # DROP DATABASE falha se houver conexões abertas nele.
            conn.execute(
                text(
                    "SELECT pg_terminate_backend(pid) FROM pg_stat_activity "
                    "WHERE datname = :nome AND pid <> pg_backend_pid()"
                ),
                {"nome": nome_banco},
            )
            conn.execute(text(f'DROP DATABASE IF EXISTS "{nome_banco}"'))
    finally:
        engine.dispose()


def _criar_banco(url_admin: str, nome_banco: str) -> None:
    engine = create_engine(url_admin, isolation_level="AUTOCOMMIT")
    try:
        with engine.connect() as conn:
            conn.execute(text(f'CREATE DATABASE "{nome_banco}"'))
    finally:
        engine.dispose()


def _aplicar_schema(url_banco: str) -> None:
    sql = SCHEMA_PATH.read_text(encoding="utf-8")
    engine = create_engine(url_banco)
    try:
        with engine.begin() as conn:
            conn.exec_driver_sql(sql)
    finally:
        engine.dispose()


def _inserir_em_lotes(url_banco: str, linhas: list[dict], tamanho_lote: int) -> float:
    """Insere `linhas` em lotes via SQLAlchemy Core (bulk insert — não passa
    pelo overhead do ORM por objeto). Retorna o tempo total em segundos."""
    engine = create_engine(url_banco)
    inicio = time.perf_counter()
    try:
        with engine.begin() as conn:
            for i in range(0, len(linhas), tamanho_lote):
                lote = linhas[i : i + tamanho_lote]
                conn.execute(insert(Ocorrencia.__table__), lote)
    finally:
        engine.dispose()
    return time.perf_counter() - inicio


def popular_escala(
    url_admin: str,
    escala: int,
    recriar: bool,
    semente: int,
    tamanho_lote: int,
    referencia: datetime | None = None,
) -> None:
    nome_banco = nome_banco_escala(escala)

    if recriar and _banco_existe(url_admin, nome_banco):
        print(f"[{nome_banco}] --recriar: derrubando banco existente...")
        _derrubar_banco(url_admin, nome_banco)

    if not _banco_existe(url_admin, nome_banco):
        print(f"[{nome_banco}] criando banco...")
        _criar_banco(url_admin, nome_banco)
        print(f"[{nome_banco}] aplicando schema.sql...")
        _aplicar_schema(url_para_banco(url_admin, nome_banco))
    else:
        print(f"[{nome_banco}] já existe, mantendo (use --recriar para começar do zero).")

    print(f"[{nome_banco}] gerando {escala} ocorrências sintéticas (semente={semente})...")
    linhas = gerar_ocorrencias_sinteticas(escala, semente=semente, referencia=referencia)

    print(f"[{nome_banco}] inserindo em lotes de {tamanho_lote}...")
    duracao = _inserir_em_lotes(url_para_banco(url_admin, nome_banco), linhas, tamanho_lote)
    print(f"[{nome_banco}] concluído: {escala} linhas em {duracao:.2f}s.")


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--escalas", type=int, nargs="+", default=ESCALAS,
        help=f"Volumes a gerar (padrão: {ESCALAS})",
    )
    parser.add_argument(
        "--recriar", action="store_true",
        help="Derruba e recria o banco de cada escala antes de popular (dataset limpo).",
    )
    parser.add_argument("--semente", type=int, default=SEMENTE_PADRAO)
    parser.add_argument("--tamanho-lote", type=int, default=TAMANHO_LOTE)
    parser.add_argument(
        "--referencia-iso", type=str, default=None,
        help=(
            "Instante ISO 8601 (ex.: 2026-08-18T12:00:00+00:00) usado como "
            "'agora' na geração de data_hora. Sem isso, cada execução usa o "
            "instante real e o dataset não é idêntico byte a byte entre "
            "execuções (mesma semente, mas data_hora desloca) — passe este "
            "valor quando precisar reproduzir exatamente o mesmo dataset."
        ),
    )
    args = parser.parse_args()

    url_admin = os.environ.get("ADMIN_DATABASE_URL")
    if not url_admin:
        raise SystemExit(
            "Defina ADMIN_DATABASE_URL (ex.: postgresql+psycopg2://user:senha@host/postgres) "
            "antes de rodar este script."
        )

    referencia = datetime.fromisoformat(args.referencia_iso) if args.referencia_iso else None

    for escala in args.escalas:
        popular_escala(
            url_admin, escala, args.recriar, args.semente, args.tamanho_lote, referencia
        )


if __name__ == "__main__":
    main()
