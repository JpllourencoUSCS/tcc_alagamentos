-- Migração de 07/10/2026: fonte 'cptec' -> 'inmet' em `ocorrencias`.
--
-- O CPTEC foi substituído pela API de previsão do INMET em 06/10/2026 (ver
-- docs/T_arquitetura_fontes_dados_final.md); o vocabulário de `fonte` acompanha
-- (backend/constants.py, FonteDado). schema.sql já cria bancos novos com 'inmet';
-- esta migração é para os bancos criados antes (o principal e os do benchmark, cujas
-- linhas sintéticas usavam 'cptec'). Idempotente: pode rodar mais de uma vez.
--
--   docker exec -i alagamentos_db psql -U alagamentos -d <banco> < backend/db/migracao_2026-10-07_fonte_inmet.sql

BEGIN;

ALTER TABLE ocorrencias DROP CONSTRAINT IF EXISTS ocorrencias_fonte_check;
ALTER TABLE ocorrencias DROP CONSTRAINT IF EXISTS ck_ocorrencias_fonte;  -- nome usado pelo ORM (db/models.py)

UPDATE ocorrencias SET fonte = 'inmet' WHERE fonte = 'cptec';

ALTER TABLE ocorrencias ADD CONSTRAINT ocorrencias_fonte_check
    CHECK (fonte IN ('usuario', 'openweather', 'ana', 'inmet'));

COMMIT;
