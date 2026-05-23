# Levantamento — OpenWeather API

## Dados da conta
- Plano: Free
- Limite: 1.000 chamadas/dia, 60/minuto
- Chave: (compartilhar internamente, não subir no GitHub)

## Endpoints relevantes para o projeto

| Endpoint | Descrição | Usado para |
|---|---|---|
| /data/2.5/weather | Clima atual por coordenada | Situação em tempo real |
| /data/2.5/forecast | Previsão 5 dias | Alerta antecipado |
| /data/2.5/rain | Precipitação mm/h | Classificação de risco |

## Campos retornados relevantes

| Campo JSON | Significado | Uso no sistema |
|---|---|---|
| main.temp | Temperatura atual | Informativo |
| rain.1h | Chuva última hora (mm) | Classificação de risco |
| weather[0].description | Descrição do clima | Exibição no app |
| coord.lat / coord.lon | Coordenadas | Validação geoespacial |

## Links
- Documentação: https://openweathermap.org/api
- Current Weather: https://openweathermap.org/current
- Forecast: https://openweathermap.org/forecast5
