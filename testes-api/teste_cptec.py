import requests
import xml.etree.ElementTree as ET
import json

# CPTEC/INPE - Serviços Web em XML, sem necessidade de chave/token.
# Documentação oficial completa: http://servicos.cptec.inpe.br/XML/

BASE_URL = "http://servicos.cptec.inpe.br/XML"

# Tabela de siglas de condição do tempo (documentação oficial)
SIGLAS_TEMPO = {
    "ec": "Encoberto com Chuvas Isoladas", "ci": "Chuvas Isoladas", "c": "Chuva",
    "in": "Instável", "pp": "Poss. de Pancadas de Chuva", "cm": "Chuva pela Manhã",
    "cn": "Chuva a Noite", "pt": "Pancadas de Chuva a Tarde", "pm": "Pancadas de Chuva pela Manhã",
    "np": "Nublado e Pancadas de Chuva", "pc": "Pancadas de Chuva", "pn": "Parcialmente Nublado",
    "cv": "Chuvisco", "ch": "Chuvoso", "t": "Tempestade", "ps": "Predomínio de Sol",
    "e": "Encoberto", "n": "Nublado", "cl": "Céu Claro", "nv": "Nevoeiro", "g": "Geada",
    "ne": "Neve", "nd": "Não Definido", "pnt": "Pancadas de Chuva a Noite",
    "psc": "Possibilidade de Chuva", "pcm": "Possibilidade de Chuva pela Manhã",
    "pct": "Possibilidade de Chuva a Tarde", "pcn": "Possibilidade de Chuva a Noite",
    "npt": "Nublado com Pancadas a Tarde", "npn": "Nublado com Pancadas a Noite",
    "ncn": "Nublado com Poss. de Chuva a Noite", "nct": "Nublado com Poss. de Chuva a Tarde",
    "ncm": "Nubl. c/ Poss. de Chuva pela Manhã", "npm": "Nublado com Pancadas pela Manhã",
    "npp": "Nublado com Possibilidade de Chuva", "vn": "Variação de Nebulosidade",
    "ct": "Chuva a Tarde", "ppn": "Poss. de Panc. de Chuva a Noite",
    "ppt": "Poss. de Panc. de Chuva a Tarde", "ppm": "Poss. de Panc. de Chuva pela Manhã",
}


def buscar_id_cidade(nome_cidade: str) -> list:
    """Busca o ID interno do CPTEC para um município (necessário para a previsão)."""
    url = f"{BASE_URL}/listaCidades"
    resp = requests.get(url, params={"city": nome_cidade}, timeout=15)
    resp.raise_for_status()
    root = ET.fromstring(resp.content)
    cidades = []
    for cidade in root.findall("cidade"):
        cidades.append({
            "nome": cidade.findtext("nome"),
            "uf": cidade.findtext("uf"),
            "id": cidade.findtext("id"),
        })
    return cidades


def buscar_previsao_4dias(id_cidade: str) -> dict:
    url = f"{BASE_URL}/cidade/{id_cidade}/previsao.xml"
    resp = requests.get(url, timeout=15)
    resp.raise_for_status()
    # O XML do CPTEC já declara sua própria codificação no cabeçalho -
    # deixar o ElementTree ler os bytes brutos e resolver sozinho evita bugs
    # de decodificação dupla (ex.: "Santo André" virando "Santo AndrÃ©").
    root = ET.fromstring(resp.content)
    previsoes = []
    for dia in root.findall(".//previsao"):
        sigla = dia.findtext("tempo")
        previsoes.append({
            "dia": dia.findtext("dia"),
            "tempo_sigla": sigla,
            "tempo_desc": SIGLAS_TEMPO.get(sigla, sigla),
            "minima": dia.findtext("minima"),
            "maxima": dia.findtext("maxima"),
            "iuv": dia.findtext("iuv"),
        })
    return {
        "cidade": root.findtext("nome"),
        "uf": root.findtext("uf"),
        "atualizacao": root.findtext("atualizacao"),
        "previsoes": previsoes,
    }


if __name__ == "__main__":
    try:
        print("=== Busca do ID da cidade (Santo André) ===")
        cidades = buscar_id_cidade("santo andre")
        print(json.dumps(cidades, indent=2, ensure_ascii=False))

        if not cidades:
            print("Nenhuma cidade encontrada - verifique o nome de busca (sem acentos).")
        else:
            cidade_sp = next((c for c in cidades if c["uf"] == "SP"), cidades[0])
            print(f"\nUsando: {cidade_sp['nome']}/{cidade_sp['uf']} (id={cidade_sp['id']})")

            with open("testes-api/cptec_busca_cidade.json", "w", encoding="utf-8") as f:
                json.dump(cidades, f, indent=2, ensure_ascii=False)

            print("\n=== Previsão de 4 dias ===")
            previsao = buscar_previsao_4dias(cidade_sp["id"])
            print(json.dumps(previsao, indent=2, ensure_ascii=False))

            with open("testes-api/cptec_previsao_santo_andre.json", "w", encoding="utf-8") as f:
                json.dump(previsao, f, indent=2, ensure_ascii=False)

        print("\nArquivos salvos em testes-api/")

    except requests.exceptions.RequestException as e:
        print(f"Falha na chamada à API do CPTEC/INPE: {e}")
    except ET.ParseError as e:
        print(f"Falha ao interpretar o XML retornado: {e}")

