"""
Testes da parte pura de benchmark/popular_banco.py (Semana 7 — Henrique).

Regressão do bug achado na primeira execução real do benchmark (03/10/2026):
`url_para_banco` usava `str(URL)`, que no SQLAlchemy 2.x mascara a senha como
"***" — a conexão com o banco de cada escala falhava por autenticação.
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmark.popular_banco import nome_banco_escala, url_para_banco


def test_url_para_banco_preserva_senha():
    url = url_para_banco(
        "postgresql+psycopg2://usuario:s3nha-real@localhost:5432/postgres",
        "alagamentos_bench_1000",
    )
    assert url == "postgresql+psycopg2://usuario:s3nha-real@localhost:5432/alagamentos_bench_1000"


def test_url_para_banco_preserva_senha_com_caracteres_especiais():
    url = url_para_banco("postgresql+psycopg2://u:a%40b@host/postgres", "x")
    assert "***" not in url
    assert url.endswith("@host/x")


def test_nome_banco_escala():
    assert nome_banco_escala(100_000) == "alagamentos_bench_100000"
