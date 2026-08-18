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

Fail-safe de fontes indisponíveis: se o pluviômetro local (ANA) ou o colaborativo
não tiverem dado para a leitura, o peso do componente ausente é redistribuído
entre os componentes disponíveis em vez de zerado silenciosamente. Isso evita
que o score seja sistematicamente subestimado em áreas sem estação ANA ativa
ou com baixa adoção do app (poucos ou nenhum reporte de usuário) — ver
docs/T15_algoritmo_risco_fundamentacao.md, seção 6.3.
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
    pluviometro_local_mm_h: float | None = None        # ANA — None se a chamada falhar
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

    # Fail-safe 1 — ANA indisponível para essa leitura (falha pontual da API,
    # por exemplo): redistribuímos o peso dela usando o split 60/40 já validado
    # entre precipitação atual e previsão (decisão explícita, documentada, não
    # um dado ausente silenciosamente ignorado). Mantido como split fixo (em
    # vez de proporcional genérico) para não alterar um comportamento já em uso.
    if entrada.pluviometro_local_mm_h is None:
        s_local = None
        peso_pluviometro = pesos["pluviometro_local"]
        pesos["pluviometro_local"] = 0.0
        pesos["precipitacao_atual"] += peso_pluviometro * 0.6
        pesos["previsao"] += peso_pluviometro * 0.4
    else:
        s_local = score_precipitacao(entrada.pluviometro_local_mm_h)

    # Fail-safe 2 — sem reportes colaborativos suficientes para essa área/janela
    # de tempo (None, não 0.0: zero reportes é diferente de reportes indicando
    # risco zero). Redistribuímos o peso do colaborativo proporcionalmente entre
    # os componentes que sobraram (já considerando o ajuste do fail-safe 1, se
    # também tiver ocorrido), em vez de descartar 15% do score silenciosamente
    # — o que subestimaria o risco em áreas com baixa adoção do app.
    s_colab = entrada.reportes_colaborativos_score
    if s_colab is None:
        pesos = _redistribuir_peso_ausente(pesos, "colaborativo")

    score_final = (
        s_precip * pesos["precipitacao_atual"]
        + s_previsao * pesos["previsao"]
        + (s_local or 0) * pesos["pluviometro_local"]
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
            "pluviometro_local": round(s_local, 1) if s_local is not None else "N/A (falha pontual na ANA)",
            "colaborativo": round(s_colab, 1) if s_colab is not None else "N/A (sem reportes suficientes na área)",
        },
    }


if __name__ == "__main__":
    # Teste com dados reais coletados em testes-api/ (Santo André, SP) - sem ANA
    # e sem reportes colaborativos disponíveis no momento do teste (piloto,
    # ainda sem base de usuários ativa).
    entrada_teste = EntradaRisco(
        precipitacao_atual_mm_h=0.35,   # openweather_atual.json -> rain.1h
        pico_previsto_mm_3h=2.14,       # openweather_previsao.json -> maior rain.3h do horizonte
        pluviometro_local_mm_h=None,    # simula falha pontual na ANA para este teste
        reportes_colaborativos_score=None,
    )
    resultado = calcular_risco(entrada_teste)
    print("=== TESTE COM DADOS REAIS (Santo André, SP) — sem ANA e sem reportes ===")
    print(resultado)

    # Mesmo cenário, mas com reportes colaborativos indicando ausência de risco
    # (não "sem dado" - reportes existem e dizem "nada acontecendo").
    entrada_com_reportes = EntradaRisco(
        precipitacao_atual_mm_h=0.35,
        pico_previsto_mm_3h=2.14,
        pluviometro_local_mm_h=None,
        reportes_colaborativos_score=0.0,
    )
    print("\n=== MESMO CENÁRIO, COM REPORTES CONFIRMANDO RISCO ZERO ===")
    print(calcular_risco(entrada_com_reportes))
