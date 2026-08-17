# Levantamento de Fontes de Dados Climáticos — Arquitetura Final

*Responsável: João | Semanas 2–3 do cronograma | Consolidado em 05/08/2026*

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
| **CPTEC/INPE** | Previsão municipal (4 dias) — validação cruzada qualitativa da previsão | Sem token | Modelo |

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
  evidência de consistência entre modelos.
- **Colaborativo (15%):** inalterado, agregação dos reportes de usuários do app.

## Próximos passos

1. Aguardar resposta da ANA ao e-mail já enviado (`docs/T_email_solicitacao_ana.md`) — este
   é hoje o único item realmente fora do seu controle.
2. Assim que a ANA responder com Identificador/Senha, rodar `testes-api/teste_ana.py` com
   `ANA_IDENTIFICADOR` e `ANA_SENHA` configurados para validar o fluxo de token de ponta a
   ponta.
3. Atualizar a seção 3.X do relatório (`T16_secao_relatorio_apis.md`) para refletir essa
   arquitetura final — o texto atual ainda cita CEMADEN e INMET como "descartados por
   documentação limitada", o que precisa virar a narrativa real: CEMADEN e INMET foram
   testados e descartados por proteção anti-bot documentada (achado metodológico), e a ANA
   e o CPTEC assumiram os papéis de dado físico e previsão redundante, respectivamente.
