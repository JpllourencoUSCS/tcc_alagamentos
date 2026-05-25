# Estrutura Preliminar do Banco de Dados

**Responsável:** Aluno 3

---

## Tabela principal: `ocorrencias`

Armazena tanto os registros inseridos pelo usuário quanto os dados captados automaticamente das APIs.

| Campo | Tipo | Obrigatório | Origem | Descrição |
|---|---|---|---|---|
| `id` | INTEGER (PK, autoincrement) | Sim | Sistema | Identificador único da ocorrência |
| `latitude` | REAL | Sim | GPS / API / Usuário | Coordenada geográfica latitude |
| `longitude` | REAL | Sim | GPS / API / Usuário | Coordenada geográfica longitude |
| `data_hora` | DATETIME | Sim | Sistema (automático) | Data e hora do registro |
| `descricao` | TEXT | Não | Usuário | Relato livre (máx. 300 chars) |
| `nivel_risco` | TEXT | Sim | Sistema / Usuário | Enum: "Baixo", "Médio", "Alto" |
| `fonte` | TEXT | Sim | Sistema | "usuario", "openweather", "inmet", "cemaden" |
| `chuva_mm` | REAL | Não | OpenWeather / API | Volume de precipitação (mm/h ou mm/3h) |
| `descricao_clima` | TEXT | Não | OpenWeather | Ex: "chuva leve", "tempestade" |
| `temperatura` | REAL | Não | OpenWeather | Temperatura no momento do registro (°C) |
| `umidade` | INTEGER | Não | OpenWeather | Umidade relativa do ar (%) |
| `id_usuario` | TEXT | Não | Sistema | Identificador do usuário (quando fonte = "usuario") |

---

## Tabela de apoio: `estacoes_referencia`

Guarda as estações de monitoramento consultadas (INMET/CEMADEN) para rastreabilidade.

| Campo | Tipo | Obrigatório | Descrição |
|---|---|---|---|
| `id` | INTEGER (PK) | Sim | Identificador interno |
| `codigo_externo` | TEXT | Sim | Código da estação na fonte (ex: "A771") |
| `nome` | TEXT | Sim | Nome da estação (ex: "SANTO ANDRE") |
| `fonte` | TEXT | Sim | "inmet" ou "cemaden" |
| `latitude` | REAL | Sim | Coordenada da estação |
| `longitude` | REAL | Sim | Coordenada da estação |

---

## Relacionamentos

```
ocorrencias
  id_estacao_ref (FK, nullable) → estacoes_referencia.id
```

Quando a ocorrência é gerada automaticamente a partir de uma estação física (INMET/CEMADEN),
o campo `id_estacao_ref` registra a fonte. Ocorrências de usuário ou OpenWeather têm `NULL`.

---

## Script de criação (SQLite — protótipo)

```sql
CREATE TABLE IF NOT EXISTS ocorrencias (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    latitude         REAL    NOT NULL,
    longitude        REAL    NOT NULL,
    data_hora        TEXT    NOT NULL,
    descricao        TEXT,
    nivel_risco      TEXT    NOT NULL CHECK(nivel_risco IN ('Baixo', 'Médio', 'Alto')),
    fonte            TEXT    NOT NULL CHECK(fonte IN ('usuario', 'openweather', 'inmet', 'cemaden')),
    chuva_mm         REAL,
    descricao_clima  TEXT,
    temperatura      REAL,
    umidade          INTEGER,
    id_usuario       TEXT,
    id_estacao_ref   INTEGER REFERENCES estacoes_referencia(id)
);

CREATE TABLE IF NOT EXISTS estacoes_referencia (
    id               INTEGER PRIMARY KEY AUTOINCREMENT,
    codigo_externo   TEXT NOT NULL,
    nome             TEXT NOT NULL,
    fonte            TEXT NOT NULL CHECK(fonte IN ('inmet', 'cemaden')),
    latitude         REAL NOT NULL,
    longitude        REAL NOT NULL
);

CREATE INDEX IF NOT EXISTS idx_ocorrencias_coords
    ON ocorrencias(latitude, longitude);

CREATE INDEX IF NOT EXISTS idx_ocorrencias_data
    ON ocorrencias(data_hora);
```

---

## Notas de projeto

- O banco utilizado no protótipo é **SQLite**, pelo baixo overhead de configuração.
  Em produção, recomenda-se migrar para **PostgreSQL + PostGIS** para consultas geoespaciais nativas.
- O campo `nivel_risco` pode ser calculado automaticamente pelo backend a partir de `chuva_mm`
  (vide regras definidas na Tarefa 12), mas também pode ser sobrescrito pelo usuário no
  formulário de ocorrência.
- O campo `fonte` garante rastreabilidade e permite distinguir dados de alta confiabilidade
  (estações INMET) de relatos populares (usuário), aspecto relevante para a análise de
  confiabilidade futura do sistema.
