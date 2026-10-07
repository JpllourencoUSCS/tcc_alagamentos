"""
Cliente da API de previsão do INMET (apiprevmet3) para São Caetano do Sul/SP.

Endpoints usados:
  GET https://apiprevmet3.inmet.gov.br/previsao/{codigo_ibge}  -> previsão de até 5 dias
  GET https://apiprevmet3.inmet.gov.br/avisos/ativos           -> avisos meteorológicos ativos (Brasil todo)

Não exige cadastro nem token. Requer um User-Agent de navegador.

Levantamento do João (06/10/2026) para substituir o CPTEC, que passou a responder
HTTP 403 em 03/10/2026. Não é o mesmo serviço do INMET descartado em agosto (o dado de
estação em tempo real da apitempo, protegido por reCAPTCHA): esta é a API de previsão
por município e de avisos meteorológicos. Testado ao vivo em 06/10/2026 a partir do
notebook com Docker: previsão e avisos respondendo (HTTP 200).
"""

from datetime import datetime

import requests

BASE_URL = "https://apiprevmet3.inmet.gov.br"
CODIGO_IBGE_SCS = "3548807"  # São Caetano do Sul/SP

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/120.0 Safari/537.36"
    ),
    "Accept": "application/json",
}

TURNOS = ("manha", "tarde", "noite")


def _remover_icones(obj):
    """Remove os campos de ícone em base64, que deixam a resposta muito pesada."""
    if isinstance(obj, dict):
        return {k: _remover_icones(v) for k, v in obj.items() if "icone" not in k}
    return obj


def buscar_previsao(codigo_ibge: str = CODIGO_IBGE_SCS, timeout: int = 30) -> list[dict]:
    """
    Retorna a previsão normalizada, um item por dia, em ordem cronológica.

    Os dois primeiros dias vêm divididos em manhã/tarde/noite.
    Os demais vêm como um único resumo diário (turnos fica vazio).
    """
    resp = requests.get(f"{BASE_URL}/previsao/{codigo_ibge}", headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    dados = _remover_icones(resp.json().get(codigo_ibge, {}))

    dias = []
    for data_br, bloco in dados.items():
        data = datetime.strptime(data_br, "%d/%m/%Y").date()
        turnos = {t: bloco[t] for t in TURNOS if t in bloco}
        partes = list(turnos.values()) or [bloco]

        maximas = [p.get("temp_max") for p in partes if isinstance(p.get("temp_max"), (int, float))]
        minimas = [p.get("temp_min") for p in partes if isinstance(p.get("temp_min"), (int, float))]

        dias.append({
            "data": data.isoformat(),
            "municipio": partes[0].get("entidade"),
            "uf": partes[0].get("uf"),
            "temp_max": max(maximas) if maximas else None,
            "temp_min": min(minimas) if minimas else None,
            "umidade_max": partes[0].get("umidade_max"),
            "umidade_min": partes[0].get("umidade_min"),
            "resumo_dia": partes[0].get("resumo") if not turnos else None,
            "turnos": {
                nome: {
                    "resumo": t.get("resumo"),
                    "dir_vento": t.get("dir_vento"),
                    "int_vento": t.get("int_vento"),
                    "cod_icone": t.get("cod_icone"),
                }
                for nome, t in turnos.items()
            },
        })

    dias.sort(key=lambda d: d["data"])
    return dias


def buscar_avisos(codigo_ibge: str = CODIGO_IBGE_SCS, timeout: int = 30) -> list[dict]:
    """
    Retorna os avisos ativos que incluem o município.
    A resposta vem agrupada em listas (ex.: "hoje" e "futuro"), por isso o laço.
    """
    resp = requests.get(f"{BASE_URL}/avisos/ativos", headers=HEADERS, timeout=timeout)
    resp.raise_for_status()
    bruto = resp.json()

    todos = bruto if isinstance(bruto, list) else [
        aviso for lista in bruto.values() if isinstance(lista, list) for aviso in lista
    ]

    avisos = []
    for aviso in todos:
        codigos = {c.strip() for c in str(aviso.get("geocodes", "")).split(",")}
        if codigo_ibge in codigos:
            avisos.append({
                "id": aviso.get("id"),
                "evento": aviso.get("descricao"),
                "severidade": aviso.get("severidade"),
                "cor": aviso.get("aviso_cor"),
                "inicio": aviso.get("inicio"),
                "fim": aviso.get("fim"),
                "riscos": aviso.get("riscos"),
                "instrucoes": aviso.get("instrucoes"),
                "poligono": aviso.get("poligono"),
            })
    return avisos


if __name__ == "__main__":
    for dia in buscar_previsao():
        print(dia["data"], dia["temp_min"], "a", dia["temp_max"], "°C")
        if dia["turnos"]:
            for nome, t in dia["turnos"].items():
                print(f"   {nome}: {t['resumo']}")
        else:
            print(f"   dia: {dia['resumo_dia']}")

    avisos = buscar_avisos()
    print(f"\nAvisos ativos para São Caetano do Sul: {len(avisos)}")
    for a in avisos:
        print(f" - {a['evento']} ({a['severidade']}) de {a['inicio']} até {a['fim']}")
