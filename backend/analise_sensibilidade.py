"""
Análise de sensibilidade dos pesos do modelo AHP (03/10/2026) — trabalho futuro
listado em docs/T15_algoritmo_risco_fundamentacao.md, seção 8.

Não altera os pesos do modelo (35/25/25/15 continuam os de algoritmo_risco.py):
mede o quanto a classificação mudaria se cada peso fosse um pouco diferente.
Para cada critério e cada perturbação (±10% e ±20% do próprio peso), o peso
perturbado é fixado e os outros três são reescalados proporcionalmente para a
soma continuar 1 — o procedimento usual de análise de sensibilidade "um fator
por vez" em AHP. Cada conjunto de pesos é aplicado a uma grade de cenários
(chuva atual × pico previsto × pluviômetro × colaborativo, incluindo fontes
ausentes) e comparado com a classificação com os pesos originais.

Uso (de backend/):  python analise_sensibilidade.py
"""

import itertools
from unittest.mock import patch

import algoritmo_risco
from algoritmo_risco import PESOS, EntradaRisco, calcular_risco

CHUVA_ATUAL_MM_H = [0.0, 1.0, 2.5, 5.0, 7.6, 15.0, 30.0, 60.0]
PICO_MM_3H = [0.0, 3.0, 7.5, 15.0, 30.0, 90.0, 150.0]
PLUVIOMETRO_MM_H = [None, 0.0, 5.0, 20.0, 60.0]
COLABORATIVO = [None, 0.0, 15.0, 45.0, 80.0]
PERTURBACOES = [-0.20, -0.10, 0.10, 0.20]


def pesos_perturbados(pesos: dict, criterio: str, variacao: float) -> dict:
    """Pura — multiplica o peso de `criterio` por (1 + variacao) e reescala os
    demais proporcionalmente para a soma continuar 1."""
    novo = pesos[criterio] * (1 + variacao)
    resto_original = 1 - pesos[criterio]
    fator = (1 - novo) / resto_original
    return {k: (novo if k == criterio else v * fator) for k, v in pesos.items()}


def cenarios() -> list[EntradaRisco]:
    return [
        EntradaRisco(c, p, l, col)
        for c, p, l, col in itertools.product(CHUVA_ATUAL_MM_H, PICO_MM_3H, PLUVIOMETRO_MM_H, COLABORATIVO)
    ]


def avaliar(pesos: dict, entradas: list[EntradaRisco]) -> list[dict]:
    with patch.dict(algoritmo_risco.PESOS, pesos):
        return [calcular_risco(e) for e in entradas]


def analisar() -> list[dict]:
    entradas = cenarios()
    base = avaliar(PESOS, entradas)
    linhas = []
    for criterio, variacao in itertools.product(PESOS, PERTURBACOES):
        resultado = avaliar(pesos_perturbados(PESOS, criterio, variacao), entradas)
        mudou = sum(b["classificacao"] != r["classificacao"] for b, r in zip(base, resultado))
        diferencas = [abs(b["score_final"] - r["score_final"]) for b, r in zip(base, resultado)]
        linhas.append({
            "criterio": criterio,
            "variacao": variacao,
            "cenarios": len(entradas),
            "mudou_classificacao": mudou,
            "pct_mudou": 100 * mudou / len(entradas),
            "delta_medio": sum(diferencas) / len(diferencas),
            "delta_max": max(diferencas),
        })
    return linhas


def main() -> None:
    linhas = analisar()
    print(f"{len(cenarios())} cenários; pesos originais: {PESOS}\n")
    print(f"{'critério':<20}{'variação':>9}{'mudou':>8}{'% mudou':>9}{'Δ médio':>9}{'Δ máx':>8}")
    for l in linhas:
        print(f"{l['criterio']:<20}{l['variacao']:>+9.0%}{l['mudou_classificacao']:>8}"
              f"{l['pct_mudou']:>8.1f}%{l['delta_medio']:>9.2f}{l['delta_max']:>8.2f}")


if __name__ == "__main__":
    main()
