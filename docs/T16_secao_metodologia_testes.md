# Seção: Metodologia de Testes e Avaliação

*Rascunho de seção do relatório final — Semana 13 do cronograma (João). Redigido em
03/10/2026. A numeração "4.X" é provisória. A subseção 4.X.6 (resultados de usabilidade)
depende das sessões com participantes, ainda não realizadas.*

---

## 4.X Metodologia de Testes e Avaliação

A avaliação do sistema combinou cinco frentes, cada uma respondendo a uma pergunta
diferente:

| Frente | Pergunta | Instrumento |
|---|---|---|
| Testes automatizados do backend | As regras e a API fazem o que foi especificado? | Suíte pytest (contrato e integração) |
| Testes funcionais do aplicativo | O app integrado à API real funciona de ponta a ponta? | Plano PT-001, execução em emulador |
| Benchmark de indexação espacial | Quanto o índice GiST reduz o custo das consultas por região? | Scripts de benchmark + `EXPLAIN ANALYZE` |
| Latência da API | O tempo de resposta atende aos requisitos não funcionais? | Script de medição HTTP + critérios de T19 |
| Usabilidade | O público-alvo consegue usar o app com facilidade? | Roteiro de tarefas + questionário + TCLE |

### 4.X.1 Plano de testes

Os testes seguem o plano **PT-001** (`docs/plano_e_fluxo_de_testes_TCC.xlsx`), elaborado com
base em boas práticas de documentação de testes (identificação, escopo, estratégia,
critérios de entrada e saída, e um registro por caso de teste com pré-condições, passos,
resultado esperado, resultado obtido, status e evidência). A técnica predominante é a de
**caixa-preta**, com cenários positivos, negativos e de limite (por exemplo, coordenada
fora do intervalo, filtro de região incompleto, valor fora do vocabulário, envio sem local
marcado, fonte externa indisponível). Cada caso tem prioridade (P1 a P3) e é rastreado até
o requisito funcional ou não funcional correspondente.

### 4.X.2 Testes automatizados do backend

A suíte pytest (`backend/tests/`) tem **98 testes** em 07/10/2026, em dois níveis:

- **Testes de contrato (90).** Substituem o banco e as fontes climáticas por implementações
  em memória, injetadas pelo mecanismo de dependências do FastAPI. Verificam rotas,
  validação, códigos de status, regras do algoritmo AHP, agregação colaborativa, cache,
  paralelismo das chamadas externas e a lógica pura dos scripts de benchmark. Rodam em
  qualquer máquina, sem banco.
- **Testes de integração (8).** Rodam contra um PostgreSQL/PostGIS real e exercitam o
  caminho completo de persistência: filtro geoespacial, busca por raio dos reportes
  colaborativos, registro do score agregado e o cálculo de risco com reportes vizinhos.
  Cada teste roda dentro de uma transação desfeita ao final (padrão recomendado pela
  documentação do SQLAlchemy), então nenhum dado de teste permanece no banco e o resultado
  não depende do que já está lá.

### 4.X.3 Testes funcionais do aplicativo integrado

O aplicativo foi instalado num emulador Android (Android 15) e apontado para a API e o
banco reais, carregados com 30 ocorrências de demonstração em São Caetano do Sul
(`backend/dados_demo.py`). Os casos do PT-001 foram executados com o auxílio de um script de
automação por `adb` (`android/scripts/adb_app.py`), que toca nos elementos da tela pelo
identificador, digita, lê os textos exibidos e captura a tela como evidência. Sempre que
possível, o resultado mostrado pelo app foi **comparado com a resposta direta da API**
para os mesmos parâmetros — por exemplo, a quantidade de ocorrências exibida para cada
combinação de filtros.

### 4.X.4 Desempenho

O desempenho foi avaliado em dois níveis, com critérios definidos antes das medições (T19):

- **Banco de dados:** benchmark com e sem índice GiST em 1 mil, 10 mil, 100 mil e 1 milhão
  de registros sintéticos, medindo o tempo de execução no PostgreSQL via `EXPLAIN ANALYZE`
  (3 execuções de aquecimento e 20 medidas por condição) e registrando o plano escolhido
  (detalhes na seção do benchmark).
- **API de ponta a ponta:** 50 requisições HTTP por cenário, após 5 de aquecimento,
  reportando a mediana (p50) e o percentil 95 (p95), no banco de demonstração e no banco de
  1 milhão de registros.

### 4.X.5 Avaliação de usabilidade

A usabilidade será avaliada com participantes do público-alvo (moradores ou frequentadores
de São Caetano do Sul), segundo o protocolo:

1. Leitura e assinatura do **Termo de Consentimento Livre e Esclarecido**
   (`docs/tcle_teste_usabilidade.md`), que informa que as ocorrências exibidas são de
   demonstração e que a participação é voluntária e anônima.
2. Execução de **cinco tarefas guiadas** no app, observadas por um integrante da equipe que
   não indica como resolvê-las: entrar no app, registrar uma ocorrência, filtrar a lista,
   localizar uma ocorrência no mapa e abrir seus detalhes.
3. **Questionário pós-teste** (`docs/questionario_teste_usabilidade.md`, aplicado pelo
   Google Forms) com perfil do participante, três afirmações em escala Likert de 1 a 5 por
   tarefa (conclusão sem ajuda, facilidade, clareza), avaliação geral e perguntas abertas.

**Critério de aprovação:** média ≥ 4 nas perguntas em escala Likert. Problemas relatados ou
observados são registrados como defeitos no PT-001 e triados pelo responsável de cada
módulo.

### 4.X.6 Resultados

**Testes automatizados:** 98 de 98 aprovados com o banco disponível; sem banco, 90
aprovados e 8 pulados por desenho (07/10/2026, incluindo a integração com o INMET e a
regra de piso dos avisos).

**Casos do PT-001 (21 casos, em 03/10/2026):**

| Status | Casos |
|---|---|
| Aprovado | 14 — CT-API-001 a 005, CT-AHP-001 a 003, CT-CAD-002 a 004, CT-LST-002, CT-NOT-001, CT-PRV-001 |
| Em execução (parte funcional aprovada; falta a avaliação com participantes) | 5 — CT-CAD-001, CT-LST-001, CT-DET-001, CT-CFG-001, CT-LOG-001 |
| Bloqueado | 2 — CT-MAP-001 e CT-MAP-002 (a chave do Google Maps só aceita os certificados Android cadastrados no Google Cloud, e o APK de teste é assinado com outro) |

Os casos de cadastro automático (CT-CAD-004) e da aba de risco (CT-PRV-001) foram
executados com dados climáticos reais do OpenWeather, e os resultados exibidos pelo app
foram conferidos com a resposta direta da API para o mesmo ponto. Os testes do app foram
repetidos com o emulador configurado em português do Brasil e no fuso de São Paulo, como
estarão os aparelhos dos participantes.

**Defeitos encontrados durante os testes de 03/10/2026, todos corrigidos no mesmo dia:**

| Defeito | Onde | Como foi encontrado |
|---|---|---|
| Chave do OpenWeather fixa como texto de exemplo; o cálculo automático de risco falharia contra a API real com erro 500 | Backend (`fusao_climatica.py`) | Revisão de código antes do teste integrado |
| Script de benchmark mascarava a senha do banco ao montar a URL de conexão e nunca conseguia conectar | Benchmark (`popular_banco.py`) | Primeira execução real do benchmark |
| Aplicação do schema pelo script de benchmark falhava por causa de um "%" num comentário do SQL | Benchmark (`popular_banco.py`) | Primeira execução real do benchmark |
| Testes de integração dependiam de o banco estar vazio | Testes (`test_ocorrencias_integracao.py`) | Rodar a suíte com os dados de demonstração carregados |
| **BUG-001:** contador da lista de alertas ignorava o filtro de nível de risco | App (`AlertasFragment.kt`) | Comparação app × API no CT-LST-002 |
| Mensagem de erro do cadastro cortada pelo limite de duas linhas do Android | App (`strings.xml`) | Captura de tela no CT-CAD-003 |
| **BUG-002:** com o aparelho em português, coordenadas exibidas como "-23,6148, -46,5435" (vírgula decimal confundida com a separadora) | App (`OcorrenciaVisual.kt`, `CadastroFragment.kt`) | Repetir os testes com o emulador em pt-BR |

O fato de quatro desses defeitos só aparecerem na primeira execução contra o banco e a API
reais — e de um quinto só aparecer com o aparelho no idioma do público-alvo — reforça a
importância de testar no ambiente mais próximo possível do real: os testes com
implementações em memória, sozinhos, não os revelariam.

**Usabilidade:** *pendente — preencher após as sessões (número de participantes, perfil,
média por pergunta Likert, taxa de conclusão por tarefa, problemas relatados e defeitos
registrados).*

---

*Seção redigida com base em `docs/plano_e_fluxo_de_testes_TCC.xlsx` (versão 1.1, 03/10/2026, 21 casos),
`backend/tests/`, `docs/T19_criterios_desempenho.md` e `docs/evidencias_testes/2026-10-03/`.*
