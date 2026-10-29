# Capturas de tela do aplicativo (relatório final)

Geradas em 29/10/2026 por `android/scripts/roteiro_capturas.py`, no emulador (Android 15,
Pixel 6, idioma português do Brasil, fuso de São Paulo), com o app ligado à API e ao banco
reais, com dados climáticos reais do OpenWeather e previsão e avisos reais do INMET.
Histórico: primeira versão (5 telas) em 03/10/2026; refeitas em 07/10/2026 depois da
liberação do mapa (SHA-1 do APK de teste cadastrado na chave do Google Maps) e da troca do
CPTEC pelo INMET, e de novo no mesmo dia com a busca por endereço no cadastro e os ícones ⓘ
da Previsão; refeitas em 29/10/2026 com as quatro melhorias da avaliação de usabilidade
(entrada sem senha, legenda das cores no mapa, explicação do nível no cadastro e endereço nos
detalhes — `docs/evidencias_testes/usabilidade/`).

**As ocorrências exibidas são de demonstração** (`backend/dados_demo.py`), não alagamentos
reais — dizer isso na legenda de cada figura. O nome do perfil, "João Pedro", é de um integrante
da equipe (desde 29/10/2026; antes, "Maria", fictício).

| Arquivo | Tela |
|---|---|
| `00_login.png` | Entrada do app: sem cadastro nem senha, nome opcional (desde 29/10/2026) |
| `01_mapa.png` | Aba Mapa: ocorrências das últimas 24 h como marcadores coloridos por nível de risco (esmaecidos os de mais de 3 h), alerta de risco alto e resumo da situação atual, que serve de legenda das cores e explica os esmaecidos |
| `02_alertas.png` | Aba Alertas com os filtros, aberta no período padrão (últimas 24 h) |
| `03_alertas_filtrados.png` | Aba Alertas filtrada: São Caetano do Sul, últimas 24 h, risco Alto |
| `04_detalhes.png` | Detalhes de uma ocorrência, com o endereço aproximado (rua e bairro) |
| `05_cadastro.png` | Registrar ocorrência: endereço buscado ("Rua Alegre, 100"), pino no mapa, endereço encontrado, nível escolhido e a explicação dos dois modos de nível |
| `06_previsao_risco.png` | Aba Previsão (modelo de três critérios, 16/10/2026): risco atual calculado pelo AHP com dados reais, aviso oficial do INMET vigente (Tempestade · Perigo Potencial, sem efeito na classe) e os dados usados no cálculo, cada um com o ícone ⓘ da origem |
| `07_ajustes.png` | Aba Ajustes: preferências de alerta e perfil (sem o filtro de fontes, retirado em 16/10/2026) |
| `08_mapa_selecionada.png` | Aba Mapa com uma ocorrência selecionada (painel com nível, fonte, data e "Ver detalhes") |
| `09_perfil.png` | Perfil do usuário (dados ficam só no aparelho) |
| `10_previsao_info_fonte.png` | Aba Previsão: cartão ⓘ da chuva atual — duas fontes (OpenWeather e Open-Meteo), regra de fusão, peso e o valor de cada fonte no momento |

Para refazer (de `android/scripts/`, com os pré-requisitos do cabeçalho do script):
`python roteiro_capturas.py ../../docs/capturas`.
