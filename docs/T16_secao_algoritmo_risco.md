# Seção: Algoritmo de Classificação de Risco de Alagamento (Modelo AHP)

---

## 3.Y Modelo de Classificação de Risco por Pesos (AHP)

Para converter os dados climáticos de múltiplas fontes em uma classificação de risco de
alagamento compreensível para o usuário final, foi adotado o método AHP (*Analytic
Hierarchy Process*), proposto por Saaty (1980). O AHP é um método de decisão
multicritério amplamente utilizado em problemas que exigem a ponderação de fatores de
naturezas distintas — neste caso, um dado instantâneo (precipitação atual), um dado
preditivo (previsão) e um dado social (reportes colaborativos de usuários). Sua adoção
também atende a um ponto observado pelo orientador: evitar que o sistema seja percebido
como uma simples agregação de chamadas de API, ao introduzir uma camada de processamento
e decisão própria sobre os dados coletados.

### 3.Y.1 Critérios do Modelo

O modelo final usa três critérios:

| Critério | Fonte | Peso |
|---|---|---|
| Precipitação atual | OpenWeather e Open-Meteo, fundidas (maior valor) | 54% |
| Previsão / tendência | OpenWeather e Open-Meteo, fundidas (maior acumulado de 3 h nas próximas 24 h) | 30% |
| Colaborativo | Reportes agregados de usuários do aplicativo | 16% |

O projeto chegou a ter um quarto critério, o **pluviômetro local**, alimentado pela rede
hidrometeorológica da ANA, com os pesos 35/25/25/15. O acesso à ANA depende de cadastro
pedido em agosto de 2026, que não foi respondido; sem dado real, o peso do pluviômetro era
sempre redistribuído entre precipitação atual e previsão. Em 16/10/2026 o critério foi
retirado do modelo (ajuste de escopo documentado), junto com a alternativa estudada — a
estação meteorológica do campus da USCS, que também não teve resposta.

### 3.Y.2 Matriz de Comparação Pareada e Consistência

Os pesos resultam de uma matriz de comparação pareada na escala de Saaty (1 a 9),
comparando cada critério aos demais quanto à sua importância relativa para a antecipação
de um evento de alagamento:

| | Precipitação atual | Previsão | Colaborativo |
|---|---|---|---|
| **Precipitação atual** | 1 | 2 | 3 |
| **Previsão** | 1/2 | 1 | 2 |
| **Colaborativo** | 1/3 | 1/2 | 1 |

A precipitação atual foi julgada moderadamente mais importante que a previsão e entre
moderada e fortemente mais importante que o componente colaborativo — uma medição
instantânea de chuva é o indício mais direto de risco iminente, enquanto um reporte de
usuário isolado é uma fonte de menor confiabilidade individual. São os mesmos julgamentos
já registrados na versão de quatro critérios, sem o critério retirado.

O autovetor principal da matriz dá os pesos 53,96%, 29,70% e 16,34%, usados no sistema
arredondados para **54/30/16, sem ajuste manual**. A Razão de Consistência é
**CR = 0,0079** (λmax = 3,0092; CI = 0,0046; RI = 0,58), bem abaixo do limite de aceitação
de 0,10 estabelecido por Saaty (1980): os julgamentos não têm contradições internas
relevantes. Na versão de quatro critérios, os pesos implementados (35/25/25/15) eram um
ajuste da equipe sobre o autovetor (42/23/23/12); a versão atual elimina esse ajuste.

### 3.Y.3 Fusão das Fontes Meteorológicas

Precipitação atual e previsão são medidas por duas fontes independentes, o OpenWeather e a
Open-Meteo (serviço aberto, sem chave de acesso). Antes do cálculo, as duas leituras de
cada variável são combinadas por uma regra explícita:

1. **Unidades comuns.** A chuva atual do OpenWeather é o acumulado da última hora (mm/h);
   a da Open-Meteo, o acumulado dos últimos 15 minutos, convertido para mm/h. A previsão
   das duas é reduzida ao maior acumulado em um bloco de 3 horas nas 24 horas seguintes.
2. **Com as duas fontes, vale o maior valor** — critério conservador, adequado a um
   sistema de alerta, em que subestimar o risco custa mais que superestimá-lo.
3. **Divergência registrada.** As fontes são consideradas divergentes quando suas leituras
   caem em faixas diferentes da escala de intensidade da OMM (a mesma usada no cálculo). A
   divergência não muda o valor usado; é registrada na resposta da API e mostrada no
   aplicativo.
4. **Com uma fonte só, vale a disponível.** Sem nenhuma, o risco não é calculado
   automaticamente: a API responde com erro 503 e o aplicativo pede que o usuário informe
   o nível de risco ao registrar a ocorrência.

### 3.Y.4 Cálculo do Score e Classificação

Cada componente (precipitação atual e pico de previsão, em mm/h equivalentes) é convertido
para uma escala comum de 0 a 100 por meio de uma função de interpolação baseada na
classificação de intensidade de chuva da Organização Meteorológica Mundial (OMM/WMO):
chuva leve (< 2,5 mm/h), moderada (2,5–7,6 mm/h), forte (7,6–50 mm/h) e violenta
(> 50 mm/h). O score final é a soma ponderada dos componentes, resultando em uma escala de
0 a 100, classificada como:

| Classificação | Faixa de score |
|---|---|
| Baixo risco | 0 – 30 |
| Médio risco | 30 – 60 |
| Alto risco | 60 – 100 |

Em caso de ausência de reportes colaborativos suficientes para a área — cenário esperado
em um piloto com poucos usuários ativos —, o peso do componente colaborativo é
redistribuído proporcionalmente entre os outros dois (64,3% para a precipitação atual e
35,7% para a previsão), em vez de ser descartado silenciosamente, o que subestimaria o score.

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

### 3.Y.5 Testes com Dado Real

O algoritmo foi validado inicialmente com dados reais coletados para o município de Santo
André, SP (precipitação atual de 0,35 mm/h e pico de previsão de 2,14 mm em 3h, ambos
obtidos via OpenWeather), resultando em um score de **4,2 (Baixo risco)** com o modelo de
quatro critérios — coerente com a chuva leve observada no momento da coleta.

Com o modelo final, em 16/10/2026, durante chuva fraca no centro de São Caetano do Sul, o
OpenWeather media 1,02 mm/h e a Open-Meteo 2,0 mm/h; a fusão usou 2,0 mm/h (as duas leituras
na faixa de chuva leve, sem divergência). Para a previsão, o maior acumulado de 3 horas foi
de 4,07 mm pelo OpenWeather e 5,1 mm pela Open-Meteo; valeu 5,1 mm. Os componentes
receberam 20,0 (precipitação atual) e 17,0 (previsão) pontos; sem reportes colaborativos
suficientes, com os pesos redistribuídos (64,3% e 35,7%), o score final foi **18,9 (Baixo
risco)**. Havia um aviso do INMET de "Tempestade — Perigo Potencial" vigente, que não eleva a
classe, como a regra do piso determina.

### 3.Y.6 Análise de Sensibilidade

Para medir o quanto a classificação depende dos pesos escolhidos, cada peso foi variado
em ±10% e ±20% (os demais reescalados para a soma continuar 1) sobre uma grade de 280
cenários de chuva atual, previsão e componente colaborativo, incluindo a ausência de
reportes. Com variação de ±10% em um peso, a classe muda em no máximo 7,1% dos cenários
(ao reduzir o peso da precipitação atual), com diferença média de score abaixo de 1,7
ponto; com ±20%, em no máximo 12,9%. O modelo é, portanto, estável a pequenas variações
nos julgamentos, e as mudanças se concentram em cenários próximos às fronteiras entre as
classes.

### 3.Y.7 Limitações

Os julgamentos de importância relativa entre os critérios da matriz de comparação
pareada foram definidos pela própria equipe do projeto, sem validação por especialistas
externos em hidrologia ou defesa civil, o que é declarado aqui como limitação
metodológica do protótipo; a análise de sensibilidade mitiga, mas não substitui, essa
validação. Os pesos são fixos e não variam por região ou sazonalidade; uma extensão
natural do trabalho seria a recalibração dos pesos por microrregião a partir de histórico
real de ocorrências. Os parâmetros da agregação colaborativa (raio de 1 km, janela de
3 horas e mínimo de dois reportes) são escolhas de projeto do protótipo, ainda não
calibradas com dados reais de uso; o mínimo de dois reportes conta reportes, não
usuários distintos. As duas fontes meteorológicas são modelos de previsão numérica, não
pluviômetros físicos: sem a ANA, o sistema não tem uma medição de chuva em solo.

---

*Seção redigida com base em `backend/algoritmo_risco.py`, `backend/fusao_climatica.py`,
`backend/servicos/colaborativo.py`, `backend/analise_sensibilidade.py` e na documentação
técnica `docs/T15_algoritmo_risco_fundamentacao.md` (consolidada em 17/08/2026; agregação
colaborativa incluída em 03/10/2026; modelo de três critérios e fusão OpenWeather ×
Open-Meteo em 16/10/2026).*
