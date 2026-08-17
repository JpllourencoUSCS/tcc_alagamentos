# Seção: Estudo e Comparação das APIs Utilizadas

---

## 3.X Levantamento e Avaliação das APIs Externas

Para o desenvolvimento do sistema, foi necessário identificar e avaliar fontes externas de dados
que pudessem fornecer informações climáticas em tempo real e suporte a georreferenciamento.
O levantamento considerou critérios como disponibilidade de acesso gratuito, qualidade e
granularidade dos dados retornados, facilidade de integração com o backend em Python e
relevância das informações para a classificação de risco de alagamento.

### 3.X.1 APIs Climáticas — Arquitetura Final

Foram avaliadas quatro fontes de dados meteorológicos: OpenWeather, INMET (Instituto Nacional
de Meteorologia), CEMADEN (Centro Nacional de Monitoramento e Alertas de Desastres Naturais) e,
posteriormente, ANA (Agência Nacional de Águas e Saneamento Básico) e CPTEC/INPE. A arquitetura
final do sistema utiliza três dessas fontes, cada uma cobrindo um papel distinto no modelo de
classificação de risco (ver seção 3.Y — Algoritmo de Classificação de Risco):

| Fonte | Papel no sistema | Autenticação |
|---|---|---|
| OpenWeather | Precipitação atual (principal) + previsão principal | Chave de API (gratuita) |
| ANA | Pluviômetro local — dado de medição física institucional | E-mail de cadastro + token OAuth (60 min) |
| CPTEC/INPE | Previsão municipal de 4 dias — validação cruzada qualitativa | Sem token |

O INMET e o CEMADEN foram avaliados e **descartados** após testes de integração, não por falta
de valor institucional, mas por proteção deliberada contra automação em seus canais de dado "ao
vivo":

- **CEMADEN**: o acesso à API de pluviômetros automáticos (PED) depende de um fluxo de
  autenticação em duas etapas — cadastro de e-mail junto ao órgão e geração de token via um
  sistema de autenticação separado (SGAA) — cuja URL exata não é documentada publicamente e
  depende de resposta institucional sem prazo definido.
- **INMET**: o endpoint que alimenta o dado "ao vivo" (`apitempo.inmet.gov.br/estacao/front/`)
  exige um token de **Google reCAPTCHA v3** gerado por página, proteção anti-bot que este
  projeto não contorna. O endpoint histórico alternativo, sem essa proteção, foi testado com
  dois intervalos de datas diferentes e retornou vazio (HTTP 204) em ambos os casos.

Esse achado é registrado aqui como resultado metodológico legítimo, não como falha do projeto:
**múltiplos órgãos brasileiros de dados hidrometeorológicos protegem especificamente o acesso
"ao vivo" contra automação**, mesmo disponibilizando os mesmos dados publicamente por outros
meios com alguma defasagem — um ponto relevante para discussão sobre os desafios práticos de
integração com dados públicos brasileiros.

A remoção do INMET não deixou nenhum peso do modelo de classificação de risco sem cobertura: o
INMET nunca teve peso próprio nesse modelo — era apenas uma fonte redundante de "precipitação
atual", papel que o OpenWeather já cumpria sozinho desde o início do projeto. Em lugar do
CEMADEN, o papel de "pluviômetro local" passou a ser cumprido pela ANA, cujo processo de
cadastro, embora também exija e-mail (`hidro@ana.gov.br`), está oficialmente documentado
(manual técnico da ANA).

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

### 3.X.3 Resultados dos Testes com a ANA

A integração com a ANA (`backend/fusao_climatica.py`, `testes-api/teste_ana.py`) segue o fluxo
oficial documentado no manual técnico do órgão: autenticação via `Identificador`/`Senha`
cadastrados por e-mail, geração de um token OAuth com validade de 60 minutos, e consulta à
série telemétrica adotada da estação (campo `Chuva_Adotada`, em mm) por código de estação —
`21477000` para Santo André, SP, confirmado junto às demais estações do ABC Paulista
(`21489000` São Caetano do Sul, `21488000` São Bernardo do Campo).

Até o fechamento desta seção, a integração está implementada e testada estruturalmente (fluxo
de token, chamada autenticada, tratamento de erro), mas a validação de ponta a ponta com dados
reais depende da aprovação do cadastro solicitado à ANA (`hidro@ana.gov.br`), pendência externa
ao controle da equipe. O sistema foi projetado para **não falhar** na ausência desse dado: caso
a chamada à ANA não retorne (credenciais pendentes, token expirado ou erro de rede), o algoritmo
de risco redistribui o peso desse componente entre precipitação atual e previsão, em vez de
travar ou descartar o cálculo (ver seção 3.Y).

### 3.X.4 Resultados dos Testes com o CPTEC/INPE

O CPTEC/INPE foi integrado como segunda fonte de previsão, usada como validação cruzada
qualitativa da previsão do OpenWeather (`backend/fusao_climatica.py`,
`testes-api/teste_cptec.py`). O endpoint de previsão de 4 dias (`/XML/cidade/{id}/previsao.xml`)
funciona de ponta a ponta para o identificador de cidade `4704` (Santo André, SP — existe também
um identificador `4703` para uma Santo André no estado da Paraíba, por isso o script filtra
explicitamente por UF=SP), retornando siglas de condição do tempo traduzidas para texto legível
(ex.: `pn` → "Parcialmente Nublado") a partir de uma tabela de siglas oficial do CPTEC.

O endpoint de condições atuais de aeroporto (METAR), inicialmente avaliado como possível fonte
de precipitação atual redundante, foi testado e descartado: o feed retornou vazio ou com erro
500 do servidor do CPTEC nos testes realizados. Por isso, o CPTEC entra no sistema apenas com a
previsão de 4 dias, e apenas como validação qualitativa — o endpoint usado não retorna volume de
chuva em mm, então não alimenta numericamente o modelo de classificação de risco.

### 3.X.5 API de Georreferenciamento

Para conversão de endereços em coordenadas geográficas (geocoding), foi avaliada a API
Nominatim, mantida pelo projeto OpenStreetMap. A API é gratuita, não requer autenticação e
retorna resultados em formato JSON com dados completos de localização.

Testes realizados com o endereço "Santo André, SP, Brasil" retornaram latitude -23.6533 e
longitude -46.5279, com identificação correta do tipo administrativo (município) e bounding box
da região. Esses resultados validam a viabilidade de uso do Nominatim para geocoding no
protótipo, especialmente em cenários onde o usuário informe um endereço textual em vez de
coordenadas diretas via GPS.

### 3.X.6 SDK de Mapas para Android

Foram comparadas duas alternativas para a camada de visualização geográfica no aplicativo
Android: o Google Maps SDK for Android e o OSMDroid, baseado em OpenStreetMap.

O OSMDroid é totalmente gratuito e de código aberto, sem necessidade de chave de API,
com boa documentação. No entanto, sua integração era considerada mais trabalhosa e menos
documentada no contexto avaliado, o que representava risco de prazo para o projeto.

O Google Maps SDK, por outro lado, oferece plano gratuito que cobre até 28.000 requisições
mensais no Dynamic Maps, volume mais do que suficiente para o protótipo, com documentação
oficial extensa. A avaliação original (Semana 1) considerou também a integração nativa com
Jetpack Compose via `maps-compose`; após a decisão de migrar a camada Android de Compose para
Views em XML (ver decisão de arquitetura da Semana 1), essa vantagem específica deixou de se
aplicar, mas não motivou reavaliação do SDK: o Google Maps SDK oferece suporte nativo e igualmente
maduro para integração via XML (`MapView`/`SupportMapFragment`), o que preservou a decisão
original sem necessidade de trocar de fornecedor.

Diante desses critérios, o Google Maps SDK foi selecionado como solução para a camada de
mapas do sistema, hoje implementada em XML (`Marlon`, Semana 3).

### 3.X.7 Síntese das Decisões Tecnológicas

| Componente | Solução Adotada | Justificativa |
|---|---|---|
| Precipitação atual + previsão principal | OpenWeather API | Documentação, plano gratuito, JSON padronizado |
| Pluviômetro local (dado físico institucional) | ANA | Papel que era do CEMADEN no modelo de risco; processo de cadastro oficialmente documentado |
| Previsão redundante (validação cruzada) | CPTEC/INPE | Sem autenticação; previsão de 4 dias funcional de ponta a ponta |
| Geocoding | Nominatim (OpenStreetMap) | Gratuito, sem autenticação, testado com sucesso |
| SDK de mapas (Android) | Google Maps SDK | Suporte nativo tanto a Compose quanto a XML Views; documentação extensa |

O INMET e o CEMADEN foram testados e descartados por proteção documentada contra automação
(reCAPTCHA v3 e fluxo de autenticação sem URL pública, respectivamente) — não por limitação de
documentação, como avaliado preliminarmente. A ANA e o CPTEC assumiram, respectivamente, os
papéis de dado físico institucional e previsão redundante que essas duas fontes ocupariam.

---

*Seção redigida com base nos testes realizados entre 23/05/2026 e 05/08/2026, e revisada em
17/08/2026 para refletir a arquitetura final de fontes de dados (`docs/T_arquitetura_fontes_dados_final.md`).
Arquivos de resultado disponíveis em `testes-api/` no repositório do projeto.*
