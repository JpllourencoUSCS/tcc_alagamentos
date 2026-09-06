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
  - `db/` — `models.py` (SQLAlchemy + GeoAlchemy2), `schema.sql` (DDL PostgreSQL/PostGIS),
    `session.py` (engine/`get_db`), `repository.py` (acesso a dados de `ocorrencias`)
  - `api/` — endpoints FastAPI (`ocorrencias.py`, `schemas.py`); app principal em `backend/main.py`
  - `servicos/` — camada de integração entre API e lógica de domínio (`classificacao.py`
    liga o endpoint de criação à fusão climática + algoritmo de risco)
  - `benchmark/` — geração de massa de dados sintética e medição de consultas
    (Semanas 7–9: `gerar_dados.py`, `popular_banco.py`, `medir_consultas.py`)
  - `tests/` — pytest; rodar com `cwd=backend/` (convenção de imports absolutos do
    projeto, ex. `from constants import ...`, sem pacote `backend.` no caminho).
    Dois tipos de teste convivem no mesmo diretório: testes de **contrato** (ex.
    `test_ocorrencias_api.py`), que trocam a implementação real por um fake em
    memória via `dependency_overrides` do FastAPI e não tocam banco nenhum; e
    testes de **integração** (ex. `test_ocorrencias_integracao.py`), que usam a
    fixture `db_session` de `conftest.py` para rodar contra um Postgres/PostGIS
    real. Essa fixture isola cada teste numa transação com SAVEPOINT e dá
    rollback no final (padrão recomendado pelo próprio SQLAlchemy para suítes de
    teste) — nenhum dado criado pelo teste sobrevive, então não importa se o
    banco está vazio ou tem dado de outra pessoa (relevante com o banco
    compartilhado por Tailscale, ver "Ambiente de desenvolvimento"). Sem
    `DATABASE_URL` definida, os testes de integração são pulados (skip), não
    falham — mesmo critério do resto do projeto para "sem Postgres disponível".
    Ao criar um teste novo que precisa de banco real, reusar `db_session` em vez
    de inventar outro padrão de setup/teardown.
- `testes-api/` — scripts de teste de API, um por fonte, nomeados `teste_<fonte>.py`
- `docs/` — documentação. `T05`–`T18` são o histórico de investigação (não apagar,
  não reescrever com conteúdo diferente do que realmente aconteceu). `T16_secao_*.md`
  são rascunhos de seções do relatório final e devem ser mantidos sincronizados com as
  decisões técnicas atuais.

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
internet aberta — porta 5432 liberada só para a interface Tailscale (regra de Firewall do
Windows "TCC Alagamentos - PostgreSQL (Tailscale)"). IP Tailscale desta máquina:
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

## Decisões técnicas já fechadas (não propor de novo sem pedido explícito)

- **CEMADEN**: descartado — autenticação (SGAA) sem URL pública documentada.
- **INMET**: descartado — dado em tempo real protegido por Google reCAPTCHA v3;
  endpoint histórico alternativo testado e sem retorno de dados.
- **ANA**: fonte ativa para o papel de "pluviômetro local" no modelo AHP. Exige
  cadastro por e-mail (`hidro@ana.gov.br`) — aguardando resposta. Ver `teste_ana.py`.
  Possível fonte alternativa/complementar em investigação desde 03/09/2026 (estação
  meteorológica do campus da USCS) — ainda não decidido, ver `docs/T_arquitetura_fontes_dados_final.md`.
- **CPTEC/INPE**: fonte ativa só para previsão de 4 dias (validação cruzada qualitativa).
  Condições atuais de aeroporto (METAR) foram testadas e descartadas.
- **Modelo AHP**: pesos fixos — precipitação atual 35%, pluviômetro local 25%,
  previsão 25%, colaborativo 15%. Não alterar sem o usuário pedir explicitamente.

## Estilo de trabalho esperado

- Sempre que uma mudança técnica for feita, refletir no `docs/CRONOGRAMA_STATUS.md`
  e, se for uma decisão de arquitetura, também no `docs/T_arquitetura_fontes_dados_final.md`.
- Preferir entregar código pronto e testado a apenas explicar como fazer.
- Validar sintaxe Python antes de considerar uma tarefa concluída.
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
