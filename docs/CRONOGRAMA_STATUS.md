# Cronograma de Implementação — TCC II

**Sistema de Monitoramento Colaborativo de Áreas com Risco de Alagamento**
Período: 01/07/2026 a 30/10/2026 (17 semanas)
*Última atualização de status: 07/10/2026 — Semana 15 (05/10 – 11/10). **Prazo antecipado:**
projeto e documento teórico até o fim da semana de 12–16/10/2026.*

## Legenda de responsáveis
- **Henrique** — backend / tech lead
- **João** — integração / full stack
- **Marlon** — Android / documentação
- **Guilherme** — Android / tarefas bem delimitadas

## Legenda de status
- ✅ Concluída
- 🟡 Em andamento / parcialmente bloqueada
- 🔴 Atrasada ou não iniciada
- ⚪ Sem status reportado — nada no repositório e nenhum relato do responsável; confirmar
  com ele (não significa necessariamente "não feito")

Aplicada a João e Henrique desde o início; passou a valer também para as atividades do
Marlon a partir do resumo que ele enviou em 20/08/2026 (Semanas 1–7), com atualização
enviada em 06/09/2026 (Semanas 5, 8, 9 e 10); e para as do Guilherme a partir do resumo
que ele enviou em 06/09/2026 (Semanas 1–10). Ambos os resumos são repasse direto, sem
validação própria do time de integração.

## Situação em 07/10/2026 — prazo antecipado

**Prazo:** houve ajuste nos prazos — app e documento teórico precisam estar concluídos até
o **fim da semana de 12–16/10/2026** (antes: rascunho ao orientador na S16 e banca em
30/10). Restam cerca de 8 dias úteis.

**Análise completa e plano dia a dia:** `docs/Documento Teórico/Analise_escopo_e_revisao_do_TCC_2026-10-06.md`.
Resumo:
1. **O sistema está praticamente pronto; o documento teórico não.** O texto consolidado
   (`docs/Documento Teórico/TCC_Alagamentos_Versao_Consolidada_Orientador_2026.docx`) está
   escrito como proposta e não tem os capítulos de Desenvolvimento, Testes e Conclusão que o
   template da USCS exige; há divergências entre o texto e o sistema (fontes, faixas de
   risco, modelo de dados, numeração de requisitos). É o maior trabalho da semana.
2. **Feito em 06–07/10:** CPTEC (403 desde 03/10) substituído pela API de previsão do INMET
   (levantamento do João) — previsão textual e avisos oficiais, no app e no backend; avisos
   de chuva do INMET como **piso** da classificação (decisão do grupo: Perigo → Médio;
   Grande Perigo → Alto); 99 testes no backend. **Mapa liberado (07/10, noite):** o João
   cadastrou o SHA-1 do APK de teste na chave do Google Maps; CT-MAP-001/002 e o cadastro
   com o local marcado no mapa verificados contra a API real, e as capturas do relatório
   refeitas (10 telas, inclusive login, perfil e avisos do INMET).
3. **Ajustes de escopo aguardando o orientador:** retirar a ANA (sem resposta desde agosto)
   e a estação da USCS; incluir a Open-Meteo para ter uma regra de fusão numérica (ponto 3
   do orientador); AHP com 3 critérios (pesos 54/30/16); contar um relato por usuário no
   colaborativo; registrar cada cálculo de risco.
4. **Ainda trava:** testes de usabilidade (sem data; o mapa, que travava as Tarefas 4–5, foi
   liberado em 07/10); firewall do notebook com Docker.

**Plano até a entrega (resumo):** qua 07 — decisões de escopo com o orientador, chave do
Maps, data da usabilidade; qua 07–qui 08 — ajustes de backend aprovados; qua 07–seg 12 —
documento no template; sex 09–seg 12 — usabilidade; ter 13 — resultados e conclusão;
qua 14 — revisão cruzada e ABNT; qui 15 — slides; sex 16 — entrega.

## Situação em 03/10/2026 — resumo atualizado

*(Mantida como registro; substituída pela "Situação em 07/10/2026" acima.)*

**Onde estamos:** fim da Semana 14 de 17. Rascunho completo ao orientador na Semana 16
(12–18/10); banca em 30/10. Em 03/10 uma sessão de trabalho no notebook com Docker
adiantou tarefas de todos os integrantes (detalhe na nota "Sessão de 03/10/2026", no fim
do documento). Tarefas de outros integrantes feitas nessa sessão estão marcadas como
feitas, mas **o responsável original deve revisar** (principalmente os rascunhos de seção).

**Os dois gargalos de 29/09 que dependiam só do time foram resolvidos:** o benchmark foi
executado (Semanas 7–10) e o app foi testado contra a API real (Semana 5). O terceiro (duas
bases do app) já tinha sido resolvido em 30/09.

**O que ainda trava:**
1. **Testes de usabilidade (S12) sem data.** Tudo está pronto (app integrado, dados de
   demonstração, roteiro e TCLE ajustados), exceto as tarefas do mapa — ver item 2.
   Resultados de usabilidade alimentam S13 e as seções de resultados do relatório.
2. **Mapa do app em branco no ambiente de testes:** a chave do Google Maps está restrita
   a certificados Android que não incluem o do APK gerado no notebook do João (SHA-1 no
   `CLAUDE.md`). Quem administra a chave no Google Cloud precisa adicionar esse SHA-1.
   Bloqueia CT-MAP-001/002, as Tarefas 4–5 da usabilidade e duas capturas de tela.
3. **Firewall do notebook com Docker:** banco e API acessíveis na rede local (não só pelo
   Tailscale) e API ainda não alcançável pelo Tailscale. Correção em
   `docs/ACESSO_BANCO_DEV.md`, seção 6 (exige administrador).
4. **Fontes externas:** ANA sem credencial (desde agosto); CPTEC respondendo 403 em 03/10.

**Pendências por integrante:**

| Integrante | Pendências |
|---|---|
| Henrique | Revisar os rascunhos `T16_secao_arquitetura.md` (S14) e `T16_secao_benchmark.md` (S15); confirmar acesso ao banco pelo Tailscale no ambiente dele (S5); apoio aos testes de usabilidade (S12) |
| João | Aplicar a correção de firewall; liberar (ou pedir a quem tem acesso) o SHA-1 na chave do Maps; conduzir os testes de usabilidade (S12); completar metodologia/resultados com a usabilidade (S13/S15); conferir a citação dos limiares de chuva (`referencias_consolidadas.md`, pendência 1); primeiro push para o CI rodar |
| Marlon | Revisar e complementar `T16_secao_app_android.md` (S14); revisar o roteiro de usabilidade ajustado (S11); conduzir as sessões de usabilidade e corrigir a interface (S12/S13); revisão ABNT (S15); slides a partir de `docs/roteiro_apresentacao.md` (S16); repassar a lista de bugs dos testes internos (S8) |
| Guilherme | Confirmar a planilha PT-001 v1.1 (S10/S11); capturas do mapa e do cadastro quando a chave for liberada (S14); consolidar resultados de usabilidade e regressão (S12/S13); revisar `referencias_consolidadas.md` e organizar anexos (S15); corrigir os bugs dos testes internos do Marlon (S8) |

**Decisões para a próxima conversa do time:** data dos testes de usabilidade; hospedagem
da API para as sessões (Tailscale no celular de teste ou hospedagem em nuvem — a imagem
Docker está pronta); prazo final para ANA/estação da USCS antes de documentar como
limitação; se o CPTEC continuar com 403, registrar como limitação.

## Situação em 29/09/2026 — resumo para colocar o time em dia

*(Mantida como registro; substituída pela "Situação em 03/10/2026" acima.)*

**Onde estamos:** Semana 14 de 17 (Fase 4, redação). Faltam ~4,5 semanas para a banca
(30/10) e ~2,5 semanas para o rascunho completo do relatório ir ao orientador (Semana 16,
12–18/10). As Semanas 11–13 não tiveram status reportado por ninguém; o que está marcado
nelas abaixo vem do que existe no repositório.

**O que está pronto:** backend (API de ocorrências, banco PostGIS, algoritmo AHP + fusão
climática em paralelo, 29 testes); app Android versionado em `android/` com Mapa, Detalhes,
Alertas, Previsão, Ajustes e Perfil (compila, dados mockados); material de teste de
usabilidade (plano PT-001, questionário e TCLE, 13/09); rascunhos de seção do relatório
sobre APIs e algoritmo de risco (`T16_secao_*.md`).

**Os três gargalos que travam quase todo o resto:**
1. **App não está integrado ao backend** (Semana 5, 🔴 desde 02/08). Sem isso não há teste
   de usabilidade (Semana 12), correções (Semana 13), latência end-to-end (Semana 11) nem
   capturas de tela reais (Semana 14). Além do código, falta decidir **onde a API roda**
   para o app acessar — hoje só o banco está exposto (Tailscale, notebook do João), a API
   FastAPI não está hospedada em lugar nenhum.
2. **Benchmark não foi executado** (Semanas 7–9). O gráfico com/sem índice GiST é o
   entregável central do ponto "complexidade computacional", e a Semana 15 (05–11/10) já
   prevê a redação dos resultados. Não depende de nada além de o Henrique rodar os scripts.
3. **Duas bases do app Android.** O `android/` do repositório não tem as telas de cadastro,
   login e filtros por região/período do Guilherme; não se sabe se as cópias locais do
   Marlon e do Guilherme são a mesma base. Precisa ser unificado antes de integrar.

**Pendências por integrante** (inclui as atrasadas de semanas anteriores):

| Integrante | Pendências |
|---|---|
| Henrique | Rodar `popular_banco.py` (S7) e `medir_consultas.py` sem índice (S8) e com índice GiST (S9) — **prioridade da semana**; confirmar acesso ao banco via Tailscale e persistência no ambiente dele (S5); otimizações pós-benchmark (S10); latência end-to-end (S11, depende da integração do app); seção do relatório sobre arquitetura final e algoritmo de risco (S14, atual — pode reaproveitar `T15`/`T16_secao_algoritmo_risco.md`) |
| João | Retorno da ANA e da estação da USCS — sem novidade registrada desde 03/09 (S3/S5); análise e documentação científica do benchmark (S8/S9, dependem do Henrique); critérios de desempenho / RNF de latência (S11, ⚪); testes de usabilidade (S12) e seção de metodologia de testes (S13, ⚪); seção sobre integração de múltiplas fontes (S14, atual — base em `T16_secao_relatorio_apis*.md`); apoiar a integração app ↔ API e a decisão de hospedagem |
| Marlon | Unificar a base Android com o Guilherme no `android/` do repositório; integrar mapa/listagem/detalhes com a API real e trocar coordenadas mockadas de São Paulo por São Caetano do Sul (S5); repassar ao Guilherme a lista de bugs dos testes internos (S8); ajustar o roteiro de usabilidade à base final do app (S11); conduzir testes de usabilidade e corrigir a interface (S12/S13); seção do relatório sobre o app Android (S14, atual) |
| Guilherme | Subir para o `android/` as telas de cadastro, login e filtros região/período; integrar cadastro com `POST /ocorrencias` (S5); notificação local de risco alto (S7 — hoje só existem as preferências em Ajustes); corrigir bugs dos testes internos (S8, aguarda lista do Marlon); testes de integração entre telas e casos de teste manuais (S9/S10); confirmar se a planilha PT-001 fecha a S11; consolidar resultados de usabilidade e testes de regressão (S12/S13); capturas de tela para o relatório (S14, atual — o ideal é após a integração) |

**Decisões para a próxima conversa do time:**
- Nova data para os testes de usabilidade (Semana 12 original já passou) — depende de
  quando a integração fica pronta; o questionário e o TCLE assumem app integrado ao backend.
- Onde hospedar a API (e o banco) para o app e para os testes com usuários externos — o
  notebook do João via Tailscale não serve para sessões com usuários.
- Até quando esperar a ANA / estação da USCS antes de documentar a ausência como limitação
  (o fail-safe de redistribuição de pesos já cobre o funcionamento sem ela).
- Quem implementa o agregador de reportes colaborativos (pendência de 17/08, sem responsável).

## FASE 1 — Replanejamento Técnico (01/07 a 14/07)

### Semana 1 (01/07 – 05/07)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Levantamento técnico de indexação espacial (GiST/R-tree) em PostGIS — base teórica para o benchmark futuro | ✅ Concluída — `docs/T17_indexacao_espacial_fundamentacao.md` (R-tree, GiST, comparação com Quadtree/SP-GiST/BRIN, hipótese O(log n) a validar no benchmark) |
| João | Pesquisa e definição do modelo de classificação de risco por pesos (AHP ou método similar) — base teórica | ✅ Concluída |
| Marlon | Estudo de migração de Jetpack Compose para Android Views (XML) — telas já planejadas | ✅ Concluída |
| Guilherme | Estudo de Android Views (XML) em conjunto com Marlon — foco em componentes simples (formulários, listas) | ✅ Concluída — estudo realizado com foco nos componentes básicos necessários para a migração das telas para XML. |

**Entregável da semana:** documento de decisão técnica registrando a saída do Compose e a adoção de XML Views, e o desenho inicial do algoritmo de classificação de risco.

### Semana 2 (06/07 – 12/07)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Modelagem do banco PostgreSQL/PostGIS revisada, incluindo estrutura para suportar múltiplas fontes de dados | ✅ Concluída — `docs/T18_modelagem_postgis.md` + `backend/db/schema.sql` + `backend/db/models.py` (fonte ana/cptec, coluna `geom` com trigger de sync, índice GiST, tabela nova `reportes_colaborativos_agregado`); DDL validado por compilação contra o dialeto PostgreSQL |
| João | Cadastro e testes iniciais nas APIs do CEMADEN e INMET (autenticação, formato de resposta, limitações) | ✅ Concluída — escopo redesenhado: CEMADEN e INMET testados e descartados (documentado), ANA e CPTEC assumiram os papéis |
| Marlon | Conversão dos wireframes/telas do app para layout XML (tela de mapa e tela de listagem) | ✅ Implementada — reportada por Marlon em 20/08; em manutenção ativa, sujeita a ajustes conforme novas atualizações e testes ao longo do projeto |
| Guilherme | Conversão de telas XML (formulário de cadastro de ocorrência e tela de login) com apoio do Marlon | ✅ Concluída — telas adaptadas para Android Views utilizando layouts XML, preparando a base para as implementações seguintes. |

**Entregável da semana:** banco atualizado com suporte a múltiplas fontes; primeiras chamadas reais documentadas.

---

## FASE 2 — Desenvolvimento Paralelo (13/07 a 09/08)

### Semana 3 (13/07 – 19/07)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Implementação dos endpoints REST principais no FastAPI (ocorrências: criar, listar, filtrar) | ✅ Concluída — `backend/main.py` + `backend/api/ocorrencias.py` (POST/GET/GET-por-id, filtros de fonte/nível/período/região); `backend/db/repository.py` isola o SQLAlchemy via `OcorrenciaRepositoryProtocol`, o que permitiu testar os 3 endpoints (8 casos, `backend/tests/test_ocorrencias_api.py`) sem Postgres/PostGIS vivo neste ambiente — integração contra o banco real fica para a Semana 5 |
| João | Implementação do módulo de integração climática consolidada (OpenWeather + ANA + CPTEC) no backend | 🟡 Código pronto e testado (`fusao_climatica.py`); falta só a ANA responder o cadastro pra validar as 3 fontes juntas em produção |
| Marlon | Implementação da tela de mapa em XML com Google Maps SDK (sem Compose) | ✅ Implementada — reportada por Marlon em 20/08; em manutenção ativa, sujeita a ajustes conforme novas atualizações e testes ao longo do projeto. **29/09/2026:** uma versão da tela está versionada no repositório (`android/`, `MapaFragment.kt` + `fragment_mapa.xml`, commit `fc8e24a`) — ver nota "Código Android versionado no repositório" abaixo |
| Guilherme | Implementação da tela de cadastro de ocorrência em XML, com validação de campos | ✅ Concluída — tela de cadastro implementada em XML com validações dos campos necessários para o registro de ocorrências. |

### Semana 4 (20/07 – 26/07)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | ~~Implementação da primeira versão do algoritmo de classificação de risco~~ | ✅ Absorvida pelo João — implementada em `algoritmo_risco.py` (Semana 4) e formalizada em `T15_algoritmo_risco_fundamentacao.md` (Semana 6) |
| João | Apoio à implementação do algoritmo de risco — testes com dados reais das APIs já integradas | ✅ Concluída — `algoritmo_risco.py` testado com dado real de Santo André (score 4.2, Baixo risco) |
| Marlon | Implementação da tela de listagem/histórico de ocorrências em XML | ✅ Implementada — reportada por Marlon em 20/08; em manutenção ativa, sujeita a ajustes conforme novas atualizações e testes ao longo do projeto. **29/09/2026:** versionada no repositório uma tela de listagem (aba "Alertas", `AlertasFragment.kt`, commit `fc8e24a`) com filtro por situação (todos / em andamento / encerrados) — não cobre o filtro por região e período da linha do Guilherme abaixo |
| Guilherme | Implementação de componentes de filtro (região e período) na interface XML | ✅ Concluída — componentes de filtragem por região e período implementados na interface para facilitar a consulta das ocorrências. |

**Entregável da semana:** primeira versão funcional do algoritmo de risco testável via backend.

### Semana 5 (27/07 – 02/08)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Integração do banco de dados com os endpoints (persistência real das ocorrências e classificações) | 🟡 `POST /ocorrencias` calcula `nivel_risco`/`chuva_mm` automaticamente via `fusao_climatica` quando o cliente não informa (`backend/servicos/classificacao.py`, T14 "Notas de projeto"); o `OcorrenciaRepository` já grava via SQLAlchemy desde a Semana 3. **Validado em 03/09/2026 num notebook específico do João** (com Docker, diferente do notebook usado no dia a dia das sessões — ver nota de 06/09 abaixo e `CLAUDE.md`) contra um Postgres/PostGIS real (Docker + `docker-compose.yml`, ver nota abaixo) — `schema.sql` aplica sem erro, PostGIS 3.4 ativo, 23/23 testes passam com `DATABASE_URL` apontando pro container. Segue 🟡 e não ✅ porque isso ainda não foi confirmado no ambiente do Henrique nem em CI — falta padronizar isso pro time todo. **03/10/2026:** API passou a rodar em contêiner (`Dockerfile`, serviço `api` no `docker-compose.yml`) contra o mesmo banco, usada pelo app nos testes do dia; criado CI no GitHub Actions que roda a suíte contra PostGIS real a cada push (`.github/workflows/ci.yml`) — vira ✅ quando o primeiro push rodar o CI com sucesso |
| João | Testes de consistência dos dados climáticos consolidados (comparação entre fontes para a mesma região/horário) | 🔴 Bloqueada — depende da ANA responder o cadastro (único item fora do controle do time). **03/10/2026:** OpenWeather validado de ponta a ponta com chave real (centro de São Caetano do Sul → Baixo, 13,7); a comparação entre fontes continua impossível: ANA sem credencial e CPTEC respondendo 403 (BrasilAPI também falhou). **06/10/2026:** CPTEC substituído pela API de previsão do INMET (só texto, sem mm) — a comparação numérica entre fontes depende de incluir a Open-Meteo (ajuste de escopo em análise) |
| Marlon | Integração da tela de mapa com dados reais do backend (consumo da API) | ✅ Concluída em 07/10/2026 (ver fim da célula). Histórico: 🟡 (era 🔴) Aguardando realização de teste com banco de dados contendo os dados reais **30/09/2026:** o consumo da API (GET /ocorrencias e /ocorrencias/{id}, `ApiCliente.kt`) já existia na cópia local do Marlon e passou ao `android/` com a unificação da base (ver nota "Tarefas do Guilherme e unificação da base Android"); mapa, alertas e detalhes não usam mais dados de exemplo. Validado só contra um servidor simulado — falta testar contra a API real, que ainda não está hospedada. Segue 🟡. **03/10/2026:** testado contra a API e o banco reais no emulador — mapa (cartão "Situação atual" com os 30 registros de demonstração), alertas e detalhes recebem os dados da API. Segue 🟡 só pelo desenho do mapa: a chave do Google Maps recusa o certificado do APK gerado no notebook do João ("Authorization failure"), então os marcadores não aparecem lá. **07/10/2026:** ✅ Concluída — com o SHA-1 do APK de teste cadastrado na chave, o mapa desenha os 30 marcadores de demonstração vindos da API, o toque abre o painel da ocorrência e "Ver detalhes" abre a mesma ocorrência (CT-MAP-001/002, evidências em `docs/evidencias_testes/2026-10-07/`); falta só a avaliação de usabilidade com participantes |
| Guilherme | Integração da tela de cadastro com o backend (envio de ocorrências reais) | ✅ Concluída em 03/10/2026 (ver fim da célula). Histórico: 🟡 Em andamento — estrutura de integração preparada com o endpoint de ocorrências, mas a validação completa do fluxo com backend e banco reais depende do ambiente integrado do projeto. **30/09/2026:** implementado no `android/` — tela "Registrar ocorrência" (`CadastroFragment.kt`) envia `POST /ocorrencias` com `fonte=usuario` e o `id_usuario` do perfil; sem nível escolhido, o backend calcula o risco (AHP). Testado no emulador contra servidor simulado (envio, validação de local obrigatório e erro sem conexão). Falta validar contra a API real — segue 🟡. **03/10/2026:** validado contra a API real — nível manual (POST 201, gravado no PostGIS), nível automático com clima real do OpenWeather (POST 201, classificado pelo AHP), envio sem local bloqueado e mensagem específica quando o cálculo automático está indisponível (HTTP 503). Casos CT-CAD-001 a 004 no PT-001 |

### Semana 6 (03/08 – 09/08)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Revisão de código backend e ajustes de performance inicial nas consultas | ✅ Concluída — 3 achados corrigidos: (1) filtro de região usava `BETWEEN` em lat/lon sem índice (full scan) → trocado para `&&`/`ST_MakeEnvelope` contra `geom`, usando o índice GiST já criado (liga direto com `T17`); (2) filtros `fonte`/`nivel_risco` da listagem aceitavam qualquer string e devolviam lista vazia em silêncio para valor inválido → tipados com os enums compartilhados, agora 422; (3) `sessionmaker(..., autocommit=False)` em `db/session.py` era parâmetro morto do SQLAlchemy 1.x (removido nas versões novas) → limpo. 11 testes passando (`backend/tests/`) |
| João | Documentação técnica do algoritmo de classificação de risco (fundamentação e funcionamento) — insumo para o relatório | ✅ Concluída em 17/08 — `docs/T15_algoritmo_risco_fundamentacao.md` (matriz AHP formalizada, CR=0.0038) + rascunho de seção `docs/T16_secao_algoritmo_risco.md` |
| Marlon | Ajustes visuais e de usabilidade nas telas Android já integradas | ✅ Implementada — reportada por Marlon em 20/08; em manutenção ativa, sujeita a ajustes conforme novas atualizações e testes ao longo do projeto |
| Guilherme | Testes manuais do fluxo cadastro → listagem → mapa, registrando bugs encontrados | 🟡 Parcialmente bloqueada — testes do cadastro e das telas disponíveis realizados, porém o fluxo completo ainda depende da integração da listagem e principalmente do mapa com os dados reais do backend. **03/10/2026:** fluxo cadastro → listagem → detalhes executado contra a API real (emulador); o trecho do mapa segue bloqueado pela chave do Google Maps (ver S5 do Marlon) |

**Entregável da fase:** protótipo com fluxo principal funcional (cadastro, listagem, mapa, classificação de risco básica).

---

## FASE 3 — Integração Avançada e Benchmark (10/08 a 13/09)

### Semana 7 (10/08 – 16/08)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Criação do ambiente de benchmark — geração de massa de dados simulada (1k, 10k, 100k registros geoespaciais) | ✅ Concluída em 03/10/2026 — inserção executada contra Postgres real em 1k, 10k, 100k e também 1M registros (1M levou ~7 min); a primeira execução real achou e corrigiu 2 bugs em `popular_banco.py` (a senha do banco era mascarada ao montar a URL de cada escala, e um "%" num comentário do `schema.sql` quebrava a aplicação do schema) e passou a rodar `ANALYZE` após a carga. Histórico: 🟡 Geração testada (8 testes), inserção não testada (sem Postgres) — `backend/benchmark/gerar_dados.py` (função pura, sementes reprodutíveis) + `backend/benchmark/popular_banco.py` (1 banco Postgres por escala: `alagamentos_bench_1000/10000/100000`, aplica `schema.sql`, insere em lotes de 5000 via SQLAlchemy Core). Achado do próprio teste: `data_hora` usava `datetime.now()` como referência recalculada a cada chamada, quebrando a promessa de "mesma semente = mesmo dataset" — corrigido com parâmetro `referencia` explícito. Pronto para rodar assim que houver `ADMIN_DATABASE_URL` |
| João | Refinamento do algoritmo de risco com dados de múltiplas fontes ponderadas | ✅ Concluída em 17/08 — `fusao_climatica.py` e `algoritmo_risco.py` agora conectados (`classificar_risco()`/`obter_classificacao_risco()`); testado com ANA disponível e indisponível |
| Marlon | Implementação de tela de detalhes da ocorrência (visualização individual) | ✅ Implementada — reportada por Marlon em 20/08; em manutenção ativa, sujeita a ajustes conforme novas atualizações e testes ao longo do projeto. **29/09/2026:** uma versão da tela está versionada no repositório (`DetalhesFragment.kt` + `fragment_detalhes.xml`, commit `fc8e24a`), aberta a partir do marcador do mapa e da lista de alertas |
| Guilherme | Implementação de notificações locais simples (alerta visual de risco alto no app) | ✅ Concluída em 30/09/2026 (detalhe no fim da célula). Histórico: 🟡 em andamento — estrutura do alerta local preparada, dependendo da disponibilização do nível de risco integrado aos dados reais do aplicativo para validação completa. **29/09/2026:** o commit `fc8e24a` trouxe só as *preferências* de notificação (aba "Ajustes": tipos de ocorrência, severidade mínima e raio, salvos em `Preferencias.kt`) — nenhuma notificação é disparada ainda; a estrutura de alerta local do Guilherme não está nesse commit **30/09/2026:** implementado (`NotificadorRisco.kt`) — ao receber ocorrências da API, o app notifica as novas (últimas 24 h) que atendem às preferências de Ajustes (nível mínimo, fontes e raio); toque abre os detalhes. Testado no emulador com servidor simulado. Limitação: só verifica com o app aberto (sem serviço em segundo plano) |

### Semana 8 (17/08 – 23/08)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Execução do benchmark sem índice espacial — medição de tempo de resposta nas consultas | ✅ Concluída em 03/10/2026 — `resultados_sem_indice.csv`; metodologia revisada antes da execução (3 execuções de aquecimento, registro do plano escolhido e uma segunda consulta só espacial, porque a do endpoint pode usar o índice de `data_hora`). Histórico: 🟡 Lógica testada (4 testes), execução real pendente — `backend/benchmark/medir_consultas.py`: mede a mesma consulta que `db/repository.py` gera para o filtro de região (bbox → `geom && ST_MakeEnvelope`, ORDER BY + LIMIT), via `EXPLAIN (ANALYZE, FORMAT JSON)` para isolar o tempo de execução no Postgres (sem ruído de rede/driver). Reutilizável para a Semana 9 (`--indice presente`/`ausente`, mesmo script). O bloqueio de "sem Postgres" foi removido em 03/09 (banco real disponível via Docker + Tailscale, ver notas), mas a execução em si ainda não foi confirmada — segue 🟡, não ✅ |
| João | Apoio à análise dos resultados do benchmark — interpretação dos dados coletados | ✅ Concluída em 03/10/2026 — análise em `docs/T16_secao_benchmark.md` (discussão O(n) × O(log n + k), escolha de plano do otimizador, ameaças à validade). Histórico: 🔴 Bloqueada — dependia da execução do benchmark |
| Marlon | Testes de usabilidade interna das telas (com os próprios colegas) | ✅ Concluído e sofrendo ajustes de acordo com o desenvolvimento das demais etapas e definição do design visual do projeto |
| Guilherme | Correção de bugs identificados nos testes de usabilidade | 🔴 Não iniciada — os testes em si já foram concluídos pelo Marlon nesta semana (ver linha dele acima), mas o levantamento consolidado dos problemas encontrados ainda não foi repassado ao Guilherme; correção pendente desse repasse. **30/09/2026:** sem mudança — a lista de bugs do Marlon ainda não está no repositório |

### Semana 9 (24/08 – 30/08)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Implementação de índice GiST no PostGIS e execução do benchmark comparativo | ✅ Concluída em 03/10/2026 — `resultados_com_indice.csv`, gráficos (`grafico_consulta_espacial.png`, `grafico_consulta_endpoint.png`) e `resumo.md` em `backend/benchmark/resultados/` (script `gerar_graficos.py`). Consulta espacial com 100k registros: 14,65 ms → 0,18 ms (81,6×); com 1M: 71,7 → 4,8 ms (14,8×, custo dominado pelas 5.194 linhas devolvidas). Histórico: 🔴 Não iniciada |
| João | Documentação científica do benchmark (fundamentação teórica de R-tree/GiST, conforme literatura) | ✅ Concluída em 03/10/2026 — `docs/T16_secao_benchmark.md` (metodologia, resultados, discussão, ameaças à validade, reprodutibilidade), apoiada em `T17`. Histórico: 🔴 Não iniciada |
| Marlon | Revisão e padronização visual de todas as telas (consistência de cores, fontes, espaçamento) | ✅ Concluído e sofrendo ajustes de acordo com o desenvolvimento das demais etapas e definição do design visual do projeto |
| Guilherme | Testes de integração entre todas as telas do app | 🟡 Parcialmente bloqueada — testes de integração iniciados, porém a validação completa depende da integração das telas com os dados reais do backend. **30/09/2026:** navegação entre todas as telas testada no emulador (login → mapa → cadastro → detalhes; alertas com filtros → detalhes; ajustes → perfil → sair), contra servidor simulado. Falta repetir com a API real. **03/10/2026:** repetido contra a API real, também com o aparelho em pt-BR; filtros conferidos contra a API em 8 combinações; achados e corrigidos BUG-001 (contador da lista ignorava o filtro de nível) e BUG-002 (coordenadas com vírgula decimal em pt-BR). Segue 🟡 só pelo mapa (chave do Google Maps) |

**Entregável da semana:** gráfico comparativo de latência antes/depois da indexação espacial — peça central da resposta sobre "complexidade computacional".

### Semana 10 (31/08 – 06/09)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Otimizações adicionais identificadas pelo benchmark (ex: paginação de resultados, cache simples) | ✅ Concluída em 03/10/2026 — avaliado `CLUSTER` pelo índice GiST (1M registros: consulta espacial 2,04 → 0,89 ms; endpoint forçando GiST 5,00 → 1,04 ms), documentado como manutenção periódica, não aplicado no fluxo; investigado o otimizador escolhendo o índice de `data_hora` em 1M (`random_page_cost` não muda a escolha; diferença de poucos ms, mantido); **cache simples implementado** para os dados climáticos (10 min por célula de ~1 km, `fusao_climatica.obter_dados_consolidados_em_cache`); paginação já existia (`skip`/`limit`). Ver `T16_secao_benchmark.md`, 4.Y.4. Histórico: 🔴 Não iniciada |
| João | Implementação de testes automatizados básicos da API (principais endpoints) | ✅ Concluída em 03/09 — camada de contrato já existia (`test_ocorrencias_api.py`, repositório fake); adicionada a camada de integração contra Postgres/PostGIS real: `backend/tests/conftest.py` (fixture `db_session`, sessão isolada por teste via SAVEPOINT + rollback — padrão recomendado pelo SQLAlchemy para suítes de teste, cobre inclusive os `db.commit()` internos do repositório) e `backend/tests/test_ocorrencias_integracao.py` (3 casos, incluindo o filtro geoespacial via `db/repository.py` real). Isolamento validado na prática: `SELECT count(*) FROM ocorrencias` no banco compartilhado por Tailscale ficou em 0 após a suíte rodar. Sem `DATABASE_URL`, os 3 testes de integração são pulados (skip), não falham — 26 testes desta frente (23 já existentes antes de 03/09, entre contrato e benchmark do Henrique + 3 novos de integração) passam com Postgres disponível, 23 sem (3 skipped). **Nota de reconciliação (06/09/2026):** o total combinado de `backend/tests/` no fim do dia 03/09 é 29, não 26 — a diferença são 3 testes de latência (`test_fusao_climatica_latencia.py`) adicionados no mesmo dia por outra frente de trabalho (ver nota "Achado de revisão — latência das chamadas climáticas externas" abaixo), que não são cobertos por esta linha. Contagem por arquivo conferida em 06/09/2026 contra o repositório: 11 (`test_ocorrencias_api.py`) + 8 (`test_gerar_dados.py`) + 4 (`test_medir_consultas.py`) + 3 (`test_ocorrencias_integracao.py`) + 3 (`test_fusao_climatica_latencia.py`) = 29 |
| Marlon | Implementação de tela de configurações/perfil simples do usuário | ✅ Concluída (ver 30/09/2026 abaixo; até 29/09: 🟡 em implementação e desenvolvimento). **29/09/2026:** parte de configurações versionada no repositório (aba "Ajustes", `AjustesFragment.kt` + `Preferencias.kt`, commit `fc8e24a`: liga/desliga alertas, tipos de ocorrência, severidade mínima, raio de monitoramento, restaurar padrões). ~~Perfil do usuário não implementado~~ **30/09/2026:** ✅ Concluída — tela de perfil implementada (`PerfilFragment.kt` + `fragment_perfil.xml` + `Perfil.kt`), aberta pelo cartão no topo da aba "Ajustes": nome (obrigatório, validado), e-mail (opcional, formato validado), bairro de São Caetano do Sul (lista fixa) e `id_usuario` gerado pelo app (conforme `T13_campos_usuario.md`). Dados salvos só no aparelho, sem backend — ver nota "Tela de perfil do usuário (30/09/2026)" abaixo |
| Guilherme | Apoio aos testes automatizados — casos de teste manuais documentados | ✅ (confirmar com o Guilherme) — em 03/10/2026 a planilha PT-001 passou à versão 1.1 com 21 casos, executados contra a API real na sessão do João; testes automatizados do app criados (`FuncoesPurasTest.kt`, 6 testes de JVM). Histórico: 🟡 Em andamento — casos de teste manuais estão sendo organizados e documentados para servir de base ao apoio dos testes automatizados. |

### Semana 11 (07/09 – 13/09)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Medição formal de latência end-to-end (app → backend → banco → resposta) em diferentes cenários | ✅ Concluída em 03/10/2026 — `backend/benchmark/medir_latencia_api.py` (50 requisições HTTP por cenário, p50/p95) no banco de demonstração, no banco de 1M registros e com clima real: leituras p95 ≤ 16,5 ms; cadastro com risco automático p95 560 ms sem cache e 56,5 ms com cache. Cliente e servidor na mesma máquina (rede móvel real não medida — limitação registrada em T19). Histórico: 🔴 Não iniciada |
| João | Consolidação dos critérios de avaliação de desempenho (RNF de latência, com base científica) | ✅ Concluída em 03/10/2026 — `docs/T19_criterios_desempenho.md`: RNF-01 a 05 baseados em Miller/Card/Nielsen, RAIL e ISO/IEC 25010, com verificação contra as medições (todos atendidos). Histórico: ⚪ Sem status reportado |
| Marlon | Preparação do roteiro de teste de usabilidade com usuários externos | ✅ (revisão do Marlon pendente) — **03/10/2026:** roteiro e TCLE alinhados ao app integrado: as 5 tarefas existem no app; texto corrigido para "ocorrências de demonstração" (antes dizia "dados reais", o que seria inverídico para os participantes); adicionada a lista de preparação do ambiente antes de cada sessão. Histórico: 🟡 Material pronto, falta alinhar ao app — commit `22791a7` ("AF - QA", 13/09, conta do João) adicionou `docs/questionario_teste_usabilidade.md` (roteiro de 5 tarefas guiadas + questionário para Google Forms) e `docs/tcle_teste_usabilidade.md`. O roteiro assume app integrado ao backend real e inclui tarefas (login, cadastro, filtro por região/período) cujas telas não estão no `android/` versionado — ajustar quando a base do app for unificada. Autoria (Marlon ou outro) não registrada |
| Guilherme | Organização da documentação de testes realizados até o momento | ✅ (confirmar com o Guilherme) — **03/10/2026:** PT-001 v1.1 (21 casos: 14 aprovados, 5 com a parte funcional aprovada aguardando usabilidade, 2 bloqueados pelo mapa) e evidências em `docs/evidencias_testes/2026-10-03/`. **07/10/2026:** PT-001 v1.2 (22 casos: 15 aprovados, 7 com a parte funcional aprovada aguardando usabilidade, nenhum bloqueado) — CT-MAP-001/002 desbloqueados, CT-CAD-001 refeito com o local marcado no mapa e novo CT-PRV-002 (avisos do INMET); evidências em `docs/evidencias_testes/2026-10-07/`. Histórico: 🟡 Base entregue em 13/09 (commit `22791a7`) — `docs/plano_e_fluxo_de_testes_TCC.xlsx`: plano PT-001 (escopo, critérios, responsáveis por módulo) e fluxo com 16 casos de teste; os de backend/algoritmo (`CT-API-*`, `CT-AHP-*`) registrados como executados, os 11 do app como "Não Executado" aguardando a integração. Confirmar com o Guilherme se é a entrega dele e se considera concluída |

**Entregável da fase:** sistema integrado, com métricas de desempenho documentadas e o diferencial tecnológico (algoritmo de risco + benchmark espacial) validado.

---

## FASE 4 — Testes, Validação e Redação Final (14/09 a 30/10)

### Semana 12 (14/09 – 20/09)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Apoio técnico aos testes de usabilidade (ajustes de backend identificados durante os testes) | 🔴 Não iniciada — os testes de usabilidade não aconteceram (ver linhas abaixo) |
| João | Execução dos testes de usabilidade com usuários externos (registro de feedback) | 🔴 Não executada — pré-requisito do próprio plano PT-001 é o app integrado ao backend real, que não existe ainda; os casos de usabilidade da planilha seguem "Não Executado" com data "A definir (lançamento do protótipo integrado)". Precisa de nova data. **03/10/2026:** pré-requisito técnico atendido (app integrado e testado contra a API real, dados de demonstração carregados); falta a data, os participantes e liberar o mapa (chave do Google Maps) para as Tarefas 4–5. **07/10/2026:** mapa liberado — faltam só a data e os participantes |
| Marlon | Execução dos testes de usabilidade com usuários externos (condução das sessões) | 🔴 Não executada — mesmo motivo da linha acima |
| Guilherme | Consolidação dos resultados de usabilidade em tabela/relatório | 🔴 Não iniciada — sem resultados para consolidar |

### Semana 13 (21/09 – 27/09)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Correções de backend apontadas pelos testes de usabilidade e desempenho | 🔴 Não iniciada — depende dos testes das Semanas 11–12 |
| João | Redação da seção de metodologia de testes e avaliação (capítulo do relatório final) | 🟡 Rascunho em 03/10/2026 — `docs/T16_secao_metodologia_testes.md` (5 frentes de avaliação, plano PT-001, testes automatizados, testes do app integrado, desempenho, protocolo de usabilidade, resultados e defeitos encontrados); falta a subseção de resultados de usabilidade. Histórico: ⚪ Sem status reportado |
| Marlon | Correções de interface apontadas pelos testes de usabilidade | 🔴 Não iniciada — depende da Semana 12 |
| Guilherme | Apoio às correções de interface e testes de regressão | 🔴 Não iniciada — depende da Semana 12 |

### Semana 14 (28/09 – 04/10)
| Responsável | Atividade | Status |
|---|---|---|
| Henrique | Redação da seção técnica sobre arquitetura final e algoritmo de classificação de risco | 🟡 Rascunho em 03/10/2026, revisão do Henrique pendente — `docs/T16_secao_arquitetura.md` (componentes, endpoints, fluxo do cadastro automático, implantação, testes, decisões); a parte do algoritmo (`T16_secao_algoritmo_risco.md`) foi atualizada com a agregação colaborativa e um exemplo real de São Caetano do Sul. Histórico: ⚪ Sem status reportado |
| João | Redação da seção sobre integração de múltiplas fontes de dados e resultados climáticos | ✅ Atualizada em 03/10/2026 — `T16_secao_relatorio_apis.md` ganhou a subseção 3.X.7 (integração atual: paralelismo, fail-safe, 503, cache, colaborativo, escopo São Caetano do Sul) e o registro do 403 do CPTEC. Histórico: ⚪ Sem status reportado — base existente: `docs/T16_secao_relatorio_apis.md` e `T16_secao_relatorio_apis_aluno3.md` (levantamento e comparação das APIs, última edição 17/08); precisa refletir a arquitetura atual (ANA/CPTEC, fusão em paralelo, escopo São Caetano do Sul) |
| Marlon | Redação da seção sobre desenvolvimento do aplicativo Android (XML) e decisões de UI | 🟡 Rascunho em 03/10/2026 a partir do código — `docs/T16_secao_app_android.md`; falta o Marlon complementar com o histórico de decisões de UI (wireframes, testes internos, padronização visual), que não está no repositório. Histórico: ⚪ Sem status reportado |
| Guilherme | Levantamento de capturas de tela e evidências visuais do sistema para o relatório | ✅ Concluída em 07/10/2026 (ver fim da célula). Histórico: 🟡 5 de 7 em 03/10/2026. ⚪ Sem status reportado — já dá para capturar o app do `android/` (compila), mas com dados mockados; capturas definitivas ficam melhores após a integração **30/09/2026:** não feito — as capturas devem ser tiradas com a API real rodando (hoje só há dados de um servidor simulado, que não servem como evidência no relatório). **03/10/2026:** 🟡 5 de 7 capturas feitas com a API real, clima real e o aparelho em pt-BR (`docs/capturas/`, script `android/scripts/roteiro_capturas.py`); faltam as do mapa e do cadastro, que dependem de liberar a chave do Google Maps. **07/10/2026:** ✅ Concluída — todas refeitas com o mapa liberado e as telas novas: 10 capturas (login, mapa, mapa com ocorrência selecionada, alertas, alertas filtrados, detalhes, cadastro, previsão com avisos do INMET, ajustes e perfil), descritas em `docs/capturas/README.md` |

### Semana 15 (05/10 – 11/10) — **semana atual** (o prazo final passou a ser o fim da S16)
| Responsável | Atividade | Status (adiantado em 03/10/2026) |
|---|---|---|
| Henrique | Redação da seção de benchmark de indexação espacial (resultados e discussão) | 🟡 Rascunho pronto (`docs/T16_secao_benchmark.md`), revisão do Henrique pendente |
| João | Redação da seção de resultados gerais e discussão sobre o diferencial tecnológico | 🟡 Rascunho pronto (`docs/T16_secao_resultados_discussao.md`), falta a subseção de usabilidade; análise de sensibilidade do AHP incluída (T15, seção 8.1) |
| Marlon | Revisão geral da redação — padronização de linguagem, normas ABNT, citações | ⚪ Não iniciada (semana ainda não começou) |
| Guilherme | Organização de anexos, apêndices e lista de referências complementares | 🟡 Referências consolidadas em ABNT (`docs/referencias_consolidadas.md`), com pendências de verificação; anexos ainda não organizados |

### Semana 16 (12/10 – 18/10)
| Responsável | Atividade | Status (adiantado em 03/10/2026) |
|---|---|---|
| Henrique | Revisão técnica cruzada do relatório (conferência de dados e resultados) | ⚪ Não iniciada |
| João | Revisão técnica cruzada do relatório (conferência de dados e resultados) | ⚪ Não iniciada (os rascunhos de 03/10 já passaram por uma conferência de números contra os CSVs e a planilha) |
| Marlon | Montagem da apresentação final (slides) | 🟡 Roteiro de 18 slides e perguntas prováveis da banca em `docs/roteiro_apresentacao.md` |
| Guilherme | Apoio à montagem da apresentação final (slides) | ⚪ Não iniciada |

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
| Latência na resposta | Semanas 7–11 (benchmark + medição formal de latência do banco); paralelização das chamadas às APIs climáticas externas corrigida em 03/09 (ver notas de status). **03/10:** critérios em T19 e todos atendidos — leituras p95 ≤ 16,5 ms com 1M registros; cadastro automático ~0,5 s sem cache e ~50 ms com cache |
| Mais fontes de dados | Semanas 1–2 (levantamento e testes) e Semana 3 (integração consolidada: OpenWeather + ANA + CPTEC); **03/10:** dado colaborativo implementado como 4ª fonte do AHP |
| Complexidade computacional do BD georreferenciado | Semanas 1, 7, 9 (estudo teórico + benchmark com/sem índice GiST). **03/10:** benchmark executado — 81,6× mais rápido com GiST em 100k registros; seção `T16_secao_benchmark.md` |
| Remoção do Jetpack Compose / uso de XML | Semanas 1–6 (toda a camada Android replanejada em XML) |
| Diferencial tecnológico | Algoritmo de classificação de risco por pesos (Semanas 1, 4–6, 9); **03/10:** agregação colaborativa, análise de sensibilidade e aba de risco no app (`GET /risco`); discussão em `T16_secao_resultados_discussao.md`, 5.X.4 |
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

**Validação contra banco real — resolvida em 03/09/2026 num notebook específico do João:**
todo o backend (Semanas 2, 3 e 5) era testado só com repositórios/serviços fake em memória.
Esse notebook (diferente do usado normalmente nas sessões de trabalho — ver nota de 06/09
abaixo) passou a ter Docker Desktop + `docker-compose.yml` (serviço `db`,
`postgis/postgis:16-3.4`) — confirmado: `schema.sql` aplica sem erro, trigger de `geom`
funciona, os 23 testes de `backend/tests/` passam com `DATABASE_URL` apontando pro
container real (ver passo a passo no `CLAUDE.md`, seção "Ambiente de desenvolvimento").

**Banco compartilhado com o time via Tailscale (03/09/2026):** em vez de cada um instalar
Docker/Postgres/PostGIS na própria máquina, o banco do João foi exposto ao time por uma
VPN privada (Tailscale) — porta 5432 liberada só pra essa interface, nunca pra internet
aberta. *(Correção de 03/10/2026: a regra de firewall na prática não ficou restrita ao
Tailscale — vale para qualquer rede, e uma regra do Docker Desktop libera todas as portas
no perfil Público. Correção pendente em `docs/ACESSO_BANCO_DEV.md`, seção 6.)* Henrique é o primeiro a testar o acesso remoto (em andamento); Marlon e Guilherme
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
necessário para validar o modelo com as 4 fontes reais em produção. **Resolvida em
03/10/2026:** `backend/servicos/colaborativo.py` (T15, seção 6.4), testado contra PostGIS
real e ligado ao cálculo automático e ao `GET /risco`.

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

**Achado de revisão — latência das chamadas climáticas externas (03/09/2026):** ao
levantar como o projeto trata "latência na resposta" (ponto do orientador), identificado
que `fusao_climatica.obter_dados_consolidados()` chamava as 4 fontes externas (OpenWeather
atual, OpenWeather previsão, ANA, CPTEC) **sequencialmente**, cada uma com timeout de 10s —
no pior caso (uma fonte lenta ou fora do ar), o `POST /ocorrencias` sem `nivel_risco`
explícito podia levar até ~40-50s pra responder ao usuário. Essa frente não estava coberta
pelo benchmark (que mede só a consulta ao banco) nem atribuída a ninguém no cronograma.
**Corrigido no mesmo dia:** as 4 chamadas agora rodam em paralelo via `ThreadPoolExecutor`
(`backend/fusao_climatica.py`) — o tempo total passa a ser limitado ao ramo mais lento
(~10-20s no pior caso, não a soma de todos), sem alterar os fail-safes existentes (ANA/CPTEC
devolvem `None` em erro; falha do OpenWeather continua propagando). Testado em
`backend/tests/test_fusao_climatica_latencia.py` (3 casos, sem rede real) — prova o
paralelismo por tempo de parede e confirma que os fail-safes continuam intactos. Suíte
completa: 29 testes (26 passam, 3 pulados sem `DATABASE_URL`). **Ainda em aberto** (não
implementado, ficou como possível trabalho futuro): cache de dados climáticos por
localização/janela de tempo, orçamento de tempo total por requisição, e migração do
endpoint para `async def`/`httpx` se o volume de requisições concorrentes crescer.

**Nota de máquina + revisão das tarefas do Henrique (06/09/2026):** o João usa mais de um
notebook para este repositório (sincronizado via OneDrive). O notebook com Docker/Postgres
das notas de 03/09 acima é um notebook específico — **não** o usado nesta sessão de
06/09/2026, que segue sem Docker/PostgreSQL/psql (confirmado hoje, `docker`/`psql` não
encontrados no PATH), igual ao estado descrito originalmente em 18/08/2026. Revisado se o
trabalho de 03/09 completou alguma tarefa do Henrique além de remover o bloqueio de
"sem Postgres": **não completou nenhuma** — `backend/benchmark/` (Semanas 7–9, dele) não
foi tocado nesse commit, só `backend/fusao_climatica.py` e a camada de testes do João
(Semana 10). As células de status do Henrique nas Semanas 5, 7, 8 e 9 já refletiam
corretamente esse estado (🟡, não ✅) e permanecem como estavam — a diferença prática de
03/09 pra ele é que o bloqueio técnico "sem Postgres disponível" deixou de existir (banco
real acessível via Tailscale, ver nota acima), mas rodar `popular_banco.py` e
`medir_consultas.py` de fato continua pendente e é tarefa dele.

**Revisão geral de consistência (06/09/2026):** após incorporar os resumos de status do
Marlon e do Guilherme enviados nesta data, revisado o documento inteiro em busca de
contradições entre linhas e contagens desatualizadas. Achados e correções:
1. Semana 8 — Marlon reportava os testes de usabilidade como ✅ concluídos, enquanto a
   linha do Guilherme (correção de bugs) dizia depender da "execução dos testes", tratando
   o mesmo evento como não-feito. Corrigido priorizando o registro concluído do Marlon como
   fato: a linha do Guilherme passou a citar como pendência real o repasse da lista de bugs
   levantados, não a execução dos testes.
2. Semana 7 — Henrique: contagem "11 testes" para a geração de dados sintéticos não batia
   com `backend/tests/test_gerar_dados.py` (conferido: 8 testes). Corrigido para 8; o total
   agregado de 23 testes citado na Semana 5 já estava certo (11+8+4).
3. Semana 10 — João: a célula citava 26 testes como total da suíte, enquanto a nota
   "Achado de revisão" mais abaixo (mesmo dia) citava 29. Ambas eram fotografias parciais
   corretas de momentos diferentes do mesmo dia (26 antes de somar os 3 testes de latência
   adicionados horas depois); reconciliado citando os dois números e a diferença entre eles,
   com a contagem por arquivo conferida contra o repositório.
4. Legenda de status — ainda dizia "Guilherme segue sem status própria reportada", o que
   deixou de ser verdade nesta data. Atualizada.
Nenhuma outra contradição entre responsáveis foi encontrada nas semanas restantes.

**Código Android versionado no repositório (29/09/2026):** até esta data nenhum código
Android estava no repositório — as entregas do Marlon e do Guilherme eram conhecidas só pelos
resumos repassados. O commit `fc8e24a` (autor João Lourenço, enviado pela conta `mrlnalvs`)
adicionou um projeto Android Studio completo na pasta `android/`, com navegação por abas
inferiores e 5 telas em XML Views (sem Compose):
- **Mapa** — Google Maps SDK, marcadores e círculos de área por ocorrência, cartão de status
  geral e painel da ocorrência selecionada (Semana 3 do Marlon);
- **Detalhes da ocorrência** — aberta pelo marcador do mapa e pela lista de alertas (Semana 7
  do Marlon);
- **Alertas** — listagem das ocorrências com filtro por situação (Semana 4 do Marlon);
- **Previsão** — condição atual, próximas horas e próximos dias com risco de alagamento.
  **Não prevista no cronograma** original de nenhum responsável;
- **Ajustes** — preferências de notificação salvas no aparelho (parte de configurações da
  Semana 10 do Marlon; perfil adicionado em 30/09/2026, ver nota abaixo).

Limitações registradas no momento do envio — por elas, nenhuma célula de status foi promovida
a ✅ com base neste commit:
1. **Não compilado nem executado.** A máquina de onde o commit saiu não tinha JDK no PATH
   (`JAVA_HOME` ausente), então o Gradle não rodou; nenhum build ou teste em emulador
   confirmado até esta data.
2. **Dados 100% mockados** (`OcorrenciaRepository.kt`, `PrevisaoRepository.kt`) — nenhuma
   tela consome a API do backend. A Semana 5 (integração do mapa com dados reais) segue 🔴
   como estava. As ocorrências de exemplo usam coordenadas de São Paulo, ainda não de
   São Caetano do Sul (escopo definido em 03/09).
3. **Relação com as telas reportadas pelo Marlon (20/08) e pelo Guilherme (06/09) não
   verificada.** O código deste commit foi desenvolvido/completado no notebook do João; não se
   sabe se é a mesma base das telas relatadas pelos dois ou uma implementação paralela.
   As telas de cadastro de ocorrência, login e filtros por região/período, relatadas pelo
   Guilherme, **não** estão neste commit. Marlon e Guilherme precisam confirmar qual base
   seguir antes de continuar o desenvolvimento, para não manter duas versões do app.
4. **Chave do Google Maps fora do repositório:** lida de `android/local.properties`
   (`MAPS_API_KEY=...`), arquivo não versionado. Quem clonar precisa adicionar essa linha com
   a chave recebida por canal privado — mesmo tratamento da `DATABASE_URL`.

**Tela de perfil do usuário (30/09/2026) — fecha a Semana 10 do Marlon:** adicionada ao
projeto `android/` a tela de perfil que faltava na tarefa "configurações/perfil simples do
usuário". Acesso por um cartão no topo da aba "Ajustes" (iniciais, nome e bairro), que abre a
tela de edição por cima da aba (volta com o botão voltar, mesmo padrão da tela de detalhes).
- **Campos:** nome (obrigatório, 2–60 caracteres), e-mail (opcional, formato validado quando
  preenchido), bairro de São Caetano do Sul (lista com os 15 bairros, escopo definido em
  03/09) e identificador do usuário (UUID gerado na primeira abertura — é o `id_usuario`
  "gerado pelo sistema" de `T13_campos_usuario.md`, pronto para ser enviado nas ocorrências
  quando a integração com o backend for feita).
- **Armazenamento:** só no aparelho (SharedPreferences `perfil`, separado das preferências de
  Ajustes — "Restaurar padrões" não apaga o perfil). "Limpar perfil" pede confirmação e
  mantém o identificador. Sem login/autenticação, que continua fora do escopo.
- **Verificação:** esta versão do `android/` compila (`assembleDebug`). O mesmo código de
  perfil foi testado em emulador (Pixel 8) na cópia local do Marlon: cartão vazio, erros de
  validação, salvar, seleção de bairro, cartão atualizado e limpar perfil.
- **Não incluído:** integração com o backend (o backend não tem tabela/endpoint de usuários).

**Tarefas do Guilherme e unificação da base Android (30/09/2026):** a pedido do João, as
tarefas pendentes do Guilherme que envolvem código foram feitas no app, e a cópia local do
Marlon passou a ser a base oficial do `android/` (resolve o gargalo nº 3 da "Situação em
29/09/2026" do lado do Marlon). O código do Guilherme **não** foi usado — ele nunca chegou ao
repositório; as telas abaixo foram escritas do zero seguindo T13, os casos de teste da planilha
PT-001 e o questionário de usabilidade. Se o Guilherme tiver algo a aproveitar da cópia dele,
deve partir desta base em vez de manter outra.
- **Login** (`LoginActivity.kt`, CT-LOG-001): tela de entrada sem autenticação real (fora do
  escopo) — qualquer nome/e-mail e senha preenchidos entram; "Sair" fica no Perfil.
- **Cadastro de ocorrência** (`CadastroFragment.kt`, CT-CAD-001/002, S3/S5): botão
  "Registrar" no Mapa e em Alertas; local por toque no mapa ou GPS (obrigatório), nível de risco
  "Automático" (o backend calcula por AHP) ou escolhido, descrição opcional (até 300 caracteres,
  como em T13); envia `POST /ocorrencias` e abre os detalhes da ocorrência criada.
- **Filtros por região e período** (aba Alertas, CT-LST-002, S4): região "Todas", "São Caetano
  do Sul" ou "Perto de mim" (raio de Ajustes) e período "Todo", "24 h", "7 dias" ou "30 dias";
  aplicados pelo próprio backend (`lat_min`…`lon_max` e `data_inicio`).
- **Notificação local** (`NotificadorRisco.kt`, CT-NOT-001, S7): ver linha da Semana 7.
- **Base unificada:** entram também o cliente da API que já estava na cópia local
  (`ApiCliente.kt`, Retrofit; endereço em `API_BASE_URL` no `local.properties`, padrão
  `http://10.0.2.2:8000/`) e a aba Previsão só com aviso de "indisponível", porque o backend
  não tem endpoint de previsão. Saem `PrevisaoRepository.kt` e os layouts da previsão mockada.
- **Verificação:** compila; testado no emulador (Pixel 8) contra um **servidor simulado** que
  imita `GET`/`POST /ocorrencias` com os mesmos filtros — Python/Docker não estavam disponíveis
  na máquina usada. Nada foi testado contra a API real, por isso as linhas das Semanas 5 e 9
  seguem 🟡.
- **Continua pendente do Guilherme:** corrigir os bugs dos testes internos (S8, aguarda a lista
  do Marlon), confirmar se a planilha PT-001 fecha a S11, e as tarefas que dependem dos testes
  com usuários (S12/S13) e da API real (capturas de tela da S14).

**Sessão de 07/10/2026 (noite) — mapa liberado, testes do mapa e capturas refeitas
(notebook com Docker, sessão do João):**
- **Mapa:** o João cadastrou o SHA-1 do certificado de depuração do notebook de testes nas
  restrições da chave do Google Maps. O mesmo APK passou a carregar o mapa (nenhum
  "Authorization failure" no logcat) — não foi preciso mudar código.
- **Testes (PT-001 v1.2, 22 casos):** CT-MAP-001 (30 marcadores da API, posição da
  ocorrência nº 879 conferida com `GET /ocorrencias/879`) e CT-MAP-002 (marcador → painel →
  "Ver detalhes" → mesma ocorrência) com a parte funcional aprovada, aguardando só a
  usabilidade, como os demais casos de usabilidade; CT-CAD-001 refeito com o local marcado
  por toque no mapa (ponto gravado no PostGIS igual ao tocado); novo CT-PRV-002 (avisos do
  INMET na aba Previsão iguais aos de `GET /risco`; aviso do dia era "Tempestade · Perigo
  Potencial", sem piso, como manda a regra). Registros de teste apagados do banco depois.
  Evidências em `docs/evidencias_testes/2026-10-07/`.
- **Capturas do relatório refeitas** (`docs/capturas/`, 10 telas) — o roteiro
  (`android/scripts/roteiro_capturas.py`) ganhou login, perfil e mapa com ocorrência
  selecionada; a aba Previsão já mostra os avisos do INMET.
- **Achado de ambiente:** depois de um boot a frio o emulador voltou ao fuso GMT (horas 3 h
  adiantadas na tela, banco correto). Corrigido com `cmd time_zone_detector` (passo anotado
  no roteiro de capturas); evidências e capturas refeitas no fuso de São Paulo.
- **Vocabulário de fonte `cptec` → `inmet` (inconsistência achada nas capturas, correção
  autorizada pelo João):** a aba Ajustes ainda listava "CPTEC/INPE" entre as fontes de dados.
  O valor vem do enum `fonte` da ocorrência; trocado em `constants.py` (`FonteDado.INMET`),
  `schema.sql`, `benchmark/gerar_dados.py` e `Ocorrencia.kt`. Bancos existentes migrados com
  `backend/db/migracao_2026-10-07_fonte_inmet.sql` (principal: nenhum registro `cptec`;
  bancos do benchmark: as linhas sintéticas `cptec` viraram `inmet`, mesmas contagens). Novo
  teste de contrato (`fonte=inmet` aceito, `fonte=cptec` → 422): **99 testes** no backend
  (91 sem banco + 8 de integração). App recompilado (6 testes de JVM) e capturas refeitas.

**Sessões de 06–07/10/2026 — prazo antecipado, INMET e documento teórico (notebook com
Docker, sessão do João):**
- **Prazo:** app e documento teórico até o fim da semana de 12–16/10/2026.
- **Análise do documento teórico** contra o template oficial da USCS e contra o sistema
  implementado, avaliação dos 15 pontos do orientador e proposta de ajustes de escopo:
  `docs/Documento Teórico/Analise_escopo_e_revisao_do_TCC_2026-10-06.md`. Achados
  principais: documento escrito como proposta, sem os capítulos de Desenvolvimento, Testes e
  Conclusão; não existe regra de fusão para uma mesma variável (ponto 3); a matriz AHP foi
  reconstruída depois da escolha dos pesos, e os pesos usados diferem do autovetor; o mínimo
  de 2 relatos do colaborativo conta relatos, não usuários (um usuário sozinho altera o
  risco).
- **INMET no lugar do CPTEC (06/10):** levantamento do João da API `apiprevmet3` (previsão
  por município e avisos oficiais, sem token); testado ao vivo para São Caetano do Sul;
  integrado ao backend (`fusao_climatica.py`, cache por município) e ao app (aba Previsão com
  avisos coloridos por severidade). Latência do cadastro automático sem cache remedida:
  p50 0,60 s e p95 1,63 s (RNF-03 atendido).
- **Avisos como piso (07/10, decisão do grupo):** Perigo → no mínimo Médio; Grande Perigo →
  Alto; Perigo Potencial → sem piso — no nível de risco de alagamento declarado pelo próprio
  INMET (T15 §6.5). Pesos e score inalterados.
- **Testes:** 98 no backend (90 sem banco + 8 de integração); app compila e passa nos 6
  testes de JVM; evidência `docs/evidencias_testes/2026-10-03/11_previsao_inmet_avisos.png`
  e captura `docs/capturas/06_previsao_risco.png` atualizadas.
- **Ambiente:** depois de reiniciar o notebook, abrir o Docker Desktop (os contêineres sobem
  sozinhos); o CPTEC continuava com 403 em 06/10.

**Sessão de 03/10/2026 — recuperação dos atrasos (notebook com Docker, sessão do João):**
o João pediu que tudo o que fosse possível fazer e testar naquele notebook fosse feito,
independente do responsável. Nada abaixo foi inventado: cada item tem arquivo, teste ou
medição no repositório. Os rascunhos de seção de outros integrantes precisam da revisão
deles.
- **Ambiente:** a máquina era o notebook com Docker (hostname `DESKTOP-NOGQFTB`). Instalados
  matplotlib (no `.venv`) e Android SDK + emulador (AVD `tcc_pixel`, Android 15); o João
  adicionou as chaves do OpenWeather (`.env`) e do Google Maps (`android/local.properties`).
- **Benchmark (S7–S10):** executado em 1k/10k/100k/1M; 2 bugs de `popular_banco.py`
  corrigidos; metodologia revisada (aquecimento, plano registrado, consulta só espacial);
  gráficos; `CLUSTER` e escolha de plano investigados. Resultados em
  `backend/benchmark/resultados/` e `docs/T16_secao_benchmark.md`.
- **Latência (S11):** `medir_latencia_api.py`; critérios e verificação em
  `docs/T19_criterios_desempenho.md` (RNF-01 a 05 atendidos). Achado: pela porta do Docker
  Desktop no Windows, cada `POST` paga ~50 ms extras (dentro do contêiner: 4,6 ms).
- **Backend:** chave do OpenWeather via ambiente (era `"sua_chave_aqui"` fixo); falha do
  OpenWeather vira HTTP 503 com mensagem clara; cache climático de 10 min; agregador
  colaborativo (pendência de 17/08); `GET /risco`; `Dockerfile` + serviço `api` no compose;
  dados de demonstração (`dados_demo.py`, 30 ocorrências em São Caetano do Sul, marcadas
  `demo-seed`); análise de sensibilidade do AHP; CI no GitHub Actions; dois testes de
  integração que dependiam do banco vazio corrigidos. Suíte: 29 → 61 testes.
- **App:** compilado e testado contra a API real no emulador (também em pt-BR); filtros
  conferidos contra a API; BUG-001 (contador ignorava o filtro de nível) e BUG-002
  (coordenadas com vírgula decimal em pt-BR) corrigidos; mensagem específica para o 503;
  aba Previsão passou a mostrar o risco atual (`GET /risco`); 6 testes de JVM; automação
  por adb (`android/scripts/`); build fora do OneDrive (`ALAGAMENTOS_BUILD_DIR`), porque
  o OneDrive trava os intermediários do Gradle.
- **Bloqueios encontrados:** chave do Google Maps restrita a certificados que não incluem o
  do APK gerado lá; CPTEC respondendo 403 (BrasilAPI também falhou); firewall do notebook
  não restringe o banco e a API ao Tailscale.
- **Documentação:** PT-001 v1.1 (21 casos); evidências em `docs/evidencias_testes/2026-10-03/`;
  capturas em `docs/capturas/`; TCLE e questionário corrigidos para "ocorrências de
  demonstração"; rascunhos de seção (arquitetura, app, metodologia de testes, benchmark,
  resultados/discussão); `T16_secao_relatorio_apis.md`, `T16_secao_algoritmo_risco.md`,
  T15 (seções 6.4 e 8.1, segundo exemplo real) e T18 (nota) atualizados; referências
  consolidadas; roteiro da apresentação; `ACESSO_BANCO_DEV.md` (API e segurança);
  `CLAUDE.md` e `T_arquitetura_fontes_dados_final.md` atualizados a pedido do João.
- **Pendência de verificação no relatório:** os limiares de chuva (2,5/7,6/50 mm/h) são
  atribuídos à OMM, mas o 7,6 mm/h parece vir da American Meteorological Society — conferir
  a citação (`docs/referencias_consolidadas.md`, pendência 1); não muda o modelo.

**Atualização de 29/09/2026 — marcador de semana e pendências:** o marcador de "semana
atual" estava parado na Semana 10 desde 06/09; movido para a Semana 14 (28/09–04/10). As
Semanas 11–14 ganharam coluna de status, preenchida só com o que existe no repositório ou já
estava documentado aqui — nenhum integrante reportou status dessas semanas. Para não
confundir "sem registro" com "não feito", foi criada a marcação ⚪ (sem status reportado).
Também nesta data: a célula da Semana 10 do Marlon começava com 🟡 embora a própria célula
e a nota do perfil a dessem como concluída — o marcador inicial passou a ✅. Resumo das
pendências por integrante na seção "Situação em 29/09/2026", no topo do documento.
Observação sobre datas: o commit `4ae21d4` (tela de perfil) e a nota acima estão datados
de 30/09/2026, mas já estavam no GitHub em 29/09/2026 — o relógio da máquina que gerou o
commit estava adiantado (fuso `+0100` no commit). O conteúdo não muda; só a data.

**Atualização de 20/08 — status do Marlon (Semanas 1–7):** Marlon reportou ao João o
resumo de suas entregas nas Semanas 1–7 (migração de telas para XML, mapa com Google Maps
SDK, listagem/histórico, ajustes visuais/usabilidade e tela de detalhes da ocorrência).
Marcadas como implementadas na camada de UI (XML), mas em estado ativo de manutenção —
sujeitas a ajustes conforme novas atualizações e testes ao longo do projeto. Nenhuma tela
está integrada com a API real ainda — a integração prevista para a Semana 5 não foi
iniciada, todas seguem com dados mockados/estáticos. Sem validação própria do time de
integração sobre esse status (repasse direto do relato do Marlon).
