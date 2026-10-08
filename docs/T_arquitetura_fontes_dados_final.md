# Levantamento de Fontes de Dados Climáticos — Arquitetura Final

*Responsável: João | Semanas 2–3 do cronograma | Consolidado em 05/08/2026 | Atualizado em
03/10/2026 (agregação colaborativa, integração atual e situação das fontes) e em 07/10/2026
(CPTEC substituído pelo INMET `apiprevmet3`; avisos oficiais como piso da classificação)*

## Decisão

O **CEMADEN** foi descartado como fonte de dados do projeto. O acesso à sua API (PED)
depende de um fluxo de autenticação em duas etapas — cadastro de e-mail junto ao órgão e
geração de token via um sistema de autenticação separado (SGAA) — cuja URL exata não é
documentada publicamente e depende de resposta institucional sem prazo definido.

O **INMET** também foi descartado (05/08/2026), incluindo o uso de dado manual/CSV, que
havia sido considerado como alternativa e depois abandonado por decisão do projeto. Os
motivos técnicos que levaram a essa decisão:
- O endpoint que alimenta o dado "ao vivo" (`apitempo.inmet.gov.br/estacao/front/`) exige
  um token de **Google reCAPTCHA v3** gerado por página — proteção anti-bot intencional,
  que este projeto não contorna.
- O endpoint histórico alternativo, sem essa proteção
  (`apitempo.inmet.gov.br/estacao/{inicio}/{fim}/{codigo}`), foi testado com dois
  intervalos de datas diferentes (uma semana de julho/2026, claramente consolidada, e os
  dois dias anteriores ao teste) e retornou vazio (204) em ambos os casos.

**Importante: essa remoção não deixa nenhum peso do modelo AHP sem cobertura.** O INMET
nunca teve peso próprio — era apenas uma fonte redundante de "precipitação atual", papel
que o OpenWeather já cumpre sozinho desde o início do projeto. Não foi necessário buscar
substituto.

Em lugar do CEMADEN, o papel de "pluviômetro local" no AHP passa a ser cumprido pela
**ANA** (Agência Nacional de Águas e Saneamento Básico). Ela também exige cadastro prévio
por e-mail (`hidro@ana.gov.br`), mas esse processo está oficialmente documentado (manual
técnico da ANA, versão 20.02.2026), então o script já está pronto para funcionar assim que
as credenciais chegarem.

## Arquitetura final de fontes

| Fonte | Papel no sistema | Autenticação | Tipo de dado |
|---|---|---|---|
| **OpenWeather** | Precipitação atual (principal) + previsão principal | Chave de API (gratuita) | Modelo/estimativa |
| **ANA** | Pluviômetro local — papel que era do CEMADEN no AHP | E-mail de cadastro + token OAuth (60 min) | Estação física (rede hidrometeorológica nacional) |
| **CPTEC/INPE** | Previsão municipal (4 dias) — validação cruzada qualitativa da previsão (**até 03/10/2026**; substituído pelo INMET, ver seção "Substituição do CPTEC pelo INMET") | Sem token | Modelo |
| **INMET (`apiprevmet3`)** | Desde 06/10/2026: previsão textual por município (validação qualitativa) + avisos meteorológicos oficiais (piso da classificação) | Sem token (User-Agent de navegador) | Previsão oficial / alerta oficial |

Essa arquitetura é mais enxuta que as versões anteriores (que incluíam CEMADEN e/ou
INMET), mas estruturalmente completa: uma fonte de precipitação atual + previsão
(OpenWeather), uma fonte de medição física institucional (ANA) e uma fonte de previsão
redundante (CPTEC) — cobrindo os três papéis que o modelo AHP realmente precisa, além do
componente colaborativo (reportes de usuários).

## Limitações a citar na seção de limitações do TCC

Vale registrar como achado metodológico, não como falha do projeto: **múltiplos órgãos
brasileiros de dados hidrometeorológicos protegem especificamente o acesso "ao vivo"
contra automação** (CEMADEN via processo de credenciamento sem URL pública, INMET via
reCAPTCHA v3), mesmo disponibilizando os mesmos dados publicamente por outros meios com
alguma defasagem. Isso é um ponto legítimo de discussão para a banca sobre os desafios
práticos de integração com dados públicos brasileiros.

## Códigos confirmados (ABC Paulista)

### ANA (rede hidrometeorológica)
| Código | Município | Código IBGE |
|---|---|---|
| `21477000` | Santo André | 3547809 |
| `21489000` | São Caetano do Sul | 3548807 |
| `21488000` | São Bernardo do Campo | 3548708 |

### CPTEC/INPE
- ID de cidade confirmado: `4704` (Santo André/SP; existe também `4703` para Santo
  André/PB — o script já filtra por UF=SP).
- Previsão de 4 dias funciona de ponta a ponta, com siglas de condição traduzidas
  (ex.: "pn" → "Parcialmente Nublado").
- Condições atuais de aeroporto (METAR) foram testadas e descartadas (feed vazio /
  erro 500 do servidor do CPTEC) — usa-se apenas a previsão de 4 dias.

## Como cada fonte se conecta ao modelo AHP

- **Precipitação atual (35%):** OpenWeather.
- **Pluviômetro local (25%):** ANA. Se a chamada falhar (ou enquanto o token não estiver
  configurado), o peso é redistribuído automaticamente entre precipitação atual e previsão
  (ver `algoritmo_risco.py`).
- **Previsão (25%):** OpenWeather forecast, com o CPTEC entrando como validação cruzada
  qualitativa (não numérica) — não altera o score, mas pode ser citado na documentação como
  evidência de consistência entre modelos. *(Desde 06/10/2026, o papel qualitativo é do
  INMET; os avisos oficiais do INMET passaram a funcionar como piso da classificação final
  — ver seção abaixo.)*
- **Colaborativo (15%):** agregação dos reportes de usuários do app — implementada em
  03/10/2026 (`backend/servicos/colaborativo.py`): relatos a até 1 km do ponto nas últimas
  3 h, cada um convertido no ponto médio da faixa de risco informada e ponderado pela
  proximidade no tempo e no espaço; com menos de 2 relatos, o componente fica ausente e o
  peso é redistribuído (T15, seção 6.4).

## Integração atual das fontes (03/10/2026)

Como as fontes acima são combinadas hoje no backend (`backend/fusao_climatica.py`,
`backend/servicos/`). Não muda nenhuma decisão de fonte — só registra o desenho em uso:

- **Chamadas em paralelo** às quatro consultas externas (OpenWeather atual e previsão, ANA,
  CPTEC), com timeout de 10 s cada (desde 03/09/2026). *Desde 06/10/2026 são cinco: o CPTEC
  deu lugar à previsão e aos avisos do INMET (duas consultas, com cache por município).*
- **Credenciais por variável de ambiente:** `OPENWEATHER_API_KEY`, `ANA_IDENTIFICADOR`,
  `ANA_SENHA` (no `.env`). Até 03/10/2026 a chave do OpenWeather era o texto fixo
  `"sua_chave_aqui"` no código, o que faria o cálculo automático falhar contra a API real.
- **Falha da fonte principal:** se o OpenWeather falhar, o cálculo automático não é feito e
  a API responde HTTP 503 com mensagem orientando a informar o nível manualmente. ANA e
  CPTEC continuam com fail-safe (ficam ausentes sem derrubar o cálculo).
- **Cache de 10 minutos** por célula de 0,01° (~1 km) para os dados consolidados.
- **Consulta do risco atual:** `GET /risco?latitude=&longitude=` devolve a classificação, o
  score de cada componente e os dados usados, sem gravar nada (usado pela aba Previsão do
  app).
- **Validado com dados reais em 03/10/2026:** centro de São Caetano do Sul → Baixo (13,7),
  com OpenWeather respondendo, ANA sem credencial e sem relatos suficientes. Cadastro com
  risco automático: ~0,5 s sem cache e ~50 ms com cache (`docs/T19_criterios_desempenho.md`).

## Situação das fontes em 03/10/2026

| Fonte | Situação |
|---|---|
| OpenWeather | ✅ Chave configurada no `.env` do notebook com Docker; funcionando de ponta a ponta |
| ANA | 🟡 Sem credencial — aguardando resposta do cadastro (sem novidade desde 03/09). O código usa a estação de Santo André (`21477000`); com a credencial, testar primeiro a de São Caetano do Sul (`21489000`), já que o escopo passou a ser São Caetano |
| CPTEC/INPE | 🔴 Todos os endpoints respondendo **HTTP 403** a partir do notebook com Docker (inclusive o `4704`, que funcionava em agosto); a BrasilAPI, que consulta o mesmo serviço, também falhou no mesmo dia. Persistiu até 06/10 → **substituído pelo INMET** (abaixo) |
| INMET (`apiprevmet3`) | ✅ Desde 06/10/2026: previsão e avisos testados ao vivo para São Caetano do Sul; integrados ao backend e ao app |
| Colaborativo | ✅ Agregação implementada e testada contra PostGIS real |
| Estação da USCS | ⚪ Em investigação, sem novidade registrada desde 03/09 |

## Substituição do CPTEC pelo INMET (06/10/2026) e avisos como piso (07/10/2026)

**Decisão (06/10/2026):** com o CPTEC fora do ar desde 03/10, o papel de validação cruzada
qualitativa passou para a **API de previsão do INMET** (`https://apiprevmet3.inmet.gov.br`),
levantada pelo João (`testes-api/teste_inmet_apiprevmet3.py`). Não reabre o descarte de
agosto: o INMET descartado era o dado **de estação em tempo real** (`apitempo`, com
reCAPTCHA); esta é a API de previsão por município e de avisos oficiais, aberta.

| Recurso | Endpoint | Uso no sistema |
|---|---|---|
| Previsão por município | `/previsao/3548807` (código IBGE de São Caetano do Sul) | Resumo textual do turno atual (manhã/tarde/noite nos dias 1–2; resumo diário nos dias 3–5) — validação qualitativa, **fora do AHP**; gravado como `descricao_clima` no cadastro com risco automático |
| Avisos ativos | `/avisos/ativos` (nacional; filtrado pelo campo `geocodes`) | Exibidos no app; os de chuva vigentes funcionam como **piso** da classificação |

Características verificadas em 06/10/2026: sem token; respondeu também sem User-Agent, mas
o cabeçalho de navegador é enviado por segurança; ~0,8 s por chamada; respostas pesadas
(~260 KB e ~440 KB, por ícones em base64) → cache de 10 min por município. Riscos: sem
documentação oficial nem garantia (mesmo tipo de risco que tirou o CPTEC do ar); possível
bloqueio de conexões de fora do Brasil (testar se a API do sistema for hospedada no
exterior). Falha do INMET = campo vazio, sem efeito na classificação.

**Decisão (07/10/2026, do grupo) — avisos como piso:** avisos de chuva vigentes para o
município elevam a classe final no nível de risco de alagamento que o próprio INMET declara
em cada severidade:

| Severidade | Texto oficial (avisos de chuva) | Piso |
|---|---|---|
| Perigo Potencial | 20–30 mm/h ou até 50 mm/dia; "baixo risco de alagamentos" | — |
| Perigo | 30–60 mm/h ou 50–100 mm/dia; "risco de alagamentos" | Médio |
| Grande Perigo | > 60 mm/h ou > 100 mm/dia; "grande risco de grandes alagamentos" | Alto |

Tipos de aviso observados no feed (93 avisos, 06/10/2026): Tempestade, Chuvas Intensas,
Acumulado de Chuva (de chuva) e Baixa Umidade, Onda de Calor (ignorados). Pesos e score do
AHP não mudam; o piso nunca reduz a classe. Detalhe em `T15_algoritmo_risco_fundamentacao.md`
§6.5.

**Vocabulário de fonte (07/10/2026):** o valor `cptec` do campo `fonte` das ocorrências
(`FonteDado` em `backend/constants.py`, `CHECK` de `schema.sql`, enum do app) virou `inmet`,
para o filtro de fontes do app não continuar oferecendo o CPTEC. Bancos já criados:
`backend/db/migracao_2026-10-07_fonte_inmet.sql` (nenhuma ocorrência real usava `cptec`; só
as linhas sintéticas do benchmark, relabeladas).

## Em investigação (03/09/2026) — estação meteorológica do campus da USCS

Descoberta de que o campus da USCS possui uma **estação meteorológica própria**. O time
está investigando junto aos responsáveis pelo equipamento a possibilidade de acesso aos
dados. Se viável, ela poderia **substituir a ANA** no papel de "pluviômetro local" do
modelo AHP (25% do peso) — motivo: o escopo do monitoramento passou a ser especificamente
a cidade de **São Caetano do Sul**, e uma estação dentro do próprio município (ou até do
próprio campus) tende a ser uma medição mais local e direta do que a rede hidrometeorológica
nacional da ANA (cujo código mais próximo, `21489000`, já é de São Caetano do Sul — ver
tabela acima — mas ainda depende de cadastro por e-mail sem resposta até esta data).

**Isto não é uma decisão fechada.** A ANA continua sendo a fonte ativa para esse papel
(ver "Decisão" acima e `CLAUDE.md`) até que: (1) o acesso aos dados da estação do campus
seja confirmado pelos responsáveis; e (2) o formato/frequência dos dados dela seja avaliado
como adequado para o AHP (ex.: precisa de um endpoint HTTP consultável programaticamente,
não só um mostrador físico ou relatório manual). Atualizar esta seção assim que o time de
integração tiver uma resposta, para qualquer um dos dois sentidos (substitui a ANA, complementa
a ANA, ou inviável).

## Próximos passos

1. Aguardar resposta da ANA ao e-mail já enviado — este é hoje o único item realmente fora
   do seu controle. *(Nota de 03/10/2026: esta linha citava `docs/T_email_solicitacao_ana.md`,
   mas esse arquivo nunca foi versionado no repositório; o texto do e-mail enviado não está
   registrado aqui.)*
2. Assim que a ANA responder com Identificador/Senha, rodar `testes-api/teste_ana.py` com
   `ANA_IDENTIFICADOR` e `ANA_SENHA` configurados para validar o fluxo de token de ponta a
   ponta.
3. ~~Atualizar a seção 3.X do relatório (`T16_secao_relatorio_apis.md`)~~ — feito em 17/08/2026.
   O texto agora reflete a narrativa real: CEMADEN e INMET foram testados e descartados por
   proteção anti-bot documentada (achado metodológico), e a ANA e o CPTEC assumiram os papéis
   de dado físico e previsão redundante, respectivamente. Inclui também seções novas com os
   resultados de teste da ANA (estrutural, pendente de credencial) e do CPTEC (funcional de
   ponta a ponta).
