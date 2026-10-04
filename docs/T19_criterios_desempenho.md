# T19 — Critérios de Avaliação de Desempenho (RNF de Latência)

*Responsável: João | Semana 11 do cronograma (consolidação dos critérios) | Redigido em
03/10/2026, junto com a primeira medição real de latência da API (Semana 11 do Henrique)
e o benchmark de indexação espacial (Semanas 8–9)*

## 1. Objetivo

Definir, com base em literatura, **quanto tempo cada operação do sistema pode levar** —
os requisitos não funcionais (RNF) de desempenho — e confrontar esses limites com o que
foi medido. Responde ao ponto do orientador sobre "latência na resposta": em vez de
afirmar que o sistema "é rápido", o trabalho declara critérios verificáveis e mostra se
foram atendidos.

## 2. Base teórica

### 2.1 Limites de tempo de resposta percebidos pelo usuário

Os três limites clássicos de tempo de resposta em interfaces (Miller, 1968; Card,
Robertson e Mackinlay, 1991; consolidados por Nielsen, 1993) são a referência mais citada
para requisitos de latência:

| Limite | Percepção do usuário |
|---|---|
| **0,1 s** | A resposta parece instantânea. Nenhum feedback especial é necessário. |
| **1 s** | O fluxo de pensamento não é interrompido, embora o atraso seja notado. |
| **10 s** | Limite para manter a atenção na tarefa. Acima disso, é preciso indicar progresso e permitir que o usuário faça outra coisa. |

O modelo RAIL, do Google, aplica os mesmos limites a aplicações modernas: responder a uma
ação em até 100 ms e carregar conteúdo em até 1 s.

### 2.2 Qualidade de produto de software

A norma ISO/IEC 25010 classifica a **eficiência de desempenho** como característica de
qualidade, com a subcaracterística **comportamento em relação ao tempo** (tempo de
resposta e de processamento). Os RNF abaixo são a instância dessa subcaracterística para o
sistema.

### 2.3 Percentis em vez de média

Os critérios usam o **percentil 95 (p95)**: 95% das requisições precisam ficar abaixo do
limite. A média esconde a cauda, e é a cauda que o usuário percebe como "o app travou"
(Dean e Barroso, 2013, *The Tail at Scale*). A mediana (p50) é reportada junto, como
valor típico.

## 3. Orçamento de tempo do app

No app, o tempo que o usuário percebe ao abrir o mapa ou a lista de alertas é a soma de
três parcelas:

```
tempo percebido = rede móvel (ida e volta) + processamento da API (inclui o banco) + desenho da tela
```

Numa rede móvel 4G, a ida e volta típica fica entre 50 e 150 ms, e o desenho da lista ou
dos marcadores leva algumas dezenas de milissegundos. Para a resposta total ficar abaixo
de 1 s (limite do fluxo de pensamento), **o servidor pode gastar no máximo ~200 ms**,
sobrando margem para redes piores. Esse é o critério das leituras (RNF-01).

## 4. Requisitos não funcionais de desempenho

| ID | Operação | Critério | Justificativa |
|---|---|---|---|
| **RNF-01** | Leitura de ocorrências: `GET /ocorrencias` (com ou sem filtro de região/período) e `GET /ocorrencias/{id}` | p95 ≤ **200 ms** no servidor | Orçamento da seção 3: resposta total < 1 s no app |
| **RNF-02** | Cadastro de ocorrência com nível informado pelo usuário (`POST` com `nivel_risco`) | p95 ≤ **500 ms** no servidor | Ação explícita do usuário com indicador "Enviando…"; continua bem abaixo de 1 s |
| **RNF-03** | Cadastro com risco calculado automaticamente (`POST` sem `nivel_risco`, consulta as fontes climáticas + AHP) | p95 ≤ **10 s**, com indicador de progresso; ≤ **1 s** quando os dados climáticos já estão em cache | Limite de atenção de 10 s. Depende de serviços externos, por isso exige feedback visual (o app mostra "Enviando…" e espera até 30 s antes de desistir) |
| **RNF-04** | Consulta espacial no banco (filtro por região) | ≤ **10 ms** com 100 mil ocorrências, e crescimento **sublinear** com o volume | Garante que o banco não consome o orçamento do RNF-01 mesmo com a base crescendo. Hipótese O(log n) de T17 |
| **RNF-05** | Falha de fonte externa | Timeout de **10 s** por fonte, chamadas em paralelo; falha da fonte principal vira erro claro (HTTP 503), nunca erro genérico | Uma fonte lenta não pode somar seu atraso às outras nem travar o cadastro sem explicação |

## 5. Verificação (medições de 03/10/2026)

**Ambiente:** notebook AMD Ryzen 5 5600G, 16 GB de RAM, Windows 11. PostgreSQL 16 +
PostGIS 3.4 em Docker Desktop. API FastAPI em contêiner (mesma imagem do `Dockerfile`) e,
para comparação, direto no Windows. Cliente HTTP na mesma máquina. Script
`backend/benchmark/medir_latencia_api.py`: 5 requisições de aquecimento descartadas e 50
medidas por cenário. Os CSVs estão em `backend/benchmark/resultados/`.

### 5.1 RNF-01 e RNF-02 — API

Banco com os 30 registros de demonstração de São Caetano do Sul (`backend/dados_demo.py`):

| Cenário | p50 (ms) | p95 (ms) | Critério | Atende? |
|---|---|---|---|---|
| Listar (sem filtro) | 4,3 | 4,8 | ≤ 200 | Sim |
| Listar por região (bbox de São Caetano do Sul) | 4,2 | 5,2 | ≤ 200 | Sim |
| Listar por região + últimas 24 h | 4,6 | 5,6 | ≤ 200 | Sim |
| Obter por id | 3,2 | 3,8 | ≤ 200 | Sim |
| Cadastrar com nível informado | 67,3 | 259,1 | ≤ 500 | Sim (ver nota) |

Mesma API apontada para o banco de benchmark com **1 milhão** de ocorrências:

| Cenário | p50 (ms) | p95 (ms) | Critério | Atende? |
|---|---|---|---|---|
| Listar (sem filtro) | 5,2 | 7,1 | ≤ 200 | Sim |
| Listar por região | 15,4 | 16,5 | ≤ 200 | Sim |
| Listar por região + últimas 24 h | 4,7 | 5,2 | ≤ 200 | Sim |
| Obter por id | 3,7 | 4,4 | ≤ 200 | Sim |
| Cadastrar com nível informado | 7,3 | 9,1 | ≤ 500 | Sim |

**Nota sobre o cadastro na API em contêiner.** Pela porta publicada do Docker Desktop, o
`POST` leva ~60 ms no p50 contra ~7 ms com a API rodando direto no Windows. Medido de
dentro do próprio contêiner, o mesmo `POST` leva 4,6 ms (p50) e 5,5 ms (p95). O atraso
vem, portanto, do encaminhamento de porta do Docker Desktop no Windows, e não da aplicação
nem do banco. Em hospedagem Linux, sem essa camada, não se aplica. Mesmo com o atraso, o
RNF-02 é atendido.

**Pelo IP Tailscale** (mesma máquina, simulando o acesso do time): valores equivalentes
(p95 das leituras entre 4,8 e 5,9 ms). Não mede rede real, já que cliente e servidor estão
na mesma máquina. A medição com celular em rede móvel fica como trabalho futuro (seção 6).

### 5.2 RNF-03 — cadastro com risco automático

Medido em 03/10/2026, depois de configurar a chave do OpenWeather, com a API recém-reiniciada
(cache vazio) e consultas reais às fontes externas (`--incluir-auto`; CSV
`latencia_api_demo_com_clima.csv`):

| Cenário | n | p50 (ms) | p95 (ms) | Critério | Atende? |
|---|---|---|---|---|---|
| Cadastro automático, **sem cache** (10 pontos em células diferentes, fontes externas consultadas de verdade) | 10 | 505,5 | 560,1 | ≤ 10 s | Sim |
| Cadastro automático, **com cache** (mesmo ponto) | 50 | 50,3 | 56,5 | ≤ 1 s | Sim |
| `GET /risco` com cache (aba Previsão) | 50 | 3,7 | 4,5 | ≤ 200 ms (RNF-01) | Sim |

O tempo sem cache (~0,5 s) é dominado pelas chamadas ao OpenWeather; no dia da medição a
ANA não estava configurada e o CPTEC respondia 403 rapidamente, então nenhuma das duas
segurou o tempo. O pior caso teórico continua sendo o timeout de 10 s de uma fonte lenta.
O cache reduz o tempo do cadastro em ~10× (os ~50 ms restantes são, em boa parte, o
encaminhamento de porta do Docker Desktop, ver nota em 5.1).

### 5.3 RNF-04 — consulta espacial no banco

Ver `T16_secao_benchmark.md` e `backend/benchmark/resultados/resumo.md`. Com 100 mil
ocorrências, a consulta espacial com índice GiST leva **0,18 ms** (mediana), contra
14,65 ms sem o índice. O critério de ≤ 10 ms é atendido com folga. De 1 mil para 100 mil
registros (100× mais dados), o tempo com índice cresce ~6×, enquanto o scan sequencial
cresce ~84×, ou seja, crescimento sublinear. Com 1 milhão, o custo com índice passa a ser
dominado pelo número de linhas devolvidas (5.194 no bbox), conforme discutido na seção do
benchmark.

### 5.4 RNF-05 — falha de fonte externa

Verificado por teste automatizado:
- Paralelismo e timeout: `backend/tests/test_fusao_climatica_latencia.py`.
- Erro de rede, falta de chave e resposta 503: `backend/tests/test_fusao_climatica_cache.py`.

## 6. Limitações e trabalho futuro

- O cache climático usa células de 0,01° (~1 km): dois pontos a poucos metros de
  distância, mas em lados opostos da borda de uma célula, não compartilham o cache.
  É um efeito esperado de qualquer grade fixa e só custa uma consulta extra.
- As medições usam cliente e servidor na mesma máquina. A latência de rede móvel real
  (celular → internet → servidor) não foi medida e depende de onde a API for hospedada.
- O RNF-03 depende de serviços externos fora do controle do projeto (OpenWeather, ANA,
  CPTEC). Os critérios valem para o processamento do sistema, não para a disponibilidade
  dessas fontes.
- A carga foi de um cliente por vez. Testes de concorrência (vários usuários
  simultâneos) não fizeram parte do escopo.

## 7. Referências

- CARD, S. K.; ROBERTSON, G. G.; MACKINLAY, J. D. The information visualizer, an
  information workspace. *Proceedings of the ACM CHI'91*, p. 181–188, 1991.
- DEAN, J.; BARROSO, L. A. The tail at scale. *Communications of the ACM*, v. 56, n. 2,
  p. 74–80, 2013.
- GOOGLE. *Measure performance with the RAIL model*. web.dev. Disponível em:
  https://web.dev/articles/rail.
- INTERNATIONAL ORGANIZATION FOR STANDARDIZATION. *ISO/IEC 25010:2011 — Systems and
  software engineering — Systems and software Quality Requirements and Evaluation
  (SQuaRE) — System and software quality models*. Genebra: ISO, 2011.
- MILLER, R. B. Response time in man-computer conversational transactions.
  *Proceedings of the AFIPS Fall Joint Computer Conference*, v. 33, p. 267–277, 1968.
- NIELSEN, J. *Usability Engineering*. San Francisco: Morgan Kaufmann, 1993. Cap. 5.
