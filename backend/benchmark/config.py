"""Configuração do ambiente de benchmark (Semana 7 — Henrique)."""

# Três ordens de grandeza, conforme o cronograma — a diferença de crescimento
# entre elas (não um volume isolado) é o que evidencia O(n) sem índice vs.
# O(log n) com GiST (ver T17_indexacao_espacial_fundamentacao.md, seção 6).
ESCALAS = [1_000, 10_000, 100_000]

# Bounding box aproximado da Grande São Paulo / ABC Paulista (lat_min, lon_min,
# lat_max, lon_max) — mesma região piloto usada nos testes reais das APIs
# (Santo André, ver testes-api/). Manter os dados sintéticos numa região real
# e razoavelmente densa evita uma distribuição artificialmente uniforme, que
# favoreceria demais qualquer índice espacial e enviesaria o benchmark.
BBOX_REGIAO_PILOTO = (-24.00, -47.00, -23.30, -46.00)

# Quantos registros por INSERT em lote — grande o bastante pra não gargalar em
# round-trips de rede, pequeno o bastante pra não estourar memória na escala
# de 100k.
TAMANHO_LOTE = 5_000

# Fixa para o benchmark ser reprodutível (mesmo dataset em reexecuções,
# relevante para comparar resultados antes/depois do índice na Semana 9).
SEMENTE_PADRAO = 42

# Ocorrências sintéticas espalhadas nos últimos N dias (exercita o filtro de
# período dos endpoints e evita empilhar todo mundo na mesma data_hora).
JANELA_DIAS = 180

# ---------------------------------------------------------------------------
# Semanas 8-9 — medição de consultas
# ---------------------------------------------------------------------------

# Viewport de mapa de ~6.6km x 6.6km centrado em Santo André (mesma
# coordenada usada em PAYLOAD_BASE dos testes da API e nos dados reais de
# testes-api/) — simula o caso de uso real ("usuário abre o mapa numa
# vizinhança"), não o bbox inteiro da região piloto, que devolveria quase
# todas as linhas e mascararia o ganho do índice.
BBOX_CONSULTA_BENCHMARK = (-23.6939, -46.5683, -23.6339, -46.5083)

NOME_INDICE_GEOM = "idx_ocorrencias_geom"
REPETICOES_PADRAO = 20
LIMITE_RESULTADOS_CONSULTA = 100  # mesmo default de limit em api/ocorrencias.py
