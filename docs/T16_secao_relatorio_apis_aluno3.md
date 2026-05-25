# Seção: Estudo e Comparação das APIs Utilizadas — Contribuição Aluno 3

---

## 3.X.6 APIs Públicas Brasileiras: INMET e CEMADEN

No processo de levantamento de fontes de dados meteorológicos para o sistema, foram
avaliadas duas APIs de origem institucional brasileira: o INMET (Instituto Nacional de
Meteorologia) e o CEMADEN (Centro Nacional de Monitoramento e Alertas de Desastres Naturais).

O INMET disponibiliza dados por meio de API pública acessível em `apitempo.inmet.gov.br`,
com endpoints que permitem consultar dados horários por estação, listar todas as estações
cadastradas em um estado e obter condições climáticas aproximadas a partir de coordenadas
geográficas. O acesso exige autenticação via token de usuário, obtido gratuitamente mediante
cadastro no portal institucional. Os dados retornados incluem campos como `CHUVA`
(precipitação acumulada em mm), `TEM_INS` (temperatura instantânea) e `UMD_INS`
(umidade relativa), em formato JSON padronizado.

Durante os testes realizados no ambiente de desenvolvimento, o endpoint de listagem de
estações retornou código HTTP 403, indicando bloqueio por política de acesso da API
fora do domínio autorizado. Esse comportamento é documentado como limitação conhecida
da API do INMET em ambientes externos, sendo necessário o cadastro de IP ou domínio
autorizado para integração em produção. O levantamento das estações próximas ao Grande ABC
paulista identificou as unidades de Santo André (cód. A771), São Bernardo do Campo (cód. A743)
e São Paulo Mirante (cód. A701) como as mais relevantes para o escopo do sistema.

O CEMADEN disponibiliza dados de pluviômetros automáticos distribuídos em municípios
classificados como de risco. O acesso é feito por meio de endpoint informal sem documentação
oficial, com estrutura de consulta por UF e código IBGE do município. Testes realizados com
o código de Santo André (IBGE: 3547809) evidenciaram a viabilidade da consulta quando
executada diretamente em ambiente externo, retornando leituras horárias de precipitação com
campos de latitude e longitude dos pluviômetros. Os resultados indicaram leituras de até
3,60 mm/h no período avaliado, consistentes com o evento de chuva registrado na mesma
janela temporal pela OpenWeather.

A principal limitação do CEMADEN para integração no protótipo é a ausência de documentação
formal e a instabilidade do endpoint, que não segue convenções REST. A URL não conta com
versionamento e pode ser descontinuada sem aviso prévio, representando risco para a
manutenção do sistema a longo prazo.

---

## 3.X.7 Modelagem Preliminar dos Dados

A partir dos campos identificados nas APIs avaliadas e nos dados de cadastro definidos pelo
Aluno 2 (Tarefa 13), foi elaborado um modelo preliminar de banco de dados para o protótipo.

A tabela central, denominada `ocorrencias`, consolida registros provenientes de três origens
distintas: inserção pelo usuário via aplicativo, captura automática pela OpenWeather API e
ingestão futura de dados de estações INMET ou CEMADEN. O campo `fonte` garante a
rastreabilidade de cada registro, aspecto relevante para a análise de confiabilidade dos dados
em estudos futuros.

Os campos de georreferenciamento — `latitude` e `longitude` — estão presentes em todos os
registros, independentemente da origem, permitindo a exibição unificada no mapa do aplicativo.
O campo `nivel_risco`, central para a funcionalidade de alerta do sistema, pode ser gerado
automaticamente pelo backend a partir do volume de precipitação (`chuva_mm`) segundo as
faixas definidas na Tarefa 12, ou pode ser informado diretamente pelo usuário no formulário
de ocorrência.

O banco adotado no protótipo é o SQLite, pela facilidade de configuração em ambiente de
desenvolvimento. A migração para PostgreSQL com a extensão PostGIS está prevista para a
fase de produção, possibilitando o uso de consultas geoespaciais nativas como cálculo de
distância entre pontos e agrupamento de ocorrências por área.

---

## 3.X.8 Comparativo Final das Fontes de Dados

| Critério | OpenWeather | INMET | CEMADEN |
|---|---|---|---|
| Autenticação | Chave API (simples) | Token cadastrado | Não exige |
| Formato | JSON padronizado | JSON padronizado | JSON (variável) |
| Documentação | Extensa | Boa | Muito limitada |
| Cobertura | Global | Nacional (estações) | Municípios de risco |
| Latência | Tempo real | Até 1 hora | ~15 min |
| Integração no protótipo | ✅ Adotada | ⏳ Trabalho futuro | ⏳ Trabalho futuro |

As fontes brasileiras permanecem como candidatas para versões futuras do sistema,
especialmente para validação cruzada dos dados de precipitação e para aumentar a aderência
a fontes institucionais nacionais.

---

*Seção redigida com base nos levantamentos realizados em 23–24/05/2026.
Arquivos de resultado disponíveis em `testes-api/` no repositório do projeto.*
