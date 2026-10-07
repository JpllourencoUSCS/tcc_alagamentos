# Seção: Resultados Gerais e Discussão

*Rascunho de seção do relatório final — Semana 15 do cronograma (João). Redigido em
03/10/2026. A numeração "5.X" é provisória. Os resultados de usabilidade (5.X.5) dependem
das sessões com participantes, ainda não realizadas.*

---

## 5.X Resultados e Discussão

Esta seção reúne os resultados do trabalho e os discute à luz dos pontos levantados pelo
orientador na avaliação do TCC I: latência na resposta, uso de mais fontes de dados,
complexidade computacional do banco georreferenciado, migração da interface para XML e o
diferencial tecnológico do sistema — que não deveria parecer uma "colagem de APIs".

### 5.X.1 O que foi entregue

| Componente | Situação em 03/10/2026 |
|---|---|
| API REST (FastAPI) | Ocorrências (criar, listar com filtros de fonte, nível, período e região, obter) e risco atual num ponto; em contêiner, com documentação OpenAPI |
| Banco geoespacial | PostgreSQL 16 + PostGIS 3.4, índice GiST, *trigger* de sincronização do ponto geográfico |
| Fusão de fontes climáticas | OpenWeather, ANA e INMET (previsão e avisos oficiais, no lugar do CPTEC) em paralelo, com cache e tolerância a falhas por fonte |
| Classificação de risco | Modelo AHP com quatro critérios (CR = 0,0038), redistribuição de pesos para fontes ausentes e agregação dos reportes colaborativos |
| Aplicativo Android | Kotlin + XML, integrado à API real: mapa, alertas com filtros, risco atual, cadastro colaborativo, detalhes, perfil e notificações |
| Qualidade | 98 testes automatizados no backend e 6 no app; plano de testes PT-001 com 21 casos; benchmark e medição de latência reproduzíveis |

### 5.X.2 Latência

Os critérios de tempo de resposta foram definidos a partir da literatura de interação
humano-computador (T19): leituras com p95 ≤ 200 ms no servidor, para que a resposta
percebida no aplicativo fique abaixo de 1 s. **Todos os critérios medidos foram
atendidos com folga** — as leituras ficaram abaixo de 6 ms no banco de demonstração e
abaixo de 17 ms com 1 milhão de ocorrências, e o cadastro com nível informado teve p95
entre 9 e 17 ms com a API fora do contêiner (o limite era 500 ms). A principal fonte potencial de lentidão do sistema —
as consultas às APIs climáticas externas no cadastro com risco automático — foi tratada no
desenho: chamadas em paralelo (o tempo é o da fonte mais lenta, não a soma), limite de 10 s
por fonte e cache de 10 minutos por região. Com dados climáticos reais, o cadastro com risco
automático levou ~0,5 s sem cache (p95 de 560 ms, contra o limite de 10 s) e ~50 ms com
cache — uma redução de cerca de 10 vezes.

### 5.X.3 Complexidade computacional do banco georreferenciado

O benchmark confirmou empiricamente a hipótese teórica da seção de indexação espacial:
sem índice, o tempo da consulta por região cresce na proporção do volume de dados (O(n));
com o índice GiST, cresce de forma sublinear. Com 100 mil registros, o índice tornou a
consulta **81,6 vezes mais rápida** (14,65 ms → 0,18 ms). O experimento também mostrou dois
limites que costumam ficar de fora da explicação teórica: com 1 milhão de registros, o
custo passa a ser dominado pela quantidade de linhas devolvidas (o termo *k* de
O(log n + k)) e pela dispersão física dessas linhas no disco — atenuada pela reordenação da
tabela segundo o índice (`CLUSTER`), que reduziu o tempo em até 5 vezes —; e o otimizador
do PostgreSQL nem sempre escolhe o índice espacial quando a consulta também ordena por
data. Os dois efeitos ficaram documentados, e nenhum deles compromete os critérios de
latência.

### 5.X.4 Diferencial tecnológico: além da "colagem de APIs"

O sistema não repassa ao usuário o que as APIs externas devolvem. Entre a coleta e a
tela há uma camada de processamento própria, com três contribuições:

1. **Fusão de fontes heterogêneas num único indicador.** Medição instantânea
   (OpenWeather), medição física institucional (ANA), previsão (OpenWeather, com o INMET como
   referência qualitativa) e
   relato humano (usuários) têm naturezas e escalas diferentes. O modelo AHP converte cada
   uma numa escala comum, baseada na classificação de intensidade de chuva da Organização
   Meteorológica Mundial, e as combina com pesos derivados de uma matriz de comparação
   pareada consistente (CR = 0,0038, bem abaixo do limite de 0,10 de Saaty).
2. **Robustez a fontes ausentes.** Fontes públicas brasileiras se mostraram instáveis ou
   protegidas contra automação (CEMADEN, INMET e, nos testes de outubro, o CPTEC). Em vez
   de falhar ou subestimar o risco, o modelo redistribui o peso da fonte ausente e
   continua classificando. A análise de sensibilidade mostrou que a classificação é
   estável: variar um peso em ±10% muda a classe em no máximo 3,7% de 1.400 cenários.
3. **O dado colaborativo como fonte de primeira classe.** Os reportes dos usuários não
   ficam só no mapa: são agregados por proximidade no tempo (3 h) e no espaço (1 km),
   com o mesmo índice espacial avaliado no benchmark, e entram no modelo com peso próprio
   (15%). Um único reporte isolado não altera a classificação. É a fonte que só este
   sistema tem e que não depende de nenhum órgão externo.

A soma dessas três camadas — e não cada API isoladamente — é o que o usuário vê na aba de
risco do aplicativo, com a explicação de quais fontes entraram no cálculo.

### 5.X.5 Usabilidade

*Pendente — preencher após as sessões com participantes (perfil da amostra, taxa de
conclusão por tarefa, média das perguntas em escala Likert comparada ao limiar de 4,
problemas relatados e correções feitas).*

### 5.X.6 Limitações

- **Credenciais externas pendentes.** A ANA não respondeu ao pedido de cadastro até esta
  data; o componente de pluviômetro local foi validado só com dados simulados e, em
  produção, opera pela redistribuição de peso. A estação meteorológica do campus da USCS
  segue em investigação como alternativa.
- **Instabilidade de fontes públicas.** O CPTEC passou a negar acesso (HTTP 403) a partir da
  rede de testes em outubro de 2026; a BrasilAPI, que consulta o mesmo serviço por outra
  infraestrutura, também falhou ao buscar a previsão no mesmo dia. Foi substituído pela API
  de previsão do INMET, também sem documentação oficial nem garantia de disponibilidade.
- **Índice × avisos oficiais.** O índice reflete a chuva medida e a prevista numericamente
  para o ponto; os avisos do INMET são alertas preventivos para áreas amplas e para o dia
  inteiro. Para que as duas informações não se contradigam, os avisos de chuva vigentes
  passaram a funcionar como piso da classe (Perigo → Médio; Grande Perigo → Alto), no nível
  de risco de alagamento declarado pelo próprio INMET — uma regra conservadora, que pode
  elevar o risco de um ponto específico onde não chove.
- **Mapa no ambiente de testes.** A chave do Google Maps do projeto está restrita aos
  certificados Android cadastrados no Google Cloud; o mapa só aparece em builds assinados com
  um desses certificados.
- **Pesos e parâmetros não calibrados com dados reais.** Os julgamentos da matriz AHP foram
  feitos pela equipe, sem especialistas em hidrologia ou defesa civil, e os parâmetros da
  agregação colaborativa (1 km, 3 h, mínimo de dois reportes) são escolhas de projeto. A
  análise de sensibilidade mitiga, mas não substitui, essa calibração.
- **Dados de demonstração.** Não houve episódio real de alagamento registrado pelo sistema
  durante o desenvolvimento; os testes do aplicativo usaram ocorrências de demonstração.
- **Hospedagem.** O ambiente de testes roda num notebook da equipe compartilhado por VPN;
  a implantação em um serviço de hospedagem fica preparada (contêineres), mas não foi feita.
- **Notificações** só são verificadas com o aplicativo aberto.

### 5.X.7 Trabalhos futuros

- Integrar a ANA (assim que as credenciais forem liberadas) ou a estação do campus da USCS
  como pluviômetro local, e validar o modelo com as quatro fontes reais.
- Recalibrar pesos e parâmetros da agregação colaborativa com histórico real de
  ocorrências e com apoio de especialistas (por exemplo, a Defesa Civil municipal).
- Notificações por *push* do servidor, para alertar com o aplicativo fechado.
- Hospedagem em nuvem e testes de carga com vários usuários simultâneos.
- Mecanismos de confiabilidade dos reportes (reputação do usuário, confirmação por
  outros usuários) para reduzir o efeito de reportes equivocados.

---

*Seção redigida com base em T15, T17, T19, nas seções do benchmark, da arquitetura e de
testes, e nos resultados de `backend/benchmark/resultados/` (03/10/2026).*
