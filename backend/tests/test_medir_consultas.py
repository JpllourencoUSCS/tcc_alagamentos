"""
Testes da parte pura do módulo de medição (Semanas 8-9 — Henrique).

`resumo_estatistico` não toca banco — testável isoladamente. As funções que
falam com o Postgres (medir_consulta_bbox, criar/remover índice) não têm como
ser testadas nesta máquina sem um banco disponível (ver CRONOGRAMA_STATUS.md);
aqui validamos só que a SQL medida compila corretamente contra o dialeto
PostgreSQL, igual já é feito para os modelos (db/models.py) e o filtro de
bbox dos endpoints (db/repository.py).
"""

import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from sqlalchemy import text
from sqlalchemy.dialects import postgresql

from benchmark.medir_consultas import SQL_CONSULTA_BBOX, resumo_estatistico


def test_resumo_estatistico_lista_vazia():
    resumo = resumo_estatistico([])
    assert resumo == {
        "n": 0, "media_ms": None, "mediana_ms": None,
        "desvio_padrao_ms": None, "minimo_ms": None, "maximo_ms": None,
    }


def test_resumo_estatistico_um_valor_desvio_padrao_zero():
    resumo = resumo_estatistico([7.5])
    assert resumo["n"] == 1
    assert resumo["media_ms"] == 7.5
    assert resumo["desvio_padrao_ms"] == 0.0


def test_resumo_estatistico_valores_conhecidos():
    resumo = resumo_estatistico([10.0, 20.0, 30.0])
    assert resumo["n"] == 3
    assert resumo["media_ms"] == 20.0
    assert resumo["mediana_ms"] == 20.0
    assert resumo["minimo_ms"] == 10.0
    assert resumo["maximo_ms"] == 30.0
    assert resumo["desvio_padrao_ms"] > 0


def test_sql_consulta_bbox_compila_para_postgresql():
    compilado = text(SQL_CONSULTA_BBOX).compile(dialect=postgresql.dialect())
    params_esperados = {"lon_min", "lat_min", "lon_max", "lat_max", "limite"}
    assert params_esperados.issubset(set(compilado.params.keys()))
