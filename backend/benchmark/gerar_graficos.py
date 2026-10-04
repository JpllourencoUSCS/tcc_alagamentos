"""
Gráficos e tabela-resumo do benchmark de indexação espacial (Semana 9 —
entregável "gráfico comparativo de latência antes/depois da indexação").

Lê os dois CSVs de `medir_consultas.py` (sem e com índice GiST) e gera, em
`benchmark/resultados/`:

- `grafico_consulta_espacial.png` — consulta só com o filtro espacial: isola o
  efeito do índice (hipótese O(n) vs. O(log n) de T17).
- `grafico_consulta_endpoint.png` — consulta real do endpoint GET /ocorrencias
  com filtro de região (ORDER BY data_hora DESC LIMIT 100).
- `resumo.md` — tabela com mediana, média, desvio, ganho e plano escolhido.

Requer matplotlib (`pip install -r requirements-benchmark.txt`, na raiz do repo).

Uso (de backend/):

    python -m benchmark.gerar_graficos \
        --sem-indice benchmark/resultados/resultados_sem_indice.csv \
        --com-indice benchmark/resultados/resultados_com_indice.csv
"""

import argparse
import csv
import statistics
from collections import defaultdict
from pathlib import Path

DIR_RESULTADOS = Path(__file__).resolve().parent / "resultados"

# Paleta categórica de referência (slots 1 e 2), validada para daltonismo e
# contraste contra a superfície clara (skill dataviz, validate_palette.js).
COR_COM_INDICE = "#2a78d6"
COR_SEM_INDICE = "#eb6834"
COR_TEXTO = "#0b0b0b"
COR_TEXTO_SECUNDARIO = "#52514e"
COR_GRADE = "#e4e3df"
COR_SUPERFICIE = "#fcfcfb"

TITULOS = {
    "espacial": "Consulta só com filtro espacial (count no bbox de São Caetano do Sul)",
    "endpoint": "Consulta do endpoint GET /ocorrencias (bbox + ORDER BY data_hora + LIMIT 100)",
}


def ler_csv(caminho: Path) -> list[dict]:
    with caminho.open(encoding="utf-8") as f:
        return list(csv.DictReader(f))


def agrupar(linhas: list[dict]) -> dict:
    """Pura — {(consulta, indice, escala): {"tempos": [...], "plano": str, "linhas": int}}."""
    grupos = defaultdict(lambda: {"tempos": [], "planos": set(), "linhas": None})
    for linha in linhas:
        chave = (linha["consulta"], linha["indice"] == "True", int(linha["escala"]))
        grupos[chave]["tempos"].append(float(linha["tempo_ms"]))
        grupos[chave]["planos"].add(linha["plano"])
        grupos[chave]["linhas"] = int(linha["linhas"])
    return dict(grupos)


def _formatar_ms(valor: float) -> str:
    """Vírgula decimal (relatório em português)."""
    texto = f"{valor:.3f}" if valor < 1 else f"{valor:.2f}"
    return texto.replace(".", ",")


def _formatar_escala(escala: int) -> str:
    return f"{escala:,}".replace(",", ".")


def gerar_resumo_md(grupos: dict, caminho: Path) -> None:
    escalas = sorted({chave[2] for chave in grupos})
    partes = [
        "# Resultados do benchmark de indexação espacial\n",
        "Gerado por `backend/benchmark/gerar_graficos.py` a partir de "
        "`resultados_sem_indice.csv` e `resultados_com_indice.csv`. Tempos em ms "
        "(\"Execution Time\" do `EXPLAIN ANALYZE`, sem rede nem planejamento); "
        "20 execuções medidas por célula, após 3 de aquecimento.\n",
    ]
    for consulta in ("espacial", "endpoint"):
        partes.append(f"\n## {TITULOS[consulta]}\n")
        # Na consulta "espacial" a raiz do plano é um count(*) (sempre 1 linha),
        # então a coluna de linhas só informa algo na consulta do endpoint.
        coluna_linhas = consulta == "endpoint"
        partes.append(
            "| Registros | Sem índice: mediana (média ± dp) | Com GiST: mediana (média ± dp) "
            "| Ganho (mediana) |" + (" Linhas devolvidas |" if coluna_linhas else "")
            + " Plano sem índice | Plano com índice |"
        )
        partes.append("|---|---|---|---|" + ("---|" if coluna_linhas else "") + "---|---|")
        for escala in escalas:
            sem = grupos[(consulta, False, escala)]
            com = grupos[(consulta, True, escala)]
            med_sem = statistics.median(sem["tempos"])
            med_com = statistics.median(com["tempos"])

            def celula(g):
                return (
                    f"{_formatar_ms(statistics.median(g['tempos']))} "
                    f"({_formatar_ms(statistics.mean(g['tempos']))} ± "
                    f"{_formatar_ms(statistics.stdev(g['tempos']))})"
                )

            ganho = f"{med_sem / med_com:.1f}".replace(".", ",")
            partes.append(
                f"| {_formatar_escala(escala)} | {celula(sem)} | {celula(com)} | {ganho}× |"
                + (f" {com['linhas']} |" if coluna_linhas else "")
                + f" {' / '.join(sorted(sem['planos']))} | {' / '.join(sorted(com['planos']))} |"
            )
    caminho.write_text("\n".join(partes) + "\n", encoding="utf-8")


def gerar_grafico(grupos: dict, consulta: str, caminho: Path) -> None:
    import matplotlib

    matplotlib.use("Agg")
    import matplotlib.pyplot as plt
    import matplotlib.ticker

    escalas = sorted({chave[2] for chave in grupos if chave[0] == consulta})
    series = [
        ("Sem índice espacial", False, COR_SEM_INDICE, "o"),
        ("Com índice GiST", True, COR_COM_INDICE, "s"),
    ]

    fig, ax = plt.subplots(figsize=(8, 4.8), dpi=200)
    fig.patch.set_facecolor(COR_SUPERFICIE)
    ax.set_facecolor(COR_SUPERFICIE)

    ultimos = {
        com_indice: statistics.median(grupos[(consulta, com_indice, escalas[-1])]["tempos"])
        for _, com_indice, _, _ in series
    }
    # Rótulos do último ponto afastados na vertical quando os valores estão
    # próximos (evita sobreposição de texto, ex.: endpoint com 1M de linhas)
    proximos = max(ultimos.values()) / min(ultimos.values()) < 1.6

    for rotulo, com_indice, cor, marcador in series:
        medianas = [statistics.median(grupos[(consulta, com_indice, e)]["tempos"]) for e in escalas]
        deslocamento_y = 0
        if proximos:
            deslocamento_y = 8 if ultimos[com_indice] >= ultimos[not com_indice] else -8
        ax.plot(
            escalas, medianas, color=cor, linewidth=2, marker=marcador, markersize=7,
            markeredgecolor=COR_SUPERFICIE, markeredgewidth=1.5, label=rotulo, zorder=3,
        )
        # Rótulo direto só no último ponto (identidade sem depender só da cor)
        ax.annotate(
            f"{_formatar_ms(medianas[-1])} ms", (escalas[-1], medianas[-1]),
            textcoords="offset points", xytext=(8, deslocamento_y), va="center",
            fontsize=9, color=COR_TEXTO,
        )

    ax.set_xscale("log")
    ax.set_yscale("log")
    ax.set_xticks(escalas)
    ax.set_xticklabels([_formatar_escala(e) for e in escalas])
    ax.set_xlim(escalas[0] * 0.7, escalas[-1] * 3.2)
    ax.set_xlabel("Registros na tabela ocorrencias (escala log)", color=COR_TEXTO_SECUNDARIO)
    ax.set_ylabel("Tempo de execução, mediana (ms, escala log)", color=COR_TEXTO_SECUNDARIO)
    ax.set_title(TITULOS[consulta], fontsize=10.5, color=COR_TEXTO, loc="left")
    ax.grid(True, which="major", color=COR_GRADE, linewidth=0.8)
    ax.minorticks_off()
    ax.yaxis.set_major_formatter(
        matplotlib.ticker.FuncFormatter(lambda v, _: f"{v:g}".replace(".", ","))
    )
    for lado in ("top", "right"):
        ax.spines[lado].set_visible(False)
    for lado in ("left", "bottom"):
        ax.spines[lado].set_color(COR_GRADE)
    ax.tick_params(colors=COR_TEXTO_SECUNDARIO, labelsize=9)
    ax.legend(frameon=False, fontsize=9, loc="upper left", labelcolor=COR_TEXTO)

    fig.tight_layout()
    fig.savefig(caminho, facecolor=COR_SUPERFICIE)
    plt.close(fig)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--sem-indice", type=Path, default=DIR_RESULTADOS / "resultados_sem_indice.csv")
    parser.add_argument("--com-indice", type=Path, default=DIR_RESULTADOS / "resultados_com_indice.csv")
    parser.add_argument("--saida", type=Path, default=DIR_RESULTADOS)
    args = parser.parse_args()

    grupos = agrupar(ler_csv(args.sem_indice) + ler_csv(args.com_indice))
    args.saida.mkdir(parents=True, exist_ok=True)
    gerar_resumo_md(grupos, args.saida / "resumo.md")
    for consulta in ("espacial", "endpoint"):
        gerar_grafico(grupos, consulta, args.saida / f"grafico_consulta_{consulta}.png")
    print(f"Gráficos e resumo salvos em {args.saida.resolve()}")


if __name__ == "__main__":
    main()
