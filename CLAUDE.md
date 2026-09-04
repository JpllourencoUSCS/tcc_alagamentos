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
    projeto, ex. `from constants import ...`, sem pacote `backend.` no caminho)
- `testes-api/` — scripts de teste de API, um por fonte, nomeados `teste_<fonte>.py`
- `docs/` — documentação. `T05`–`T18` são o histórico de investigação (não apagar,
  não reescrever com conteúdo diferente do que realmente aconteceu). `T16_secao_*.md`
  são rascunhos de seções do relatório final e devem ser mantidos sincronizados com as
  decisões técnicas atuais.

## Ambiente de desenvolvimento

**Atualizado em 03/09/2026:** esta máquina (a do João, usuário deste repositório) agora
tem Docker Desktop instalado e um Postgres/PostGIS real disponível via
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

Isso é **local ao ambiente do João**: Henrique, Marlon e
Guilherme não têm Docker confirmado nas máquinas deles, então não assuma banco vivo
disponível ao planejar tarefas do time sem confirmar antes. `docker-compose.yml` está no
repo para replicar em qualquer máquina com Docker instalado.

## Decisões técnicas já fechadas (não propor de novo sem pedido explícito)

- **CEMADEN**: descartado — autenticação (SGAA) sem URL pública documentada.
- **INMET**: descartado — dado em tempo real protegido por Google reCAPTCHA v3;
  endpoint histórico alternativo testado e sem retorno de dados.
- **ANA**: fonte ativa para o papel de "pluviômetro local" no modelo AHP. Exige
  cadastro por e-mail (`hidro@ana.gov.br`) — aguardando resposta. Ver `teste_ana.py`.
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
