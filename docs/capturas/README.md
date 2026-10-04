# Capturas de tela do aplicativo (relatório final)

Geradas em 03/10/2026 por `android/scripts/roteiro_capturas.py`, no emulador (Android 15,
Pixel 6, idioma português do Brasil, fuso de São Paulo), com o app ligado à API e ao banco
reais e com dados climáticos reais do OpenWeather.

**As ocorrências exibidas são de demonstração** (`backend/dados_demo.py`), não alagamentos
reais — dizer isso na legenda de cada figura.

| Arquivo | Tela |
|---|---|
| `02_alertas.png` | Aba Alertas, lista completa com os filtros |
| `03_alertas_filtrados.png` | Aba Alertas filtrada: São Caetano do Sul, últimas 24 h, risco Alto |
| `04_detalhes.png` | Detalhes de uma ocorrência |
| `06_previsao_risco.png` | Aba Previsão: risco atual calculado pelo AHP com dados reais e as fontes usadas |
| `07_ajustes.png` | Aba Ajustes: preferências de alerta e perfil |

**Pendentes:** mapa (`01_mapa.png`) e cadastro (`05_cadastro.png`), que mostram o mapa do
Google. A chave do projeto ainda não aceita o certificado do APK de teste (ver
`docs/questionario_teste_usabilidade.md`, preparação, item 3). Depois de liberar, rodar de
novo o script (de `android/scripts/`): `python roteiro_capturas.py ../../docs/capturas`.
