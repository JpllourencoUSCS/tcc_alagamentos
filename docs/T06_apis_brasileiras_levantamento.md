# Levantamento — APIs Públicas Brasileiras (INMET / CEMADEN)

## 1. INMET — Instituto Nacional de Meteorologia

### Acesso
- Portal: https://portal.inmet.gov.br/
- API pública: https://apitempo.inmet.gov.br/
- Autenticação: token de usuário (cadastro gratuito no portal)
- Formato de resposta: JSON

### Endpoints relevantes identificados

| Endpoint | Descrição | Observação |
|---|---|---|
| `/estacao/{tipo}/{data-ini}/{data-fim}/{codEst}` | Dados horários por estação | Requer código da estação |
| `/estacao/T/hora/{data}` | Dados de todas as estações em uma hora | Volume alto de dados |
| `/estacoes/{tipo}` | Lista de estações cadastradas | Tipo: T (todas), M (manuais) |
| `/condicoes/{lat}/{lon}` | Condições aproximadas por coordenada | Depende da estação mais próxima |

### Campos relevantes retornados (dados horários)

| Campo | Significado | Uso no sistema |
|---|---|---|
| `CHUVA` | Precipitação acumulada no período (mm) | Classificação de risco |
| `TEM_INS` | Temperatura instantânea (°C) | Informativo |
| `UMD_INS` | Umidade relativa instantânea (%) | Informativo |
| `DT_MEDICAO` | Data/hora da medição | Rastreabilidade |
| `CD_ESTACAO` | Código da estação que gerou o dado | Validação da fonte |

### Viabilidade
- **Positivo:** fonte institucional brasileira, dados oficiais, cobertura nacional
- **Negativo:** requer cadastro, dados dependem da proximidade de estações físicas (cobertura irregular em área urbana densa), atualização pode ter atraso de até 1 hora
- **Conclusão preliminar:** viável como fonte complementar ou de validação, mas não ideal como fonte primária para o protótipo

---

## 2. CEMADEN — Centro Nacional de Monitoramento e Alertas de Desastres Naturais

### Acesso
- Portal: http://www.cemaden.gov.br/
- Dados abertos: http://www.cemaden.gov.br/mapainterativo/
- Webservice (pluviômetros automáticos): http://sjc.salvar.cemaden.gov.br/resources/graficos/interface/prec.php
- Autenticação: não exige autenticação para os dados públicos de pluviômetros
- Formato de resposta: JSON (estrutura não padronizada, varia por município)

### Acesso aos dados de pluviômetros

Endpoint identificado para consulta de dados de precipitação:

```
GET http://sjc.salvar.cemaden.gov.br/resources/graficos/interface/prec.php
    ?uf={UF}&municipio={cod_ibge}&inicio={AAAA-MM-DD HH:MM:SS}&fim={AAAA-MM-DD HH:MM:SS}
```

Exemplo para São Paulo — SP (IBGE: 3550308):
```
http://sjc.salvar.cemaden.gov.br/resources/graficos/interface/prec.php
  ?uf=SP&municipio=3550308&inicio=2026-05-23 00:00:00&fim=2026-05-23 23:59:59
```

### Campos retornados

| Campo | Significado | Uso no sistema |
|---|---|---|
| `codestacao` | Código do pluviômetro | Rastreabilidade |
| `municipio` | Nome do município | Filtro |
| `uf` | Unidade da federação | Filtro |
| `datahora` | Data e hora da medição | Rastreabilidade |
| `valorMedida` | Volume de chuva no período (mm) | Classificação de risco |
| `latitude` / `longitude` | Coordenadas do pluviômetro | Georreferenciamento |

### Viabilidade
- **Positivo:** foco específico em municípios de risco, dados de pluviômetros automáticos distribuídos, gratuito e sem autenticação
- **Negativo:** documentação muito limitada (não há swagger ou guia oficial de integração), estrutura do JSON varia entre consultas, URL não é um endpoint REST formal, pode mudar sem aviso
- **Conclusão preliminar:** fonte com alto valor institucional, porém com complexidade de integração elevada. Recomendado para versão futura do sistema, não para o protótipo inicial.

---

## 3. Comparativo INMET × CEMADEN × OpenWeather

| Critério | INMET | CEMADEN | OpenWeather |
|---|---|---|---|
| Autenticação | Token (cadastro) | Não exige | Chave API (cadastro) |
| Formato | JSON padronizado | JSON (variável) | JSON padronizado |
| Documentação | Boa (portal oficial) | Muito limitada | Extensa (OpenAPI) |
| Cobertura geográfica | Nacional (estações) | Municípios de risco | Global |
| Latência dos dados | Até 1h | ~15 min | Tempo real |
| Foco em precipitação | Sim | Sim (especializado) | Sim |
| Facilidade de integração | Média | Baixa | Alta |

---

## 4. Conclusão do Levantamento

Para o protótipo do TCC, as APIs brasileiras (INMET e CEMADEN) apresentam valor institucional significativo, mas ambas oferecem barreiras de integração maiores que a OpenWeather. A principal limitação do INMET é a dependência de estações físicas próximas ao ponto de interesse. A principal limitação do CEMADEN é a ausência de documentação formal e a estrutura de endpoint não padronizada.

Ambas permanecem como fontes candidatas para validação cruzada em versões futuras do sistema.
