-- Schema de produção — PostgreSQL/PostGIS
-- Semana 2 do cronograma (Henrique) — reconstruído em 18/08/2026.
--
-- Evolução do protótipo SQLite documentado em docs/T14_modelo_banco_de_dados.md:
--   - lat/lon deixam de ser os únicos campos geográficos: ganham uma coluna `geom`
--     (geometry Point, SRID 4326) mantida em sincronia por trigger, que é o que o
--     índice GiST (docs/T17_indexacao_espacial_fundamentacao.md) efetivamente indexa.
--   - `fonte` (em ambas as tabelas) troca inmet/cemaden por ana/cptec, refletindo a
--     decisão de arquitetura registrada em docs/T_arquitetura_fontes_dados_final.md.
--   - nova tabela `reportes_colaborativos_agregado`: ainda não tem processo que a
--     popule (módulo de agregação pendente, ver nota de 17/08 no CRONOGRAMA_STATUS.md),
--     mas o modelo já reserva o espaço para não exigir migração extra quando o módulo
--     existir.

CREATE EXTENSION IF NOT EXISTS postgis;

-- ---------------------------------------------------------------------------
-- Tabela de apoio: estacoes_referencia
-- Criada antes de `ocorrencias` porque esta a referencia via FK.
-- Antes: fonte IN ('inmet', 'cemaden'). Hoje só existe estação física para 'ana'
-- (CPTEC não tem estações — é previsão por município, ver fusao_climatica.py).
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS estacoes_referencia (
    id               BIGSERIAL PRIMARY KEY,
    codigo_externo   TEXT NOT NULL,
    nome             TEXT NOT NULL,
    fonte            TEXT NOT NULL CHECK (fonte IN ('ana')),
    latitude         DOUBLE PRECISION NOT NULL,
    longitude        DOUBLE PRECISION NOT NULL,
    geom             GEOMETRY(Point, 4326)
);

-- ---------------------------------------------------------------------------
-- Tabela principal: ocorrencias
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS ocorrencias (
    id               BIGSERIAL PRIMARY KEY,
    latitude         DOUBLE PRECISION NOT NULL,
    longitude        DOUBLE PRECISION NOT NULL,
    geom             GEOMETRY(Point, 4326),
    data_hora        TIMESTAMPTZ NOT NULL DEFAULT now(),
    descricao        TEXT,
    nivel_risco      TEXT NOT NULL CHECK (nivel_risco IN ('Baixo', 'Médio', 'Alto')),
    fonte            TEXT NOT NULL CHECK (fonte IN ('usuario', 'openweather', 'ana', 'cptec')),
    chuva_mm         DOUBLE PRECISION,
    descricao_clima  TEXT,
    temperatura      DOUBLE PRECISION,
    umidade          INTEGER,
    id_usuario       TEXT,
    id_estacao_ref   BIGINT REFERENCES estacoes_referencia(id)
);

-- ---------------------------------------------------------------------------
-- Tabela nova: reportes_colaborativos_agregado
-- Componente "colaborativo" do AHP (15% do score, ver algoritmo_risco.py) precisa
-- de um score 0-100 já agregado por área/janela de tempo. O módulo que calcula
-- esse agregado a partir dos reportes brutos (fonte='usuario' em `ocorrencias`)
-- ainda não existe — esta tabela só reserva onde o resultado vai morar.
-- ---------------------------------------------------------------------------
CREATE TABLE IF NOT EXISTS reportes_colaborativos_agregado (
    id               BIGSERIAL PRIMARY KEY,
    geom_area        GEOMETRY(Polygon, 4326) NOT NULL,
    janela_inicio    TIMESTAMPTZ NOT NULL,
    janela_fim       TIMESTAMPTZ NOT NULL,
    score            DOUBLE PRECISION NOT NULL CHECK (score BETWEEN 0 AND 100),
    quantidade_reportes INTEGER NOT NULL DEFAULT 0,
    calculado_em     TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- ---------------------------------------------------------------------------
-- Sincronização automática de geom a partir de latitude/longitude
-- (ST_MakePoint espera (longitude, latitude), nessa ordem)
-- ---------------------------------------------------------------------------
CREATE OR REPLACE FUNCTION trg_sync_geom() RETURNS trigger AS $$
BEGIN
    NEW.geom := ST_SetSRID(ST_MakePoint(NEW.longitude, NEW.latitude), 4326);
    RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER ocorrencias_sync_geom
    BEFORE INSERT OR UPDATE OF latitude, longitude ON ocorrencias
    FOR EACH ROW EXECUTE FUNCTION trg_sync_geom();

CREATE TRIGGER estacoes_referencia_sync_geom
    BEFORE INSERT OR UPDATE OF latitude, longitude ON estacoes_referencia
    FOR EACH ROW EXECUTE FUNCTION trg_sync_geom();

-- ---------------------------------------------------------------------------
-- Índices
-- ---------------------------------------------------------------------------

-- Espacial (GiST/R-tree) — objeto de estudo da Semana 1 (T17) e do benchmark
-- comparativo das Semanas 7-9. Criado aqui só para a modelagem ficar completa;
-- o benchmark da Semana 8 mede o tempo de consulta ANTES deste índice existir,
-- então ele será dropado/recriado sob controle do script de benchmark.
CREATE INDEX IF NOT EXISTS idx_ocorrencias_geom
    ON ocorrencias USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_estacoes_geom
    ON estacoes_referencia USING GIST (geom);

CREATE INDEX IF NOT EXISTS idx_reportes_geom_area
    ON reportes_colaborativos_agregado USING GIST (geom_area);

-- Não-espaciais, para os filtros mais comuns dos endpoints (Semana 3)
CREATE INDEX IF NOT EXISTS idx_ocorrencias_data_hora ON ocorrencias(data_hora);
CREATE INDEX IF NOT EXISTS idx_ocorrencias_fonte ON ocorrencias(fonte);
