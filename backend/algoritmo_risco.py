"""
Algoritmo de classificação de risco de alagamento (modelo AHP).

Desde 16/10/2026, três critérios (decisão do grupo: a ANA e a estação da USCS saíram do
projeto por falta de acesso, e com elas o critério "pluviômetro local"). Os pesos são o
autovetor principal da matriz de comparação pareada com os mesmos julgamentos registrados
em docs/T15_algoritmo_risco_fundamentacao.md (C1, C3 e C4 da matriz original), usados sem
ajuste manual — autovetor 53,96% / 29,70% / 16,34%, arredondado para:
- Precipitação atual (OpenWeather + Open-Meteo, maior valor): 54%
- Previsão / pico das próximas 24 h (idem):                    30%
- Dado colaborativo (usuários do app):                         16%
λmax = 3,0092; CI = 0,0046; RI = 0,58; CR = 0,0079 (limite de Saaty: 0,10).

Até 16/10/2026 eram quatro critérios — precipitação atual 35%, pluviômetro local (ANA)
25%, previsão 25%, colaborativo 15% (CR = 0,0038) — com o peso da ANA sempre
redistribuído (60/40 entre precipitação e previsão), porque a credencial nunca foi
liberada: na prática, 50/35/15.

Escala final: 0 a 100
- Baixo risco:  0  a 30
- Médio risco: 30  a 60
- Alto risco:  60 a 100

Os limiares de intensidade de chuva seguem a classificação da OMM (WMO) para
chuva em mm/h: leve (<2.5), moderada (2.5–7.6), forte (7.6–50), violenta (>50).

Fail-safe: sem reportes colaborativos suficientes para a área, o peso do colaborativo
é redistribuído proporcionalmente entre os demais, em vez de zerado silenciosamente
(evita subestimar o risco em áreas com pouca adoção do app) — ver T15, seção 6.3.
"""

from dataclasses import dataclass


PESOS = {
    "precipitacao_atual": 0.54,
    "previsao": 0.30,
    "colaborativo": 0.16,
}

LIMIARES_CHUVA_MM_H = {
    "leve": 2.5,
    "moderada": 7.6,
    "forte": 50.0,
}


def score_precipitacao(mm_h: float) -> float:
    """Converte mm/h em score 0-100 pela classificação da OMM."""
    if mm_h <= 0:
        return 0.0
    if mm_h < LIMIARES_CHUVA_MM_H["leve"]:
        return (mm_h / LIMIARES_CHUVA_MM_H["leve"]) * 25
    if mm_h < LIMIARES_CHUVA_MM_H["moderada"]:
        return 25 + ((mm_h - LIMIARES_CHUVA_MM_H["leve"]) /
                      (LIMIARES_CHUVA_MM_H["moderada"] - LIMIARES_CHUVA_MM_H["leve"])) * 25
    if mm_h < LIMIARES_CHUVA_MM_H["forte"]:
        return 50 + ((mm_h - LIMIARES_CHUVA_MM_H["moderada"]) /
                      (LIMIARES_CHUVA_MM_H["forte"] - LIMIARES_CHUVA_MM_H["moderada"])) * 30
    return 100.0


def score_previsao(pico_mm_3h: float) -> float:
    """Converte o pico de precipitação previsto (mm/3h) em score 0-100."""
    mm_h_equivalente = pico_mm_3h / 3
    return score_precipitacao(mm_h_equivalente)


def faixa_intensidade(mm_h: float) -> int:
    """Faixa da classificação da OMM (0 leve, 1 moderada, 2 forte, 3 violenta) — usada
    pela regra de fusão para dizer quando duas fontes divergem (fusao_climatica.fundir)."""
    if mm_h < LIMIARES_CHUVA_MM_H["leve"]:
        return 0
    if mm_h < LIMIARES_CHUVA_MM_H["moderada"]:
        return 1
    if mm_h < LIMIARES_CHUVA_MM_H["forte"]:
        return 2
    return 3


@dataclass
class EntradaRisco:
    precipitacao_atual_mm_h: float          # já fundida (maior entre OpenWeather e Open-Meteo)
    pico_previsto_mm_3h: float              # idem, maior acumulado de 3 h nas próximas 24 h
    reportes_colaborativos_score: float | None = None  # 0-100 já agregado, ou None se não há
                                                         # reportes suficientes para a área/janela


def _redistribuir_peso_ausente(pesos: dict, chave_ausente: str) -> dict:
    """Zera o peso de `chave_ausente` e o redistribui proporcionalmente entre
    as demais chaves com peso > 0 (mantém a proporção relativa entre elas)."""
    pesos = dict(pesos)
    peso_livre = pesos[chave_ausente]
    pesos[chave_ausente] = 0.0
    soma_restante = sum(v for k, v in pesos.items() if k != chave_ausente)
    if soma_restante == 0:
        return pesos
    return {
        k: (v + peso_livre * (v / soma_restante) if k != chave_ausente else 0.0)
        for k, v in pesos.items()
    }


def calcular_risco(entrada: EntradaRisco) -> dict:
    s_precip = score_precipitacao(entrada.precipitacao_atual_mm_h)
    s_previsao = score_previsao(entrada.pico_previsto_mm_3h)

    pesos = dict(PESOS)

    # Fail-safe — sem reportes colaborativos suficientes para essa área/janela
    # de tempo (None, não 0.0: zero reportes é diferente de reportes indicando
    # risco zero). Redistribuímos o peso do colaborativo proporcionalmente entre
    # os outros dois critérios, em vez de descartar 16% do score silenciosamente
    # — o que subestimaria o risco em áreas com baixa adoção do app.
    s_colab = entrada.reportes_colaborativos_score
    if s_colab is None:
        pesos = _redistribuir_peso_ausente(pesos, "colaborativo")

    score_final = (
        s_precip * pesos["precipitacao_atual"]
        + s_previsao * pesos["previsao"]
        + (s_colab or 0) * pesos["colaborativo"]
    )

    if score_final < 30:
        classificacao = "Baixo"
    elif score_final < 60:
        classificacao = "Médio"
    else:
        classificacao = "Alto"

    return {
        "score_final": round(score_final, 1),
        "classificacao": classificacao,
        "componentes": {
            "precipitacao_atual": round(s_precip, 1),
            "previsao": round(s_previsao, 1),
            "colaborativo": round(s_colab, 1) if s_colab is not None else "N/A (sem reportes suficientes na área)",
        },
        "pesos": {k: round(v, 4) for k, v in pesos.items()},
    }


if __name__ == "__main__":
    # Teste com dados reais coletados em testes-api/ (Santo André, SP), sem reportes
    # colaborativos disponíveis no momento do teste (piloto, sem base de usuários ativa).
    entrada_teste = EntradaRisco(
        precipitacao_atual_mm_h=0.35,   # openweather_atual.json -> rain.1h
        pico_previsto_mm_3h=2.14,       # openweather_previsao.json -> maior rain.3h do horizonte
        reportes_colaborativos_score=None,
    )
    print("=== TESTE COM DADOS REAIS (Santo André, SP) — sem reportes ===")
    print(calcular_risco(entrada_teste))

    # Mesmo cenário, mas com reportes colaborativos indicando ausência de risco
    # (não "sem dado" - reportes existem e dizem "nada acontecendo").
    entrada_com_reportes = EntradaRisco(
        precipitacao_atual_mm_h=0.35,
        pico_previsto_mm_3h=2.14,
        reportes_colaborativos_score=0.0,
    )
    print("\n=== MESMO CENÁRIO, COM REPORTES CONFIRMANDO RISCO ZERO ===")
    print(calcular_risco(entrada_com_reportes))
