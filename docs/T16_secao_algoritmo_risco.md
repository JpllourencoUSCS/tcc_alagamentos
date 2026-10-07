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

O algoritmo também trata explicitamente a indisponibilidade de duas de suas fontes. Em
caso de falha pontual da ANA (rede ou expiração do token de autenticação, por exemplo), o
peso do pluviômetro local é redistribuído entre precipitação atual e previsão. Em caso de
ausência de reportes colaborativos suficientes para a área — cenário esperado em um
piloto com poucos usuários ativos —, o peso do componente colaborativo é redistribuído
proporcionalmente entre os demais componentes disponíveis, em vez de ser descartado
silenciosamente. Em ambos os casos, a decisão de projeto é a mesma: evitar que a
indisponibilidade temporária ou estrutural de uma fonte subestime artificialmente o
score final.

O componente colaborativo é calculado a partir dos reportes feitos pelos próprios
usuários no aplicativo. Entram os reportes a até 1 km do ponto avaliado, feitos nas
últimas 3 horas. Cada um é convertido no ponto médio da faixa de risco informada (Baixo →
15, Médio → 45, Alto → 80) e ponderado pela proximidade no tempo e no espaço: reportes mais
recentes e mais próximos pesam mais. O score do componente é a média ponderada desses
valores. Com menos de dois reportes na vizinhança, o componente é considerado ausente e
entra a redistribuição de peso descrita acima, para que um único reporte isolado não
altere a classificação. A busca dos reportes vizinhos usa o mesmo índice espacial GiST
avaliado no benchmark do sistema.

Por fim, os avisos meteorológicos oficiais do INMET para o município funcionam como piso
da classificação final, sem alterar os pesos nem o score do modelo. O nível do piso segue
o risco de alagamento que o próprio INMET declara em cada nível de aviso de chuva: um
aviso de "Perigo" (chuva de 30 a 60 mm/h, "risco de alagamentos") eleva a classe a, no
mínimo, Médio; um aviso de "Grande Perigo" (acima de 60 mm/h, "grande risco de grandes
alagamentos") a eleva a Alto; um aviso de "Perigo Potencial", para o qual o INMET declara
baixo risco de alagamento, não altera a classe. Só contam avisos de chuva vigentes no
momento do cálculo. A regra evita que o sistema indique risco baixo enquanto há um alerta
oficial de alagamento para a cidade, e usa o julgamento do órgão oficial em vez de um
critério novo da equipe. O aplicativo informa quando a classe foi elevada por um aviso.

### 3.Y.4 Teste com Dado Real

O algoritmo foi validado com dados reais coletados para o município de Santo André, SP
(precipitação atual de 0,35 mm/h e pico de previsão de 2,14 mm em 3h, ambos obtidos via
OpenWeather), resultando em um score final de **4,2 (Baixo risco)** — resultado coerente
com a condição de chuva leve observada no momento da coleta.

Um segundo teste foi feito em 03/10/2026 já com o sistema integrado, para o centro de São
Caetano do Sul, escopo atual do monitoramento: sem chuva no momento (0,0 mm/h), com pico
previsto de 12,5 mm em 3 horas nas 24 horas seguintes, pluviômetro da ANA indisponível e
sem reportes colaborativos suficientes. O componente de previsão recebeu 33,2 pontos (chuva
equivalente de 4,2 mm/h, moderada) e o de precipitação atual, zero. Com os pesos dos dois
componentes ausentes redistribuídos, a previsão passou a pesar 41,2%, resultando em um
score final de **13,7 (Baixo risco)** — coerente com um dia ainda seco, com chuva moderada
prevista.

### 3.Y.5 Limitações

Os julgamentos de importância relativa entre os critérios da matriz de comparação
pareada foram definidos pela própria equipe do projeto, sem validação por especialistas
externos em hidrologia ou defesa civil, o que é declarado aqui como limitação
metodológica do protótipo. Os pesos são fixos e não variam por região ou sazonalidade;
uma extensão natural do trabalho seria a recalibração dos pesos por microrregião a
partir de histórico real de ocorrências. Da mesma forma, os parâmetros da agregação
colaborativa (raio de 1 km, janela de 3 horas e mínimo de dois reportes) são escolhas de
projeto do protótipo, ainda não calibradas com dados reais de uso.

---

*Seção redigida com base em `backend/algoritmo_risco.py`, `backend/servicos/colaborativo.py`
e na documentação técnica `docs/T15_algoritmo_risco_fundamentacao.md` (consolidada em
17/08/2026; agregação colaborativa incluída em 03/10/2026).*
