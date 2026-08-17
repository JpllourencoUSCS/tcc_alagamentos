# Cronograma de Implementação — TCC II

**Sistema de Monitoramento Colaborativo de Áreas com Risco de Alagamento**
Período: 01/07/2026 a 30/10/2026 (17 semanas)
*Última atualização de status: 13/08/2026*

## Legenda de responsáveis
- **Henrique** — backend / tech lead
- **João** — integração / full stack
- **Marlon** — Android / documentação
- **Guilherme** — Android / tarefas bem delimitadas

## Legenda de status (tarefas do João)
- ✅ Concluída
- 🟡 Em andamento / parcialmente bloqueada
- 🔴 Atrasada ou não iniciada

---

## FASE 1 — Replanejamento Técnico (01/07 a 14/07)

### Semana 1 (01/07 – 05/07)
| Responsável | Atividade | Status (João) |
|---|---|---|
| Henrique | Levantamento técnico de indexação espacial (GiST/R-tree) em PostGIS — base teórica para o benchmark futuro | |
| João | Pesquisa e definição do modelo de classificação de risco por pesos (AHP ou método similar) — base teórica | ✅ Concluída |
| Marlon | Estudo de migração de Jetpack Compose para Android Views (XML) — telas já planejadas | |
| Guilherme | Estudo de Android Views (XML) em conjunto com Marlon — foco em componentes simples (formulários, listas) | |

**Entregável da semana:** documento de decisão técnica registrando a saída do Compose e a adoção de XML Views, e o desenho inicial do algoritmo de classificação de risco.

### Semana 2 (06/07 – 12/07)
| Responsável | Atividade | Status (João) |
|---|---|---|
| Henrique | Modelagem do banco PostgreSQL/PostGIS revisada, incluindo estrutura para suportar múltiplas fontes de dados | |
| João | Cadastro e testes iniciais nas APIs do CEMADEN e INMET (autenticação, formato de resposta, limitações) | ✅ Concluída — escopo redesenhado: CEMADEN e INMET testados e descartados (documentado), ANA e CPTEC assumiram os papéis |
| Marlon | Conversão dos wireframes/telas do app para layout XML (tela de mapa e tela de listagem) | |
| Guilherme | Conversão de telas XML (formulário de cadastro de ocorrência e tela de login) com apoio do Marlon | |

**Entregável da semana:** banco atualizado com suporte a múltiplas fontes; primeiras chamadas reais documentadas.

---

## FASE 2 — Desenvolvimento Paralelo (13/07 a 09/08)

### Semana 3 (13/07 – 19/07)
| Responsável | Atividade | Status (João) |
|---|---|---|
| Henrique | Implementação dos endpoints REST principais no FastAPI (ocorrências: criar, listar, filtrar) | |
| João | Implementação do módulo de integração climática consolidada (OpenWeather + ANA + CPTEC) no backend | 🟡 Código pronto e testado (`fusao_climatica.py`); falta só a ANA responder o cadastro pra validar as 3 fontes juntas em produção |
| Marlon | Implementação da tela de mapa em XML com Google Maps SDK (sem Compose) | |
| Guilherme | Implementação da tela de cadastro de ocorrência em XML, com validação de campos | |

### Semana 4 (20/07 – 26/07)
| Responsável | Atividade | Status (João) |
|---|---|---|
| Henrique | Implementação da primeira versão do algoritmo de classificação de risco (lógica de pesos definida na Semana 1) | |
| João | Apoio à implementação do algoritmo de risco — testes com dados reais das APIs já integradas | ✅ Concluída — `algoritmo_risco.py` testado com dado real de Santo André (score 4.2, Baixo risco) |
| Marlon | Implementação da tela de listagem/histórico de ocorrências em XML | |
| Guilherme | Implementação de componentes de filtro (região e período) na interface XML | |

**Entregável da semana:** primeira versão funcional do algoritmo de risco testável via backend.

### Semana 5 (27/07 – 02/08)
| Responsável | Atividade | Status (João) |
|---|---|---|
| Henrique | Integração do banco de dados com os endpoints (persistência real das ocorrências e classificações) | |
| João | Testes de consistência dos dados climáticos consolidados (comparação entre fontes para a mesma região/horário) | 🔴 Bloqueada — depende da ANA responder o cadastro (único item fora do controle do time) |
| Marlon | Integração da tela de mapa com dados reais do backend (consumo da API) | |
| Guilherme | Integração da tela de cadastro com o backend (envio de ocorrências reais) | |

### Semana 6 (03/08 – 09/08)
| Responsável | Atividade | Status (João) |
|---|---|---|
| Henrique | Revisão de código backend e ajustes de performance inicial nas consultas | |
| João | Documentação técnica do algoritmo de classificação de risco (fundamentação e funcionamento) — insumo para o relatório | 🔴 **Atrasada — ainda não iniciada, sem bloqueio externo** |
| Marlon | Ajustes visuais e de usabilidade nas telas Android já integradas | |
| Guilherme | Testes manuais do fluxo cadastro → listagem → mapa, registrando bugs encontrados | |

**Entregável da fase:** protótipo com fluxo principal funcional (cadastro, listagem, mapa, classificação de risco básica).

---

## FASE 3 — Integração Avançada e Benchmark (10/08 a 13/09)

### Semana 7 (10/08 – 16/08) — **semana atual**
| Responsável | Atividade | Status (João) |
|---|---|---|
| Henrique | Criação do ambiente de benchmark — geração de massa de dados simulada (1k, 10k, 100k registros geoespaciais) | |
| João | Refinamento do algoritmo de risco com dados de múltiplas fontes ponderadas | 🔴 Não iniciada — depende parcialmente da Semana 6 (documentação) estar pronta primeiro |
| Marlon | Implementação de tela de detalhes da ocorrência (visualização individual) | |
| Guilherme | Implementação de notificações locais simples (alerta visual de risco alto no app) | |

### Semana 8 (17/08 – 23/08)
| Responsável | Atividade |
|---|---|
| Henrique | Execução do benchmark sem índice espacial — medição de tempo de resposta nas consultas |
| João | Apoio à análise dos resultados do benchmark — interpretação dos dados coletados |
| Marlon | Testes de usabilidade interna das telas (com os próprios colegas) |
| Guilherme | Correção de bugs identificados nos testes de usabilidade |

### Semana 9 (24/08 – 30/08)
| Responsável | Atividade |
|---|---|
| Henrique | Implementação de índice GiST no PostGIS e execução do benchmark comparativo |
| João | Documentação científica do benchmark (fundamentação teórica de R-tree/GiST, conforme literatura) |
| Marlon | Revisão e padronização visual de todas as telas (consistência de cores, fontes, espaçamento) |
| Guilherme | Testes de integração entre todas as telas do app |

**Entregável da semana:** gráfico comparativo de latência antes/depois da indexação espacial — peça central da resposta sobre "complexidade computacional".

### Semana 10 (31/08 – 06/09)
| Responsável | Atividade |
|---|---|
| Henrique | Otimizações adicionais identificadas pelo benchmark (ex: paginação de resultados, cache simples) |
| João | Implementação de testes automatizados básicos da API (principais endpoints) |
| Marlon | Implementação de tela de configurações/perfil simples do usuário |
| Guilherme | Apoio aos testes automatizados — casos de teste manuais documentados |

### Semana 11 (07/09 – 13/09)
| Responsável | Atividade |
|---|---|
| Henrique | Medição formal de latência end-to-end (app → backend → banco → resposta) em diferentes cenários |
| João | Consolidação dos critérios de avaliação de desempenho (RNF de latência, com base científica) |
| Marlon | Preparação do roteiro de teste de usabilidade com usuários externos |
| Guilherme | Organização da documentação de testes realizados até o momento |

**Entregável da fase:** sistema integrado, com métricas de desempenho documentadas e o diferencial tecnológico (algoritmo de risco + benchmark espacial) validado.

---

## FASE 4 — Testes, Validação e Redação Final (14/09 a 30/10)

### Semana 12 (14/09 – 20/09)
| Responsável | Atividade |
|---|---|
| Henrique | Apoio técnico aos testes de usabilidade (ajustes de backend identificados durante os testes) |
| João | Execução dos testes de usabilidade com usuários externos (registro de feedback) |
| Marlon | Execução dos testes de usabilidade com usuários externos (condução das sessões) |
| Guilherme | Consolidação dos resultados de usabilidade em tabela/relatório |

### Semana 13 (21/09 – 27/09)
| Responsável | Atividade |
|---|---|
| Henrique | Correções de backend apontadas pelos testes de usabilidade e desempenho |
| João | Redação da seção de metodologia de testes e avaliação (capítulo do relatório final) |
| Marlon | Correções de interface apontadas pelos testes de usabilidade |
| Guilherme | Apoio às correções de interface e testes de regressão |

### Semana 14 (28/09 – 04/10)
| Responsável | Atividade |
|---|---|
| Henrique | Redação da seção técnica sobre arquitetura final e algoritmo de classificação de risco |
| João | Redação da seção sobre integração de múltiplas fontes de dados e resultados climáticos |
| Marlon | Redação da seção sobre desenvolvimento do aplicativo Android (XML) e decisões de UI |
| Guilherme | Levantamento de capturas de tela e evidências visuais do sistema para o relatório |

### Semana 15 (05/10 – 11/10)
| Responsável | Atividade |
|---|---|
| Henrique | Redação da seção de benchmark de indexação espacial (resultados e discussão) |
| João | Redação da seção de resultados gerais e discussão sobre o diferencial tecnológico |
| Marlon | Revisão geral da redação — padronização de linguagem, normas ABNT, citações |
| Guilherme | Organização de anexos, apêndices e lista de referências complementares |

### Semana 16 (12/10 – 18/10)
| Responsável | Atividade |
|---|---|
| Henrique | Revisão técnica cruzada do relatório (conferência de dados e resultados) |
| João | Revisão técnica cruzada do relatório (conferência de dados e resultados) |
| Marlon | Montagem da apresentação final (slides) |
| Guilherme | Apoio à montagem da apresentação final (slides) |

**Entregável da semana:** rascunho completo do relatório final para revisão do orientador.

### Semana 17 (19/10 – 30/10)
| Responsável | Atividade |
|---|---|
| Henrique | Ajustes finais conforme retorno do orientador (técnico) |
| João | Ajustes finais conforme retorno do orientador (integração/dados) |
| Marlon | Ajustes finais de formatação e ensaio da apresentação |
| Guilherme | Ajustes finais de formatação e ensaio da apresentação |

**Entregável final:** relatório consolidado + protótipo funcional + apresentação para banca (30/10/2026).

---

## Resumo de cobertura dos pontos do orientador

| Ponto observado | Onde é endereçado |
|---|---|
| Latência na resposta | Semanas 7–11 (benchmark + medição formal de latência) |
| Mais fontes de dados | Semanas 1–2 (levantamento e testes) e Semana 3 (integração consolidada: OpenWeather + ANA + CPTEC) |
| Complexidade computacional do BD georreferenciado | Semanas 1, 7, 9 (estudo teórico + benchmark com/sem índice GiST) |
| Remoção do Jetpack Compose / uso de XML | Semanas 1–6 (toda a camada Android replanejada em XML) |
| Diferencial tecnológico | Algoritmo de classificação de risco por pesos (Semanas 1, 4–6, 9) |
| Não parecer "colagem de APIs" | Algoritmo de risco como camada de processamento próprio + benchmark como contribuição técnica |
| Remoção de "baixo custo" do título | Decidido com o orientador |

---

## Notas de status (mantidas fora do cronograma original)

Este arquivo é atualizado manualmente conforme o progresso real do time. Decisões técnicas
que alteraram o escopo original (troca de CEMADEN/INMET por ANA/CPTEC) estão detalhadas em
`docs/T_arquitetura_fontes_dados_final.md`.

**Pendência crítica no caminho:** resposta da ANA ao cadastro de acesso (`hidro@ana.gov.br`),
que bloqueia as Semanas 3 (parcialmente) e 5 (totalmente).

**Item atrasado sem bloqueio externo:** documentação técnica do algoritmo de risco (Semana 6,
encerrada em 09/08) — pode ser retomado a qualquer momento.
