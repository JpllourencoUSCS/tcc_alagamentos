import requests
import json
import os

# ANA - HidroWebService (API oficial, confirmada pelo manual técnico da ANA,
# versão 20.02.2026: gov.br/ana .../manual-hidrowebservice_publica.pdf)
#
# IMPORTANTE: existe uma API mais antiga em snirh.gov.br/hidroweb/rest/api que
# retorna 401 - foi descontinuada. A API correta e documentada hoje é esta aqui.
#
# Fluxo de autenticação (token expira em 60 minutos, precisa ser renovado):
#   1) Solicitar cadastro por e-mail a hidro@ana.gov.br (ver docs/T_email_solicitacao_ana.md)
#   2) Receber Identificador (CPF/CNPJ) + Senha por e-mail
#   3) GET .../OAUth/v1 com headers Identificador e Senha -> retorna tokenautenticacao
#   4) Usar o token como "Authorization: Bearer {token}" nas consultas de dados

BASE_URL = "https://www.ana.gov.br/hidrowebservice/EstacoesTelemetricas"

IDENTIFICADOR = os.environ.get("ANA_IDENTIFICADOR", "")  # CPF ou CNPJ cadastrado
SENHA = os.environ.get("ANA_SENHA", "")

# Códigos de estação do ABC Paulista (levantados no portal da ANA)
CODIGO_ESTACAO_SANTO_ANDRE = "21477000"
CODIGO_ESTACAO_SAO_CAETANO_SUL = "21489000"
CODIGO_ESTACAO_SAO_BERNARDO = "21488000"


def gerar_token(identificador: str, senha: str) -> str:
    url = f"{BASE_URL}/OAUth/v1"
    resp = requests.get(
        url,
        headers={"Identificador": identificador, "Senha": senha},
        timeout=15,
    )
    resp.raise_for_status()
    data = resp.json()
    token = data.get("items", {}).get("tokenautenticacao")
    if not token:
        raise RuntimeError(f"Resposta sem token: {data}")
    return token


def consultar_serie_telemetrica(codigo_estacao: str, token: str, dias: int = 30) -> dict:
    """Retorna a série de dados adotados (chuva, cota, vazão) da estação,
    filtrando pelos últimos N dias de leitura."""
    url = f"{BASE_URL}/HidroinfoanaSerieTelemetricaAdotada/v1"
    params = {
        "CodigoDaEstacao": codigo_estacao,
        "TipoFiltroData": "DATA_LEITURA",
        "RangeIntervaloDeBusca": f"DIAS_{dias}",
    }
    resp = requests.get(url, params=params, headers={"Authorization": f"Bearer {token}"}, timeout=15)
    resp.raise_for_status()
    return resp.json()


def consultar_inventario(token: str) -> dict:
    """Retorna metadados das estações (nome, lat/lon, tipo, operadora)."""
    url = f"{BASE_URL}/HidroInventarioEstacoes/v1"
    resp = requests.get(url, headers={"Authorization": f"Bearer {token}"}, timeout=15)
    resp.raise_for_status()
    return resp.json()


if __name__ == "__main__":
    if not (IDENTIFICADOR and SENHA):
        print("Defina ANA_IDENTIFICADOR (CPF/CNPJ) e ANA_SENHA antes de rodar:")
        print('  export ANA_IDENTIFICADOR="seu_cpf_ou_cnpj"')
        print('  export ANA_SENHA="senha_recebida_por_email"')
        print("\nAinda não tem credencial? Ver docs/T_email_solicitacao_ana.md")
        raise SystemExit(1)

    try:
        print("=== Gerando token de autenticação ===")
        token = gerar_token(IDENTIFICADOR, SENHA)
        print("Token obtido com sucesso (válido por 60 minutos).")

        print(f"\n=== Série telemétrica - Santo André ({CODIGO_ESTACAO_SANTO_ANDRE}) ===")
        serie = consultar_serie_telemetrica(CODIGO_ESTACAO_SANTO_ANDRE, token)
        print(json.dumps(serie, indent=2, ensure_ascii=False)[:2000])

        with open("testes-api/ana_serie_santo_andre.json", "w", encoding="utf-8") as f:
            json.dump(serie, f, indent=2, ensure_ascii=False)

        print("\nArquivo salvo em testes-api/ana_serie_santo_andre.json")

    except requests.exceptions.HTTPError as e:
        print(f"Erro HTTP: {e}")
        if e.response is not None and e.response.status_code == 401:
            print("Identificador/Senha inválidos, ou cadastro ainda não aprovado pela ANA.")
    except requests.exceptions.RequestException as e:
        print(f"Falha na chamada à API da ANA: {e}")
    except RuntimeError as e:
        print(f"Erro: {e}")
