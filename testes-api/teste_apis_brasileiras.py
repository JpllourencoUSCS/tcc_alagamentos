import requests
import json
from datetime import datetime, timedelta

# ============================================================
# Teste 1 — INMET: lista de estações em SP
# ============================================================
url_estacoes = "https://apitempo.inmet.gov.br/estacoes/T"
headers = {"User-Agent": "tcc-uscs-alagamentos"}

print("=== INMET — Buscando estações ===")
try:
    resp = requests.get(url_estacoes, headers=headers, timeout=10)
    print(f"Status: {resp.status_code}")
    estacoes = resp.json()

    # Filtrar estações de SP
    estacoes_sp = [e for e in estacoes if e.get("SG_ESTADO") == "SP"]
    print(f"Total de estações em SP: {len(estacoes_sp)}")

    # Mostrar 3 mais próximas do Grande ABC (lat ~-23.65, lon ~-46.52)
    def distancia(e):
        try:
            return abs(float(e["VL_LATITUDE"]) - (-23.65)) + abs(float(e["VL_LONGITUDE"]) - (-46.52))
        except Exception:
            return 999

    estacoes_sp.sort(key=distancia)
    mais_proximas = estacoes_sp[:3]

    print("\nEstações mais próximas do Grande ABC:")
    for e in mais_proximas:
        print(f"  - {e.get('DC_NOME')} | Cód: {e.get('CD_ESTACAO')} | Lat: {e.get('VL_LATITUDE')} | Lon: {e.get('VL_LONGITUDE')}")

    with open("testes-api/inmet_estacoes_sp.json", "w", encoding="utf-8") as f:
        json.dump(mais_proximas, f, indent=2, ensure_ascii=False)
    print("\nResultado salvo em testes-api/inmet_estacoes_sp.json")

except Exception as ex:
    print(f"Erro ao acessar INMET: {ex}")

# ============================================================
# Teste 2 — CEMADEN: pluviômetros de Santo André, SP
# ============================================================
# IBGE Santo André: 3547809
hoje = datetime.now().strftime("%Y-%m-%d")
ontem = (datetime.now() - timedelta(days=1)).strftime("%Y-%m-%d")

url_cemaden = (
    f"http://sjc.salvar.cemaden.gov.br/resources/graficos/interface/prec.php"
    f"?uf=SP&municipio=3547809"
    f"&inicio={ontem} 00:00:00"
    f"&fim={hoje} 23:59:59"
)

print("\n=== CEMADEN — Pluviômetros de Santo André ===")
print(f"URL: {url_cemaden}")
try:
    resp_cem = requests.get(url_cemaden, headers=headers, timeout=15)
    print(f"Status: {resp_cem.status_code}")
    data_cem = resp_cem.json()

    print(f"Registros retornados: {len(data_cem)}")
    if len(data_cem) > 0:
        print("Primeiro registro:")
        print(json.dumps(data_cem[0], indent=2, ensure_ascii=False))

    with open("testes-api/cemaden_santo_andre.json", "w", encoding="utf-8") as f:
        json.dump(data_cem, f, indent=2, ensure_ascii=False)
    print("\nResultado salvo em testes-api/cemaden_santo_andre.json")

except Exception as ex:
    print(f"Erro ao acessar CEMADEN: {ex}")
