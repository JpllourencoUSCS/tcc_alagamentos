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

Atualização de 06/10/2026 — CPTEC substituído pelo INMET (apiprevmet3): o CPTEC
passou a responder HTTP 403 em todos os endpoints a partir de 03/10/2026 (a
BrasilAPI, que consulta o mesmo serviço, também falhou). No mesmo papel de validação
cruzada qualitativa — fora do AHP — entra a API de previsão por município do INMET
(`apiprevmet3.inmet.gov.br`), mais os avisos meteorológicos oficiais ativos para o
município. É outro serviço do INMET, diferente do descartado em agosto (o dado de
estação em tempo real da apitempo, protegido por reCAPTCHA). Levantamento em
`testes-api/teste_inmet_apiprevmet3.py`.

Atualização de 16/10/2026 — ANA retirada, Open-Meteo e regra de fusão (decisão do grupo):
a ANA nunca liberou a credencial (pedida em agosto) e a estação da USCS não teve resposta;
as duas saíram do projeto. No lugar, a Open-Meteo (gratuita, sem chave) mede as MESMAS
variáveis que o OpenWeather — chuva atual e previsão —, o que permite uma regra de fusão de
verdade (`fundir`): com as duas fontes, vale o MAIOR valor (critério conservador, adequado
a alerta) e a divergência é registrada quando elas caem em faixas diferentes da escala de
intensidade da OMM; com uma só, vale a disponível; sem nenhuma, o risco não é calculado
(FonteClimaticaIndisponivel -> HTTP 503). Até aqui, a falha do OpenWeather sozinho já dava
503; agora a Open-Meteo cobre essa falha.
"""

import logging
import os
import threading
import time
import requests
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from dataclasses import dataclass, field

from algoritmo_risco import EntradaRisco, calcular_risco, faixa_intensidade


# Lida do ambiente (03/10/2026) — até
# então era o texto fixo "sua_chave_aqui", e todo POST /ocorrencias sem
# nivel_risco falhava contra a API real com 401 do OpenWeather.
OPENWEATHER_API_KEY = os.environ.get("OPENWEATHER_API_KEY", "")


class FonteClimaticaIndisponivel(RuntimeError):
    """Nenhuma fonte meteorológica numérica (OpenWeather ou Open-Meteo) respondeu
    para a chuva atual ou para a previsão — o risco não pode ser calculado
    automaticamente."""


OPEN_METEO_URL = "https://api.open-meteo.com/v1/forecast"
_log = logging.getLogger(__name__)

INMET_BASE_URL = "https://apiprevmet3.inmet.gov.br"
INMET_CODIGO_IBGE_SCS = "3548807"  # São Caetano do Sul/SP (código IBGE de 7 dígitos)
# A API não é documentada oficialmente; projetos que a usam relatam que o firewall do
# INMET pode recusar requisições sem User-Agent de navegador (em 06/10/2026 respondeu
# mesmo sem ele, mas o cabeçalho é mantido por segurança).
INMET_HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json",
}
# Fuso de Brasília sem horário de verão (abolido em 2019) — usado para escolher o dia
# e o turno da previsão. Fixo, sem zoneinfo: a imagem slim do Docker não traz a base
# de fusos horários.
FUSO_BRASILIA = timezone(timedelta(hours=-3))


@dataclass
class DadosClimaticosConsolidados:
    lat: float
    lon: float
    # Valores já fundidos (maior entre OpenWeather e Open-Meteo) — o que entra no AHP
    precipitacao_atual_mm_h: float
    pico_previsto_mm_3h: float
    fonte_precipitacao_atual: str
    fonte_previsao: str
    # Detalhe da fusão de cada variável: valor de cada fonte, valor usado, divergência
    fusao_precipitacao: dict = field(default_factory=dict)
    fusao_previsao: dict = field(default_factory=dict)
    # Validação cruzada qualitativa — não entra no AHP (06/10/2026: INMET no lugar do CPTEC)
    previsao_inmet: str | None = None  # ex.: "Muitas nuvens com pancadas de chuva isoladas"
    avisos_inmet: list[dict] = field(default_factory=list)  # avisos oficiais ativos para o município


# ---------- OpenWeather ----------

def _exigir_chave_openweather() -> None:
    if not OPENWEATHER_API_KEY:
        raise FonteClimaticaIndisponivel(
            "OPENWEATHER_API_KEY não definida — configure no .env (ver .env.example)."
        )


def _buscar_openweather_atual(lat: float, lon: float) -> dict:
    _exigir_chave_openweather()
    url = (
        f"https://api.openweathermap.org/data/2.5/weather"
        f"?lat={lat}&lon={lon}&appid={OPENWEATHER_API_KEY}&units=metric&lang=pt_br"
    )
    resp = requests.get(url, timeout=10)
    resp.raise_for_status()
    return resp.json()


def _buscar_openweather_previsao(lat: float, lon: float) -> dict:
    _exigir_chave_openweather()
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


# ---------- Open-Meteo (16/10/2026) ----------

def _buscar_open_meteo(lat: float, lon: float) -> dict | None:
    """Chuva atual e previsão horária da Open-Meteo (sem chave). None em caso de
    falha (fail-safe: a fusão segue com o OpenWeather)."""
    try:
        resp = requests.get(
            OPEN_METEO_URL,
            params={
                "latitude": lat,
                "longitude": lon,
                "current": "precipitation",
                "hourly": "precipitation",
                "timezone": "America/Sao_Paulo",
                "forecast_days": 2,
            },
            timeout=10,
        )
        resp.raise_for_status()
        return resp.json()
    except (requests.exceptions.RequestException, ValueError):
        return None


def precipitacao_atual_open_meteo(dados: dict | None) -> float | None:
    """Pura — chuva atual em mm/h. A Open-Meteo informa o acumulado do último intervalo
    do modelo (`current.interval`, 900 s = 15 min); convertido para mm/h para ficar na
    mesma unidade do OpenWeather (rain.1h)."""
    atual = (dados or {}).get("current") or {}
    valor = atual.get("precipitation")
    if valor is None:
        return None
    intervalo = atual.get("interval") or 3600
    return float(valor) * 3600 / intervalo


def pico_3h_open_meteo(dados: dict | None) -> float | None:
    """Pura — maior acumulado de 3 h nas próximas 24 h, em blocos de 3 horas a partir da
    hora em curso (o mesmo formato da previsão do OpenWeather: 8 blocos de 3 h). Cada
    valor horário da Open-Meteo é o acumulado da hora que termina naquele horário."""
    horario = (dados or {}).get("hourly") or {}
    tempos, valores = horario.get("time") or [], horario.get("precipitation") or []
    agora = ((dados or {}).get("current") or {}).get("time") or ""
    inicio = next((i for i, t in enumerate(tempos) if t > agora), len(tempos))
    proximas = [v or 0.0 for v in valores[inicio:inicio + 24]]
    if not proximas:
        return None
    return max(sum(proximas[i:i + 3]) for i in range(0, len(proximas), 3))


# ---------- Regra de fusão (16/10/2026) ----------

def fundir(openweather: float | None, open_meteo: float | None, horas: int = 1) -> dict | None:
    """Pura — funde duas medidas da mesma variável (chuva atual em mm/h, horas=1; ou
    acumulado previsto de 3 h, horas=3). Com as duas, vale o MAIOR valor (critério
    conservador, adequado a um sistema de alerta) e há divergência quando elas caem em
    faixas diferentes da escala de intensidade da OMM (a mesma do índice). Com uma, vale
    a disponível. Sem nenhuma, None."""
    medidas = {"OpenWeather": openweather, "Open-Meteo": open_meteo}
    disponiveis = {fonte: v for fonte, v in medidas.items() if v is not None}
    if not disponiveis:
        return None
    valor = max(disponiveis.values())
    fontes = [fonte for fonte, v in disponiveis.items() if v == valor]
    divergente = len(disponiveis) == 2 and (
        faixa_intensidade(openweather / horas) != faixa_intensidade(open_meteo / horas)
    )
    return {
        "openweather": openweather,
        "open_meteo": open_meteo,
        "valor": valor,
        "fonte": " e ".join(fontes),
        "divergente": divergente,
    }


# ---------- INMET (apiprevmet3) — no lugar do CPTEC desde 06/10/2026 ----------

def turno_inmet(hora: int) -> str:
    """Pura — turno da previsão do INMET para uma hora local (0-23)."""
    if 6 <= hora < 12:
        return "manha"
    if 12 <= hora < 18:
        return "tarde"
    return "noite"


def resumo_previsao_inmet(dias: dict, agora: datetime) -> str | None:
    """Pura — resumo textual da previsão para o dia e o turno de `agora` (horário de
    Brasília). Os dois primeiros dias da resposta vêm divididos em manhã/tarde/noite;
    os seguintes, com um resumo único por dia. Na madrugada (0h-6h) vale o turno
    "noite" do dia anterior, se ele ainda estiver na resposta; se a data de hoje não
    estiver na resposta, usa o primeiro dia disponível."""
    if not dias:
        return None
    local = agora.astimezone(FUSO_BRASILIA)
    data = local - timedelta(days=1) if local.hour < 6 else local
    bloco = dias.get(data.strftime("%d/%m/%Y")) or dias.get(local.strftime("%d/%m/%Y"))
    if bloco is None:
        bloco = dias[min(dias, key=lambda d: datetime.strptime(d, "%d/%m/%Y"))]
    turno = bloco.get(turno_inmet(local.hour))
    if isinstance(turno, dict):
        return turno.get("resumo")
    return bloco.get("resumo")


# A previsão é por município (~260 KB com os ícones) e igual para qualquer ponto
# dele: cache próprio de 10 min por código IBGE, em vez de baixar de novo para cada
# célula de ~1 km do cache de dados.
_previsao_cache: dict[str, tuple[float, dict]] = {}
_previsao_trava = threading.Lock()


def _buscar_inmet_previsao(
    codigo_ibge: str | None, agora: datetime | None = None, instante: float | None = None
) -> str | None:
    """Previsão textual do INMET para o município (ex.: "Muitas nuvens com pancadas
    de chuva isoladas"). Validação cruzada qualitativa da previsão numérica do
    OpenWeather — não entra no AHP. None em caso de falha (fail-safe)."""
    if not codigo_ibge:
        return None
    instante = time.monotonic() if instante is None else instante
    with _previsao_trava:
        item = _previsao_cache.get(codigo_ibge)
    if item is not None and instante - item[0] < CACHE_TTL_S:
        dias = item[1]
    else:
        try:
            resp = requests.get(f"{INMET_BASE_URL}/previsao/{codigo_ibge}", headers=INMET_HEADERS, timeout=10)
            resp.raise_for_status()
            dias = resp.json().get(codigo_ibge, {})
        except (requests.exceptions.RequestException, ValueError, AttributeError):
            return None
        with _previsao_trava:
            _previsao_cache[codigo_ibge] = (instante, dias)
    try:
        return resumo_previsao_inmet(dias, agora or datetime.now(timezone.utc))
    except (ValueError, TypeError, AttributeError):
        return None


def filtrar_avisos_inmet(bruto, codigo_ibge: str) -> list[dict]:
    """Pura — avisos que incluem o município (campo `geocodes`), já sem os campos
    pesados (ícone, polígono). A resposta da API vem agrupada em listas ("hoje",
    "futuro")."""
    todos = bruto if isinstance(bruto, list) else [
        aviso for lista in (bruto or {}).values() if isinstance(lista, list) for aviso in lista
    ]
    avisos = []
    for aviso in todos:
        codigos = {c.strip() for c in str(aviso.get("geocodes", "")).split(",")}
        if codigo_ibge in codigos:
            riscos = aviso.get("riscos")
            avisos.append({
                "evento": aviso.get("descricao"),
                "severidade": aviso.get("severidade"),
                "cor": aviso.get("aviso_cor"),
                "inicio": aviso.get("inicio"),
                "fim": aviso.get("fim"),
                "riscos": " ".join(riscos) if isinstance(riscos, list) else riscos,
            })
    return avisos


# ---------- Piso de classificação pelos avisos do INMET (07/10/2026) ----------
#
# Decisão do grupo (07/10/2026): avisos oficiais do INMET para o município funcionam
# como PISO da classificação — elevam a classe final, nunca a reduzem, e não mexem nos
# pesos nem no score do AHP. O piso segue a avaliação de risco de alagamento que o
# próprio INMET publica em cada nível dos avisos de chuva (textos oficiais observados
# no feed de avisos em 06/10/2026):
#   Perigo Potencial: "chuva entre 20 e 30 mm/h ou até 50 mm/dia ... Baixo risco de
#                      alagamentos"                                    -> sem piso
#   Perigo:           "chuva entre 30 e 60 mm/h ou 50 e 100 mm/dia ... Risco de
#                      alagamentos"                                    -> piso Médio
#   Grande Perigo:    "chuva superior a 60 mm/h ou maior que 100 mm/dia ... Grande
#                      risco de grandes alagamentos"                   -> piso Alto
# Só contam avisos de chuva (os demais — Baixa Umidade, Onda de Calor... — não têm
# relação com alagamento) e só os vigentes no instante do cálculo.
EVENTOS_CHUVA_INMET = {"Tempestade", "Chuvas Intensas", "Acumulado de Chuva"}
PISO_POR_SEVERIDADE_INMET = {"Perigo Potencial": None, "Perigo": "Médio", "Grande Perigo": "Alto"}
_ORDEM_NIVEL = {"Baixo": 0, "Médio": 1, "Alto": 2}


def aviso_de_chuva(aviso: dict) -> bool:
    """Pura — o aviso trata de chuva? Pelo tipo de evento ou, para um tipo que não
    esteja na lista, por o texto de riscos mencionar alagamento."""
    if aviso.get("evento") in EVENTOS_CHUVA_INMET:
        return True
    return "alagament" in str(aviso.get("riscos") or "").lower()


def aviso_vigente(aviso: dict, agora: datetime) -> bool:
    """Pura — `agora` está entre o início e o fim do aviso? O INMET publica os horários
    no horário de Brasília (ex.: "2026-10-06 08:52")."""
    try:
        inicio = datetime.fromisoformat(str(aviso["inicio"])).replace(tzinfo=FUSO_BRASILIA)
        fim = datetime.fromisoformat(str(aviso["fim"])).replace(tzinfo=FUSO_BRASILIA)
    except (KeyError, TypeError, ValueError):
        return False
    return inicio <= agora <= fim


def piso_por_avisos(avisos: list[dict], agora: datetime) -> dict | None:
    """Pura — o maior piso entre os avisos de chuva vigentes, com o aviso que o
    determinou, ou None quando nenhum aviso impõe piso."""
    melhor = None
    for aviso in avisos or []:
        nivel = PISO_POR_SEVERIDADE_INMET.get(aviso.get("severidade"))
        if nivel is None or not aviso_de_chuva(aviso) or not aviso_vigente(aviso, agora):
            continue
        if melhor is None or _ORDEM_NIVEL[nivel] > _ORDEM_NIVEL[melhor["nivel"]]:
            melhor = {"nivel": nivel, "evento": aviso.get("evento"), "severidade": aviso.get("severidade")}
    return melhor


def aplicar_piso(classificacao: str, piso: dict | None) -> str:
    """Pura — eleva a classificação até o piso; nunca reduz."""
    if piso is None or _ORDEM_NIVEL[piso["nivel"]] <= _ORDEM_NIVEL[classificacao]:
        return classificacao
    return piso["nivel"]


# A lista de avisos é nacional (~400 KB) e igual para qualquer ponto: fica em cache
# próprio de 10 min, em vez de ser baixada de novo para cada célula do cache de dados.
_avisos_cache: dict = {"instante": None, "bruto": None}
_avisos_trava = threading.Lock()


def _buscar_inmet_avisos(codigo_ibge: str | None, agora: float | None = None) -> list[dict] | None:
    """Avisos meteorológicos oficiais do INMET ativos para o município. None em caso de
    falha (fail-safe); lista vazia quando não há aviso."""
    if not codigo_ibge:
        return None
    agora = time.monotonic() if agora is None else agora
    with _avisos_trava:
        instante, bruto = _avisos_cache["instante"], _avisos_cache["bruto"]
    if instante is None or agora - instante >= CACHE_TTL_S:
        try:
            resp = requests.get(f"{INMET_BASE_URL}/avisos/ativos", headers=INMET_HEADERS, timeout=10)
            resp.raise_for_status()
            bruto = resp.json()
        except (requests.exceptions.RequestException, ValueError):
            return None
        with _avisos_trava:
            _avisos_cache.update(instante=agora, bruto=bruto)
    return filtrar_avisos_inmet(bruto, codigo_ibge)


# ---------- Consolidação ----------

def _openweather_ou_none(futuro, nome: str):
    """Resultado de uma chamada ao OpenWeather, ou None se ela falhou (sem chave,
    timeout, 401...). A falha só derruba o cálculo se a Open-Meteo também faltar."""
    try:
        return futuro.result()
    except Exception as erro:  # noqa: BLE001 — qualquer falha vira "fonte ausente"
        _log.warning("OpenWeather (%s) indisponível: %s", nome, erro)
        return None


def obter_dados_consolidados(
    lat: float,
    lon: float,
    codigo_ibge_inmet: str | None = INMET_CODIGO_IBGE_SCS,
) -> DadosClimaticosConsolidados:
    # As chamadas são independentes entre si (nenhuma usa o resultado da
    # outra) — rodar em paralelo em vez de sequencial evita que o pior caso
    # (uma fonte lenta ou fora do ar) some até a soma dos timeouts de 10s
    # (na época, mais o da autenticação da ANA) no tempo de resposta ao usuário; em
    # paralelo, o tempo total fica limitado ao ramo mais lento, não à soma de
    # todos (achado de revisão de latência, 03/09/2026 — ver
    # docs/CRONOGRAMA_STATUS.md). Cada fonte tem fail-safe próprio; desde
    # 16/10/2026 nenhuma derruba sozinha o cálculo (ver `fundir`).
    with ThreadPoolExecutor(max_workers=5) as executor:
        futuro_atual = executor.submit(_buscar_openweather_atual, lat, lon)
        futuro_previsao = executor.submit(_buscar_openweather_previsao, lat, lon)
        futuro_open_meteo = executor.submit(_buscar_open_meteo, lat, lon)
        futuro_inmet_previsao = executor.submit(_buscar_inmet_previsao, codigo_ibge_inmet)
        futuro_inmet_avisos = executor.submit(_buscar_inmet_avisos, codigo_ibge_inmet)

        atual = _openweather_ou_none(futuro_atual, "condição atual")
        previsao = _openweather_ou_none(futuro_previsao, "previsão")
        open_meteo = futuro_open_meteo.result()
        previsao_inmet = futuro_inmet_previsao.result()
        avisos_inmet = futuro_inmet_avisos.result()

    fusao_precip = fundir(
        atual.get("rain", {}).get("1h", 0.0) if atual is not None else None,
        precipitacao_atual_open_meteo(open_meteo),
        horas=1,
    )
    fusao_prev = fundir(
        _pico_precipitacao_3h(previsao) if previsao is not None else None,
        pico_3h_open_meteo(open_meteo),
        horas=3,
    )
    if fusao_precip is None or fusao_prev is None:
        # Nenhuma fonte para uma das variáveis: a API traduz em 503 com mensagem
        # clara, em vez de um 500 genérico ou de um risco calculado pela metade.
        faltando = "chuva atual" if fusao_precip is None else "previsão"
        raise FonteClimaticaIndisponivel(
            f"OpenWeather e Open-Meteo indisponíveis para a {faltando}."
        )

    return DadosClimaticosConsolidados(
        lat=lat,
        lon=lon,
        precipitacao_atual_mm_h=fusao_precip["valor"],
        pico_previsto_mm_3h=fusao_prev["valor"],
        fonte_precipitacao_atual=fusao_precip["fonte"],
        fonte_previsao=fusao_prev["fonte"],
        fusao_precipitacao=fusao_precip,
        fusao_previsao=fusao_prev,
        previsao_inmet=previsao_inmet,
        avisos_inmet=avisos_inmet or [],
    )


# ---------- Cache de dados climáticos (Semana 10, otimização — 03/10/2026) ----------

# OpenWeather atualiza a condição atual a cada ~10 min; buscar de novo antes
# disso só repete o mesmo dado pagando 5 chamadas externas (latência de
# segundos no POST). A chave arredonda lat/lon em 2 casas (~1,1 km), escala
# compatível com a resolução das fontes (OpenWeather e Open-Meteo são por grade,
# o INMET por município) — dois reportes no mesmo bairro em poucos minutos
# reaproveitam a mesma consulta. Era um dos itens "ainda em aberto" do achado
# de latência de 03/09/2026 (ver docs/CRONOGRAMA_STATUS.md).
CACHE_TTL_S = 600
CACHE_CASAS_DECIMAIS = 2
_cache_dados: dict[tuple[float, float], tuple[float, DadosClimaticosConsolidados]] = {}
_cache_trava = threading.Lock()


def chave_cache(lat: float, lon: float) -> tuple[float, float]:
    return (round(lat, CACHE_CASAS_DECIMAIS), round(lon, CACHE_CASAS_DECIMAIS))


def limpar_cache() -> None:
    with _cache_trava:
        _cache_dados.clear()
    with _avisos_trava:
        _avisos_cache.update(instante=None, bruto=None)
    with _previsao_trava:
        _previsao_cache.clear()


def obter_dados_consolidados_em_cache(
    lat: float, lon: float, agora: float | None = None
) -> tuple[DadosClimaticosConsolidados, bool]:
    """Como `obter_dados_consolidados`, mas reaproveita o resultado de uma
    consulta da mesma célula (~1 km) feita há menos de CACHE_TTL_S. Retorna
    (dados, veio_do_cache). Falhas não entram no cache: a próxima chamada tenta
    as fontes de novo."""
    agora = time.monotonic() if agora is None else agora
    chave = chave_cache(lat, lon)
    with _cache_trava:
        item = _cache_dados.get(chave)
    if item is not None and agora - item[0] < CACHE_TTL_S:
        return item[1], True

    dados = obter_dados_consolidados(lat, lon)
    with _cache_trava:
        _cache_dados[chave] = (agora, dados)
    return dados, False


# ---------- Integração com o algoritmo de risco (Semana 7) ----------

def classificar_risco(
    dados: DadosClimaticosConsolidados,
    reportes_colaborativos_score: float | None = None,
    agora: datetime | None = None,
) -> dict:
    """Aplica o modelo AHP (algoritmo_risco.calcular_risco) sobre os dados já
    consolidados de uma localização. Fecha o ciclo fusão -> classificação: até
    aqui, os dois módulos existiam prontos e testados isoladamente, mas nada
    ligava a saída de um à entrada do outro.

    reportes_colaborativos_score é None por padrão (não 0.0): ausência de
    reportes é diferente de reportes confirmando risco zero, e o algoritmo de
    risco trata os dois casos de forma diferente (ver fail-safe 2 em
    algoritmo_risco.calcular_risco). Quem chamar esta função com um score já
    agregado dos reportes reais deve passá-lo explicitamente.

    A previsão textual do INMET (até 03/10/2026, do CPTEC) não entra no cálculo -
    é apenas anexada ao resultado. Os avisos oficiais do INMET também não entram no
    AHP, mas desde 07/10/2026 funcionam como piso da classificação final
    (`piso_por_avisos`): `classificacao_indice` é a classe do AHP e `classificacao`,
    a final, depois do piso. O score não muda. Ver
    docs/T15_algoritmo_risco_fundamentacao.md, seção 6.5.
    """
    entrada = EntradaRisco(
        precipitacao_atual_mm_h=dados.precipitacao_atual_mm_h,
        pico_previsto_mm_3h=dados.pico_previsto_mm_3h,
        reportes_colaborativos_score=reportes_colaborativos_score,
    )
    resultado = calcular_risco(entrada)
    piso = piso_por_avisos(dados.avisos_inmet, agora or datetime.now(timezone.utc))
    resultado["classificacao_indice"] = resultado["classificacao"]
    resultado["classificacao"] = aplicar_piso(resultado["classificacao"], piso)
    resultado["piso_aviso_inmet"] = piso
    resultado["validacao_cruzada_inmet"] = dados.previsao_inmet
    resultado["avisos_inmet"] = dados.avisos_inmet
    resultado["fontes"] = {
        "precipitacao_atual": dados.fonte_precipitacao_atual,
        "previsao": dados.fonte_previsao,
    }
    resultado["fusao"] = {
        "precipitacao_atual": dados.fusao_precipitacao,
        "previsao": dados.fusao_previsao,
    }
    return resultado


def obter_classificacao_risco(
    lat: float,
    lon: float,
    reportes_colaborativos_score: float | None = None,
    codigo_ibge_inmet: str | None = INMET_CODIGO_IBGE_SCS,
) -> dict:
    """Ponto de entrada único do backend: busca dados de todas as fontes para
    uma coordenada e devolve a classificação de risco já pronta. Encadeia
    obter_dados_consolidados() + classificar_risco()."""
    dados = obter_dados_consolidados(lat, lon, codigo_ibge_inmet)
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

    # Só o OpenWeather neste exemplo offline (sem rede para a Open-Meteo)
    fusao_precip = fundir(atual.get("rain", {}).get("1h", 0.0), None, horas=1)
    fusao_prev = fundir(_pico_precipitacao_3h(previsao), None, horas=3)
    dados = DadosClimaticosConsolidados(
        lat=atual["coord"]["lat"],
        lon=atual["coord"]["lon"],
        precipitacao_atual_mm_h=fusao_precip["valor"],
        pico_previsto_mm_3h=fusao_prev["valor"],
        fonte_precipitacao_atual=fusao_precip["fonte"],
        fonte_previsao=fusao_prev["fonte"],
        fusao_precipitacao=fusao_precip,
        fusao_previsao=fusao_prev,
    )
    print("=== DADOS CONSOLIDADOS (a partir dos JSONs já coletados) ===")
    print(dados)

    print("\n=== CLASSIFICAÇÃO DE RISCO (fusão + algoritmo AHP) ===")
    print(classificar_risco(dados))
