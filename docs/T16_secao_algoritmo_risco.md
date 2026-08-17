# Seção: Algoritmo de Classificação de Risco de Alagamento (Modelo AHP)

---

## 3.Y Modelo de Classificação de Risco por Pesos (AHP)

Para converter os dados climáticos de múltiplas fontes em uma classificação de risco de
alagamento compreensível para o usuário final, foi adotado o método AHP (*Analytic
Hierarchy Process*), proposto por Saaty (1980). O AHP é um método de decisão
multicritério amplamente utilizado em problemas que exigem a ponderação de fatores de
naturezas distintas — neste caso, um dado instantâneo (precipitação atual), um dado de
medição física institucional (pluviômetro), um dado preditivo (previsão) e um dado
social (reportes colaborativos de usuários). Sua adoção também atende a um ponto
observado pelo orientador: evitar que o sistema seja percebido como uma simples
agregação de chamadas de API, ao introduzir uma camada de processamento e decisão
própria sobre os dados coletados.

### 3.Y.1 Critérios do Modelo

Foram definidos quatro critérios, cada um associado a uma fonte de dado do sistema:

| Critério | Fonte | Peso |
|---|---|---|
| Precipitação atual | OpenWeather (`rain.1h`) | 35% |
| Pluviômetro local | ANA — rede hidrometeorológica nacional | 25% |
| Previsão / tendência | OpenWeather (previsão de 3h, pico nas próximas 24h) | 25% |
| Colaborativo | Reportes agregados de usuários do aplicativo | 15% |

### 3.Y.2 Matriz de Comparação Pareada e Consistência

Os pesos foram formalizados por meio de uma matriz de comparação pareada na escala de
Saaty (1 a 9), comparando cada critério aos demais quanto à sua importância relativa
para a antecipação de um evento de alagamento. A precipitação atual foi julgada
moderadamente mais importante que o pluviômetro local e a previsão, e entre moderada e
fortemente mais importante que o componente colaborativo — refletindo o fato de que uma
medição instantânea de chuva é o indício mais direto de risco iminente, enquanto um
reporte de usuário isolado é uma fonte de menor confiabilidade individual.

A partir do autovetor principal dessa matriz, calculou-se a Razão de Consistência do
julgamento: **CR = 0,0038**, valor bem abaixo do limite de aceitação de 0,10 estabelecido
por Saaty (1980), confirmando que os julgamentos de importância relativa entre os
critérios não apresentam contradições internas relevantes.

Os pesos finais adotados no sistema (35/25/25/15) representam um ajuste, feito pela
equipe do projeto, sobre o resultado bruto do autovetor (aproximadamente 42/23/23/12),
reduzindo a dependência do score em relação a uma única leitura instantânea e reforçando
o peso das fontes redundantes e independentes (pluviômetro físico e componente
colaborativo). A ordem de importância relativa entre os critérios (precipitação atual >
pluviômetro = previsão > colaborativo) foi preservada em relação ao resultado do método.

### 3.Y.3 Cálculo do Score e Classificação

Cada componente de entrada (precipitação atual e pico de previsão, em mm/h) é convertido
para uma escala comum de 0 a 100 por meio de uma função de interpolação baseada na
classificação de intensidade de chuva da Organização Meteorológica Mundial (OMM/WMO):
chuva leve (< 2,5 mm/h), moderada (2,5–7,6 mm/h), forte (7,6–50 mm/h) e violenta
(> 50 mm/h). O score final é a soma ponderada dos quatro componentes, resultando em uma
escala de 0 a 100, classificada como:

| Classificação | Faixa de score |
|---|---|
| Baixo risco | 0 – 30 |
| Médio risco | 30 – 60 |
| Alto risco | 60 – 100 |

O algoritmo também trata explicitamente a indisponibilidade pontual da fonte ANA (por
exemplo, em caso de falha de rede ou expiração do token de autenticação): nesse cenário,
o peso do pluviômetro local é redistribuído proporcionalmente entre precipitação atual e
previsão, em vez de descartado silenciosamente — uma decisão de projeto que evita
distorcer o score por indisponibilidade temporária de uma única fonte externa.

### 3.Y.4 Teste com Dado Real

O algoritmo foi validado com dados reais coletados para o município de Santo André, SP
(precipitação atual de 0,35 mm/h e pico de previsão de 2,14 mm em 3h, ambos obtidos via
OpenWeather), resultando em um score final de **4,2 (Baixo risco)** — resultado coerente
com a condição de chuva leve observada no momento da coleta.

### 3.Y.5 Limitações

Os julgamentos de importância relativa entre os critérios da matriz de comparação
pareada foram definidos pela própria equipe do projeto, sem validação por especialistas
externos em hidrologia ou defesa civil, o que é declarado aqui como limitação
metodológica do protótipo. Os pesos são fixos e não variam por região ou sazonalidade;
uma extensão natural do trabalho seria a recalibração dos pesos por microrregião a
partir de histórico real de ocorrências.

---

*Seção redigida com base em `backend/algoritmo_risco.py` e na documentação técnica
`docs/T15_algoritmo_risco_fundamentacao.md`, consolidada em 17/08/2026.*
