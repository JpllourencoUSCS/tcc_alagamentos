# Seção: Benchmark de Indexação Espacial (Resultados e Discussão)

*Rascunho de seção do relatório final — Semana 15 do cronograma (Henrique). Redigido em
03/10/2026 a partir da primeira execução real do benchmark (Semanas 7–9). A numeração
"4.Y" é provisória e deve ser ajustada na montagem do relatório.*

---

## 4.Y Avaliação Experimental da Indexação Espacial

Esta seção responde ao ponto levantado pelo orientador sobre a **complexidade
computacional do banco de dados georreferenciado**. A fundamentação teórica (R-tree,
GiST e a hipótese de crescimento O(n) sem índice e O(log n) com índice) está na seção de
indexação espacial (T17). Aqui ela é confrontada com medições.

### 4.Y.1 Metodologia

**Massa de dados.** Foram gerados quatro bancos independentes, com 1 mil, 10 mil, 100 mil
e 1 milhão de ocorrências sintéticas. O cronograma previa três escalas; a de 1 milhão foi
acrescentada para observar o comportamento numa ordem de grandeza acima. Os pontos foram
distribuídos uniformemente na região metropolitana de São Paulo e no ABC Paulista
(latitudes −24,00 a −23,30; longitudes −47,00 a −46,00), com datas nos últimos 180 dias.
O gerador é determinístico (semente 42, instante de referência fixo), então o mesmo
dataset pode ser reproduzido (`backend/benchmark/gerar_dados.py`). Cada banco usa o
`schema.sql` de produção, e as estatísticas do otimizador são atualizadas (`ANALYZE`) após
a carga.

**Consultas medidas.** Ambas usam o bbox de uma janela de mapa de ~6,6 km × 6,6 km
centrada em São Caetano do Sul, que contém cerca de 0,5% dos registros:

1. **Consulta espacial**: `SELECT count(*) … WHERE geom && ST_MakeEnvelope(…)`. Só o
   filtro espacial, sem ordenação. Isola o efeito do índice GiST.
2. **Consulta do endpoint**: a mesma que a API executa para `GET /ocorrencias` com filtro
   de região (`ORDER BY data_hora DESC LIMIT 100`). Representa o uso real do aplicativo.

**Condições.** Cada consulta foi medida sem o índice `idx_ocorrencias_geom` (Semana 8) e
com ele (Semana 9). O índice B-tree de `data_hora`, parte do schema de produção, foi mantido
nas duas condições.

**Métrica.** Tempo de execução reportado pelo `EXPLAIN (ANALYZE, FORMAT JSON)` do
PostgreSQL. Ele mede só a execução do plano, sem rede nem driver. Por condição: 3
execuções de aquecimento descartadas e 20 medidas. Reporta-se a mediana, por ser robusta a
valores extremos, junto com média e desvio padrão. O plano escolhido pelo otimizador foi
registrado em cada execução, como evidência de que o índice foi de fato usado.

**Ambiente.** PostgreSQL 16 com PostGIS 3.4 (imagem `postgis/postgis:16-3.4`) em Docker
Desktop, num notebook com AMD Ryzen 5 5600G e 16 GB de RAM, configuração padrão do
PostgreSQL.

### 4.Y.2 Resultados

**Consulta espacial** (tempos em ms; Figura 4.Y.1: `backend/benchmark/resultados/grafico_consulta_espacial.png`):

| Registros | Linhas no bbox | Sem índice (mediana) | Com GiST (mediana) | Ganho |
|---|---|---|---|---|
| 1.000 | 7 | 0,175 | 0,031 | 5,6× |
| 10.000 | 48 | 1,84 | 0,048 | 38,8× |
| 100.000 | 496 | 14,65 | 0,179 | 81,6× |
| 1.000.000 | 5.194 | 71,73 | 4,83 | 14,8× |

Plano sem índice: varredura sequencial (`Seq Scan`); com 1 milhão, varredura sequencial
paralela (`Gather`). Plano com índice: `Bitmap Index Scan` em `idx_ocorrencias_geom`
seguido de `Bitmap Heap Scan`, em todas as escalas.

**Consulta do endpoint** (Figura 4.Y.2: `backend/benchmark/resultados/grafico_consulta_endpoint.png`):

| Registros | Sem índice (mediana) | Com GiST (mediana) | Ganho | Plano com GiST disponível |
|---|---|---|---|---|
| 1.000 | 0,159 | 0,032 | 5,0× | GiST + ordenação |
| 10.000 | 1,49 | 0,067 | 22,3× | GiST + ordenação |
| 100.000 | 8,06 | 0,328 | 24,6× | GiST + ordenação |
| 1.000.000 | 10,71 | 11,04 | 1,0× | índice de `data_hora` (GiST não usado) |

A tabela completa (média, desvio padrão e planos) está em
`backend/benchmark/resultados/resumo.md`, e os dados brutos nos CSVs da mesma pasta.

### 4.Y.3 Discussão

**A hipótese de T17 se confirma até 100 mil registros.** Sem índice, o tempo da consulta
espacial cresce praticamente na proporção dos dados: de 1 mil para 100 mil registros
(100× mais), o tempo aumenta 84×, o comportamento O(n) da varredura sequencial. Com o
índice GiST, o mesmo aumento de volume eleva o tempo só 5,8×. Com 100 mil registros, o
índice torna a consulta **81,6 vezes mais rápida**.

**Em 1 milhão, o custo passa a ser dominado pelo resultado, não pela busca.** A
complexidade de uma busca em R-tree é O(log n + k), onde k é o número de elementos
devolvidos. Como o bbox sempre cobre ~0,5% dos dados, k cresce junto com n (7, 48, 496,
5.194 linhas), e com 1 milhão de registros o termo k domina: o índice localiza os pontos
rapidamente, mas o banco ainda precisa ler do disco as páginas onde estão as 5.194
linhas. Como os dados sintéticos foram inseridos em ordem aleatória no espaço, essas linhas
estão espalhadas por boa parte da tabela. O ganho cai para 14,8×, também porque nessa
escala o PostgreSQL passa a paralelizar a varredura sequencial. Num cenário real, em que a
janela do mapa tem tamanho fixo e a base cresce por acúmulo histórico, o efeito é o mesmo:
o que pesa é quantos pontos caem na janela.

**O otimizador do PostgreSQL nem sempre escolhe o índice espacial.** Na consulta do
endpoint, a partir de 100 mil registros sem GiST, e em 1 milhão mesmo com GiST, o
otimizador prefere percorrer o índice de `data_hora` do mais recente para o mais antigo e
parar ao achar as 100 primeiras ocorrências dentro do bbox. Com 1 milhão de registros essa
estratégia leva ~11 ms. Em teste separado, forçar o uso do GiST
(`SET enable_indexscan = off`) reduziu a mesma consulta para ~5 ms. O otimizador
subestima o custo da estratégia por data, e ajustar o custo de leitura aleatória para SSD
(`random_page_cost = 1.1`) não mudou a escolha. Como os dois tempos ficam muito abaixo do
limite de 200 ms do RNF-01 (T19), o comportamento foi documentado e mantido, sem forçar
planos na aplicação.

### 4.Y.4 Otimizações avaliadas (Semana 10)

A partir dos resultados, duas otimizações foram avaliadas no banco de 1 milhão de
registros:

| Otimização | Consulta espacial | Endpoint (forçando GiST) |
|---|---|---|
| Antes (dados em ordem de inserção) | 2,04 ms | 5,00 ms |
| Após `CLUSTER ocorrencias USING idx_ocorrencias_geom` | 0,89 ms | 1,04 ms |

O `CLUSTER` reordena fisicamente a tabela segundo o índice espacial, de modo que pontos
próximos no mapa passam a ficar nas mesmas páginas do disco. Isso reduz as leituras do
`Bitmap Heap Scan` e corta o tempo pela metade (consulta espacial) ou em até 5× (endpoint
com GiST). A limitação é que o `CLUSTER` não é mantido automaticamente: novas inserções
entram fora de ordem, e o comando bloqueia a tabela enquanto roda. Por isso, ele é indicado
como manutenção periódica (por exemplo, semanal) quando a base passar de centenas de
milhares de registros, e não foi aplicado ao fluxo da aplicação.

Os valores "antes" desta tabela (2,04 ms) diferem da execução principal (4,83 ms) para a
mesma consulta e escala. A diferença vem do estado do cache do sistema operacional entre
as duas sessões: a execução principal ocorreu logo após a criação do índice. Isso reforça a
importância de comparar condições medidas na mesma sessão, como foi feito na tabela da
seção 4.Y.2.

Também no escopo da Semana 10, foi implementado um **cache de dados climáticos** de 10
minutos por célula de ~1 km no backend. Ele evita repetir as quatro chamadas às APIs
externas quando vários usuários reportam ocorrências na mesma região em sequência, o que
afeta diretamente a latência do cadastro com risco automático (RNF-03 em T19). A
paginação dos resultados já existia (`skip`/`limit` no endpoint, limitado a 500).

### 4.Y.5 Ameaças à validade

- **Dados sintéticos uniformes.** Ocorrências reais se concentram em pontos de
  alagamento recorrentes. Distribuições concentradas tendem a beneficiar ainda mais o
  índice, por ter mais pontos em poucas páginas.
- **Uma única máquina e configuração padrão.** Os valores absolutos dependem do hardware
  e de parâmetros como `shared_buffers`. As conclusões se apoiam nas **tendências** entre
  escalas, não nos valores absolutos.
- **Cache.** As execuções de aquecimento eliminam o efeito de cache frio dentro de uma
  sessão, mas não entre sessões (seção 4.Y.4).
- **Tempo de banco, não de usuário.** O `EXPLAIN ANALYZE` exclui rede e aplicação. A
  latência de ponta a ponta da API está em T19, seção 5.

### 4.Y.6 Reprodutibilidade

Com o banco do `docker-compose.yml` no ar, a partir de `backend/`:

```
python -m benchmark.popular_banco --escalas 1000 10000 100000 1000000 --recriar --referencia-iso 2026-10-03T12:00:00+00:00
python -m benchmark.medir_consultas --escalas 1000 10000 100000 1000000 --indice ausente --saida benchmark/resultados/resultados_sem_indice.csv
python -m benchmark.medir_consultas --escalas 1000 10000 100000 1000000 --indice presente --saida benchmark/resultados/resultados_com_indice.csv
python -m benchmark.gerar_graficos
```

(`ADMIN_DATABASE_URL` deve apontar para o banco `postgres` do servidor.) A carga de 1 milhão
de registros levou ~7 minutos nesta máquina.

---

*Seção redigida com base nos resultados de `backend/benchmark/resultados/` (execução de
03/10/2026) e em `docs/T17_indexacao_espacial_fundamentacao.md`.*
