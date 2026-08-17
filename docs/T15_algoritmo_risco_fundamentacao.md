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

### 6.3 Tratamento de falha da fonte ANA (fail-safe)

Como a ANA depende de credenciais externas e pode falhar pontualmente (ver
`docs/T_arquitetura_fontes_dados_final.md`), o algoritmo trata a ausência do dado do
pluviômetro local como um caso explícito, não como um erro: o peso de C2 (25%) é
redistribuído proporcionalmente — 60% para C1 (precipitação atual) e 40% para C3
(previsão) — em vez de simplesmente zerar esse componente do score. Essa decisão evita
que uma falha pontual de uma única fonte externa distorça o score para baixo
artificialmente.

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

## 8. Limitações e trabalhos futuros

- **Pesos fixos**: o modelo atual usa pesos estáticos (não variam por região ou estação
  do ano). Uma extensão futura poderia recalibrar os pesos por microrregião com base em
  histórico de ocorrências.
- **Validação com especialistas**: os julgamentos da matriz de comparação pareada
  (seção 4) foram feitos pela própria equipe do projeto, não por especialistas em
  hidrologia/defesa civil — uma limitação a declarar explicitamente na seção de
  limitações do relatório final.
- **Componente colaborativo ainda não instrumentado end-to-end**: `reportes_colaborativos_score`
  é recebido pronto pelo algoritmo; a lógica de agregação dos reportes brutos do app em
  um score 0–100 é responsabilidade de outro módulo (fora do escopo deste documento).
- **Sem análise de sensibilidade formal**: não foi medido o quanto o score final muda
  para pequenas variações nos pesos — recomendado como trabalho futuro se houver tempo
  na Fase 4.

## 9. Referências

- SAATY, T. L. *The Analytic Hierarchy Process: Planning, Priority Setting, Resource
  Allocation.* New York: McGraw-Hill, 1980.
- World Meteorological Organization (WMO/OMM) — classificação de intensidade de
  precipitação em mm/h, usada em `LIMIARES_CHUVA_MM_H`.
