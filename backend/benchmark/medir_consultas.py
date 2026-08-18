"""
Medição de tempo de consulta geoespacial, com e sem índice GiST (Semanas 8-9
— Henrique, reconstruído em 18/08/2026).

Um módulo só para as duas semanas: a métrica e a consulta medida são
idênticas, muda apenas se o índice existe ou não no momento da medição — é
exatamente o contraste que o benchmark precisa isolar. Semana 8 usa
`--indice ausente`; Semana 9 soma `--indice presente` (mesmo script, mesmas
escalas) e o gráfico comparativo cruza os dois CSVs de saída.

A consulta medida é a mesma que `db/repository.OcorrenciaRepository.listar`
gera para um filtro de região (bbox -> `geom && ST_MakeEnvelope`, ORDER BY
data_hora DESC, LIMIT) — o benchmark mede o caso de uso real do endpoint, não
uma consulta sintética à parte.

Usa `EXPLAIN (ANALYZE, FORMAT JSON)` em vez de cronometrar em Python: isola o
tempo de execução dentro do Postgres, sem ruído de rede/driver/serialização —
metodologia mais defensável para comparar O(n) vs. O(log n) na banca do que
wall-clock do lado do cliente.

Não roda sozinho neste ambiente (sem Postgres/PostGIS — ver CRONOGRAMA_STATUS.md).
Pronto para rodar assim que houver banco populado (ver benchmark/popular_banco.py):

    export ADMIN_DATABASE_URL=postgresql+psycopg2://usuario:senha@host/postgres
    cd backend
    python -m benchmark.medir_consultas --indice ausente --saida resultados_sem_indice.csv
"""

import argparse
import csv
import os
import statistics
from pathlib import Path

from sqlalchemy import create_engine, text

from benchmark.config import (
    BBOX_CONSULTA_BENCHMARK,
    ESCALAS,
    LIMITE_RESULTADOS_CONSULTA,
    NOME_INDICE_GEOM,
    REPETICOES_PADRAO,
)
from benchmark.popular_banco import nome_banco_escala, url_para_banco

SQL_CONSULTA_BBOX = """
    SELECT * FROM ocorrencias
    WHERE geom && ST_MakeEnvelope(:lon_min, :lat_min, :lon_max, :lat_max, 4326)
    ORDER BY data_hora DESC
    LIMIT :limite
"""


def indice_existe(url_banco: str, nome_indice: str = NOME_INDICE_GEOM) -> bool:
    engine = create_engine(url_banco)
    try:
        with engine.connect() as conn:
            resultado = conn.execute(
                text("SELECT 1 FROM pg_indexes WHERE indexname = :nome"),
                {"nome": nome_indice},
            )
            return resultado.first() is not None
    finally:
        engine.dispose()


def remover_indice(url_banco: str, nome_indice: str = NOME_INDICE_GEOM) -> None:
    engine = create_engine(url_banco)
    try:
        with engine.begin() as conn:
            conn.execute(text(f'DROP INDEX IF EXISTS "{nome_indice}"'))
    finally:
        engine.dispose()


def criar_indice(
    url_banco: str,
    nome_indice: str = NOME_INDICE_GEOM,
    tabela: str = "ocorrencias",
    coluna: str = "geom",
) -> None:
    engine = create_engine(url_banco)
    try:
        with engine.begin() as conn:
            conn.execute(
                text(f'CREATE INDEX "{nome_indice}" ON {tabela} USING GIST ({coluna})')
            )
    finally:
        engine.dispose()


def medir_consulta_bbox(
    url_banco: str,
    bbox: tuple[float, float, float, float] = BBOX_CONSULTA_BENCHMARK,
    limite: int = LIMITE_RESULTADOS_CONSULTA,
    repeticoes: int = REPETICOES_PADRAO,
) -> list[float]:
    """Roda a consulta `repeticoes` vezes via EXPLAIN ANALYZE e retorna os
    tempos de execução em milissegundos (só o que o Postgres gastou
    executando o plano — "Execution Time" do JSON de saída do EXPLAIN, não
    inclui planejamento nem round-trip de rede)."""
    lat_min, lon_min, lat_max, lon_max = bbox
    params = {
        "lat_min": lat_min, "lon_min": lon_min,
        "lat_max": lat_max, "lon_max": lon_max,
        "limite": limite,
    }
    engine = create_engine(url_banco)
    tempos = []
    try:
        with engine.connect() as conn:
            for _ in range(repeticoes):
                plano = conn.execute(
                    text(f"EXPLAIN (ANALYZE, FORMAT JSON) {SQL_CONSULTA_BBOX}"), params
                ).scalar_one()
                tempos.append(plano[0]["Execution Time"])
    finally:
        engine.dispose()
    return tempos


def resumo_estatistico(tempos: list[float]) -> dict:
    """Pura — não toca banco, testável isoladamente."""
    if not tempos:
        return {"n": 0, "media_ms": None, "mediana_ms": None, "desvio_padrao_ms": None,
                "minimo_ms": None, "maximo_ms": None}
    return {
        "n": len(tempos),
        "media_ms": statistics.mean(tempos),
        "mediana_ms": statistics.median(tempos),
        "desvio_padrao_ms": statistics.stdev(tempos) if len(tempos) > 1 else 0.0,
        "minimo_ms": min(tempos),
        "maximo_ms": max(tempos),
    }


def medir_escala(
    url_admin: str, escala: int, com_indice: bool, repeticoes: int
) -> list[dict]:
    nome_banco = nome_banco_escala(escala)
    url_banco = url_para_banco(url_admin, nome_banco)

    if com_indice and not indice_existe(url_banco):
        print(f"[{nome_banco}] criando {NOME_INDICE_GEOM}...")
        criar_indice(url_banco)
    elif not com_indice and indice_existe(url_banco):
        print(f"[{nome_banco}] removendo {NOME_INDICE_GEOM} (medição sem índice)...")
        remover_indice(url_banco)

    print(f"[{nome_banco}] medindo {repeticoes} execuções (índice={'sim' if com_indice else 'não'})...")
    tempos = medir_consulta_bbox(url_banco, repeticoes=repeticoes)
    resumo = resumo_estatistico(tempos)
    print(f"[{nome_banco}] média={resumo['media_ms']:.2f}ms mediana={resumo['mediana_ms']:.2f}ms")

    return [
        {"escala": escala, "indice": com_indice, "repeticao": i, "tempo_ms": t}
        for i, t in enumerate(tempos)
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--escalas", type=int, nargs="+", default=ESCALAS)
    parser.add_argument(
        "--indice", choices=["presente", "ausente"], required=True,
        help="'ausente' = Semana 8 (baseline); 'presente' = Semana 9 (comparação).",
    )
    parser.add_argument("--repeticoes", type=int, default=REPETICOES_PADRAO)
    parser.add_argument("--saida", type=str, required=True, help="Caminho do CSV de resultados.")
    args = parser.parse_args()

    url_admin = os.environ.get("ADMIN_DATABASE_URL")
    if not url_admin:
        raise SystemExit(
            "Defina ADMIN_DATABASE_URL (ex.: postgresql+psycopg2://user:senha@host/postgres) "
            "antes de rodar este script."
        )

    com_indice = args.indice == "presente"
    linhas = []
    for escala in args.escalas:
        linhas.extend(medir_escala(url_admin, escala, com_indice, args.repeticoes))

    caminho_saida = Path(args.saida)
    with caminho_saida.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=["escala", "indice", "repeticao", "tempo_ms"])
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"\nResultados salvos em {caminho_saida.resolve()}")


if __name__ == "__main__":
    main()
