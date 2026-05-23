import requests
import json

# Geocoding — converter endereço em coordenadas
endereco = "Santo André, SP, Brasil"
url = f"https://nominatim.openstreetmap.org/search?q={endereco}&format=json"
resp = requests.get(url, headers={"User-Agent": "tcc-uscs-alagamentos"})
data = resp.json()

print(f"Endereço: {endereco}")
print(f"Latitude: {data[0]['lat']}")
print(f"Longitude: {data[0]['lon']}")

with open("testes-api/coordenadas_resultado.json", "w", encoding="utf-8") as f:
    json.dump(data[0], f, indent=2, ensure_ascii=False)