# Cronograma de Implementação — TCC II

**Sistema de Monitoramento Colaborativo de Áreas com Risco de Alagamento**
Período: 01/07/2026 a 30/10/2026 (17 semanas)
*Última atualização de status: 03/09/2026*

## Legenda de responsáveis
- **Henrique** — backend / tech lead
- **João** — integração / full stack
- **Marlon** — Android / documentação
- **Guilherme** — Android / tarefas bem delimitadas

## Legenda de status
- ✅ Concluída
- 🟡 Em andamento / parcialmente bloqueada
- 🔴 Atrasada ou não iniciada

Aplicada a João e Henrique desde o início; passou a valer também para as atividades do
Marlon a partir do resumo que ele enviou em 20/08/2026 (Semanas 1–7). Guilherme segue sem
status própria reportada.

## FASE 1 — Replanejamento Técnico (01/07 a 14/07)

### Semana 1 (01/07 – 05/07)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Levantamento técnico de indexação espacial (GiST/R-tree) em PostGIS — base teórica para o benchmark futuro | ✅ Concluída — `docs/T17_indexacao_espacial_fundamentacao.md` (R-tree, GiST, comparação com Quadtree/SP-GiST/BRIN, hipótese O(log n) a validar no benchmark) |
| João | Pesquisa e definição do modelo de classificação de risco por pesos (AHP ou método similar) — base teórica | ✅ Concluída |
| Marlon | Estudo de migração de Jetpack Compose para Android Views (XML) — telas já planejadas | ✅ Concluída |
| Guilherme | Estudo de Android Views (XML) em conjunto com Marlon — foco em componentes simples (formulários, listas) | |

**Entregável da semana:** documento de decisão técnica registrando a saída do Compose e a adoção de XML Views, e o desenho inicial do algoritmo de classificação de risco.

### Semana 2 (06/07 – 12/07)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Modelagem do banco PostgreSQL/PostGIS revisada, incluindo estrutura para suportar múltiplas fontes de dados | ✅ Concluída — `docs/T18_modelagem_postgis.md` + `backend/db/schema.sql` + `backend/db/models.py` (fonte ana/cptec, coluna `geom` com trigger de sync, índice GiST, tabela nova `reportes_colaborativos_agregado`); DDL validado por compilação contra o dialeto PostgreSQL |
| João | Cadastro e testes iniciais nas APIs do CEMADEN e INMET (autenticação, formato de resposta, limitações) | ✅ Concluída — escopo redesenhado: CEMADEN e INMET testados e descartados (documentado), ANA e CPTEC assumiram os papéis |
| Marlon | Conversão dos wireframes/telas do app para layout XML (tela de mapa e tela de listagem) | ✅ Implementada — reportada por Marlon em 20/08; em manutenção ativa, sujeita a ajustes conforme novas atualizações e testes ao longo do projeto |
| Guilherme | Conversão de telas XML (formulário de cadastro de ocorrência e tela de login) com apoio do Marlon | |

**Entregável da semana:** banco atualizado com suporte a múltiplas fontes; primeiras chamadas reais documentadas.

---

## FASE 2 — Desenvolvimento Paralelo (13/07 a 09/08)

### Semana 3 (13/07 – 19/07)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Implementação dos endpoints REST principais no FastAPI (ocorrências: criar, listar, filtrar) | ✅ Concluída — `backend/main.py` + `backend/api/ocorrencias.py` (POST/GET/GET-por-id, filtros de fonte/nível/período/região); `backend/db/repository.py` isola o SQLAlchemy via `OcorrenciaRepositoryProtocol`, o que permitiu testar os 3 endpoints (8 casos, `backend/tests/test_ocorrencias_api.py`) sem Postgres/PostGIS vivo neste ambiente — integração contra o banco real fica para a Semana 5 |
| João | Implementação do módulo de integração climática consolidada (OpenWeather + ANA + CPTEC) no backend | 🟡 Código pronto e testado (`fusao_climatica.py`); falta só a ANA responder o cadastro pra validar as 3 fontes juntas em produção |
| Marlon | Implementação da tela de mapa em XML com Google Maps SDK (sem Compose) | ✅ Implementada — reportada por Marlon em 20/08; em manutenção ativa, sujeita a ajustes conforme novas atualizações e testes ao longo do projeto |
| Guilherme | Implementação da tela de cadastro de ocorrência em XML, com validação de campos | |

### Semana 4 (20/07 – 26/07)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | ~~Implementação da primeira versão do algoritmo de classificação de risco~~ | ✅ Absorvida pelo João — implementada em `algoritmo_risco.py` (Semana 4) e formalizada em `T15_algoritmo_risco_fundamentacao.md` (Semana 6) |
| João | Apoio à implementação do algoritmo de risco — testes com dados reais das APIs já integradas | ✅ Concluída — `algoritmo_risco.py` testado com dado real de Santo André (score 4.2, Baixo risco) |
| Marlon | Implementação da tela de listagem/histórico de ocorrências em XML | ✅ Implementada — reportada por Marlon em 20/08; em manutenção ativa, sujeita a ajustes conforme novas atualizações e testes ao longo do projeto |
| Guilherme | Implementação de componentes de filtro (região e período) na interface XML | |

**Entregável da semana:** primeira versão funcional do algoritmo de risco testável via backend.

### Semana 5 (27/07 – 02/08)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Integração do banco de dados com os endpoints (persistência real das ocorrências e classificações) | 🟡 `POST /ocorrencias` calcula `nivel_risco`/`chuva_mm` automaticamente via `fusao_climatica` quando o cliente não informa (`backend/servicos/classificacao.py`, T14 "Notas de projeto"); o `OcorrenciaRepository` já grava via SQLAlchemy desde a Semana 3. **Validado em 03/09/2026 na máquina do João** contra um Postgres/PostGIS real (Docker + `docker-compose.yml`, ver nota abaixo) — `schema.sql` aplica sem erro, PostGIS 3.4 ativo, 23/23 testes passam com `DATABASE_URL` apontando pro container. Segue 🟡 e não ✅ porque isso ainda não foi confirmado no ambiente do Henrique nem em CI — falta padronizar isso pro time todo |
| João | Testes de consistência dos dados climáticos consolidados (comparação entre fontes para a mesma região/horário) | 🔴 Bloqueada — depende da ANA responder o cadastro (único item fora do controle do time) |
| Marlon | Integração da tela de mapa com dados reais do backend (consumo da API) | 🔴 Não iniciada — tela de mapa ainda não vinculada à API real, dados mockados/estáticos |
| Guilherme | Integração da tela de cadastro com o backend (envio de ocorrências reais) | |

### Semana 6 (03/08 – 09/08)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Revisão de código backend e ajustes de performance inicial nas consultas | ✅ Concluída — 3 achados corrigidos: (1) filtro de região usava `BETWEEN` em lat/lon sem índice (full scan) → trocado para `&&`/`ST_MakeEnvelope` contra `geom`, usando o índice GiST já criado (liga direto com `T17`); (2) filtros `fonte`/`nivel_risco` da listagem aceitavam qualquer string e devolviam lista vazia em silêncio para valor inválido → tipados com os enums compartilhados, agora 422; (3) `sessionmaker(..., autocommit=False)` em `db/session.py` era parâmetro morto do SQLAlchemy 1.x (removido nas versões novas) → limpo. 11 testes passando (`backend/tests/`) |
| João | Documentação técnica do algoritmo de classificação de risco (fundamentação e funcionamento) — insumo para o relatório | ✅ Concluída em 17/08 — `docs/T15_algoritmo_risco_fundamentacao.md` (matriz AHP formalizada, CR=0.0038) + rascunho de seção `docs/T16_secao_algoritmo_risco.md` |
| Marlon | Ajustes visuais e de usabilidade nas telas Android já integradas | ✅ Implementada — reportada por Marlon em 20/08; em manutenção ativa, sujeita a ajustes conforme novas atualizações e testes ao longo do projeto |
| Guilherme | Testes manuais do fluxo cadastro → listagem → mapa, registrando bugs encontrados | |

**Entregável da fase:** protótipo com fluxo principal funcional (cadastro, listagem, mapa, classificação de risco básica).

---

## FASE 3 — Integração Avançada e Benchmark (10/08 a 13/09)

### Semana 7 (10/08 – 16/08)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Criação do ambiente de benchmark — geração de massa de dados simulada (1k, 10k, 100k registros geoespaciais) | 🟡 Geração testada (11 testes), inserção não testada (sem Postgres) — `backend/benchmark/gerar_dados.py` (função pura, sementes reprodutíveis) + `backend/benchmark/popular_banco.py` (1 banco Postgres por escala: `alagamentos_bench_1000/10000/100000`, aplica `schema.sql`, insere em lotes de 5000 via SQLAlchemy Core). Achado do próprio teste: `data_hora` usava `datetime.now()` como referência recalculada a cada chamada, quebrando a promessa de "mesma semente = mesmo dataset" — corrigido com parâmetro `referencia` explícito. Pronto para rodar assim que houver `ADMIN_DATABASE_URL` |
| João | Refinamento do algoritmo de risco com dados de múltiplas fontes ponderadas | ✅ Concluída em 17/08 — `fusao_climatica.py` e `algoritmo_risco.py` agora conectados (`classificar_risco()`/`obter_classificacao_risco()`); testado com ANA disponível e indisponível |
| Marlon | Implementação de tela de detalhes da ocorrência (visualização individual) | ✅ Implementada — reportada por Marlon em 20/08; em manutenção ativa, sujeita a ajustes conforme novas atualizações e testes ao longo do projeto |
| Guilherme | Implementação de notificações locais simples (alerta visual de risco alto no app) | |

### Semana 8 (17/08 – 23/08)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Execução do benchmark sem índice espacial — medição de tempo de resposta nas consultas | 🟡 Lógica testada (4 testes), execução real pendente — `backend/benchmark/medir_consultas.py`: mede a mesma consulta que `db/repository.py` gera para o filtro de região (bbox → `geom && ST_MakeEnvelope`, ORDER BY + LIMIT), via `EXPLAIN (ANALYZE, FORMAT JSON)` para isolar o tempo de execução no Postgres (sem ruído de rede/driver). Reutilizável para a Semana 9 (`--indice presente`/`ausente`, mesmo script). O bloqueio de "sem Postgres" foi removido em 03/09 (banco real disponível via Docker + Tailscale, ver notas), mas a execução em si ainda não foi confirmada — segue 🟡, não ✅ |
| João | Apoio à análise dos resultados do benchmark — interpretação dos dados coletados | 🔴 Bloqueada — depende da execução do benchmark pelo Henrique (item acima); nada a analisar enquanto não houver números |
| Marlon | Testes de usabilidade interna das telas (com os próprios colegas) | ⬜ Sem status reportado — o resumo do Marlon em 20/08 cobriu só as Semanas 1–7 |
| Guilherme | Correção de bugs identificados nos testes de usabilidade | ⬜ Sem status reportado |

### Semana 9 (24/08 – 30/08)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Implementação de índice GiST no PostGIS e execução do benchmark comparativo | 🔴 Não iniciada — depende da Semana 8 (benchmark sem índice) estar concluída primeiro |
| João | Documentação científica do benchmark (fundamentação teórica de R-tree/GiST, conforme literatura) | 🔴 Não iniciada — sem resultados de benchmark ainda para documentar (depende do Henrique); a base teórica de `T17_indexacao_espacial_fundamentacao.md` (Semana 1) já existe e pode ser reaproveitada |
| Marlon | Revisão e padronização visual de todas as telas (consistência de cores, fontes, espaçamento) | ⬜ Sem status reportado |
| Guilherme | Testes de integração entre todas as telas do app | ⬜ Sem status reportado |

**Entregável da semana:** gráfico comparativo de latência antes/depois da indexação espacial — peça central da resposta sobre "complexidade computacional".

### Semana 10 (31/08 – 06/09) — **semana atual**
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Otimizações adicionais identificadas pelo benchmark (ex: paginação de resultados, cache simples) | 🔴 Não iniciada — depende dos resultados das Semanas 8–9 |
| João | Implementação de testes automatizados básicos da API (principais endpoints) | ✅ Concluída em 03/09 — camada de contrato já existia (`test_ocorrencias_api.py`, repositório fake); adicionada a camada de integração contra Postgres/PostGIS real: `backend/tests/conftest.py` (fixture `db_session`, sessão isolada por teste via SAVEPOINT + rollback — padrão recomendado pelo SQLAlchemy para suítes de teste, cobre inclusive os `db.commit()` internos do repositório) e `backend/tests/test_ocorrencias_integracao.py` (3 casos, incluindo o filtro geoespacial via `db/repository.py` real). Isolamento validado na prática: `SELECT count(*) FROM ocorrencias` no banco compartilhado por Tailscale ficou em 0 após a suíte rodar. Sem `DATABASE_URL`, os 3 testes de integração são pulados (skip), não falham — 26/26 testes passam com Postgres disponível, 23/26 sem (3 skipped) |
| Marlon | Implementação de tela de configurações/perfil simples do usuário | ⬜ Sem status reportado |
| Guilherme | Apoio aos testes automatizados — casos de teste manuais documentados | ⬜ Sem status reportado |

### Semana 11 (07/09 – 13/09)
| Responsável | Atividade |
|---|---|
| Henrique | Medição formal de latência end-to-end (app → backend → banco → resposta) em diferentes cenários |
| João | Consolidação dos critérios de avaliação de desempenho (RNF de latência, com base científica) |
| Marlon | Preparação do roteiro de teste de usabilidade com usuários externos |
| Guilherme | Organização da documentação de testes realizados até o momento |

**Entregável da fase:** sistema integrado, com métricas de desempenho documentadas e o diferencial tecnológico (algoritmo de risco + benchmark espacial) validado.

---

## FASE 4 — Testes, Validação e Redação Final (14/09 a 30/10)

### Semana 12 (14/09 – 20/09)
| Responsável | Atividade |
|---|---|
| Henrique | Apoio técnico aos testes de usabilidade (ajustes de backend identificados durante os testes) |
| João | Execução dos testes de usabilidade com usuários externos (registro de feedback) |
| Marlon | Execução dos testes de usabilidade com usuários externos (condução das sessões) |
| Guilherme | Consolidação dos resultados de usabilidade em tabela/relatório |

### Semana 13 (21/09 – 27/09)
| Responsável | Atividade |
|---|---|
| Henrique | Correções de backend apontadas pelos testes de usabilidade e desempenho |
| João | Redação da seção de metodologia de testes e avaliação (capítulo do relatório final) |
| Marlon | Correções de interface apontadas pelos testes de usabilidade |
| Guilherme | Apoio às correções de interface e testes de regressão |

### Semana 14 (28/09 – 04/10)
| Responsável | Atividade |
|---|---|
| Henrique | Redação da seção técnica sobre arquitetura final e algoritmo de classificação de risco |
| João | Redação da seção sobre integração de múltiplas fontes de dados e resultados climáticos |
| Marlon | Redação da seção sobre desenvolvimento do aplicativo Android (XML) e decisões de UI |
| Guilherme | Levantamento de capturas de tela e evidências visuais do sistema para o relatório |

### Semana 15 (05/10 – 11/10)
| Responsável | Atividade |
|---|---|
| Henrique | Redação da seção de benchmark de indexação espacial (resultados e discussão) |
| João | Redação da seção de resultados gerais e discussão sobre o diferencial tecnológico |
| Marlon | Revisão geral da redação — padronização de linguagem, normas ABNT, citações |
| Guilherme | Organização de anexos, apêndices e lista de referências complementares |

### Semana 16 (12/10 – 18/10)
| Responsável | Atividade |
|---|---|
| Henrique | Revisão técnica cruzada do relatório (conferência de dados e resultados) |
| João | Revisão técnica cruzada do relatório (conferência de dados e resultados) |
| Marlon | Montagem da apresentação final (slides) |
| Guilherme | Apoio à montagem da apresentação final (slides) |

**Entregável da semana:** rascunho completo do relatório final para revisão do orientador.

### Semana 17 (19/10 – 30/10)
| Responsável | Atividade |
|---|---|
| Henrique | Ajustes finais conforme retorno do orientador (técnico) |
| João | Ajustes finais conforme retorno do orientador (integração/dados) |
| Marlon | Ajustes finais de formatação e ensaio da apresentação |
| Guilherme | Ajustes finais de formatação e ensaio da apresentação |

**Entregável final:** relatório consolidado + protótipo funcional + apresentação para banca (30/10/2026).

---

## Resumo de cobertura dos pontos do orientador

| Ponto observado | Onde é endereçado |
|---|---|
| Latência na resposta | Semanas 7–11 (benchmark + medição formal de latência) |
| Mais fontes de dados | Semanas 1–2 (levantamento e testes) e Semana 3 (integração consolidada: OpenWeather + ANA + CPTEC) |
| Complexidade computacional do BD georreferenciado | Semanas 1, 7, 9 (estudo teórico + benchmark com/sem índice GiST) |
| Remoção do Jetpack Compose / uso de XML | Semanas 1–6 (toda a camada Android replanejada em XML) |
| Diferencial tecnológico | Algoritmo de classificação de risco por pesos (Semanas 1, 4–6, 9) |
| Não parecer "colagem de APIs" | Algoritmo de risco como camada de processamento próprio + benchmark como contribuição técnica |
| Remoção de "baixo custo" do título | Decidido com o orientador |

---

## Notas de status (mantidas fora do cronograma original)

Este arquivo é atualizado manualmente conforme o progresso real do time. Decisões técnicas
que alteraram o escopo original (troca de CEMADEN/INMET por ANA/CPTEC) estão detalhadas em
`docs/T_arquitetura_fontes_dados_final.md`.

**Pendência crítica no caminho:** resposta da ANA ao cadastro de acesso (`hidro@ana.gov.br`),
que bloqueia as Semanas 3 (parcialmente) e 5 (totalmente).

**Item que estava atrasado sem bloqueio externo:** documentação técnica do algoritmo de risco
(Semana 6, encerrada em 09/08) — concluído em 17/08 (`docs/T15_algoritmo_risco_fundamentacao.md`).

**Validação contra banco real — resolvida na máquina do João em 03/09/2026:** todo o
backend (Semanas 2, 3 e 5) era testado só com repositórios/serviços fake em memória.
Agora há Docker Desktop + `docker-compose.yml` (serviço `db`, `postgis/postgis:16-3.4`)
nesta máquina — confirmado: `schema.sql` aplica sem erro, trigger de `geom` funciona,
os 23 testes de `backend/tests/` passam com `DATABASE_URL` apontando pro container real
(ver passo a passo no `CLAUDE.md`, seção "Ambiente de desenvolvimento").

**Banco compartilhado com o time via Tailscale (03/09/2026):** em vez de cada um instalar
Docker/Postgres/PostGIS na própria máquina, o banco do João foi exposto ao time por uma
VPN privada (Tailscale) — porta 5432 liberada só pra essa interface, nunca pra internet
aberta. Henrique é o primeiro a testar o acesso remoto (em andamento); Marlon e Guilherme
ainda não. Guia de acesso e teste em `docs/ACESSO_BANCO_DEV.md`. Isso destrava o time pra
testar/implementar contra um banco real **sem esperar** a decisão de hospedagem definitiva.
**Ainda pendente:** confirmar que Henrique, Marlon e Guilherme conseguem de fato conectar
e rodar os testes das próprias máquinas, e decidir se o time padroniza em Docker local
(cada um) ou um Postgres gerenciado (ex.: Supabase) pra produção — por ora o único banco
vivo é o da máquina do João, ligado via Tailscale.

**Decisão estrutural de 17/08:** mantido o componente colaborativo (15%) no algoritmo de risco
— é o diferencial do projeto frente ao ponto do orientador sobre "não parecer colagem de APIs".
Adicionado fail-safe de redistribuição proporcional de peso quando não há reportes suficientes
para uma área (antes, isso zerava 15% do score silenciosamente). **Pendência nova identificada:**
o módulo que agrega reportes brutos de usuários em um score 0–100 ainda não existe em nenhum
repositório do time — não é bloqueio para o protótipo (o fail-safe cobre a ausência), mas é
necessário para validar o modelo com as 4 fontes reais em produção.

**Correção de data (03/09/2026):** o cronograma estava com o marcador de "semana atual"
parado na Semana 8 (17/08–23/08) desde a última atualização de conteúdo (20/08), embora o
calendário já estivesse na Semana 10 (31/08–06/09). Marcador movido para a Semana 10.
Semanas 8 e 9 tiveram suas células de status (antes em branco) preenchidas com o que
realmente é sabido hoje — nenhum trabalho novo foi inventado ou dado como concluído, só
documentado o que estava faltando e por quê (a maioria depende da execução do benchmark
pelo Henrique, agora destravada tecnicamente pelo Docker/Tailscale de 03/09, mas ainda não
confirmada).

**Possível fonte alternativa/complementar à ANA — em investigação (03/09/2026):**
descoberta de que o campus da USCS possui uma estação meteorológica própria. Time está
investigando junto aos responsáveis a possibilidade de acesso aos dados; se viável, poderia
substituir a ANA no papel de "pluviômetro local" do modelo AHP. Também definido nesta data
que o escopo do monitoramento é especificamente a cidade de São Caetano do Sul. Não altera
a pendência crítica da ANA registrada acima (ela continua sendo a fonte ativa até essa
investigação concluir) — detalhes em `docs/T_arquitetura_fontes_dados_final.md`.

**Atualização de 20/08 — status do Marlon (Semanas 1–7):** Marlon reportou ao João o
resumo de suas entregas nas Semanas 1–7 (migração de telas para XML, mapa com Google Maps
SDK, listagem/histórico, ajustes visuais/usabilidade e tela de detalhes da ocorrência).
Marcadas como implementadas na camada de UI (XML), mas em estado ativo de manutenção —
sujeitas a ajustes conforme novas atualizações e testes ao longo do projeto. Nenhuma tela
está integrada com a API real ainda — a integração prevista para a Semana 5 não foi
iniciada, todas seguem com dados mockados/estáticos. Sem validação própria do time de
integração sobre esse status (repasse direto do relato do Marlon).
