# Reunião com o Orientador — 20/08/2026

**Sistema de Monitoramento Colaborativo de Áreas com Risco de Alagamento**
TCC II — Prof. Dr. Marcos Alberto Bussab
Semana atual do cronograma: **Semana 8 de 17** (17/08 – 23/08)

---

## Resumo executivo

- O algoritmo de classificação de risco (AHP) está definido, implementado e documentado
  cientificamente — é o diferencial técnico do projeto.
- A arquitetura de fontes de dados foi fechada: CEMADEN e INMET foram testados e
  descartados (achado metodológico, não falha), ANA e CPTEC assumiram seus papéis.
- O backend (Semanas 1–7) está funcionalmente completo e testado com fakes/mocks, mas
  **ainda não validado contra um banco PostgreSQL/PostGIS real** — esta é a maior
  pendência técnica ativa.
- O Android (Marlon) está com as Semanas 1–7 implementadas na camada de UI (XML), em
  manutenção ativa — mas nenhuma tela está integrada com a API real ainda, todas seguem
  com dados mockados/estáticos (a integração prevista para a Semana 5 não foi iniciada).
- Maior bloqueio externo ao time: resposta da ANA ao cadastro de acesso.

---

## Avanços por área

### 1. Algoritmo de risco e integração de dados (João)
- Modelo AHP formalizado com pesos fixos: precipitação atual 35%, pluviômetro local (ANA)
  25%, previsão 25%, componente colaborativo 15% — matriz de comparação com **CR = 0,0038**
  (consistente). Documentado em `docs/T15_algoritmo_risco_fundamentacao.md`.
- `algoritmo_risco.py` e `fusao_climatica.py` conectados e testados, inclusive com a ANA
  indisponível — fail-safe redistribui o peso proporcionalmente entre as demais fontes em
  vez de zerar o score silenciosamente.
- Arquitetura final de fontes fechada e documentada em
  `docs/T_arquitetura_fontes_dados_final.md`:
  - **OpenWeather** — precipitação atual + previsão principal.
  - **ANA** — pluviômetro local (papel que seria do CEMADEN).
  - **CPTEC/INPE** — previsão de 4 dias, validação cruzada qualitativa.
  - CEMADEN e INMET testados e descartados por proteção anti-bot documentada
    (autenticação sem URL pública / reCAPTCHA v3) — ponto legítimo de discussão
    metodológica com a banca sobre acesso a dados públicos brasileiros.

### 2. Backend (Henrique)
- Modelagem PostgreSQL/PostGIS revisada, com suporte a múltiplas fontes de dados
  (`backend/db/schema.sql`, `models.py`) — DDL validado por compilação contra o dialeto
  PostgreSQL.
- Endpoints REST no FastAPI completos (criar, listar, filtrar ocorrências) —
  `backend/main.py`, `backend/api/ocorrencias.py`, testados com 8 casos automatizados.
- Persistência real ligada ao cálculo automático de `nivel_risco`/`chuva_mm` via
  `fusao_climatica` quando o cliente não informa (`backend/servicos/classificacao.py`).
- Revisão de performance nas consultas: 3 achados corrigidos, incluindo troca de filtro
  de região sem índice (`BETWEEN`) por consulta espacial usando o índice GiST
  (`&&`/`ST_MakeEnvelope`). 11 testes passando em `backend/tests/`.
- Ambiente de benchmark criado — geração de massa de dados sintética (1k/10k/100k
  registros) com sementes reprodutíveis (`backend/benchmark/gerar_dados.py`) e script de
  medição de latência via `EXPLAIN (ANALYZE, FORMAT JSON)` (`medir_consultas.py`), pronto
  para rodar assim que houver um banco disponível.

### 3. Android (Marlon — reportado em 20/08)
Semanas 1 a 7 implementadas na camada de UI (XML), em manutenção ativa (sujeitas a
ajustes conforme novos testes ao longo do projeto):
- Migração de Compose para Views (XML) planejada e executada.
- Tela de mapa em XML com Google Maps SDK.
- Tela de listagem/histórico de ocorrências em XML.
- Ajustes visuais e de usabilidade nas telas.
- Tela de detalhes da ocorrência (visualização individual).

Nenhuma tela está integrada com a API real ainda — a integração da tela de mapa com
dados reais do backend, prevista para a Semana 5, não foi iniciada; todas as telas
(mapa, listagem, detalhes) seguem consumindo dados mockados/estáticos.

---

## Pendências e bloqueios

| Item | Situação | Bloqueia |
|---|---|---|
| **Resposta da ANA** ao cadastro (`hidro@ana.gov.br`) | Aguardando — único item fora do controle do time | Validação do pluviômetro local em produção; testes de consistência entre fontes (João, Semana 5) |
| **Validação contra banco real** | Todo o backend (Semanas 2, 3, 5) foi testado só com fakes/mocks — esta máquina não tem PostgreSQL/PostGIS/Docker instalado | Confirmar `schema.sql`, trigger de `geom`, filtros espaciais contra dados persistidos de verdade |
| **Execução real do benchmark** | Geração de dados testada; inserção em banco e medição de latência ainda não executadas (dependem do banco real) | Semanas 8–9 (comparação de latência com/sem índice GiST) — peça central da resposta sobre complexidade computacional |
| **Agregação do componente colaborativo** | Módulo que transforma reportes brutos de usuários em score 0–100 ainda não existe em nenhum repositório | Validação do modelo AHP com as 4 fontes reais em produção (fail-safe cobre a ausência por ora, não é bloqueio para o protótipo) |
| **Integração das telas Android com a API real** | Ainda não iniciada (Semana 5 do Marlon) — nenhuma tela integrada, todas com dados mockados/estáticos | Demonstração do app com dados reais (mapa, listagem e detalhes) |

---

## Próximos passos

**Semana 8 (atual, até 23/08):**
- Definir e viabilizar ambiente de banco real (ver "Pontos em aberto" abaixo) para
  destravar a execução do benchmark.
- Marlon/Guilherme: testes de usabilidade interna e correção de bugs encontrados.

**Semana 9 (24/08 – 30/08):**
- Implementação de índice GiST no PostGIS e execução do benchmark comparativo —
  entregável: gráfico de latência antes/depois da indexação espacial.
- João: documentação científica do benchmark (fundamentação teórica R-tree/GiST).
- Marlon: revisão e padronização visual das telas.

**Semanas 10–11:**
- Otimizações adicionais (paginação, cache), testes automatizados da API, medição formal
  de latência end-to-end, consolidação dos critérios de avaliação de desempenho.

---

## Pontos em aberto para discutir com o orientador

1. **Contingência para a ANA** — se a resposta ao cadastro continuar sem prazo, o fail-safe
   de redistribuição de peso já garante que o protótipo funciona sem ela; vale validar com o
   orientador se isso é aceitável como limitação documentada do projeto ou se devemos buscar
   uma fonte alternativa de pluviômetro local.

---

*Documento gerado a partir de `docs/CRONOGRAMA_STATUS.md` e `docs/T_arquitetura_fontes_dados_final.md`.*
