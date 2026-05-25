import requests
import json

# Complemento ao teste do Aluno 2
# Aluno 2 testou: "Santo André, SP, Brasil"
# Aluno 3 testa: múltiplos pontos de interesse para o sistema de alagamentos

headers = {"User-Agent": "tcc-uscs-alagamentos"}

pontos = [
    "Santo André, SP, Brasil",
    "São Bernardo do Campo, SP, Brasil",
    "Diadema, SP, Brasil",
    "Mauá, SP, Brasil",
]

resultados = []

for endereco in pontos:
    url = f"https://nominatim.openstreetmap.org/search?q={endereco}&format=json"
    resp = requests.get(url, headers=headers, timeout=10)
    data = resp.json()

    if data:
        r = data[0]
        entrada = {
            "endereco_consultado": endereco,
            "nome_retornado": r.get("display_name"),
            "latitude": r.get("lat"),
            "longitude": r.get("lon"),
            "tipo": r.get("type"),
            "osm_type": r.get("osm_type"),
            "boundingbox": r.get("boundingbox"),
        }
        resultados.append(entrada)
        print(f"{endereco}")
        print(f"  -> Lat: {r['lat']}, Lon: {r['lon']}")
    else:
        print(f"Sem resultado para: {endereco}")

with open("testes-api/coordenadas_multiplos_pontos.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, indent=2, ensure_ascii=False)

print("\nArquivo salvo em testes-api/coordenadas_multiplos_pontos.json")
