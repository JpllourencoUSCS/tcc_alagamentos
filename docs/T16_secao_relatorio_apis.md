# Seção: Estudo e Comparação das APIs Utilizadas

---

## 3.X Levantamento e Avaliação das APIs Externas

Para o desenvolvimento do sistema, foi necessário identificar e avaliar fontes externas de dados
que pudessem fornecer informações climáticas em tempo real e suporte a georreferenciamento.
O levantamento considerou critérios como disponibilidade de acesso gratuito, qualidade e
granularidade dos dados retornados, facilidade de integração com o backend em Python e
relevância das informações para a classificação de risco de alagamento.

### 3.X.1 APIs Climáticas

Foram avaliadas três fontes de dados meteorológicos: OpenWeather, INMET (Instituto Nacional
de Meteorologia) e CEMADEN (Centro Nacional de Monitoramento e Alertas de Desastres
Naturais).

O INMET disponibiliza dados históricos e em tempo real por meio de API pública, com cobertura
de estações meteorológicas distribuídas pelo território nacional. Contudo, a integração exige
autenticação via token e os dados retornados variam conforme a proximidade de estações
físicas, o que pode comprometer a cobertura em áreas sem estação cadastrada próxima.

O CEMADEN, por sua vez, é o principal órgão federal de monitoramento de riscos de desastres
naturais no Brasil e disponibiliza dados de pluviômetros automáticos em municípios de risco.
Embora seja uma fonte com alto valor institucional, a API apresenta documentação limitada e
acesso menos padronizado, o que eleva a complexidade de integração dentro do escopo deste
projeto.

A OpenWeather mostrou-se a alternativa mais viável para o protótipo. A plataforma oferece
plano gratuito com limite de 1.000 requisições por dia e 60 por minuto, suficiente para operação
em ambiente de testes e demonstração. A API é amplamente documentada, com suporte nativo
a respostas em português e retorno em formato JSON padronizado.

Os endpoints avaliados foram o de clima atual (`/data/2.5/weather`) e o de previsão de cinco
dias (`/data/2.5/forecast`), ambos acessados via requisição HTTP com parâmetros de latitude,
longitude, unidade métrica e idioma. Testes foram realizados com as coordenadas de
Santo André, SP (latitude -23.6573, longitude -46.5289), e os resultados confirmaram o
funcionamento esperado da API.

### 3.X.2 Resultados dos Testes com a OpenWeather

Os testes foram executados por meio de scripts em Python utilizando a biblioteca `requests`,
com os resultados salvos em arquivos JSON para análise. O endpoint de clima atual retornou,
no momento do teste, temperatura de 16,65°C, umidade relativa de 93%, cobertura de nuvens
de 100% e precipitação de 0,35 mm na última hora, com descrição "chuva leve". Esses dados
confirmam a granularidade necessária para alimentar as regras de classificação de risco do
sistema.

O endpoint de previsão retornou 40 entradas em intervalos de três horas, cobrindo um horizonte
de cinco dias. A análise dos dados obtidos identificou tendência de aumento de precipitação nas
horas seguintes ao teste, com pico projetado de 2,14 mm em um intervalo de três horas, seguido
de gradual redução a partir do segundo dia. Esse comportamento demonstra a viabilidade de uso
da previsão como mecanismo de alerta antecipado no sistema.

Os campos selecionados para uso no sistema são: `rain.1h` (precipitação na última hora, em mm),
`weather[0].description` (descrição textual do clima), `main.temp` (temperatura atual),
`main.humidity` (umidade relativa) e `coord` (validação das coordenadas retornadas).

### 3.X.3 API de Georreferenciamento

Para conversão de endereços em coordenadas geográficas (geocoding), foi avaliada a API
Nominatim, mantida pelo projeto OpenStreetMap. A API é gratuita, não requer autenticação e
retorna resultados em formato JSON com dados completos de localização.

Testes realizados com o endereço "Santo André, SP, Brasil" retornaram latitude -23.6533 e
longitude -46.5279, com identificação correta do tipo administrativo (município) e bounding box
da região. Esses resultados validam a viabilidade de uso do Nominatim para geocoding no
protótipo, especialmente em cenários onde o usuário informe um endereço textual em vez de
coordenadas diretas via GPS.

### 3.X.4 SDK de Mapas para Android

Foram comparadas duas alternativas para a camada de visualização geográfica no aplicativo
Android: o Google Maps SDK for Android e o OSMDroid, baseado em OpenStreetMap.

O OSMDroid é totalmente gratuito e de código aberto, sem necessidade de chave de API,
com boa documentação. No entanto, sua integração com Jetpack Compose — framework adotado
para a interface do aplicativo — é trabalhosa e menos documentada, o que representa risco de
prazo para o projeto.

O Google Maps SDK, por outro lado, oferece integração nativa com Jetpack Compose por meio
da biblioteca `maps-compose`, mantida pelo próprio Google. O plano gratuito cobre até 28.000
requisições mensais no Dynamic Maps, volume mais do que suficiente para o protótipo.
A documentação oficial é extensa e há ampla disponibilidade de exemplos específicos para
Android com Kotlin.

Diante desses critérios, o Google Maps SDK foi selecionado como solução para a camada de
mapas do sistema.

### 3.X.5 Síntese das Decisões Tecnológicas

| Componente | Solução Adotada | Justificativa |
|---|---|---|
| Dados climáticos em tempo real | OpenWeather API | Documentação, plano gratuito, JSON padronizado |
| Previsão meteorológica | OpenWeather Forecast | Mesmo provedor, 5 dias em intervalos de 3h |
| Geocoding | Nominatim (OpenStreetMap) | Gratuito, sem autenticação, testado com sucesso |
| SDK de mapas (Android) | Google Maps SDK | Integração nativa com Jetpack Compose |

As APIs descartadas nesta versão — INMET e CEMADEN — permanecem como fontes
complementares a serem avaliadas em trabalhos futuros, especialmente para validação
cruzada dos dados de precipitação e maior aderência a fontes institucionais brasileiras.

---

*Seção redigida com base nos testes realizados em 23/05/2026.
Arquivos de resultado disponíveis em `testes-api/` no repositório do projeto.*
