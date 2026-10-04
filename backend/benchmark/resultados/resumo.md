# Resultados do benchmark de indexação espacial

Gerado por `backend/benchmark/gerar_graficos.py` a partir de `resultados_sem_indice.csv` e `resultados_com_indice.csv`. Tempos em ms ("Execution Time" do `EXPLAIN ANALYZE`, sem rede nem planejamento); 20 execuções medidas por célula, após 3 de aquecimento.


## Consulta só com filtro espacial (count no bbox de São Caetano do Sul)

| Registros | Sem índice: mediana (média ± dp) | Com GiST: mediana (média ± dp) | Ganho (mediana) | Plano sem índice | Plano com índice |
|---|---|---|---|---|---|
| 1.000 | 0,175 (0,178 ± 0,025) | 0,031 (0,033 ± 0,004) | 5,6× | Aggregate > Seq Scan | Aggregate > Bitmap Heap Scan > Bitmap Index Scan[idx_ocorrencias_geom] |
| 10.000 | 1,84 (1,77 ± 0,272) | 0,048 (0,050 ± 0,007) | 38,8× | Aggregate > Seq Scan | Aggregate > Bitmap Heap Scan > Bitmap Index Scan[idx_ocorrencias_geom] |
| 100.000 | 14,65 (14,79 ± 0,358) | 0,179 (0,184 ± 0,014) | 81,6× | Aggregate > Seq Scan | Aggregate > Bitmap Heap Scan > Bitmap Index Scan[idx_ocorrencias_geom] |
| 1.000.000 | 71,73 (73,34 ± 5,05) | 4,83 (4,82 ± 0,415) | 14,8× | Aggregate > Gather > Aggregate > Seq Scan | Aggregate > Bitmap Heap Scan > Bitmap Index Scan[idx_ocorrencias_geom] |

## Consulta do endpoint GET /ocorrencias (bbox + ORDER BY data_hora + LIMIT 100)

| Registros | Sem índice: mediana (média ± dp) | Com GiST: mediana (média ± dp) | Ganho (mediana) | Linhas devolvidas | Plano sem índice | Plano com índice |
|---|---|---|---|---|---|---|
| 1.000 | 0,159 (0,188 ± 0,056) | 0,032 (0,033 ± 0,004) | 5,0× | 7 | Limit > Sort > Seq Scan | Limit > Sort > Bitmap Heap Scan > Bitmap Index Scan[idx_ocorrencias_geom] |
| 10.000 | 1,49 (1,59 ± 0,251) | 0,067 (0,070 ± 0,008) | 22,3× | 48 | Limit > Sort > Seq Scan | Limit > Sort > Bitmap Heap Scan > Bitmap Index Scan[idx_ocorrencias_geom] |
| 100.000 | 8,06 (8,00 ± 0,403) | 0,328 (0,335 ± 0,016) | 24,6× | 100 | Limit > Index Scan[idx_ocorrencias_data_hora] | Limit > Sort > Bitmap Heap Scan > Bitmap Index Scan[idx_ocorrencias_geom] |
| 1.000.000 | 10,71 (10,52 ± 1,57) | 11,04 (10,96 ± 1,08) | 1,0× | 100 | Limit > Index Scan[idx_ocorrencias_data_hora] | Limit > Index Scan[idx_ocorrencias_data_hora] |
