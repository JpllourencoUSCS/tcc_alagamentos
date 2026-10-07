# T15 — Fundamentação Técnica do Algoritmo de Classificação de Risco (AHP)

*Responsável: João | Semana 6 do cronograma (atrasada, concluída em 17/08/2026) |
Insumo direto para a seção 3.Y do relatório final (ver `T16_secao_algoritmo_risco.md`)*

## 1. Objetivo

Documentar a fundamentação teórica e o funcionamento do algoritmo de classificação de
risco de alagamento implementado em [`backend/algoritmo_risco.py`](../backend/algoritmo_risco.py),
que converte dados climáticos de múltiplas fontes em um score de risco (0–100) e uma
classificação (Baixo/Médio/Alto).

## 2. Por que AHP (Analytic Hierarchy Process)

O AHP (Saaty, 1980) é um método de decisão multicritério que estrutura um problema em
uma hierarquia de critérios, atribui pesos de importância relativa a cada critério por
meio de comparações par a par, e agrega esses pesos em um score único. Foi escolhido
para este projeto por três motivos:

- **Transparência**: cada componente do score final é rastreável a uma fonte de dado
  específica, o que é importante para explicar ao usuário por que uma área foi
  classificada como "Alto risco".
- **Combina fontes heterogêneas**: o sistema precisa fundir dado instantâneo
  (precipitação atual), dado físico institucional (pluviômetro ANA), dado preditivo
  (previsão) e dado social (reportes colaborativos) — grandezas de naturezas diferentes,
  que o AHP normaliza para uma escala comum de 0 a 100 antes de ponderar.
- **Mecanismo próprio de verificação**: o AHP inclui um teste de consistência (Razão de
  Consistência, CR) que audita se os julgamentos de importância relativa fazem sentido
  entre si — relevante para defender o modelo perante a banca como algo além de uma
  "colagem de APIs com pesos arbitrários".

## 3. Critérios e hierarquia

| Critério | Papel | Peso implementado |
|---|---|---|
| C1 — Precipitação atual | OpenWeather `rain.1h` | 35% |
| C2 — Pluviômetro local | ANA (estação telemétrica física) | 25% |
| C3 — Previsão / tendência | OpenWeather forecast (pico `rain.3h` no horizonte de 24h) | 25% |
| C4 — Colaborativo | Agregação de reportes de usuários do app | 15% |

Ver `docs/T_arquitetura_fontes_dados_final.md` para o detalhamento de como cada fonte
alimenta cada critério.

## 4. Matriz de comparação pareada e cálculo de consistência

**Nota sobre a origem desta matriz:** os pesos 35/25/25/15 foram definidos na Semana 1
por julgamento direto da equipe, sem uma matriz de comparação pareada formalmente
registrada no momento. A matriz abaixo é uma **reconstrução formal**, feita agora como
parte desta documentação, que reproduz o mesmo julgamento qualitativo já adotado pelo
projeto — não uma transcrição do processo original de decisão. Ela serve para dar
rastreabilidade metodológica ao modelo e permitir reportar um CR real e auditável, como
o rigor do método exige.

Escala de Saaty utilizada (1 = igual importância, 3 = moderadamente mais importante,
5 = fortemente mais importante, valores intermediários pares para nuance):

| | C1 | C2 | C3 | C4 |
|---|---|---|---|---|
| **C1** | 1 | 2 | 2 | 3 |
| **C2** | 1/2 | 1 | 1 | 2 |
| **C3** | 1/2 | 1 | 1 | 2 |
| **C4** | 1/3 | 1/2 | 1/2 | 1 |

Julgamentos representados:
- C1 é julgado moderadamente mais importante que C2 e C3 (a₁₂ = a₁₃ = 2): a precipitação
  instantânea é o sinal mais direto de alagamento iminente.
- C1 é julgado entre moderada e fortemente mais importante que C4 (a₁₄ = 3): um reporte
  colaborativo isolado é menos confiável que uma medição instantânea de chuva.
- C2 e C3 são julgados igualmente importantes entre si (a₂₃ = 1): medição física local e
  previsão de curto prazo têm peso comparável na antecipação do risco.
- C2 e C3 são julgados moderadamente mais importantes que C4 (a₂₄ = a₃₄ = 2).

**Cálculo pelo método do autovetor principal** (Saaty, 1980):

- λmax = 4,0104
- Índice de Consistência: CI = (λmax − n) / (n − 1) = (4,0104 − 4) / 3 = 0,0035
- Índice Aleatório para n=4 (tabela de Saaty): RI = 0,90
- **Razão de Consistência: CR = CI / RI = 0,0038**

Como CR < 0,10 (limite de aceitação de Saaty), a matriz é considerada consistente — na
verdade, com folga confortável (CR praticamente zero), o que indica que os julgamentos
qualitativos acima não têm contradições internas relevantes.

## 5. Do autovetor aos pesos implementados

O autovetor principal da matriz acima produz os seguintes pesos brutos:

| Critério | Peso do autovetor | Peso implementado no sistema |
|---|---|---|
| C1 — Precipitação atual | 42,4% | **35%** |
| C2 — Pluviômetro local | 22,7% | **25%** |
| C3 — Previsão | 22,7% | **25%** |
| C4 — Colaborativo | 12,2% | **15%** |

Os pesos implementados não são uma cópia direta do autovetor: representam um ajuste
deliberado de projeto, reduzindo a dominância da precipitação instantânea (C1) e
elevando moderadamente pluviômetro, previsão e colaborativo, para não deixar o score
excessivamente dependente de uma única leitura pontual do OpenWeather e para dar mais
peso a fontes redundantes/independentes (ANA, colaborativo). Ajustar a saída bruta de um
AHP por decisão informada dos responsáveis é prática reconhecida na literatura do método
— o teste de consistência (seção 4) garante que o ponto de partida do ajuste era
racional, não que o resultado final tenha que ser usado sem revisão de bom senso.
A ordem relativa de importância (C1 > C2 = C3 > C4) é preservada em ambos os conjuntos
de pesos.

**Os pesos implementados (35/25/25/15) são uma decisão técnica fechada do projeto — ver
`CLAUDE.md` — e não são alterados por esta documentação.**

## 6. Funcionamento do algoritmo

Implementado em [`backend/algoritmo_risco.py`](../backend/algoritmo_risco.py).

### 6.1 Conversão de mm/h em score (0–100)

A função `score_precipitacao()` converte intensidade de chuva (mm/h) em um score 0–100,
usando os limiares de intensidade de chuva da OMM/WMO:

| Classificação OMM | mm/h | Faixa de score |
|---|---|---|
| Leve | < 2,5 | 0 – 25 |
| Moderada | 2,5 – 7,6 | 25 – 50 |
| Forte | 7,6 – 50 | 50 – 80 |
| Violenta | > 50 | 80 – 100 |

A interpolação dentro de cada faixa é linear. A previsão (`score_previsao()`) usa a
mesma função, convertendo o pico de precipitação previsto (mm em 3h) para uma taxa
equivalente em mm/h antes de aplicar a mesma escala.

### 6.2 Score final e classificação

O score final é a soma ponderada dos quatro componentes (pesos da seção 5), resultando
em uma escala de 0 a 100:

| Classificação | Faixa de score |
|---|---|
| Baixo risco | 0 – 30 |
| Médio risco | 30 – 60 |
| Alto risco | 60 – 100 |

### 6.3 Tratamento de fontes indisponíveis (fail-safe)

O algoritmo trata a ausência de dado de dois componentes como um caso explícito, não
como um erro nem como "risco zero":

- **ANA (C2) indisponível** — dependência de credenciais externas que podem falhar
  pontualmente (ver `docs/T_arquitetura_fontes_dados_final.md`): o peso de C2 (25%) é
  redistribuído com um split fixo 60% para C1 (precipitação atual) e 40% para C3
  (previsão).
- **Colaborativo (C4) indisponível** — sem reportes suficientes de usuários para a
  área/janela de tempo (`reportes_colaborativos_score=None`, distinto de `0.0`, que
  significa "há reportes e eles indicam risco zero"): o peso de C4 (15%) é redistribuído
  **proporcionalmente** entre os componentes que restaram disponíveis (preservando a
  proporção relativa entre eles), em vez do split fixo usado para a ANA. Essa correção
  foi adicionada em 17/08/2026 — antes disso, a ausência de reportes zerava
  silenciosamente 15% do peso do score, subestimando sistematicamente o risco em áreas
  com baixa adoção do app (cenário provável no piloto, com poucos usuários ativos).

Os dois fail-safes são independentes e compostos quando ambas as fontes faltam ao mesmo
tempo: primeiro a redistribuição da ANA é aplicada, depois a redistribuição proporcional
do colaborativo ocorre sobre os pesos já ajustados. Em qualquer combinação, os pesos
somam 1,0. Ver `_redistribuir_peso_ausente()` em `backend/algoritmo_risco.py`.

### 6.4 Agregação dos reportes colaborativos (implementada em 03/10/2026)

O componente C4 recebe um score 0–100 calculado por `backend/servicos/colaborativo.py` a
partir dos reportes brutos de usuários (`ocorrencias.fonte = 'usuario'`). Até esta data o
componente entrava sempre como `None` (ver seção 8).

- **Vizinhança espacial e temporal:** entram os reportes a até **1 km** do ponto avaliado,
  feitos nas **últimas 3 horas**. Alagamento é um fenômeno local e transitório: um reporte
  de outro bairro ou do dia anterior não informa sobre o risco ali e naquele momento. A
  busca usa o índice GiST (`&&` contra um bbox expandido) e depois `ST_DWithin` em
  `geography`, para o raio exato em metros.
- **Valor de cada reporte:** o nível informado pelo usuário vira o ponto médio da faixa
  correspondente da própria escala do modelo: Baixo (0–30) → 15, Médio (30–60) → 45,
  Alto (60–100) → 80. Assim, o componente fica na mesma escala dos outros três.
- **Peso de cada reporte:** o produto de dois decaimentos lineares, um no tempo (1 no
  instante do reporte, 0 após 3 h) e outro na distância (1 no ponto, 0 a 1 km).
  Reportes mais recentes e mais próximos pesam mais, pela mesma lógica da ponderação pelo
  inverso da distância usada em interpolação espacial. O score é a média ponderada dos
  valores.
- **Mínimo de 2 reportes:** com menos do que isso, o resultado é `None` e entra o
  fail-safe 2 (seção 6.3). Um reporte isolado não move o score, o que reduz o efeito de
  reportes equivocados ou mal-intencionados.

Cada score calculado é registrado em `reportes_colaborativos_agregado` (área, janela de
tempo, score e quantidade de reportes), na mesma transação da ocorrência que motivou o
cálculo. Isso deixa rastreável qual valor do componente colaborativo entrou em cada
classificação.

**Exemplo:** um reporte "Alto" feito agora (peso 1) e um "Baixo" feito há 90 min (peso 0,5),
ambos no ponto avaliado, resultam em (80 × 1 + 15 × 0,5) / 1,5 = **58,3**.

Os parâmetros (1 km, 3 h, mínimo de 2) são escolhas de projeto do protótipo, não
calibradas com dados reais. Recalibrá-los a partir do histórico de uso fica como trabalho
futuro, junto com a recalibração dos pesos (seção 8).

### 6.5 Piso pelos avisos oficiais do INMET (decisão de 07/10/2026)

Os avisos meteorológicos oficiais do INMET para o município (`apiprevmet3`, ver
`T16_secao_relatorio_apis.md` §3.X.4.1) **não entram no AHP** — os pesos e o score não
mudam —, mas funcionam como **piso** da classificação final: elevam a classe quando ela
está abaixo do nível indicado pelo aviso, e nunca a reduzem.

O piso segue a avaliação de risco de alagamento que o **próprio INMET** publica em cada
nível dos avisos de chuva (textos oficiais do feed de avisos, observados em 06/10/2026):

| Nível do aviso | Chuva prevista pelo INMET | Risco de alagamento declarado pelo INMET | Piso |
|---|---|---|---|
| Perigo Potencial | 20–30 mm/h ou até 50 mm/dia | "Baixo risco de alagamentos" | nenhum |
| Perigo | 30–60 mm/h ou 50–100 mm/dia | "Risco de alagamentos" | **Médio** |
| Grande Perigo | > 60 mm/h ou > 100 mm/dia | "Grande risco de grandes alagamentos" | **Alto** |

Regras complementares:
- **Só avisos de chuva:** Tempestade, Chuvas Intensas e Acumulado de Chuva (os tipos de
  chuva observados nos 93 avisos do feed em 06/10/2026), ou qualquer outro tipo cujo texto
  de riscos mencione alagamento. Avisos sem relação com alagamento (Baixa Umidade, Onda de
  Calor...) são ignorados.
- **Só avisos vigentes:** o instante do cálculo precisa estar entre o início e o fim do
  aviso (horário de Brasília). Um aviso para amanhã não eleva o risco de hoje.
- **Vários avisos:** vale o maior piso.
- **Transparência:** a API devolve a classe do índice (`classificacao_indice`), a classe
  final (`classificacao`) e o aviso que causou a elevação (`piso_aviso_inmet`); o
  aplicativo exibe "Elevado de BAIXO para MÉDIO pelo aviso do INMET (Tempestade · Perigo)".

**Justificativa.** O índice reflete a chuva medida no ponto e a previsão numérica de
curto prazo; o aviso é a avaliação oficial, para a região, de um evento esperado. Sem o
piso, o aplicativo podia mostrar risco Baixo ao lado de um aviso oficial de risco de
alagamento — situação que um usuário leria como contradição. Adotar como piso o risco de
alagamento declarado pelo próprio INMET evita introduzir um julgamento novo da equipe: o
nível vem do órgão oficial. Por coerência, o aviso "Perigo Potencial" — para o qual o INMET
declara *baixo* risco de alagamento — não eleva a classe; foi o caso observado em
06/10/2026 (aviso de Tempestade, Perigo Potencial; classe Baixo).

**Limitação.** O aviso vale para áreas amplas (vários municípios) e para o dia inteiro;
o piso é, portanto, uma regra conservadora de alerta, não uma medida local. Implementação
e testes: `backend/fusao_climatica.py` (`piso_por_avisos`, `aplicar_piso`) e
`backend/tests/test_inmet.py`.

## 7. Exemplo com dado real

Executando `backend/algoritmo_risco.py` com os dados reais coletados em `testes-api/`
para Santo André, SP (precipitação atual 0,35 mm/h, pico de previsão 2,14 mm/3h, ANA
indisponível neste teste):

```
{'score_final': 4.2, 'classificacao': 'Baixo',
 'componentes': {'precipitacao_atual': 3.5, 'previsao': 7.1,
                 'pluviometro_local': 'N/A (falha pontual na ANA)', 'colaborativo': 0.0}}
```

Resultado coerente com a condição real observada (chuva leve, sem indício de risco de
alagamento).

**Segundo exemplo (03/10/2026, sistema integrado, `GET /risco` para o centro de São Caetano
do Sul):** precipitação atual 0,0 mm/h, pico previsto 12,5 mm/3h, ANA indisponível, sem
reportes colaborativos suficientes →

```
precipitação atual = 0,0 · previsão = 33,2 (4,17 mm/h equivalentes, faixa moderada)
pesos após os dois fail-safes: precipitação 0,588 · previsão 0,412
score = 33,2 × 0,412 = 13,7 → Baixo
```

## 8. Limitações e trabalhos futuros

- **Pesos fixos**: o modelo atual usa pesos estáticos (não variam por região ou estação
  do ano). Uma extensão futura poderia recalibrar os pesos por microrregião com base em
  histórico de ocorrências.
- **Validação com especialistas**: os julgamentos da matriz de comparação pareada
  (seção 4) foram feitos pela própria equipe do projeto, não por especialistas em
  hidrologia/defesa civil — uma limitação a declarar explicitamente na seção de
  limitações do relatório final.
- ~~**Componente colaborativo ainda não instrumentado end-to-end**~~ — **resolvido em
  03/10/2026** (seção 6.4). Até então, a lógica de agregação dos reportes brutos do app em
  um score 0–100 não existia em nenhum repositório do projeto (confirmado em 17/08/2026), e
  o componente entrava sempre como `None`. Continua em aberto a calibração dos parâmetros
  da agregação (raio, janela e mínimo de reportes) com dados reais de uso.
- ~~**Sem análise de sensibilidade formal**~~ — **feita em 03/10/2026** (seção 8.1).

### 8.1 Análise de sensibilidade dos pesos (03/10/2026)

`backend/analise_sensibilidade.py` mede o quanto a classificação mudaria se cada peso
fosse um pouco diferente, **sem alterar os pesos do modelo**. Método "um fator por vez":
o peso de um critério é multiplicado por 0,8, 0,9, 1,1 ou 1,2, e os outros três são
reescalados proporcionalmente para a soma continuar 1. Cada conjunto de pesos é aplicado a
**1.400 cenários**: chuva atual (8 valores de 0 a 60 mm/h) × pico previsto (7 valores de 0
a 150 mm/3h) × pluviômetro (5 valores, incluindo ausente) × colaborativo (5 valores,
incluindo ausente).

| Critério (peso) | −20% | −10% | +10% | +20% | Variação média do score (±20%) |
|---|---|---|---|---|---|
| Precipitação atual (35%) | 6,9% | 3,2% | 3,7% | 7,1% | 2,0 pontos |
| Previsão (25%) | 5,6% | 3,2% | 2,8% | 4,9% | 1,6 ponto |
| Pluviômetro local (25%) | 4,9% | 2,7% | 2,6% | 4,7% | 1,5 ponto |
| Colaborativo (15%) | 2,8% | 1,9% | 1,1% | 2,4% | 0,8 ponto |

*(Percentual dos 1.400 cenários que mudam de classe — Baixo/Médio/Alto — em relação aos
pesos originais. Maior variação individual do score: 7,6 pontos, na escala de 0 a 100.)*

**Leitura:** com erros de até ±10% no julgamento de um peso, no máximo 3,7% dos cenários
mudam de classe; com ±20%, no máximo 7,1%. As mudanças ocorrem nos cenários próximos aos
limites de 30 e 60 pontos, onde qualquer modelo de faixas é sensível. A ordem de
influência acompanha a ordem dos pesos (precipitação atual > previsão ≈ pluviômetro >
colaborativo). O modelo é, portanto, **estável a imprecisões moderadas** nos julgamentos
da matriz pareada — o que reduz, sem eliminar, a limitação de os julgamentos terem sido
feitos pela própria equipe.

## 9. Referências

- SAATY, T. L. *The Analytic Hierarchy Process: Planning, Priority Setting, Resource
  Allocation.* New York: McGraw-Hill, 1980.
- World Meteorological Organization (WMO/OMM) — classificação de intensidade de
  precipitação em mm/h, usada em `LIMIARES_CHUVA_MM_H`.
