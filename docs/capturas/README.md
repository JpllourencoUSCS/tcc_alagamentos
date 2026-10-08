# Capturas de tela do aplicativo (relatório final)

Geradas em 07/10/2026 por `android/scripts/roteiro_capturas.py`, no emulador (Android 15,
Pixel 6, idioma português do Brasil, fuso de São Paulo), com o app ligado à API e ao banco
reais, com dados climáticos reais do OpenWeather e previsão e avisos reais do INMET.
Histórico: primeira versão (5 telas) em 03/10/2026; refeitas em 07/10/2026 depois da
liberação do mapa (SHA-1 do APK de teste cadastrado na chave do Google Maps) e da troca do
CPTEC pelo INMET, e de novo no mesmo dia com a busca por endereço no cadastro e os ícones ⓘ
da Previsão.

**As ocorrências exibidas são de demonstração** (`backend/dados_demo.py`), não alagamentos
reais — dizer isso na legenda de cada figura. O nome "Maria" do login e do perfil também é
fictício.

| Arquivo | Tela |
|---|---|
| `00_login.png` | Entrada do app (protótipo, sem verificação de senha) |
| `01_mapa.png` | Aba Mapa: ocorrências das últimas 24 h como marcadores coloridos por nível de risco (esmaecidos os de mais de 3 h), alerta de risco alto e resumo da situação atual |
| `02_alertas.png` | Aba Alertas com os filtros, aberta no período padrão (últimas 24 h) |
| `03_alertas_filtrados.png` | Aba Alertas filtrada: São Caetano do Sul, últimas 24 h, risco Alto |
| `04_detalhes.png` | Detalhes de uma ocorrência |
| `05_cadastro.png` | Registrar ocorrência: endereço buscado ("Rua Alegre, 100"), pino no mapa, endereço encontrado e nível escolhido |
| `06_previsao_risco.png` | Aba Previsão: risco atual calculado pelo AHP com dados reais, aviso oficial do INMET vigente (Tempestade · Perigo Potencial, sem efeito na classe) e os dados usados no cálculo, cada um com o ícone ⓘ da origem |
| `07_ajustes.png` | Aba Ajustes: preferências de alerta e perfil |
| `08_mapa_selecionada.png` | Aba Mapa com uma ocorrência selecionada (painel com nível, fonte, data e "Ver detalhes") |
| `09_perfil.png` | Perfil do usuário (dados ficam só no aparelho) |
| `10_previsao_info_fonte.png` | Aba Previsão: cartão aberto pelo ícone ⓘ do pluviômetro local (origem do dado: ANA) |

Para refazer (de `android/scripts/`, com os pré-requisitos do cabeçalho do script):
`python roteiro_capturas.py ../../docs/capturas`.
