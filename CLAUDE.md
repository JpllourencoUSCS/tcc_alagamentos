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

**18/08/2026:** Henrique perdeu os arquivos originais do backend (Semanas 1–7: modelagem
PostgreSQL/PostGIS, endpoints FastAPI, ambiente de benchmark — nada disso chegou a ser
versionado). O time decidiu reconstruir do zero em vez de tentar recuperar, e o João fez
essa reconstrução integrando ao que já existia (`algoritmo_risco.py`, `fusao_climatica.py`).
Por isso boa parte de `backend/` foi escrita numa sessão só, fora do padrão usual de autoria
por responsável — ver detalhes e o que ainda falta validar no incidente registrado em
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

Esta máquina **não tem PostgreSQL, PostGIS, Docker nem nenhum serviço de banco
instalado** (confirmado em 18/08/2026 — sem `psql`, sem `docker`, sem serviço no Windows).
Todo código de banco (`backend/db/`, `backend/benchmark/`) é testado com fakes/mocks e
validado por compilação de SQL contra o dialeto PostgreSQL, nunca contra um banco vivo.
Antes de assumir que dá para "só rodar e ver", verifique se isso mudou; se não mudou, todo
trabalho de banco fica com um passo de validação real pendente — deixe isso explícito no
`CRONOGRAMA_STATUS.md`, não implícito.

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
