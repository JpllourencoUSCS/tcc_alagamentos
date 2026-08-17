"""
Algoritmo de classificação de risco de alagamento (modelo AHP).

Pesos definidos na Semana 1 e formalizados na Semana 6 com matriz de comparação
pareada e teste de consistência (CR=0.0038, dentro do limite de Saaty de 0.10) —
ver docs/T15_algoritmo_risco_fundamentacao.md para a fundamentação completa:
- Precipitação atual (OpenWeather rain.1h):           35%
- Pluviômetro local (ANA, estação telemétrica):       25%
- Previsão / tendência (OpenWeather forecast):        25%
- Dado colaborativo (usuários do app):                15%

Escala final: 0 a 100
- Baixo risco:  0  a 30
- Médio risco: 30  a 60
- Alto risco:  60 a 100

Os limiares de intensidade de chuva seguem a classificação da OMM (WMO) para
chuva em mm/h: leve (<2.5), moderada (2.5–7.6), forte (7.6–50), violenta (>50).
"""

from dataclasses import dataclass


PESOS = {
    "precipitacao_atual": 0.35,
    "pluviometro_local": 0.25,
    "previsao": 0.25,
    "colaborativo": 0.15,
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


@dataclass
class EntradaRisco:
    precipitacao_atual_mm_h: float          # OpenWeather rain.1h
    pico_previsto_mm_3h: float               # maior rain.3h nas próximas leituras
    pluviometro_local_mm_h: float | None = None   # ANA — None se a chamada falhar
    reportes_colaborativos_score: float = 0.0      # 0-100, já agregado dos reportes de usuários


def calcular_risco(entrada: EntradaRisco) -> dict:
    s_precip = score_precipitacao(entrada.precipitacao_atual_mm_h)
    s_previsao = score_previsao(entrada.pico_previsto_mm_3h)

    # Enquanto o dado da ANA não estiver disponível para essa leitura (falha
    # pontual da API, por exemplo), redistribuímos o peso dele proporcionalmente
    # entre precipitação atual e previsão (decisão explícita, documentada, não
    # um dado ausente silenciosamente ignorado).
    if entrada.pluviometro_local_mm_h is None:
        peso_precip = PESOS["precipitacao_atual"] + PESOS["pluviometro_local"] * 0.6
        peso_previsao = PESOS["previsao"] + PESOS["pluviometro_local"] * 0.4
        peso_colab = PESOS["colaborativo"]
        s_local = None
        peso_local = 0.0
    else:
        s_local = score_precipitacao(entrada.pluviometro_local_mm_h)
        peso_precip = PESOS["precipitacao_atual"]
        peso_previsao = PESOS["previsao"]
        peso_local = PESOS["pluviometro_local"]
        peso_colab = PESOS["colaborativo"]

    score_final = (
        s_precip * peso_precip
        + s_previsao * peso_previsao
        + (s_local or 0) * peso_local
        + entrada.reportes_colaborativos_score * peso_colab
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
            "pluviometro_local": round(s_local, 1) if s_local is not None else "N/A (falha pontual na ANA)",
            "colaborativo": round(entrada.reportes_colaborativos_score, 1),
        },
    }


if __name__ == "__main__":
    # Teste com dados reais coletados em testes-api/ (Santo André, SP)
    entrada_teste = EntradaRisco(
        precipitacao_atual_mm_h=0.35,   # openweather_atual.json -> rain.1h
        pico_previsto_mm_3h=2.14,       # openweather_previsao.json -> maior rain.3h do horizonte
        pluviometro_local_mm_h=None,    # simula falha pontual na ANA para este teste
        reportes_colaborativos_score=0.0,
    )
    resultado = calcular_risco(entrada_teste)
    print("=== TESTE COM DADOS REAIS (Santo André, SP) ===")
    print(resultado)
