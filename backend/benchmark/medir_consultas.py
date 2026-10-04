"""
Medição de tempo de consulta geoespacial, com e sem índice GiST (Semanas 8-9
— Henrique, reconstruído em 18/08/2026; metodologia revisada em 03/10/2026,
antes da primeira execução real).

Um módulo só para as duas semanas: a métrica e as consultas medidas são
idênticas, muda apenas se o índice existe ou não no momento da medição — é
exatamente o contraste que o benchmark precisa isolar. Semana 8 usa
`--indice ausente`; Semana 9 soma `--indice presente` (mesmo script, mesmas
escalas) e `benchmark/gerar_graficos.py` cruza os dois CSVs de saída.

Duas consultas são medidas (revisão de 03/10/2026):

- `endpoint`: a mesma que `db/repository.OcorrenciaRepository.listar` gera
  para um filtro de região (bbox -> `geom && ST_MakeEnvelope`, ORDER BY
  data_hora DESC, LIMIT) — o caso de uso real do app.
- `espacial`: só o filtro espacial (`count(*)` das linhas no bbox), sem
  ORDER BY/LIMIT. Isola o efeito do índice GiST: na consulta `endpoint`, o
  planner pode preferir percorrer `idx_ocorrencias_data_hora` de trás para
  frente e parar ao achar as 100 primeiras linhas no bbox — custo que depende
  da seletividade do bbox, não de n —, o que mascara o crescimento O(n) do
  scan sequencial que a hipótese de T17 quer evidenciar.

Usa `EXPLAIN (ANALYZE, FORMAT JSON)` em vez de cronometrar em Python: isola o
tempo de execução dentro do Postgres, sem ruído de rede/driver/serialização —
metodologia mais defensável para comparar O(n) vs. O(log n) na banca do que
wall-clock do lado do cliente. O mesmo JSON informa o plano escolhido (scan
sequencial, bitmap/index scan no GiST etc.), registrado no CSV como evidência
de que o índice foi de fato usado quando presente.

Uso (Postgres do docker-compose.yml; ver CLAUDE.md, "Ambiente de desenvolvimento"):

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
    AQUECIMENTO_PADRAO,
    BBOX_CONSULTA_BENCHMARK,
    ESCALAS,
    LIMITE_RESULTADOS_CONSULTA,
    NOME_INDICE_GEOM,
    REPETICOES_PADRAO,
)
from benchmark.popular_banco import atualizar_estatisticas, nome_banco_escala, url_para_banco

SQL_CONSULTA_BBOX = """
    SELECT * FROM ocorrencias
    WHERE geom && ST_MakeEnvelope(:lon_min, :lat_min, :lon_max, :lat_max, 4326)
    ORDER BY data_hora DESC
    LIMIT :limite
"""

SQL_CONSULTA_FILTRO_ESPACIAL = """
    SELECT count(*) FROM ocorrencias
    WHERE geom && ST_MakeEnvelope(:lon_min, :lat_min, :lon_max, :lat_max, 4326)
"""

CONSULTAS = {
    "endpoint": SQL_CONSULTA_BBOX,
    "espacial": SQL_CONSULTA_FILTRO_ESPACIAL,
}

CAMPOS_CSV = ["escala", "indice", "consulta", "repeticao", "tempo_ms", "linhas", "plano"]


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


def resumir_plano(no: dict) -> str:
    """Pura — resume a árvore de um plano do EXPLAIN (FORMAT JSON) numa linha
    legível, da raiz às folhas: ex. "Aggregate > Bitmap Heap Scan > Bitmap
    Index Scan[idx_ocorrencias_geom]". É o que prova, no CSV, se o planner
    usou o índice GiST ou fez scan sequencial."""
    rotulo = no["Node Type"]
    if no.get("Index Name"):
        rotulo += f"[{no['Index Name']}]"
    filhos = [resumir_plano(filho) for filho in no.get("Plans", [])]
    if not filhos:
        return rotulo
    if len(filhos) == 1:
        return f"{rotulo} > {filhos[0]}"
    return f"{rotulo} > ({' | '.join(filhos)})"


def medir_consulta(
    url_banco: str,
    sql: str = SQL_CONSULTA_BBOX,
    bbox: tuple[float, float, float, float] = BBOX_CONSULTA_BENCHMARK,
    limite: int = LIMITE_RESULTADOS_CONSULTA,
    repeticoes: int = REPETICOES_PADRAO,
    aquecimento: int = AQUECIMENTO_PADRAO,
) -> list[dict]:
    """Roda `aquecimento` execuções descartadas e depois `repeticoes` medidas
    via EXPLAIN ANALYZE. Retorna, para cada execução medida, o tempo de
    execução em milissegundos (só o que o Postgres gastou executando o plano —
    "Execution Time" do JSON, não inclui planejamento nem round-trip de rede),
    as linhas devolvidas pela raiz do plano e o plano resumido."""
    lat_min, lon_min, lat_max, lon_max = bbox
    params = {
        "lat_min": lat_min, "lon_min": lon_min,
        "lat_max": lat_max, "lon_max": lon_max,
        "limite": limite,
    }
    engine = create_engine(url_banco)
    medicoes = []
    try:
        with engine.connect() as conn:
            for i in range(aquecimento + repeticoes):
                plano = conn.execute(
                    text(f"EXPLAIN (ANALYZE, FORMAT JSON) {sql}"), params
                ).scalar_one()[0]
                if i < aquecimento:
                    continue
                medicoes.append({
                    "tempo_ms": plano["Execution Time"],
                    "linhas": plano["Plan"]["Actual Rows"],
                    "plano": resumir_plano(plano["Plan"]),
                })
    finally:
        engine.dispose()
    return medicoes


def medir_consulta_bbox(
    url_banco: str,
    bbox: tuple[float, float, float, float] = BBOX_CONSULTA_BENCHMARK,
    limite: int = LIMITE_RESULTADOS_CONSULTA,
    repeticoes: int = REPETICOES_PADRAO,
) -> list[float]:
    """Compatibilidade com a versão de 18/08: só os tempos da consulta do
    endpoint, sem aquecimento."""
    medicoes = medir_consulta(url_banco, SQL_CONSULTA_BBOX, bbox, limite, repeticoes, aquecimento=0)
    return [m["tempo_ms"] for m in medicoes]


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
    url_admin: str,
    escala: int,
    com_indice: bool,
    repeticoes: int,
    aquecimento: int = AQUECIMENTO_PADRAO,
) -> list[dict]:
    nome_banco = nome_banco_escala(escala)
    url_banco = url_para_banco(url_admin, nome_banco)

    if com_indice and not indice_existe(url_banco):
        print(f"[{nome_banco}] criando {NOME_INDICE_GEOM}...")
        criar_indice(url_banco)
    elif not com_indice and indice_existe(url_banco):
        print(f"[{nome_banco}] removendo {NOME_INDICE_GEOM} (medição sem índice)...")
        remover_indice(url_banco)
    # Estatísticas recalculadas depois de mexer no índice, para o planner
    # decidir com a mesma informação nas duas condições.
    atualizar_estatisticas(url_banco)

    linhas = []
    for nome_consulta, sql in CONSULTAS.items():
        print(
            f"[{nome_banco}] consulta '{nome_consulta}': {aquecimento} aquecimento + "
            f"{repeticoes} medidas (índice={'sim' if com_indice else 'não'})..."
        )
        medicoes = medir_consulta(url_banco, sql, repeticoes=repeticoes, aquecimento=aquecimento)
        resumo = resumo_estatistico([m["tempo_ms"] for m in medicoes])
        print(
            f"[{nome_banco}]   média={resumo['media_ms']:.3f}ms "
            f"mediana={resumo['mediana_ms']:.3f}ms  plano: {medicoes[0]['plano']}"
        )
        linhas.extend(
            {
                "escala": escala,
                "indice": com_indice,
                "consulta": nome_consulta,
                "repeticao": i,
                **m,
            }
            for i, m in enumerate(medicoes)
        )
    return linhas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--escalas", type=int, nargs="+", default=ESCALAS)
    parser.add_argument(
        "--indice", choices=["presente", "ausente"], required=True,
        help="'ausente' = Semana 8 (baseline); 'presente' = Semana 9 (comparação).",
    )
    parser.add_argument("--repeticoes", type=int, default=REPETICOES_PADRAO)
    parser.add_argument("--aquecimento", type=int, default=AQUECIMENTO_PADRAO)
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
        linhas.extend(medir_escala(url_admin, escala, com_indice, args.repeticoes, args.aquecimento))

    caminho_saida = Path(args.saida)
    caminho_saida.parent.mkdir(parents=True, exist_ok=True)
    with caminho_saida.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=CAMPOS_CSV)
        escritor.writeheader()
        escritor.writerows(linhas)
    print(f"\nResultados salvos em {caminho_saida.resolve()}")


if __name__ == "__main__":
    main()
