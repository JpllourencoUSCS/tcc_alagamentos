"""
Módulo de integração climática consolidada (Semana 3 — João).

Responsável por buscar dados de todas as fontes disponíveis para uma coordenada
e devolver um pacote único, pronto para alimentar o algoritmo de risco
(backend/algoritmo_risco.py).

Arquitetura final de fontes (decisão de 04-05/08/2026 — CEMADEN e INMET
descartados, substituídos por ANA e CPTEC):

- OpenWeather: precipitação atual + previsão principal (integrada e testada)
- ANA:         rede hidrometeorológica nacional — pluviômetro físico institucional,
                cumpre o papel de "dado de medição real" no modelo AHP
                (ver testes-api/teste_ana.py)
- CPTEC/INPE:  previsão municipal (4 dias) — segunda fonte de previsão/validação
                cruzada qualitativa (ver testes-api/teste_cptec.py)

Nota: o INMET foi avaliado e removido do projeto em 05/08/2026. Ele nunca teve
peso próprio no AHP (era só uma fonte redundante de "precipitação atual"), então
sua remoção não deixa nenhum componente do modelo sem cobertura - o OpenWeather
segue sozinho nesse papel. Motivo da remoção: o dado em tempo real é protegido
por reCAPTCHA v3 (não automatizável por princípio) e o endpoint histórico
alternativo não respondeu em nenhum dos testes realizados.
"""

import os
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timedelta
from dataclasses import dataclass

from algoritmo_risco import EntradaRisco, calcular_risco


OPENWEATHER_API_KEY = "sua_chave_aqui"  # mesma chave usada em teste_openweather.py

ANA_BASE_URL = "https://www.ana.gov.br/hidrowebservice/EstacoesTelemetricas"
ANA_IDENTIFICADOR = os.environ.get("ANA_IDENTIFICADOR")  # CPF/CNPJ cadastrado junto à ANA
ANA_SENHA = os.environ.get("ANA_SENHA")
ANA_CODIGO_ESTACAO_SANTO_ANDRE = "21477000"
_ana_token_cache = {"token": None, "obtido_em": None}

CPTEC_BASE_URL = "http://servicos.cptec.inpe.br/XML"
CPTEC_ID_CIDADE_SANTO_ANDRE = "4704"  # confirmado em 05/08/2026 (Santo André/SP; existe também 4703 para Santo André/PB)

# Tabela de siglas de condição do tempo do CPTEC (documentação oficial)
CPTEC_SIGLAS_TEMPO = {
    "ec": "Encoberto com Chuvas Isoladas", "ci": "Chuvas Isoladas", "c": "Chuva",
    "in": "Instável", "pp": "Poss. de Pancadas de Chuva", "cm": "Chuva pela Manhã",
    "cn": "Chuva a Noite", "pt": "Pancadas de Chuva a Tarde", "pm": "Pancadas de Chuva pela Manhã",
    "np": "Nublado e Pancadas de Chuva", "pc": "Pancadas de Chuva", "pn": "Parcialmente Nublado",
    "cv": "Chuvisco", "ch": "Chuvoso", "t": "Tempestade", "ps": "Predomínio de Sol",
    "e": "Encoberto", "n": "Nublado", "cl": "Céu Claro", "nv": "Nevoeiro", "g": "Geada",
    "ne": "Neve", "nd": "Não Definido",
}


@dataclass
class DadosClimaticosConsolidados:
    lat: float
    lon: float
    precipitacao_atual_mm_h: float
    pico_previsto_mm_3h: float
    fonte_precipitacao_atual: str
    fonte_previsao: str
    pluviometro_local_mm_h: float | None = None
    fonte_pluviometro_local: str | None = None
    validacao_cptec: str | None = None  # condição textual (ex. "Chuvoso"), só p/ validação cruzada, não entra no AHP


# ---------- OpenWeather ----------

def _buscar_openweather_atual(lat: float, lon: float) -> dict:
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _buscar_openweather_previsao(lat: float, lon: float) -> dict:
    url = (
        f"https://api.openweathermap.org/data/2.5/forecast"
        f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _pico_precipitacao_3h(previsao_json: dict) -> float:
    """Maior valor de rain.3h dentro das próximas 24h (8 leituras de 3h)."""
    picos = [item.get("rain", {}).get("3h", 0.0) for item in previsao_json.get("list", [])[:8]]
    return max(picos) if picos else 0.0


# ---------- ANA ----------

def _obter_token_ana() -> str | None:
    """Gera (ou reaproveita, se ainda válido) o token da ANA. Token expira em
    60 minutos. Retorna None se as credenciais não estiverem configuradas ou
    se a autenticação falhar (fail-safe)."""
    if not (ANA_IDENTIFICADOR and ANA_SENHA):
        return None

    agora = datetime.utcnow()
    if _ana_token_cache["token"] and _ana_token_cache["obtido_em"]:
        if agora - _ana_token_cache["obtido_em"] < timedelta(minutes=55):
            return _ana_token_cache["token"]

    try:
        resp = requests.get(
            f"{ANA_BASE_URL}/OAUth/v1",
            headers={"Identificador": ANA_IDENTIFICADOR, "Senha": ANA_SENHA},
            timeout=10,
        )
        resp.raise_for_status()
        token = resp.json().get("items", {}).get("tokenautenticacao")
        if token:
            _ana_token_cache["token"] = token
            _ana_token_cache["obtido_em"] = agora
        return token
    except (requests.exceptions.RequestException, ValueError, KeyError):
        return None


def _buscar_ana(codigo_estacao: str = ANA_CODIGO_ESTACAO_SANTO_ANDRE) -> float | None:
    """Precipitação da leitura mais recente da estação telemétrica da ANA
    (campo Chuva_Adotada, em mm). Retorna None em caso de falha (fail-safe:
    nunca derruba a fusão por causa de uma fonte indisponível)."""
    token = _obter_token_ana()
    if not token:
        return None
    try:
        resp = requests.get(
            f"{ANA_BASE_URL}/HidroinfoanaSerieTelemetricaAdotada/v1",
            params={
                "CodigoDaEstacao": codigo_estacao,
                "TipoFiltroData": "DATA_LEITURA",
                "RangeIntervaloDeBusca": "DIAS_1",
            },
            headers={"Authorization": f"Bearer {token}"},
            timeout=10,
        )
        resp.raise_for_status()
        items = resp.json().get("items", [])
        if items:
            return float(items[-1].get("Chuva_Adotada", 0) or 0)
        return None
    except (requests.exceptions.RequestException, ValueError, TypeError, KeyError):
        return None


# ---------- CPTEC/INPE ----------

def _buscar_cptec_previsao(id_cidade: str | None):
    """Condição textual prevista pelo CPTEC (ex.: 'Parcialmente Nublado'), usada
    só como validação cruzada qualitativa da previsão do OpenWeather - o CPTEC
    não retorna mm de chuva diretamente nesse endpoint, então não entra no AHP."""
    if not id_cidade:
        return None
    try:
        url = f"{CPTEC_BASE_URL}/cidade/{id_cidade}/previsao.xml"
        resp = requests.get(url, timeout=10)
        resp.raise_for_status()
        root = ET.fromstring(resp.content)
        primeira_previsao = root.find(".//previsao")
        if primeira_previsao is not None:
            sigla = primeira_previsao.findtext("tempo")
            return CPTEC_SIGLAS_TEMPO.get(sigla, sigla)
        return None
    except (requests.exceptions.RequestException, ET.ParseError):
        return None


# ---------- Consolidação ----------

def obter_dados_consolidados(
    lat: float,
    lon: float,
    codigo_estacao_ana: str = ANA_CODIGO_ESTACAO_SANTO_ANDRE,
    id_cidade_cptec=CPTEC_ID_CIDADE_SANTO_ANDRE,
) -> DadosClimaticosConsolidados:
    atual = _buscar_openweather_atual(lat, lon)
    previsao = _buscar_openweather_previsao(lat, lon)

    precipitacao_atual = atual.get("rain", {}).get("1h", 0.0)
    fonte_precip_atual = "OpenWeather"

    pico_previsto = _pico_precipitacao_3h(previsao)

    pluviometro_local = _buscar_ana(codigo_estacao_ana)
    fonte_local = "ANA" if pluviometro_local is not None else None

    cptec_validacao = _buscar_cptec_previsao(id_cidade_cptec)

    return DadosClimaticosConsolidados(
        lat=lat,
        lon=lon,
        precipitacao_atual_mm_h=precipitacao_atual,
        pico_previsto_mm_3h=pico_previsto,
        fonte_precipitacao_atual=fonte_precip_atual,
        fonte_previsao="OpenWeather",
        pluviometro_local_mm_h=pluviometro_local,
        fonte_pluviometro_local=fonte_local,
        validacao_cptec=cptec_validacao,
    )


# ---------- Integração com o algoritmo de risco (Semana 7) ----------

def classificar_risco(
    dados: DadosClimaticosConsolidados,
    reportes_colaborativos_score: float = 0.0,
) -> dict:
    """Aplica o modelo AHP (algoritmo_risco.calcular_risco) sobre os dados já
    consolidados de uma localização. Fecha o ciclo fusão -> classificação: até
    aqui, os dois módulos existiam prontos e testados isoladamente, mas nada
    ligava a saída de um à entrada do outro.

    A validação qualitativa do CPTEC (dados.validacao_cptec) não entra no
    cálculo do AHP - é apenas anexada ao resultado, como documentado em
    docs/T15_algoritmo_risco_fundamentacao.md.
    """
    entrada = EntradaRisco(
        precipitacao_atual_mm_h=dados.precipitacao_atual_mm_h,
        pico_previsto_mm_3h=dados.pico_previsto_mm_3h,
        pluviometro_local_mm_h=dados.pluviometro_local_mm_h,
        reportes_colaborativos_score=reportes_colaborativos_score,
    )
    resultado = calcular_risco(entrada)
    resultado["validacao_cruzada_cptec"] = dados.validacao_cptec
    resultado["fontes"] = {
        "precipitacao_atual": dados.fonte_precipitacao_atual,
        "previsao": dados.fonte_previsao,
        "pluviometro_local": dados.fonte_pluviometro_local,
    }
    return resultado


def obter_classificacao_risco(
    lat: float,
    lon: float,
    reportes_colaborativos_score: float = 0.0,
    codigo_estacao_ana: str = ANA_CODIGO_ESTACAO_SANTO_ANDRE,
    id_cidade_cptec=CPTEC_ID_CIDADE_SANTO_ANDRE,
) -> dict:
    """Ponto de entrada único do backend: busca dados de todas as fontes para
    uma coordenada e devolve a classificação de risco já pronta. Encadeia
    obter_dados_consolidados() + classificar_risco()."""
    dados = obter_dados_consolidados(lat, lon, codigo_estacao_ana, id_cidade_cptec)
    return classificar_risco(dados, reportes_colaborativos_score)


if __name__ == "__main__":
    # Exemplo de uso local com os JSONs já coletados (sem chamada de rede),
    # simulando o retorno esperado de obter_dados_consolidados() e já
    # aplicando o algoritmo de risco sobre o resultado.
    import json

    with open("testes-api/openweather_atual.json", encoding="utf-8") as f:
        atual = json.load(f)
    with open("testes-api/openweather_previsao.json", encoding="utf-8") as f:
        previsao = json.load(f)

    dados = DadosClimaticosConsolidados(
        lat=atual["coord"]["lat"],
        lon=atual["coord"]["lon"],
        precipitacao_atual_mm_h=atual.get("rain", {}).get("1h", 0.0),
        pico_previsto_mm_3h=_pico_precipitacao_3h(previsao),
        fonte_precipitacao_atual="OpenWeather",
        fonte_previsao="OpenWeather",
        # ANA indisponível neste exemplo offline (sem credenciais/rede) -
        # simula exatamente o cenário de fail-safe descrito na Semana 6.
    )
    print("=== DADOS CONSOLIDADOS (a partir dos JSONs já coletados) ===")
    print(dados)

    print("\n=== CLASSIFICAÇÃO DE RISCO (fusão + algoritmo AHP) ===")
    print(classificar_risco(dados))
