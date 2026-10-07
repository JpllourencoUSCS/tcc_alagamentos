# TCC — Sistema de Monitoramento Colaborativo de Alagamentos

Contexto para o Claude Code: leia isto antes de qualquer tarefa neste repositório.

## Antes de começar

1. Leia `docs/CRONOGRAMA_STATUS.md` para saber o que está concluído, em andamento ou
   atrasado, e qual semana do cronograma estamos.
2. Leia `docs/T_arquitetura_fontes_dados_final.md` para entender as decisões técnicas
   já tomadas sobre fontes de dados — não reabra debates já fechados sem o usuário pedir.

## Sobre o projeto

TCC II de Ciência da Computação (USCS), orientador Prof. Dr. Marcos Alberto Bussab.
Sistema de monitoramento colaborativo de risco de alagamento, com pipeline de integração
de múltiplas fontes climáticas alimentando um algoritmo de classificação de risco (AHP).

**Equipe:** Henrique (backend/tech lead), João (integração/full stack — usuário deste
repositório), Marlon e Guilherme (Android).

**20/08/2026:** Marlon reportou ao João as entregas Android das Semanas 1–7 (telas de mapa,
listagem/histórico e detalhes da ocorrência em XML, com Google Maps SDK) como implementadas
na camada de UI, porém em manutenção ativa — sujeitas a ajustes conforme novas atualizações
e testes ao longo do projeto. Nenhuma tela está integrada com a API real ainda — a integração
prevista para a Semana 5 não foi iniciada, todas seguem com dados mockados/estáticos. Repasse direto do relato
do Marlon, sem validação própria do time de integração. Detalhe semana a semana no
`docs/CRONOGRAMA_STATUS.md`.

**29/09/2026:** o código Android passou a estar versionado no repositório (pasta `android/`,
ver "Convenções do repositório") — antes disso as entregas do Marlon e do Guilherme eram
conhecidas só pelos resumos repassados. Continua **sem integração com a API** (dados
mockados). O `android/` não tem as telas de cadastro, login e filtros por região/período
relatadas pelo Guilherme; ainda não confirmado se as cópias locais do Marlon e do Guilherme
são a mesma base. Nesta data o cronograma estava na Semana 14 (28/09–04/10), com as
pendências de todos consolidadas na seção "Situação em 29/09/2026" do
`docs/CRONOGRAMA_STATUS.md`.

**03/10/2026 (Semana 14):** sessão grande de recuperação de atrasos, no notebook com Docker
(ver "Ambiente de desenvolvimento"). Resumo — detalhe na nota de 03/10/2026 do
`docs/CRONOGRAMA_STATUS.md`:
- **Benchmark executado pela primeira vez** (1k/10k/100k/1M, com e sem GiST) + gráficos +
  otimizações da Semana 10 (`CLUSTER`); resultados em `backend/benchmark/resultados/`.
- **Latência ponta a ponta medida** e critérios de desempenho escritos (`docs/T19_criterios_desempenho.md`).
- **Backend:** agregador do componente colaborativo do AHP (pendência de 17/08), cache
  climático, chave do OpenWeather via `.env` (era texto fixo), HTTP 503 quando a fonte
  principal falha, novo `GET /risco`, API em contêiner, CI no GitHub Actions.
- **App testado contra a API real** pela primeira vez (emulador, também em pt-BR): 2
  defeitos achados e corrigidos; aba Previsão passou a mostrar o risco atual (`GET /risco`).
  **Mapa ainda bloqueado:** a chave do Google Maps está restrita a certificados Android que
  não incluem o do APK gerado no notebook do João (ver seção `android/` abaixo) — liberado
  em 07/10/2026.
- **Relatório:** rascunhos de seção de arquitetura, app, metodologia de testes, benchmark e
  resultados/discussão; análise de sensibilidade do AHP; referências consolidadas; roteiro
  da apresentação.
- **Segurança:** a porta do banco (e a da API) não estava restrita ao Tailscale como este
  arquivo dizia — ver "Ambiente de desenvolvimento".

**06–07/10/2026 (Semana 15) — prazo antecipado:** o projeto (app e documento teórico)
precisa ser concluído até o **fim da semana de 12–16/10/2026** (antes, banca em 30/10).
- **Documento teórico:** o grupo criou `docs/Documento Teórico/` com o template oficial da
  USCS (PDF), a versão consolidada do texto (`.docx`, ainda escrita como proposta) e os
  "15 pontos" do orientador. A análise completa — escopo, revisão do texto contra o template
  e contra o sistema, avaliação dos 15 pontos e plano até a entrega — está em
  `docs/Documento Teórico/Analise_escopo_e_revisao_do_TCC_2026-10-06.md`. O orientador
  permite ajustar o escopo documentando o motivo.
- **CPTEC substituído pelo INMET (06/10):** o CPTEC respondia 403 desde 03/10; levantamento
  do João encontrou a API de previsão do INMET (`apiprevmet3`), integrada no mesmo papel.
- **Avisos do INMET como piso da classificação (07/10, decisão do grupo):** ver "Decisões
  técnicas já fechadas".
- **Mapa liberado (07/10, noite):** o João cadastrou o SHA-1 do APK de teste na chave do
  Google Maps. CT-MAP-001/002 e o cadastro com o local marcado no mapa verificados contra a
  API real (PT-001 v1.2, 22 casos, nenhum bloqueado; evidências em
  `docs/evidencias_testes/2026-10-07/`); capturas do relatório refeitas (10 telas).
- **Fonte `cptec` → `inmet` (07/10):** o enum de fonte das ocorrências acompanhou a troca do
  CPTEC pelo INMET (backend, `schema.sql`, app); bancos existentes migrados com
  `backend/db/migracao_2026-10-07_fonte_inmet.sql`.
- **Ajustes de escopo ainda aguardando decisão** (seção 4 da análise): retirar a ANA e a
  estação da USCS; incluir a Open-Meteo como segunda fonte numérica com regra de fusão;
  AHP com 3 critérios (pesos 54/30/16, que mudariam os pesos fechados abaixo); contar um
  relato por usuário no colaborativo; registrar cada cálculo de risco.

**03/09/2026:** descoberta de que o campus da USCS possui uma estação meteorológica
própria. Time está investigando junto aos responsáveis a possibilidade de acesso aos
dados — se viável, poderia "substituir" a ANA no papel de pluviômetro local do modelo AHP.
Também nesta data, o escopo do monitoramento foi definido especificamente como a cidade de
São Caetano do Sul (antes tratado de forma mais genérica/regional). Ainda em investigação,
não é decisão fechada — ver `docs/T_arquitetura_fontes_dados_final.md`, seção "Em
investigação (03/09/2026)".

## Convenções do repositório

- `backend/` — lógica de produção:
  - `algoritmo_risco.py`, `fusao_climatica.py` — modelo AHP e fusão de fontes climáticas
  - `constants.py` — enums `NivelRisco`/`FonteDado`, vocabulário único reusado pelo ORM e pela API
    (`FonteDado`: `usuario`, `openweather`, `ana`, `inmet` — até 07/10/2026 era `cptec`;
    espelhado em `schema.sql` e no `Ocorrencia.kt` do app)
  - `db/` — `models.py` (SQLAlchemy + GeoAlchemy2), `schema.sql` (DDL PostgreSQL/PostGIS),
    `session.py` (engine/`get_db`), `repository.py` (acesso a dados de `ocorrencias`),
    `migracao_2026-10-07_fonte_inmet.sql` (para bancos criados antes da troca `cptec` → `inmet`)
  - `api/` — endpoints FastAPI (`ocorrencias.py`: `POST`/`GET /ocorrencias`, `GET /ocorrencias/{id}`;
    `risco.py`: `GET /risco`, risco atual num ponto, sem gravar nada; `schemas.py`); app
    principal em `backend/main.py`
  - `servicos/` — camada de integração entre API e lógica de domínio (`classificacao.py`
    liga os endpoints à fusão climática + agregador colaborativo + algoritmo de risco;
    `colaborativo.py` agrega relatos de usuário — 1 km, 3 h, mínimo 2 — no score 0–100 do
    componente colaborativo e registra em `reportes_colaborativos_agregado`)
  - `fusao_climatica.py` lê `OPENWEATHER_API_KEY`/`ANA_IDENTIFICADOR`/`ANA_SENHA` do ambiente;
    falha do OpenWeather vira `FonteClimaticaIndisponivel` (a API responde 503); cache de
    10 min por célula de 0,01° (`obter_dados_consolidados_em_cache`). Desde 06/10/2026
    consulta o INMET (`apiprevmet3`, código IBGE `3548807`, sem token, com User-Agent de
    navegador): previsão textual do turno atual e avisos oficiais do município, com cache
    de 10 min **por município** (as respostas pesam ~700 KB). Desde 07/10/2026 aplica o
    piso dos avisos (`piso_por_avisos`/`aplicar_piso`): a resposta traz
    `classificacao_indice` (AHP), `classificacao` (final) e `piso_aviso_inmet`. Horário de
    Brasília fixo em UTC−3 (`FUSO_BRASILIA`), sem `zoneinfo` — a imagem slim do Docker não
    traz a base de fusos
  - `benchmark/` — massa sintética, medição de consultas e de latência
    (`gerar_dados.py`, `popular_banco.py`, `medir_consultas.py`, `gerar_graficos.py`,
    `medir_latencia_api.py`; resultados versionados em `benchmark/resultados/`). Gráficos
    exigem `pip install -r requirements-benchmark.txt` (matplotlib)
  - `dados_demo.py` — 30 ocorrências **de demonstração** em São Caetano do Sul
    (`id_usuario='demo-seed'`; `python -m dados_demo` / `--limpar`), usadas nos testes do app
    e nas capturas. Não são dados reais.
  - `analise_sensibilidade.py` — análise de sensibilidade dos pesos do AHP (não altera os pesos)
  - `tests/` — pytest; rodar com `cwd=backend/` (convenção de imports absolutos do
    projeto, ex. `from constants import ...`, sem pacote `backend.` no caminho).
    Dois tipos de teste convivem no mesmo diretório: testes de **contrato** (ex.
    `test_ocorrencias_api.py`), que trocam a implementação real por um fake em
    memória via `dependency_overrides` do FastAPI e não tocam banco nenhum; e
    testes de **integração** (ex. `test_ocorrencias_integracao.py`), que usam a
    fixture `db_session` de `conftest.py` para rodar contra um Postgres/PostGIS
    real. Essa fixture isola cada teste numa transação com SAVEPOINT e dá
    rollback no final (padrão recomendado pelo próprio SQLAlchemy para suítes de
    teste) — nenhum dado criado pelo teste sobrevive. Os testes também não podem
    depender do que já existe no banco (dados de demonstração ou de outra pessoa,
    no banco compartilhado por Tailscale): consultar só os dados que o próprio teste
    criou, por exemplo com um bbox pequeno em volta deles — até 03/10/2026 dois testes
    assumiam o banco vazio e quebravam. 99 testes em 07/10/2026 (91 sem banco + 8 de
    integração). Sem
    `DATABASE_URL` definida, os testes de integração são pulados (skip), não
    falham — mesmo critério do resto do projeto para "sem Postgres disponível".
    Ao criar um teste novo que precisa de banco real, reusar `db_session` em vez
    de inventar outro padrão de setup/teardown.
- `android/` — app Android (projeto Android Studio, Kotlin + XML Views, sem Compose;
  pacote `com.example.alagamentos`), versionado desde 29/09/2026. Entrada por
  `LoginActivity.kt` (sem autenticação real); depois, navegação por abas inferiores em
  `MainActivity.kt` com um `Fragment` por tela (Mapa, Alertas, Previsão, Ajustes; Detalhes,
  Cadastro e Perfil abrem por cima). Desde 30/09/2026 os dados vêm da API real via
  `ApiCliente.kt` (Retrofit) + `OcorrenciaRepository.kt` — `GET`/`POST /ocorrencias`, com os
  filtros de região/período do backend; a aba Previsão usa `GET /risco` (risco AHP atual +
  fontes do cálculo + previsão e avisos oficiais do INMET; quando um aviso eleva a classe,
  a tela diz "Elevado de BAIXO para MÉDIO pelo aviso do INMET"). **Testado contra a API real em 03/10/2026** (emulador, inclusive em
  pt-BR/fuso de São Paulo) — evidências em `docs/evidencias_testes/2026-10-03/`. Endereço
  da API em `API_BASE_URL` no `android/local.properties` (padrão `http://10.0.2.2:8000/`,
  o localhost do computador visto pelo emulador). Preferências, perfil e sessão ficam só
  no aparelho (SharedPreferences, `Preferencias.kt`/`Perfil.kt`); notificações locais em
  `NotificadorRisco.kt`. Coordenadas exibidas sempre com ponto decimal
  (`textoCoordenadas`, em `OcorrenciaVisual.kt`) — em pt-BR o `%.4f` gerava vírgulas
  ambíguas. A chave do Google Maps vem de `android/local.properties` (`MAPS_API_KEY=...`),
  arquivo não versionado e repassado por canal privado; **a chave é restrita por
  certificado**: o APK precisa ser assinado por um certificado cujo SHA-1 esteja nas
  restrições da chave no Google Cloud, senão o mapa aparece em branco ("Authorization
  failure" no logcat). O certificado de depuração do notebook com Docker (SHA-1
  `35:BA:18:CE:CD:B4:F8:85:29:AD:A2:8B:4B:09:20:C8:57:D3:6B:72`) foi cadastrado em
  07/10/2026 e o mapa funciona nos APKs gerados lá; outras máquinas precisam cadastrar o
  SHA-1 do certificado delas. Build pelo
  Gradle (`android/gradlew assembleDebug`) exige JDK e Android SDK — confirmar na máquina
  da sessão. Com o repositório dentro do OneDrive, definir
  `ALAGAMENTOS_BUILD_DIR=C:\gradle-build\alagamentos` (lido por `android/build.gradle.kts`):
  sem isso o OneDrive trava os intermediários e o build falha com "Unable to delete
  directory". Testes de JVM: `gradlew testDebugUnitTest` (`FuncoesPurasTest.kt`).
  `android/scripts/`: `adb_app.py` (automação do app no emulador via adb, usada nos testes
  de 03/10 e 07/10) e `roteiro_capturas.py` (as 10 capturas do relatório em `docs/capturas/`).
- `testes-api/` — scripts de teste de API, um por fonte, nomeados `teste_<fonte>.py`
  (`teste_inmet_apiprevmet3.py`: levantamento do João de 06/10/2026). Atenção:
  `teste_openweather.py` sobrescreve os JSONs do teste original de Santo André
- `docs/` — documentação. `T05`–`T18` são o histórico de investigação (não apagar,
  não reescrever com conteúdo diferente do que realmente aconteceu). `T16_secao_*.md`
  são rascunhos de seções do relatório final e devem ser mantidos sincronizados com as
  decisões técnicas atuais. Material de teste (13/09/2026): `plano_e_fluxo_de_testes_TCC.xlsx`
  (plano PT-001 + casos de teste; versão 1.2 com 22 casos em 07/10/2026),
  `questionario_teste_usabilidade.md` e `tcle_teste_usabilidade.md` (ambos dizem
  explicitamente que as ocorrências do teste são de demonstração). Desde 03/10/2026:
  `T19_criterios_desempenho.md` (RNF de latência + medições), `T16_secao_arquitetura.md`,
  `T16_secao_app_android.md`, `T16_secao_metodologia_testes.md`, `T16_secao_benchmark.md`,
  `T16_secao_resultados_discussao.md`, `referencias_consolidadas.md` (ABNT, com
  pendências de verificação), `roteiro_apresentacao.md` (banca), `capturas/` e
  `evidencias_testes/`. Desde 06/10/2026: `Documento Teórico/` (template USCS, texto
  consolidado, pontos do orientador e a análise de escopo/revisão). O texto final segue a
  estrutura do template (1 Introdução, 2 Referencial Teórico, 3 Pesquisa/Amostragem,
  4 Desenvolvimento, 5 Testes, 6 Conclusão); os `T16_secao_*.md` são a matéria-prima dos
  capítulos 4 a 6.
- Raiz: `Dockerfile` (imagem da API), `docker-compose.yml` (serviços `db` e `api`),
  `.env.example` (variáveis esperadas no `.env`), `requirements.txt`,
  `requirements-benchmark.txt`, `.github/workflows/ci.yml` (pytest contra PostGIS real +
  build e testes do app a cada push — criado em 03/10/2026; primeira execução no GitHub em
  07/10/2026, com os dois jobs aprovados).

## Ambiente de desenvolvimento

**Atenção — identidade de máquina (nota adicionada em 06/09/2026):** o João usa mais de
um notebook para este repositório (sincronizado via OneDrive). O notebook com Docker/
Postgres descrito logo abaixo (configurado em 03/09/2026, dispositivo Tailscale
`tcc-alagamentos-joao`) **não é necessariamente** o notebook rodando a sessão atual — é
um notebook específico do João. Confirmado em 06/09/2026, numa sessão rodando no notebook
"original" (o mesmo descrito em 18/08/2026): sem `docker`, sem `psql`, nenhum dos dois
comandos encontrado no PATH. Nunca assumir Docker/Postgres disponível só porque este
arquivo os descreve — confirmar (`Get-Command docker`/`psql`) na máquina da sessão atual
antes de depender deles.

**Atualizado em 03/09/2026:** o notebook do João usado naquela sessão passou a ter
Docker Desktop instalado e um Postgres/PostGIS real disponível via
`docker-compose.yml` (serviço `db`, imagem `postgis/postgis:16-3.4`, porta 5432).
Credenciais **não** ficam no `docker-compose.yml` — vêm de um `.env` local (copiado de
`.env.example`, no `.gitignore`, nunca commitado). `.venv/` criado e populado a partir de
`requirements.txt`. Fluxo para subir e validar:

```
cp .env.example .env   # editar a senha antes de usar de verdade
docker compose up -d
docker exec -i alagamentos_db psql -U alagamentos -d alagamentos < backend/db/schema.sql
$env:DATABASE_URL = "postgresql+psycopg2://alagamentos:<senha-do-.env>@localhost:5432/alagamentos"
cd backend; ..\.venv\Scripts\python.exe -m pytest tests/
```

Validado nesta data: `schema.sql` aplica sem erro, PostGIS 3.4 ativo, as 23 suítes de
`backend/tests/` passam tanto sem `DATABASE_URL` (fakes/mocks) quanto contra o container
real. Isso destrava o passo de validação real da Semana 5 mencionado no
`CRONOGRAMA_STATUS.md`.

**Atualizado em 03/09/2026 (Semana 10):** adicionada a camada de testes de integração
(`backend/tests/conftest.py` + `test_ocorrencias_integracao.py`, ver "Convenções do
repositório") — total agora é 26 testes: 23 passam sempre, 3 são de integração e só
rodam com `DATABASE_URL` definida (skip, não falha, sem ela). Validado contra o
container desta máquina: os 3 passam, e `SELECT count(*) FROM ocorrencias` depois da
suíte confirma 0 linhas — o rollback por SAVEPOINT não deixa dado nenhum no banco
compartilhado por Tailscale.

**Banco compartilhado com o time via Tailscale (03/09/2026):** o banco desta máquina foi
exposto ao time via [Tailscale](https://tailscale.com) (VPN privada) em vez de exposto na
internet aberta. A intenção era liberar a porta 5432 só para o Tailscale (regra de Firewall
do Windows "TCC Alagamentos - PostgreSQL (Tailscale)"), mas **a revisão de 03/10/2026
mostrou que não está assim**: a regra vale para qualquer interface, endereço e perfil de
rede, e uma regra "Docker Desktop Backend" libera todas as portas do Docker no perfil
Público — o banco (5432) e a API (8000) ficam alcançáveis na rede local do notebook (não na
internet, por causa do NAT). A correção (PowerShell como administrador) está em
`docs/ACESSO_BANCO_DEV.md`, seção 6; até ser aplicada, a API **não** é alcançável pelo
Tailscale (falta a regra da porta 8000 no perfil Privado). IP Tailscale desta máquina:
`100.114.69.115` (pode mudar se o Tailscale for reinstalado/reconfigurado — conferir com
`tailscale ip -4`). Cada colega recebe um link de "Share" gerado no console do Tailscale
(https://login.tailscale.com/admin/machines, no dispositivo `tcc-alagamentos-joao`) — isso
dá acesso só a esta máquina, sem juntar ninguém na tailnet pessoal do João. A
`DATABASE_URL` completa (com a senha real) é repassada ao time por canal privado (Discord/
WhatsApp), nunca pelo Git. **Isso só funciona enquanto o notebook do João estiver ligado,
com Docker Desktop aberto e conectado à internet** — não é solução de produção, é só para
o time conseguir testar/desenvolver contra um banco real até decidirem hospedagem
definitiva (Supabase ou outro, ver `docs/CRONOGRAMA_STATUS.md`).

Isso é **local a um notebook específico do João** (o usado em 03/09/2026, não
necessariamente o desta sessão — ver nota no início desta seção): Henrique, Marlon,
Guilherme e o próprio João em outras máquinas não têm Docker confirmado, então não assuma
banco vivo disponível ao planejar tarefas do time sem confirmar antes. `docker-compose.yml`
está no repo para replicar em qualquer máquina com Docker instalado.

**Estado do notebook com Docker em 03/10/2026** (hostname `DESKTOP-NOGQFTB`, dispositivo
Tailscale `tcc-alagamentos-joao`, Windows 11, Ryzen 5 5600G, 16 GB):
- `docker compose up -d` sobe `alagamentos_db` e `alagamentos_api` (API em
  `http://localhost:8000`, docs em `/docs`). A API lê `OPENWEATHER_API_KEY` (e as da ANA, se
  houver) do `.env` — a do OpenWeather já está configurada. Depois de mudar o `.env`, rodar
  `docker compose up -d api` para o contêiner pegar o valor novo; depois de mudar código do
  backend, `docker compose up -d --build api`.
- O banco principal tem as 30 ocorrências de demonstração (`backend/dados_demo.py`); os
  bancos `alagamentos_bench_1000/10000/100000/1000000` são do benchmark (o de 1M ficou
  reorganizado por `CLUSTER` no experimento da Semana 10 — recriar com
  `popular_banco --recriar` antes de repetir a medição principal).
- Para benchmark e scripts: `ADMIN_DATABASE_URL` = mesma URL do `DATABASE_URL` trocando o
  banco por `postgres`.
- **Android SDK e emulador instalados** em `%LOCALAPPDATA%\Android\Sdk` (cmdline-tools
  novos: `sdkmanager` virou o `android` CLI; usar `--no-metrics`), AVD `tcc_pixel`
  (Android 15, Google APIs), JDK em `C:\Program Files\Java\jdk-24`. Subir com
  `emulator -avd tcc_pixel -gpu host` — com `swiftshader` (renderização por software) o
  emulador ficou lento a ponto de dar ANR. O emulador está em pt-BR; o fuso de São Paulo
  **pode voltar a GMT a cada boot** (horas 3 h adiantadas na tela; o banco fica certo) —
  conferir com `adb shell date` e corrigir com `adb root`,
  `adb shell settings put global auto_time_zone 0` e
  `adb shell cmd time_zone_detector suggest_manual_time_zone --zone_id America/Sao_Paulo`
  antes de capturas e evidências.
- Pela porta publicada do Docker Desktop, um `POST` leva ~50–60 ms a mais do que dentro do
  contêiner (medido: 4,6 ms dentro, ~60 ms pela porta) — efeito do encaminhamento de porta
  do Docker Desktop no Windows, não da aplicação (ver T19).

## Decisões técnicas já fechadas (não propor de novo sem pedido explícito)

- **CEMADEN**: descartado — autenticação (SGAA) sem URL pública documentada.
- **INMET — dado de estação em tempo real (`apitempo`)**: descartado — protegido por Google
  reCAPTCHA v3; endpoint histórico alternativo testado e sem retorno de dados. Não confundir
  com a API de **previsão e avisos** do INMET (`apiprevmet3`), que está em uso desde
  06/10/2026 (ver CPTEC abaixo).
- **ANA**: fonte ativa para o papel de "pluviômetro local" no modelo AHP. Exige
  cadastro por e-mail (`hidro@ana.gov.br`) — aguardando resposta. Ver `teste_ana.py`.
  Possível fonte alternativa/complementar em investigação desde 03/09/2026 (estação
  meteorológica do campus da USCS) — ainda não decidido, ver `docs/T_arquitetura_fontes_dados_final.md`.
- **CPTEC/INPE → substituído pelo INMET (`apiprevmet3`) em 06/10/2026.** O CPTEC era a
  validação cruzada qualitativa (previsão de 4 dias, fora do AHP); METAR já tinha sido
  descartado. A partir de 03/10/2026 todos os endpoints do CPTEC responderam 403 (a
  BrasilAPI, que consulta o mesmo serviço, também falhou), e o 403 persistiu. No mesmo papel
  entrou a API de previsão do INMET: previsão textual por município (`/previsao/{IBGE}`) e
  avisos oficiais (`/avisos/ativos`, filtrados pelo código IBGE). A previsão textual **não
  entra no AHP**. Riscos registrados: API sem documentação oficial; projetos relatam
  bloqueio de conexões de fora do Brasil (testar se a API for hospedada no exterior).
- **Avisos do INMET como piso da classificação (decisão do grupo, 07/10/2026):** avisos de
  chuva (Tempestade, Chuvas Intensas, Acumulado de Chuva, ou texto que mencione alagamento)
  **vigentes** para o município elevam a classe final, no nível de risco de alagamento que o
  próprio INMET declara: **Perigo → no mínimo Médio; Grande Perigo → Alto; Perigo Potencial
  → sem piso** ("baixo risco de alagamentos" no texto oficial). Não muda os pesos nem o
  score; nunca reduz a classe. Detalhe em T15 §6.5.
- **Modelo AHP**: pesos fixos — precipitação atual 35%, pluviômetro local 25%,
  previsão 25%, colaborativo 15%. Não alterar sem o usuário pedir explicitamente. A análise
  de sensibilidade de 03/10/2026 (`backend/analise_sensibilidade.py`, T15 seção 8.1) só mede
  o efeito de variar os pesos; não os altera. Os parâmetros da agregação colaborativa
  (1 km, 3 h, mínimo de 2 relatos, T15 seção 6.4) são escolhas de projeto do protótipo, não
  calibradas.

## Estilo de trabalho esperado

- Sempre que uma mudança técnica for feita, refletir no `docs/CRONOGRAMA_STATUS.md`
  e, se for uma decisão de arquitetura, também no `docs/T_arquitetura_fontes_dados_final.md`.
- Preferir entregar código pronto e testado a apenas explicar como fazer.
- Validar sintaxe Python antes de considerar uma tarefa concluída.
- Nunca gravar chaves ou senhas em arquivos versionados: `OPENWEATHER_API_KEY`, credenciais
  da ANA e senha do banco ficam no `.env`; `MAPS_API_KEY` no `android/local.properties`
  (ambos no `.gitignore`). Atenção: o logcat do Android imprime a chave do Maps por extenso
  em erros de autorização — não copiar esse log para documentos.
- Dados de demonstração (`dados_demo.py`) nunca devem ser apresentados como reais no
  relatório, nas capturas ou no teste de usabilidade.
- `backend/` tem suíte pytest (`backend/tests/`) — rodar antes de considerar uma mudança de
  backend concluída (`cd backend; python -m pytest tests/`). Sem Postgres disponível (ver
  "Ambiente de desenvolvimento"), o que não pode ser testado contra banco real fica marcado
  🟡 no cronograma, não ✅ — não arredondar isso para "concluído".

## Fechamento de sessão

Este arquivo (CLAUDE.md) e o `docs/CRONOGRAMA_STATUS.md` são estáticos — não se
atualizam sozinhos. Ao final de qualquer sessão de trabalho em que algo relevante tenha
mudado (uma tarefa concluída, uma decisão técnica tomada, um bloqueio resolvido ou
identificado), pergunte ao usuário se deve atualizar o `CLAUDE.md` e o
`docs/CRONOGRAMA_STATUS.md` antes de encerrar — e, se a mudança for de arquitetura,
também o `docs/T_arquitetura_fontes_dados_final.md`. Não decida sozinho reescrever esses
arquivos sem perguntar primeiro, mas também não deixe de perguntar — é fácil esquecer
esse passo no meio do trabalho técnico.
