# T18 — Modelagem do Banco PostgreSQL/PostGIS (revisada)

*Responsável: Henrique | Semana 2 do cronograma (reconstruído em 18/08/2026 após perda dos
arquivos originais) | Evolui o protótipo SQLite de `docs/T14_modelo_banco_de_dados.md` para
o schema de produção usado pelos endpoints (Semana 3) e pela persistência real (Semana 5)*

## 1. Objetivo

Revisar o modelo de dados do protótipo (T14, SQLite) para PostgreSQL/PostGIS, com estrutura
que suporte as múltiplas fontes de dados climáticos hoje ativas no projeto (OpenWeather, ANA,
CPTEC — ver `T_arquitetura_fontes_dados_final.md`) e sirva de base para o benchmark de
indexação espacial (Semanas 7–9, fundamentado em `T17_indexacao_espacial_fundamentacao.md`).

Entregáveis: [`backend/db/schema.sql`](../backend/db/schema.sql) (DDL) e
[`backend/db/models.py`](../backend/db/models.py) (ORM SQLAlchemy + GeoAlchemy2, usado pelo
código da aplicação).

## 2. O que muda em relação ao protótipo (T14)

| Aspecto | T14 (protótipo, SQLite) | T18 (produção, PostgreSQL/PostGIS) |
|---|---|---|
| Coordenadas | `latitude`/`longitude` (REAL) | Mantidos, **+ coluna `geom` (`GEOMETRY(Point, 4326)`)** sincronizada por trigger — é o que o índice espacial (GiST) de fato indexa |
| `fonte` (ocorrencias) | `usuario, openweather, inmet, cemaden` | `usuario, openweather, ana, cptec` — acompanha a saída do INMET/CEMADEN e a entrada da ANA/CPTEC decidida em 05/08 |
| `fonte` (estacoes_referencia) | `inmet, cemaden` | `ana` — única fonte com estação física hoje; CPTEC é previsão por município, não tem estação |
| `data_hora` | TEXT | `TIMESTAMPTZ`, default `now()` |
| Componente colaborativo | Sem tabela própria (só `ocorrencias.fonte='usuario'`) | + `reportes_colaborativos_agregado` (ver seção 4) |
| Índice geoespacial | `idx_ocorrencias_coords` (B-tree composto em lat/lon) | `idx_ocorrencias_geom` (**GiST**, sobre `geom`) — B-tree em duas colunas não pooda por bounding box; GiST sim (fundamentação em T17) |

O protótipo SQLite (T14) não é apagado nem invalidado — continua correto como descrição do
que rodou nos testes iniciais do algoritmo de risco. Este documento e o schema em
`backend/db/schema.sql` é o que passa a valer para qualquer trabalho de banco daqui em
diante (endpoints, persistência, benchmark).

## 3. Por que a coluna `geom` além de latitude/longitude

Manter `latitude`/`longitude` como colunas próprias (em vez de só derivar do `geom`) é
deliberado: são o formato mais simples para o app Android enviar/receber via JSON, sem exigir
que o cliente conheça WKT/GeoJSON. A coluna `geom` existe só para o banco — é o tipo que o
PostGIS entende nativamente e sobre o qual o índice GiST opera. Um trigger (`trg_sync_geom`
em `schema.sql`) mantém as duas representações em sincronia a cada INSERT/UPDATE, então a
aplicação nunca precisa escrever `geom` diretamente nem os dois valores podem divergir.

## 4. Tabela nova: `reportes_colaborativos_agregado`

O algoritmo de risco (`algoritmo_risco.py`) já espera um `reportes_colaborativos_score`
(0–100) agregado por área/janela de tempo — mas, como registrado no CRONOGRAMA_STATUS.md em
17/08, **o módulo que calcula esse agregado a partir dos reportes brutos ainda não existe**.
Esta tabela reserva onde esse resultado vai morar (`geom_area` como polígono, janela de
tempo, score, contagem de reportes), para que a implementação futura do módulo de agregação
não exija uma migração de schema adicional. A lógica de cálculo em si **não faz parte desta
tarefa** (Semana 2 é modelagem, não o módulo de agregação) — fica registrada como pendência
em aberto, já sinalizada no cronograma.

## 5. Índices e o que fica para a Semana 9

`schema.sql` já cria o índice GiST (`idx_ocorrencias_geom`) como parte da modelagem — é
necessário para o sistema funcionar corretamente em produção. Isso não conflita com o
benchmark da Semana 8 ("execução sem índice espacial"): o script de benchmark (Semana 7/8)
vai gerenciar seu próprio ciclo DROP INDEX / consulta / CREATE INDEX / consulta sobre uma
cópia dos dados, para isolar o efeito do índice sem depender do schema de produção estar
"errado" de propósito.

## 6. Como aplicar

```bash
psql -d nome_do_banco -f backend/db/schema.sql
```

Requer a extensão PostGIS disponível no servidor PostgreSQL (`CREATE EXTENSION postgis`, já
incluído no início do script). Os modelos SQLAlchemy em `backend/db/models.py` foram
validados por compilação do DDL contra o dialeto PostgreSQL (sem necessidade de um servidor
ativo neste ambiente de desenvolvimento) — a aplicação real contra um Postgres com PostGIS
fica para a Semana 5 (persistência) e para o ambiente de benchmark (Semana 7).
