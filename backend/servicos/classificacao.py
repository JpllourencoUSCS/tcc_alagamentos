"""
Wrapper fino sobre fusao_climatica (Semana 5 — Henrique, reconstruído em
18/08/2026): isola o endpoint de criação de ocorrências da chamada real às
APIs externas (OpenWeather/ANA/CPTEC), pelo mesmo motivo de
db/repository.py isolar o SQLAlchemy — fusao_climatica.obter_dados_consolidados
faz requests HTTP de verdade, o que não pode rodar em teste automatizado sem
rede e credenciais (ANA_IDENTIFICADOR/ANA_SENHA).
"""

from typing import Protocol

from fusao_climatica import classificar_risco, obter_dados_consolidados


class ClassificadorRiscoProtocol(Protocol):
    def classificar(self, lat: float, lon: float) -> dict: ...


class ClassificadorRiscoReal:
    """Implementação real: fusão de fontes + algoritmo AHP (Semana 7), já
    prontos e testados em backend/fusao_climatica.py e backend/algoritmo_risco.py.

    Devolve só o que o endpoint precisa gravar (classificação e a precipitação
    atual usada no cálculo) — o resto do resultado da fusão (previsão, fontes,
    validação CPTEC) fica disponível para quem quiser consumir
    obter_dados_consolidados/classificar_risco diretamente, mas não é
    persistido em `ocorrencias` hoje.
    """

    def classificar(self, lat: float, lon: float) -> dict:
        dados = obter_dados_consolidados(lat, lon)
        resultado = classificar_risco(dados)
        return {
            "classificacao": resultado["classificacao"],
            "chuva_mm": dados.precipitacao_atual_mm_h,
        }
