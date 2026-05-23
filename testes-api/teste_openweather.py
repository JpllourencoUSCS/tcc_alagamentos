import requests
import json
from datetime import datetime

API_KEY = "sua_chave_aqui"
lat = -23.6573  # Santo André
lon = -46.5289

# Teste 1 — Clima atual
url_atual = f"https://api.openweathermap.org/data/2.5/weather?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
resp_atual = requests.get(url_atual)
data_atual = resp_atual.json()

# Teste 2 — Previsão
url_prev = f"https://api.openweathermap.org/data/2.5/forecast?lat={lat}&lon={lon}&appid={API_KEY}&units=metric&lang=pt_br"
resp_prev = requests.get(url_prev)
data_prev = resp_prev.json()

# Salvar resultados
with open("testes-api/openweather_atual.json", "w", encoding="utf-8") as f:
    json.dump(data_atual, f, indent=2, ensure_ascii=False)

with open("testes-api/openweather_previsao.json", "w", encoding="utf-8") as f:
    json.dump(data_prev, f, indent=2, ensure_ascii=False)

print("=== CLIMA ATUAL EM SANTO ANDRÉ ===")
print(f"Temperatura: {data_atual['main']['temp']}°C")
print(f"Clima: {data_atual['weather'][0]['description']}")
print(f"Chuva última hora: {data_atual.get('rain', {}).get('1h', 0)} mm")
print(f"\nArquivos salvos em testes-api/")
