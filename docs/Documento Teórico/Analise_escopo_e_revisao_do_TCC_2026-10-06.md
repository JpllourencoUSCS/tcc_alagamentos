# Análise de escopo, revisão do documento teórico e dos pontos do orientador

*06/10/2026 — preparado para o grupo (Henrique, João, Marlon, Guilherme) e para a conversa
com o orientador. Base: código do repositório, `docs/CRONOGRAMA_STATUS.md`,
`TCC_Alagamentos_Versao_Consolidada_Orientador_2026.docx` (aqui chamado de "documento
teórico"), `para completar o tcc.docx` (os "15 pontos") e
`Template_USCS_TCC_Computacao-versao-2026-2.pdf` (o "template").*

**Prazo:** fim da próxima semana — tratado aqui como **sexta, 16/10/2026** para a entrega,
com o fim de semana (17–18/10) como margem. São ~8 dias úteis.

---

## 1. Resumo

1. **O sistema está praticamente pronto; o documento não.** O backend, o banco, o modelo de
   risco, o benchmark, as medições de latência e o app integrado à API existem e foram
   testados (61 testes automatizados no backend, 6 no app, 21 casos no plano PT-001). Já o
   documento teórico continua escrito como **proposta** (tudo no futuro: "será", "deverá")
   e não tem os capítulos que o template exige para o TCC concluído — **Desenvolvimento
   (com implementação e telas), Testes e Conclusão**. Esse é o maior trabalho da semana.
2. **Há divergências entre o documento e o sistema** que a banca vai notar: fontes citadas
   que não usamos (Open-Meteo, INMET, CEMADEN), a ANA ausente do texto, quatro faixas de
   risco no texto contra três no sistema, entidades de banco que não existem, View Binding
   que o app não usa, numeração de requisitos diferente entre documento e plano de testes.
3. **Três pontos técnicos fracos para a banca**, com correção rápida:
   - **Fusão:** hoje cada fonte cobre um critério diferente; não há duas fontes medindo a
     mesma variável, logo não existe a "regra de fusão" que o ponto 3 do orientador pede.
     *(Atualização de 06/10, à noite: o CPTEC foi substituído pelo INMET — previsão textual
     e avisos oficiais —, o que mantém duas fontes meteorológicas (OpenWeather + INMET,
     atende o RF04). Mas o INMET é qualitativo: a fusão de uma mesma variável numérica
     continua dependendo da Open-Meteo.)*
   - **Pesos do AHP:** o T15 registra que os pesos foram escolhidos por julgamento direto e
     a matriz foi reconstruída depois; e os pesos usados (35/25/25/15) diferem do autovetor
     (42,4/22,7/22,7/12,2). O próprio documento teórico (2.9) alerta contra isso.
   - **Colaborativo:** o mínimo de 2 relatos conta relatos, não usuários — um único usuário
     com dois relatos altera o risco da região (exatamente o risco do ponto 7).
4. **Ajuste de escopo recomendado (validar com o orientador):** retirar a ANA e a estação
   da USCS; incluir a **Open-Meteo** (testada em 06/10: responde sem chave, com precipitação
   atual e horária) como segunda fonte, o que permite uma **regra de fusão real**; refazer o
   AHP com 3 critérios usando **os mesmos julgamentos** já registrados (pesos 54/30/16,
   CR = 0,0079, usados sem ajuste manual); manter o CPTEC só se voltar a responder.

---

## 2. Situação do projeto

### 2.1 Concluído e testado

| Parte | Evidência |
|---|---|
| API REST (FastAPI): ocorrências (criar, listar com filtros de fonte/nível/período/região, obter) e `GET /risco` | `backend/api/`, 61 testes (`backend/tests/`) |
| Banco PostgreSQL 16 + PostGIS 3.4: `geom` Point SRID 4326 por *trigger*, índice GiST, 3 tabelas | `backend/db/schema.sql` |
| Modelo de risco (AHP, 4 critérios, CR = 0,0038), normalização pela intensidade de chuva, redistribuição de pesos de fonte ausente | `backend/algoritmo_risco.py`, T15 |
| Agregação colaborativa (1 km, 3 h, mínimo de 2 relatos, ponderação por tempo e distância) | `backend/servicos/colaborativo.py`, T15 §6.4 |
| Fusão em paralelo, cache de 10 min, HTTP 503 se o OpenWeather falhar | `backend/fusao_climatica.py` |
| Análise de sensibilidade dos pesos (1.400 cenários) | `backend/analise_sensibilidade.py`, T15 §8.1 |
| Benchmark GiST (1k, 10k, 100k e 1M; mediana/média/dp; plano de execução registrado) + `CLUSTER` | `backend/benchmark/resultados/`, `T16_secao_benchmark.md` |
| Latência ponta a ponta + critérios (RNF de T19), todos atendidos | `T19_criterios_desempenho.md` |
| App Android (Kotlin/XML) integrado à API real: login, alertas com filtros, detalhes, cadastro (manual e automático), risco atual, ajustes/perfil, notificação local | `android/`, `docs/evidencias_testes/2026-10-03/` |
| Plano de testes PT-001 v1.1 (21 casos) | `docs/plano_e_fluxo_de_testes_TCC.xlsx` |
| Rascunhos de seção do relatório (arquitetura, app, metodologia de testes, benchmark, resultados, APIs, algoritmo) | `docs/T16_secao_*.md` |

### 2.2 Pendente — dá para concluir até 16/10

| Pendência | Responsável sugerido | Depende de |
|---|---|---|
| **Reescrever o documento teórico no template** (ver seções 3 e 5) | todos; João consolida | rascunhos T16 (prontos) |
| **Testes de usabilidade** (5–8 participantes, protocolo e TCLE prontos) | Marlon conduz, Guilherme consolida | data; mapa liberado |
| Liberar o SHA-1 `35:BA:18:CE:CD:B4:F8:85:29:AD:A2:8B:4B:09:20:C8:57:D3:6B:72` na chave do Google Maps (Google Cloud → Credenciais → restrições de app Android) | quem criou a chave (provavelmente Marlon) | **Feito em 07/10** (pelo João): mapa funcionando, CT-MAP-001/002 executados e capturas refeitas |
| Ajustes de escopo da seção 4 (Open-Meteo + fusão, AHP 3 critérios, deduplicação do colaborativo) | backend (João/Henrique) | aprovação do orientador |
| Completar o benchmark com as consultas que o documento promete (raio com `ST_DWithin`, vizinhos mais próximos, `EXPLAIN (ANALYZE, BUFFERS)`) e percentis | Henrique | — |
| Separar a latência por etapa dentro da API (fontes externas, banco, cálculo do índice) — ponto 13 | Henrique | — |
| Corrigir o firewall do notebook com Docker; primeiro push (para o CI rodar) | João | administrador — **push feito em 07/10**: primeiro CI aprovado (backend e app); firewall ainda pendente |
| Slides (roteiro pronto em `docs/roteiro_apresentacao.md`) | Marlon, Guilherme | resultados finais |
| Conferir as citações pendentes (`docs/referencias_consolidadas.md`), incluindo a origem dos limiares de chuva | Guilherme | — |

### 2.3 Não concluído — e por quê

| Item | Motivo | Como documentar |
|---|---|---|
| **ANA** como pluviômetro local | Cadastro pedido em agosto (`hidro@ana.gov.br`); nenhuma resposta até 06/10. Acesso exige credencial. | Ajuste de escopo: fonte retirada por indisponibilidade de acesso; integração implementada e testada estruturalmente, mas não validada com dado real. |
| **Estação meteorológica da USCS** | Investigação aberta em 03/09, sem resposta dos responsáveis; não há interface programática confirmada. | Retirada; citar como trabalho futuro. |
| **CPTEC/INPE** (validação qualitativa) | Todos os endpoints respondem HTTP 403 desde 03/10 (06/10 inclusive); a BrasilAPI, que consulta o mesmo serviço, também falhou. | **Resolvido em 06/10:** substituído pela API de previsão do INMET (`apiprevmet3`, levantamento do João) — previsão por município e avisos oficiais, no mesmo papel qualitativo, fora do AHP. Implementado, testado (82 testes) e visível no app. |
| Comparação de consistência entre fontes (S5) | Exigia duas fontes da mesma variável; com ANA e CPTEC indisponíveis, não havia par. | Resolvido se a Open-Meteo entrar (seção 4). |
| Hospedagem em nuvem | Não decidida; não é requisito do MVP. | Ambiente controlado (Docker); imagem pronta para hospedar. |
| Notificação com o app fechado (*push*) | Exige serviço de *push*; fora do escopo do MVP. | Limitação + trabalho futuro. |
| Autenticação real de usuários | Fora do escopo desde o TCC I. | Já declarado. |
| Lista de bugs dos testes internos do Marlon (S8) | Nunca repassada ao repositório. | Se não vier, registrar que os testes internos não tiveram registro formal. |
| Latência em rede móvel real | Cliente e servidor medidos na mesma máquina. | Limitação (T19 §6). |
| Validação dos pesos por especialistas | Sem acesso a especialistas no prazo. | Limitação; análise de sensibilidade como mitigação. |

---

## 3. Revisão do documento teórico

### 3.1 Problema central

O documento é uma **versão-base de proposta**: a própria "Nota de consolidação" diz que ele
"não antecipa resultados de implementação". Hoje os resultados existem. É preciso:

1. **Passar do futuro para o passado** tudo o que foi feito, separando sempre, como pede o
   orientador, *proposto* × *implementado* × *testado* × *demonstrado pelos resultados*.
2. **Acrescentar os capítulos que faltam no template** — Desenvolvimento (requisitos,
   cronograma em Gantt, arquitetura, banco, implementação com telas e link do GitHub),
   Testes (planos e cenários, com resultados) e Conclusão.
3. **Alinhar o texto ao sistema real** (tabela 3.3).

### 3.2 Conformidade com o template USCS

| Elemento do template | No documento teórico | Ação |
|---|---|---|
| Capa: "Universidade Municipal de São Caetano do Sul / Escola de Tecnologias da USCS / Curso Superior de Graduação em Ciência da Computação", autores, título, "São Caetano do Sul – SP", ano | Só "UNIVERSIDADE... – USCS / CURSO DE CIÊNCIA DA COMPUTAÇÃO"; cidade sem "– SP" | Ajustar ao modelo |
| Folha com nomes e **RA** de cada autor | Ausente | Incluir |
| Folha de rosto: "...como requisito parcial para a obtenção do Título de Bacharel em Ciência da Computação. Orientador: Prof. [Titulação] [Nome]" | "como requisito acadêmico" | Usar a frase do template |
| Ficha catalográfica | Ausente | Incluir (o template cita "Escola Politécnica da USCS" na ficha e "Escola de Tecnologias" na capa — confirmar com a coordenação qual usar) |
| Página da reitoria/gestão do curso | Ausente | Incluir |
| Folha de aprovação (banca) | Ausente | Incluir |
| Dedicatória, agradecimentos, epígrafe | Ausentes | Agradecimentos recomendados; os outros são opcionais |
| Resumo / Abstract: objetivo, método, **resultados e conclusões**; palavras-chave separadas por **ponto** | Sem resultados (futuro); palavras-chave separadas por ponto e vírgula | Reescrever com resultados; trocar separador |
| Listas de ilustrações, tabelas, abreviaturas e siglas, símbolos | Ausentes | Incluir (siglas: AHP, API, CR, GiST, IRA, PostGIS, RNF, SRID...) |
| Sumário | Ausente | Incluir |
| Título com até 15 palavras, formato "TÍTULO: subtítulo" | 18 palavras, sem subtítulo | Sugestões abaixo (validar com o orientador) |
| Capítulos: 1 Introdução (Objetivos, Justificativa, Delimitação); 2 Referencial Teórico; 3 Pesquisa/Amostragem; 4 Desenvolvimento (4.1 Requisitos, 4.2 Cronograma em Gantt com papéis, 4.3 Arquitetura, 4.4 Banco de dados, 4.5 Implementação com telas e link do GitHub); 5 Testes (5.1 Planos, 5.2 Cenários); 6 Conclusão | 1 Introdução; 2 Fundamentação; 3 Metodologia; 4 Levantamento bibliográfico e estudo tecnológico; 5 Proposta da solução — **sem Testes e sem Conclusão** | Reorganizar (mapa na seção 3.5) |
| "Nota de consolidação e premissas adotadas" | Antes do Resumo | Não é elemento do template: retirar; o conteúdo vai para a Delimitação e a Metodologia |

**Sugestões de título (≤ 15 palavras):**
- *Risco de alagamento urbano: sistema colaborativo com fusão de dados meteorológicos e PostGIS* (13 palavras)
- *Alagamentos em São Caetano do Sul: classificação colaborativa de risco com dados georreferenciados* (13 palavras)

### 3.3 Divergências entre o documento e o sistema implementado

| Onde | O documento diz | O sistema tem | Ação recomendada |
|---|---|---|---|
| Nota, 1.3, 4.2, 5.3 (RF04) | Fontes candidatas: OpenWeather, **Open-Meteo**, INMET, CEMADEN, CPTEC; pelo menos duas integradas | OpenWeather (ativa), **ANA** (não citada no texto; sem credencial), CPTEC (403), relatos colaborativos; INMET e CEMADEN descartados em agosto | Tabela final de fontes com situação e motivo de cada uma; com o ajuste da seção 4, OpenWeather + Open-Meteo integradas |
| 2.8, 4.7 | Modelo canônico com provedor, instante de referência, **instante de coleta, unidade, qualidade/status**; regra explícita para divergências | Estrutura com os valores e o nome da fonte; sem instantes, unidade ou status; **sem regra de divergência** (não há duas fontes da mesma variável) | Implementar com a Open-Meteo (seção 4) ou reescrever 2.8/4.7 conforme o que existe |
| 2.9, 5.6 | AHP opcional; "não usar para dar aparência científica"; faixas **baixo, moderado, alto e crítico**; versão de pesos guardada com o cálculo; componentes candidatos incluem precipitação **acumulada** e **histórico local** | AHP com 4 critérios, pesos ajustados manualmente; **3 faixas** (Baixo/Médio/Alto); versão de pesos **não** guardada; componentes: precipitação atual, pluviômetro, previsão, colaborativo | Fórmula final real (T15/T16); 3 faixas; versão dos pesos registrada (seção 4) |
| 5.6 | Degradação por **renormalização** dos pesos disponíveis | Colaborativo: redistribuição proporcional ✔; ANA: divisão fixa 60/40 entre precipitação e previsão | Some se a ANA sair (seção 4); senão, descrever as duas regras |
| 2.6, 3.8, 5.7, Apêndice A | Benchmark com raio (`ST_DWithin`), interseção com área, vizinhos mais próximos, `EXPLAIN (ANALYZE, BUFFERS)`, percentis | Filtro por retângulo (`&&` + `ST_MakeEnvelope`) e contagem; sem `BUFFERS`; mediana, média e desvio | Completar o benchmark (cerca de meio dia) **ou** ajustar o texto |
| 2.10, 4.3 | "View Binding será preferido" | O app usa `findViewById` | Retirar a frase (não vale refatorar agora) |
| 5.3 / PT-001 | RF01 mapa, RF02 registrar, ..., RF10 detalhes | Planilha PT-001: RF-01 cadastro, RF-02 listagem, RF-03 mapa, ..., RF-09 algoritmo | **Unificar a numeração** e criar a matriz requisito → critério de aceitação → caso de teste → resultado |
| 5.4 / T19 | RNF01–RNF08 (plataforma, OpenAPI, SRID...) | T19 usa RNF-01 a RNF-05 para desempenho | Unificar numa só lista (ex.: RNF01–RNF08 do documento + RNF09–RNF13 de desempenho) |
| 5.5 | Entidades Usuário, Ocorrência, ObservaçãoMeteorológica, Fonte, CálculoIRA, ExecuçãoBenchmark | Tabelas `ocorrencias`, `estacoes_referencia`, `reportes_colaborativos_agregado`; perfil só no aparelho | DER real (template 4.4); incluir `calculos_risco` se o ajuste da seção 4 for feito |
| RF07, RF09 | Histórico de classificações e proveniência dos dados usados no cálculo | A ocorrência guarda nível, chuva e fonte; os componentes do cálculo não ficam registrados | Registrar cada cálculo (seção 4) |
| 3.11 | Cronograma com homologação em 07/11 | Prazo agora é 16/10; cronograma real em `CRONOGRAMA_STATUS.md` | Gantt do que foi executado, com papéis (template 4.2) |
| 4.6 | "O mapa poderá utilizar Google Maps SDK" | Usa | Passar para o passado |
| 1.6 | "cinco seções primárias... resultados incorporados posteriormente" | — | Reescrever conforme a estrutura final (6 capítulos) |
| Referências | PostgreSQL **18** Documentation | O sistema usa PostgreSQL **16** | Citar a versão 16 |
| Referências | Sem Saaty, Guttman, Hellerstein, Nielsen, Dean e Barroso, ISO/IEC 25010, Peffers (este já está) | Usados nas seções novas | Incorporar de `docs/referencias_consolidadas.md` |
| 2.2.1/IRA | — | Os limiares de chuva (2,5/7,6/50 mm/h) são atribuídos à OMM no código e no T15; o 7,6 mm/h parece vir da American Meteorological Society | Conferir e citar corretamente (não muda o modelo) |

### 3.4 Observações por capítulo

- **Resumo e Abstract:** reescrever com resultados: 81,6× de ganho com GiST em 100 mil
  registros; leituras com p95 abaixo de 17 ms com 1 milhão de registros; cadastro com risco
  automático em ~0,5 s sem cache; usabilidade (média Likert); fontes efetivamente
  integradas; limitação da ANA.
- **1 Introdução:** o texto é bom. Ajustar: 1.4.2 (objetivos específicos) — marcar o que foi
  atingido no capítulo de conclusão; 1.5 (Delimitação) — incluir a área de estudo
  (São Caetano do Sul, cerca de 15 km² e 165 mil habitantes — conferir no IBGE), a
  justificativa da escolha e os ajustes de escopo (ANA, estação da USCS, CPTEC).
- **2 Referencial Teórico:** sólido e bem referenciado. Faltam: fundamentação do AHP
  (Saaty: matriz, autovetor, CR) — hoje só condicional ("caso seja utilizado"); R-tree/GiST
  (Guttman; Hellerstein et al.); limites de tempo de resposta (Miller, Card, Nielsen) que
  embasam os RNF; e trabalhos correlatos **concretos** em 2.13 (a tabela atual compara
  categorias genéricas). Candidatos a verificar: CGE da Prefeitura de São Paulo, relatos
  de alagamento no Waze, alertas da Defesa Civil por SMS (40199), e estudos de
  *crowdsourcing* já citados (Helmrich et al., 2021; Songchon et al., 2021).
- **3 Pesquisa/Amostragem:** DSR bem colocada. Atualizar 3.7 (o protocolo do índice foi
  executado — análise de sensibilidade), 3.8 (benchmark executado; descrever o que de fato
  foi medido), 3.9 (usabilidade: número de participantes, perfil, tarefas, critério ≥ 4).
- **4 Levantamento tecnológico:** hoje é a mistura de "estudo tecnológico" com decisões.
  No template, o conteúdo se divide entre o Referencial Teórico (2) e o Desenvolvimento (4).
  A tabela 4.2 precisa virar a tabela final de fontes.
- **5 Proposta da solução:** vira o capítulo **4 Desenvolvimento**, no passado, com DER,
  diagrama de arquitetura (figura), fórmula final do índice, consultas espaciais com
  exemplos de SQL, telas do app e link do repositório.
- **Faltam inteiros:** capítulo de **Testes** (base: `T16_secao_metodologia_testes.md`,
  `T16_secao_benchmark.md`, T19) e **Conclusão** (resposta explícita à questão de pesquisa
  da seção 1.2, objetivos atingidos, limitações, trabalhos futuros — base:
  `T16_secao_resultados_discussao.md`).
- **Apêndices:** substituir o "Apêndice A — checklist" pelos anexos reais: plano PT-001,
  roteiro e questionário de usabilidade, TCLE, especificação OpenAPI (gerada pelo FastAPI
  em `/openapi.json`), tabelas completas do benchmark.

### 3.5 Mapa: o que já está escrito → capítulo do template

| Capítulo do template | Fonte do conteúdo |
|---|---|
| 1 Introdução | Documento teórico 1.1–1.6 (ajustado) |
| 2 Referencial Teórico | Documento teórico 2.x + T15 (AHP), T17 (GiST), T19 §2 (tempo de resposta) |
| 3 Pesquisa/Amostragem | Documento teórico 3.x (DSR) + área de estudo + ajustes de escopo |
| 4.1 Requisitos | Documento teórico 5.3/5.4 + T19 (unificados, com critérios de aceitação) |
| 4.2 Cronograma | `CRONOGRAMA_STATUS.md` → Gantt com responsáveis |
| 4.3 Arquitetura | `T16_secao_arquitetura.md` (redesenhar a figura) |
| 4.4 Banco de dados | `backend/db/schema.sql`, T18 → DER + consultas espaciais |
| 4.5 Implementação | `T16_secao_algoritmo_risco.md`, `T16_secao_relatorio_apis.md`, `T16_secao_app_android.md`, `docs/capturas/`, link do GitHub |
| 5 Testes | `T16_secao_metodologia_testes.md`, `T16_secao_benchmark.md`, T19, PT-001, resultados de usabilidade |
| 6 Conclusão | `T16_secao_resultados_discussao.md` + resposta à questão de pesquisa |

---

## 4. Ajustes de escopo recomendados (para validar com o orientador)

O orientador autorizou ajustar o escopo documentando o motivo. A recomendação é ajustar
o mínimo necessário e, ao mesmo tempo, fechar os três pontos fracos da seção 1.

| # | Ajuste | Motivo documentado | Esforço | Efeito |
|---|---|---|---|---|
| A | **Retirar a ANA** | Sem resposta ao pedido de acesso desde agosto | Baixo | Remove um critério que nunca teve dado real |
| B | **Retirar a estação da USCS** | Sem resposta; sem interface programática | Nenhum | Encerra uma pendência aberta |
| C | **Incluir a Open-Meteo** como segunda fonte meteorológica | Gratuita, sem chave, documentada (já citada no documento teórico como candidata); testada em 06/10 com sucesso para São Caetano do Sul | ~1 dia (backend + testes + texto) | Mantém "pelo menos duas fontes" (RF04) e permite **fusão de verdade**: duas medidas da mesma variável |
| D | **Regra de fusão explícita** para precipitação atual e previsão: com as duas fontes disponíveis, usar a **maior** delas (critério conservador, adequado a alerta) e registrar a divergência quando ela passar de um limiar; com uma só, usar a disponível e indicar confiança reduzida; com nenhuma, não calcular (HTTP 503) | Responde ao ponto 3 | Incluído em C | Algoritmo reproduzível e documentável |
| E | **AHP com 3 critérios** (precipitação atual, previsão, colaborativo), com os **mesmos julgamentos** de T15: pesos **54 / 30 / 16**, CR = 0,0079, usados **sem ajuste manual** | Sem a ANA, o critério "pluviômetro local" fica permanentemente vazio; e elimina a crítica do ajuste manual | Baixo | Simulação em 280 cenários: 6,8% mudam de classe em relação ao comportamento atual sem ANA (diferença média de 1,8 ponto) |
| F | **Deduplicar relatos por usuário** no colaborativo (contar no máximo um relato — o mais recente — por usuário) | Fecha a brecha do ponto 7 | ~2 horas | Um usuário sozinho deixa de alterar o risco |
| G | **Registrar cada cálculo** (componentes, pesos, versão dos pesos, fontes, instantes) numa tabela `calculos_risco` | RF07/RF09 e ponto 4 (reprodutibilidade) | ~meio dia | Rastreabilidade de cada classificação |
| H | ~~CPTEC: manter com *fail-safe*~~ **Feito em 06/10:** CPTEC substituído pelo INMET (previsão + avisos oficiais) | 403 desde 03/10 | Feito | Mantém duas fontes meteorológicas (RF04) |
| I | **Feito em 07/10 (decisão do grupo):** avisos de chuva vigentes do INMET funcionam como **piso** da classe, no nível de risco de alagamento declarado pelo INMET: Perigo → Médio; Grande Perigo → Alto; Perigo Potencial → sem piso | Em 06/10 o app mostrou risco Baixo com um aviso de "Tempestade — Perigo Potencial" ativo | Feito | Pesos e score inalterados; T15 §6.5 |

**Observação sobre os pesos:** o `CLAUDE.md` registra os pesos 35/25/25/15 como decisão
fechada que só muda com pedido explícito. O ajuste E precisa da concordância do grupo e do
orientador.

---

## 5. Avaliação dos 15 pontos do orientador

**Os pontos estão corretos e bem priorizados.** Duas correções factuais: no ponto 2, a lista
de fontes ("OpenWeather, INMET, CEMADEN, Open-Meteo") está desatualizada — INMET e CEMADEN
foram testados e descartados em agosto, e a ANA e o CPTEC entraram no lugar; no ponto 5, o
exemplo de pesos ("chuva 40%, colaborativo 20%") não corresponde aos nossos (35% e 15%), e
a escolha do AHP já está fechada (não é mais "AHP ou método similar").

| # | Ponto | Situação hoje | Evidência | O que falta |
|---|---|---|---|---|
| 1 | Área geográfica | ✅ Definida: São Caetano do Sul | Escopo de 03/09; bbox no app/benchmark; dados de demonstração | Extensão, população e justificativa da escolha no texto |
| 2 | Fontes efetivamente usadas | 🟡 (06/10: INMET no lugar do CPTEC) | T_arquitetura, `T16_secao_relatorio_apis.md` | Tabela final com variáveis, frequência, resolução e limitações; decidir o escopo (seção 4) |
| 3 | Regra de fusão | 🔴 **Não existe** como regra de divergência | — | Ajustes C e D |
| 4 | Definição matemática do índice | 🟡 Completa no código e no T15/T16 | `algoritmo_risco.py`, T15 | Levar a fórmula completa (normalização por faixas, pesos, redistribuição, faixas, exemplo numérico) para o documento; adotar o nome IRA de forma consistente |
| 5 | Justificativa dos pesos | 🟡 AHP documentado, mas com matriz reconstruída e pesos ajustados | T15 §4–5 | Ajuste E, ou declarar com honestidade que os pesos são julgamento da equipe e o AHP verifica a coerência |
| 6 | Validação e sensibilidade | 🟡 Sensibilidade dos **pesos** feita | T15 §8.1 | Cenários controlados por **variável** (o índice cresce quando a chuva cresce etc.) — testes de monotonicidade, ~1 hora |
| 7 | Tratamento dos colaborativos | 🟡 Validade 3 h, raio 1 km, mínimo 2, ponderação | T15 §6.4 | Ajuste F; registrar o que **não** foi feito (confirmação por outros usuários, reputação) como limitação |
| 8 | Modelo de dados definitivo | 🟡 Implementado | `schema.sql`, T18 | DER (figura), SRID, *geometry* × *geography*, índices e política de histórico no texto |
| 9 | Consultas espaciais implementadas | 🟡 `&&`/`ST_MakeEnvelope` (região), `ST_DWithin` + `ST_Distance` em *geography* (colaborativo), `ST_Buffer`, `ST_Expand` | `repository.py`, `colaborativo.py` | Documentar com SQL de exemplo; vizinhos mais próximos não implementado (opcional) |
| 10 | Arquitetura e fluxo completo | 🟡 | `T16_secao_arquitetura.md` | Diagrama em figura, com os fluxos de erro (503, *fail-safe*) |
| 11 | RF/RNF verificáveis | 🟡 Listas existem em três lugares com numerações diferentes | Documento 5.3/5.4, PT-001, T19 | Lista única com critério de aceitação e matriz de rastreabilidade |
| 12 | Benchmark completo | ✅ Feito (1k–1M, com/sem GiST, aquecimento, repetições, plano) | `T16_secao_benchmark.md` | `BUFFERS`, percentis e as consultas de raio/vizinhos prometidas no texto |
| 13 | Latência por etapa | 🟡 Banco (EXPLAIN), API total e com/sem cache | T19 | Medir dentro da API o tempo de cada etapa (fontes externas, banco, cálculo do índice) |
| 14 | Protocolo e resultados de testes | 🟡 Protocolo e testes funcionais/integração/falhas prontos | PT-001, `T16_secao_metodologia_testes.md` | **Resultados de usabilidade** |
| 15 | Resultados, discussão, questão de pesquisa | 🟡 Rascunho | `T16_secao_resultados_discussao.md` | Resposta explícita à questão de pesquisa (seção 1.2), comparação com correlatos concretos, usabilidade |

**O que falta na lista do orientador:**
1. **Adequação ao template** — capítulos de Testes e Conclusão, Gantt, telas e link do
   GitHub, elementos pré-textuais (seção 3.2).
2. **Documentar os ajustes de escopo** (ANA, estação da USCS, CPTEC, Open-Meteo) como
   decisões metodológicas, com data e motivo.
3. **Ética e dados de demonstração:** deixar claro no texto que os testes do app e a
   usabilidade usaram ocorrências de demonstração (já corrigido no TCLE e no questionário).
4. **Acesso da banca ao código:** o template pede o link do GitHub
   (`github.com/JpllourencoUSCS/tcc_alagamentos`); confirmar que o repositório está
   acessível à banca (público ou com convite).
5. **Apêndices reais** (PT-001, OpenAPI, questionário, TCLE, tabelas do benchmark).
6. **Origem dos limiares de chuva** (OMM × American Meteorological Society).

---

## 6. Plano até a entrega

| Dia | Tarefa | Quem |
|---|---|---|
| **Qua 07/10** | Validar com o orientador os ajustes da seção 4 e o título; liberar o SHA-1 na chave do Maps (feito em 07/10); marcar as sessões de usabilidade; corrigir o firewall; push | João (orientador), Marlon (chave) |
| **Qua 07 – Qui 08/10** | Implementar os ajustes aprovados (C, D, E, F, G), latência por etapa, benchmark complementar; testes; atualizar T15/T16 | Backend (Henrique/João) |
| **Qua 07 – Seg 12/10** | Reescrever o documento no template: elementos pré-textuais, capítulos 1–3 ajustados, capítulo 4 (Desenvolvimento) e 5 (Testes) a partir dos T16 | Todos, por capítulo; João consolida |
| **Sex 09 – Seg 12/10** | Sessões de usabilidade (5–8 participantes) e consolidação | Marlon, Guilherme |
| **Ter 13/10** | Resultados de usabilidade no texto; Conclusão; Resumo/Abstract com resultados; correções de interface pequenas | João, Marlon |
| **Qua 14/10** | Revisão cruzada (números × CSVs/planilha), ABNT, referências, listas, sumário | Henrique, João (técnica); Guilherme (ABNT) |
| **Qui 15/10** | Slides e ensaio | Marlon, Guilherme |
| **Sex 16/10** | Entrega | — |

---

## 7. Decisões necessárias agora

1. **Escopo:** aprovar os ajustes A–G (principalmente C/D — Open-Meteo e fusão — e E —
   pesos). Os ajustes H (INMET no lugar do CPTEC, 06/10) e I (avisos do INMET como piso,
   07/10) já foram feitos.
2. **Título** (≤ 15 palavras).
3. **Data e local da usabilidade** e quem libera a chave do Maps.
4. **Formato do documento final:** reescrever em Word a partir do `.docx` atual ou partir do
   template oficial (se houver versão .docx/LaTeX do template, usá-la).
