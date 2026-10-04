# Seção: Desenvolvimento do Aplicativo Android

*Rascunho de seção do relatório final — Semana 14 do cronograma (Marlon). Redigido em
03/10/2026 a partir do código de `android/` (base unificada em 30/09/2026, integrada à API
real e testada em emulador em 03/10/2026). A numeração "3.V" é provisória. **Marlon e
Guilherme: revisar e complementar com o histórico de decisões de UI de vocês (wireframes,
testes internos da Semana 8, padronização visual da Semana 9), que não está registrado no
repositório.***

---

## 3.V Aplicativo Android

O aplicativo é o ponto de contato do cidadão com o sistema: mostra as ocorrências de
alagamento registradas em São Caetano do Sul, permite registrar novas ocorrências,
apresenta o risco calculado pelo modelo AHP e avisa sobre ocorrências de risco perto do
usuário.

### 3.V.1 Tecnologias e decisões

| Item | Escolha | Motivo |
|---|---|---|
| Linguagem | Kotlin | Linguagem recomendada pelo Google para Android; corrotinas para chamadas de rede sem travar a interface. |
| Interface | XML + Android Views (Material Components 3), sem Jetpack Compose | Decisão de replanejamento da Fase 1, alinhada com o orientador; reduz a curva de aprendizado do time e usa componentes maduros e bem documentados. |
| Mapa | Google Maps SDK for Android | Ver comparação de SDKs (T07 / seção de APIs). |
| Comunicação | Retrofit + Gson | Cliente HTTP declarativo: cada endpoint da API é um método de interface (`AlagamentosApi`). |
| Armazenamento local | SharedPreferences | Preferências de alerta, perfil e sessão ficam no aparelho; o backend não guarda dados pessoais. |
| Compatibilidade | Android 7.0 (API 24) ou superior; alvo API 37 | Cobre a grande maioria dos aparelhos em uso; datas ISO 8601 da API via *desugaring* de `java.time`. |

### 3.V.2 Estrutura de navegação

O app tem uma tela de entrada (`LoginActivity`) e, depois dela, uma atividade principal
(`MainActivity`) com **barra de navegação inferior** de quatro abas, cada uma um
`Fragment`:

| Aba / tela | Função |
|---|---|
| **Mapa** | Marcadores coloridos por nível de risco (verde, laranja, vermelho), com um círculo de 250 m em volta de cada ocorrência; cartão "Situação atual" com a contagem por nível e o registro mais recente; alerta em destaque quando há ocorrências de risco alto. |
| **Alertas** | Lista das ocorrências, da mais recente para a mais antiga, com filtros de região (todas, São Caetano do Sul, "perto de mim"), período (todo, 24 h, 7 dias, 30 dias) e nível de risco. |
| **Previsão** | Risco de alagamento calculado agora para a posição do usuário (ou o centro da cidade), com cada fonte que entrou no cálculo AHP (chuva atual, pico previsto, pluviômetro, relatos de usuários e previsão do CPTEC). |
| **Ajustes** | Preferências de alerta (ligar/desligar, nível mínimo, fontes e raio de 1 a 20 km) e acesso ao perfil. |
| Detalhes *(sobre a aba)* | Informações completas de uma ocorrência; aberta pelo marcador do mapa, pela lista ou por uma notificação. |
| Registrar ocorrência *(sobre a aba)* | Formulário de cadastro, aberto pelo botão "Registrar" do Mapa e dos Alertas. |
| Perfil *(sobre a aba)* | Nome, e-mail (opcional), bairro de São Caetano do Sul e identificador do usuário gerado pelo app. |

### 3.V.3 Integração com a API

Todas as telas consomem a API REST do backend pelo `ApiCliente.kt`:

- `GET /ocorrencias` alimenta o mapa e a lista. Os filtros de **região** e **período**
  são enviados como parâmetros (bbox e `data_inicio`) e aplicados **pelo próprio backend**,
  usando o índice espacial. O filtro "perto de mim" envia o quadrado que contém o círculo do
  raio configurado e o app corta para o círculo exato com a fórmula de haversine.
- `GET /ocorrencias/{id}` abre os detalhes.
- `POST /ocorrencias` registra o reporte do usuário (`fonte = usuario`), com o identificador
  do perfil.
- `GET /risco` alimenta a aba Previsão.

O tempo limite de leitura foi ampliado para 30 s, porque o cadastro com risco automático
consulta fontes climáticas externas antes de responder (T19, RNF-03). Falhas de rede e
respostas de erro são tratadas com mensagens específicas: sem conexão (o formulário fica
preenchido para reenviar), dados recusados (422) e risco automático indisponível (503,
orientando o usuário a escolher o nível manualmente).

### 3.V.4 Cadastro colaborativo

O cadastro é o que torna o sistema colaborativo. O usuário:
1. marca o local tocando no mapa ou usando a localização do aparelho (obrigatório; o app
   avisa se o ponto estiver fora de São Caetano do Sul);
2. escolhe o nível de risco — **Automático** (o servidor calcula pelo AHP) ou Baixo, Médio
   ou Alto, quando ele está vendo a situação na rua;
3. descreve a situação, opcionalmente (até 300 caracteres).

Após o envio, o app abre os detalhes da ocorrência criada, já com o nível calculado. Cada
reporte passa a compor o componente colaborativo do AHP para quem estiver a até 1 km nas
3 horas seguintes (T15, seção 6.4).

### 3.V.5 Notificações locais

Ao receber ocorrências da API, o app verifica as das últimas 24 h que atendem às
preferências do usuário (nível mínimo, fontes e raio em relação à posição atual) e mostra
uma notificação agrupada ("N novas ocorrências de alagamento — X com risco alto"). Cada
ocorrência é avisada uma única vez, e tocar na notificação abre os detalhes. A verificação
acontece enquanto o app está aberto: notificações com o app fechado exigiriam um serviço
em segundo plano ou *push* pelo servidor (Firebase Cloud Messaging), registrados como
trabalho futuro.

### 3.V.6 Identidade visual e acessibilidade

O app usa tema escuro, com cores de alto contraste para os três níveis de risco (verde,
laranja e vermelho). O nível nunca é comunicado só pela cor: ele aparece também por
extenso ("ALTO", "MÉDIO", "BAIXO") em todas as telas. Os textos estão em português, e a
única tela de entrada não pede cadastro real — o protótipo não implementa autenticação
(fora do escopo).

### 3.V.7 Verificação

O app foi testado em emulador (Android 15, perfil Pixel 6) contra a API e o banco reais em
03/10/2026: login, listagem com 8 combinações de filtros conferidas contra respostas
diretas da API, cadastro com nível manual e com nível automático (classificado pelo AHP com
dados climáticos reais do OpenWeather), bloqueio de envio sem local, mensagem de risco
automático indisponível, aba de risco atual conferida com a API, detalhes, perfil
persistido e notificação local. Os testes foram repetidos com o aparelho em português do
Brasil e no fuso de São Paulo. Foram encontrados e corrigidos no mesmo dia dois defeitos:
o contador da lista ignorava o filtro de nível, e, em português, as coordenadas saíam com
vírgula decimal ("-23,6148, -46,5435"), ambíguas. A metodologia e os resultados estão na
seção de testes; as capturas de tela estão em `docs/capturas/`.

**Limitações:** o mapa depende de uma chave do Google Maps cujas restrições incluam o
certificado com que o APK foi assinado; as notificações só funcionam com o app aberto;
perfil e preferências não são sincronizados entre aparelhos.

---

*Seção redigida com base em `android/app/src/main/` (estado de 03/10/2026) e em
`docs/evidencias_testes/2026-10-03/`.*
