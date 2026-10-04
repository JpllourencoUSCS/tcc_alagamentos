"""
Medição de latência ponta a ponta da API (Semana 11 — Henrique; implementado
em 03/10/2026).

Diferente de `medir_consultas.py` (que isola o tempo dentro do Postgres via
EXPLAIN ANALYZE), aqui o relógio é o do cliente HTTP: o tempo medido inclui
rede, FastAPI/Pydantic, SQLAlchemy, a consulta e a serialização do JSON — é a
latência que o app sente. Compara com os critérios de
docs/T19_criterios_desempenho.md.

Cenários (cada um com aquecimento descartado e N medições):

- `listar`          GET /ocorrencias (sem filtro, limit padrão)
- `listar_regiao`   GET /ocorrencias com bbox de São Caetano do Sul (o que o
                    mapa e a aba Alertas do app fazem)
- `listar_periodo`  GET /ocorrencias com bbox + data_inicio nas últimas 24 h
- `obter`           GET /ocorrencias/{id}
- `criar_manual`    POST /ocorrencias com nivel_risco informado (não consulta
                    fontes externas) — as linhas criadas levam
                    id_usuario='latencia-teste' e são apagadas ao final se
                    DATABASE_URL estiver definida
- `criar_auto_sem_cache`  POST sem nivel_risco em 10 pontos de células de cache
                    diferentes: consulta as fontes climáticas externas de verdade
                    (pior caso). Rodar logo depois de reiniciar a API.
- `criar_auto`      POST sem nivel_risco no mesmo ponto (dados climáticos em cache)
- `risco`           GET /risco no mesmo ponto (em cache)
  (os três `*auto*`/`risco` só com --incluir-auto; exigem OPENWEATHER_API_KEY no servidor)

Uso (de backend/):

    python -m benchmark.medir_latencia_api --base-url http://localhost:8000 \
        --rotulo demo --saida benchmark/resultados/latencia_api_demo.csv
"""

import argparse
import csv
import os
import statistics
import time
from datetime import datetime, timedelta, timezone
from pathlib import Path

import httpx

MARCADOR = "latencia-teste"
BBOX_SCS = {"lat_min": -23.650, "lon_min": -46.600, "lat_max": -23.595, "lon_max": -46.535}
PONTO_SCS = {"latitude": -23.6229, "longitude": -46.5548}


def percentil(valores: list[float], p: float) -> float:
    """Pura — percentil por interpolação linear (mesmo método do numpy padrão)."""
    if not valores:
        raise ValueError("lista vazia")
    ordenados = sorted(valores)
    k = (len(ordenados) - 1) * p / 100
    baixo, alto = int(k), min(int(k) + 1, len(ordenados) - 1)
    return ordenados[baixo] + (ordenados[alto] - ordenados[baixo]) * (k - baixo)


def _cenarios(cliente: httpx.Client, incluir_auto: bool) -> dict:
    primeira = cliente.get("/ocorrencias", params={"limit": 1}).json()
    id_existente = primeira[0]["id"] if primeira else None
    data_inicio = (datetime.now(timezone.utc) - timedelta(hours=24)).isoformat()

    cenarios = {
        "listar": lambda: cliente.get("/ocorrencias"),
        "listar_regiao": lambda: cliente.get("/ocorrencias", params=BBOX_SCS),
        "listar_periodo": lambda: cliente.get(
            "/ocorrencias", params={**BBOX_SCS, "data_inicio": data_inicio}
        ),
        "criar_manual": lambda: cliente.post("/ocorrencias", json={
            **PONTO_SCS, "nivel_risco": "Médio", "fonte": "usuario", "id_usuario": MARCADOR,
        }),
    }
    if id_existente is not None:
        cenarios["obter"] = lambda: cliente.get(f"/ocorrencias/{id_existente}")
    if incluir_auto:
        cenarios["criar_auto"] = lambda: cliente.post("/ocorrencias", json={
            **PONTO_SCS, "fonte": "usuario", "id_usuario": MARCADOR,
        })
        cenarios["risco"] = lambda: cliente.get("/risco", params=PONTO_SCS)
    return cenarios


# Pontos em células de cache diferentes (passo > 0,01°, a resolução do cache de
# fusao_climatica), todos na região de São Caetano do Sul / ABC: cada POST
# nesses pontos consulta as fontes climáticas externas de verdade.
PONTOS_SEM_CACHE = [{"latitude": -23.595 - 0.011 * i, "longitude": -46.575} for i in range(10)]


def _registrar(linhas, nome, i, ms, resp):
    if resp.status_code >= 400:
        raise SystemExit(f"{nome}: HTTP {resp.status_code} — {resp.text[:200]}")
    linhas.append({
        "cenario": nome, "repeticao": i, "tempo_ms": ms,
        "status": resp.status_code, "bytes": len(resp.content),
    })


def medir(base_url: str, repeticoes: int, aquecimento: int, incluir_auto: bool) -> list[dict]:
    linhas = []
    with httpx.Client(base_url=base_url, timeout=60) as cliente:
        if incluir_auto:
            # Sem aquecimento de propósito: é o pior caso (cache vazio para a
            # célula), que só é confiável logo depois de reiniciar a API —
            # o cache vive na memória do processo e dura 10 min.
            for i, ponto in enumerate(PONTOS_SEM_CACHE):
                inicio = time.perf_counter()
                resp = cliente.post("/ocorrencias", json={**ponto, "fonte": "usuario", "id_usuario": MARCADOR})
                _registrar(linhas, "criar_auto_sem_cache", i, (time.perf_counter() - inicio) * 1000, resp)
        for nome, requisicao in _cenarios(cliente, incluir_auto).items():
            for i in range(aquecimento + repeticoes):
                inicio = time.perf_counter()
                resp = requisicao()
                ms = (time.perf_counter() - inicio) * 1000
                if i >= aquecimento:
                    _registrar(linhas, nome, i, ms, resp)
                elif resp.status_code >= 400:
                    raise SystemExit(f"{nome}: HTTP {resp.status_code} — {resp.text[:200]}")
    return linhas


def resumir(linhas: list[dict]) -> list[dict]:
    por_cenario: dict[str, list[dict]] = {}
    for linha in linhas:
        por_cenario.setdefault(linha["cenario"], []).append(linha)
    resumo = []
    for cenario, itens in por_cenario.items():
        tempos = [i["tempo_ms"] for i in itens]
        resumo.append({
            "cenario": cenario, "n": len(tempos),
            "p50_ms": percentil(tempos, 50), "p95_ms": percentil(tempos, 95),
            "max_ms": max(tempos), "media_ms": statistics.mean(tempos),
            "bytes": itens[0]["bytes"],
        })
    return resumo


def limpar_linhas_de_teste(desde: datetime | None = None) -> int:
    """Apaga as ocorrências criadas pela medição e, se `desde` for informado, os
    scores colaborativos registrados a partir desse instante — os POSTs de teste
    são relatos de usuário e, a partir do segundo no mesmo ponto, geram registros
    em reportes_colaborativos_agregado."""
    if "DATABASE_URL" not in os.environ:
        print("DATABASE_URL não definida: linhas de teste (id_usuario='latencia-teste') não foram apagadas.")
        return 0
    from sqlalchemy import delete

    from db.models import Ocorrencia, ReporteColaborativoAgregado
    from db.session import SessionLocal

    with SessionLocal() as db:
        apagadas = db.execute(delete(Ocorrencia).where(Ocorrencia.id_usuario == MARCADOR)).rowcount
        if desde is not None:
            agregados = db.execute(
                delete(ReporteColaborativoAgregado).where(ReporteColaborativoAgregado.calculado_em >= desde)
            ).rowcount
            if agregados:
                print(f"{agregados} scores colaborativos gerados pela medição apagados.")
        db.commit()
    return apagadas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--base-url", default="http://localhost:8000")
    parser.add_argument("--rotulo", required=True, help="Nome do cenário de ambiente (ex.: demo, 1M).")
    parser.add_argument("--repeticoes", type=int, default=50)
    parser.add_argument("--aquecimento", type=int, default=5)
    parser.add_argument("--incluir-auto", action="store_true")
    parser.add_argument("--saida", type=Path, required=True)
    args = parser.parse_args()

    inicio_medicao = datetime.now(timezone.utc)
    try:
        linhas = medir(args.base_url, args.repeticoes, args.aquecimento, args.incluir_auto)
    finally:
        apagadas = limpar_linhas_de_teste(desde=inicio_medicao)
        if apagadas:
            print(f"{apagadas} linhas de teste apagadas.")

    args.saida.parent.mkdir(parents=True, exist_ok=True)
    with args.saida.open("w", newline="", encoding="utf-8") as f:
        escritor = csv.DictWriter(f, fieldnames=["rotulo", *linhas[0].keys()])
        escritor.writeheader()
        escritor.writerows({"rotulo": args.rotulo, **linha} for linha in linhas)

    print(f"\n{'cenário':<22}{'n':>4}{'p50 ms':>10}{'p95 ms':>10}{'máx ms':>10}{'bytes':>9}")
    for r in resumir(linhas):
        print(f"{r['cenario']:<22}{r['n']:>4}{r['p50_ms']:>10.1f}{r['p95_ms']:>10.1f}"
              f"{r['max_ms']:>10.1f}{r['bytes']:>9}")
    print(f"\nCSV salvo em {args.saida.resolve()}")


if __name__ == "__main__":
    main()
