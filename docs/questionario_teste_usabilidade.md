# Questionário de Teste de Usabilidade — Sistema de Monitoramento Colaborativo de Alagamentos

**TCC II — Ciência da Computação (USCS)**
Orientador: Prof. Dr. Marcos Alberto Bussab
Equipe: Henrique, João, Marlon e Guilherme

> Este formulário foi elaborado para ser aplicado via Google Forms (modelo de referência
> conforme material da Unidade II) ao público-alvo dos testes de usabilidade previstos na
> Semana 12 do cronograma (14–20/09/2026). O texto abaixo é o roteiro completo de perguntas
> e alternativas a serem transcritas para o Forms; a numeração de seções facilita a
> configuração de "seções" no próprio Google Forms.
>
> **Importante:** este roteiro assume o aplicativo já **integrado ao backend real**
> (validado em 03/10/2026 — ver `docs/evidencias_testes/2026-10-03/`), com as **ocorrências
> de demonstração** de São Caetano do Sul carregadas (`backend/dados_demo.py`) e a
> classificação de risco calculada pelo sistema. A tela de login não implementa
> autenticação real (não faz parte do escopo do sistema) — ver também o TCLE,
> `docs/tcle_teste_usabilidade.md`.

---

## Seção 0 — Introdução (texto de abertura do Forms)

> Olá! Obrigado por participar da avaliação do aplicativo do nosso Trabalho de Conclusão de
> Curso: um sistema de monitoramento colaborativo de risco de alagamento para São Caetano
> do Sul. Você vai navegar pelo aplicativo, com ocorrências de demonstração criadas pela
> equipe para este teste, e depois responder a este questionário sobre sua experiência. Não existem
> respostas certas ou erradas — queremos sua opinião sincera. A participação é voluntária e
> as respostas são anônimas. Antes de continuar, leia e assine o Termo de Consentimento
> Livre e Esclarecido (TCLE) que acompanha este link.

---

## Seção 1 — Perfil do participante

1. **Faixa etária**
   - Menos de 18 anos
   - 18–24 anos
   - 25–34 anos
   - 35–44 anos
   - 45–59 anos
   - 60 anos ou mais

2. **Você mora ou trabalha em São Caetano do Sul?**
   - Sim, moro em São Caetano do Sul
   - Sim, trabalho em São Caetano do Sul (mas não moro)
   - Não, mas conheço a região
   - Não tenho relação com São Caetano do Sul

3. **Você já vivenciou ou presenciou situações de alagamento na sua região?**
   - Sim, com frequência
   - Sim, algumas vezes
   - Raramente
   - Nunca

4. **Qual seu nível de familiaridade com aplicativos de celular no geral?**
   (Escala Likert 1–5: 1 = Nada familiarizado(a), 5 = Muito familiarizado(a))

5. **Você já usou algum aplicativo de alerta climático ou de monitoramento de riscos antes?**
   - Sim
   - Não
   - Não sei / não tenho certeza

---

## Seção 2 — Tarefas guiadas (a serem realizadas no protótipo antes de responder)

> Instrução no Forms: "Antes de responder às próximas perguntas, realize as seguintes
> tarefas no aplicativo, na ordem indicada. Um(a) integrante da equipe estará com você para
> observar e esclarecer dúvidas, mas não vai indicar como resolver os passos."

- **Tarefa 1:** Abra o aplicativo e acesse a tela inicial/login.
- **Tarefa 2:** Cadastre uma nova ocorrência de alagamento (dados fictícios).
- **Tarefa 3:** Acesse a listagem/histórico de ocorrências e aplique um filtro (região ou período).
- **Tarefa 4:** Abra o mapa e toque em um dos marcadores exibidos.
- **Tarefa 5:** A partir do marcador, acesse a tela de detalhes da ocorrência.

Estas tarefas correspondem aos casos de teste `CT-CAD-001`, `CT-LST-002`, `CT-MAP-001/002`
e `CT-DET-001` do Fluxo de Teste (`docs/plano_e_fluxo_de_testes_TCC.xlsx`).

---

## Seção 3 — Facilidade de uso (por tarefa)

Para cada tarefa da Seção 2, repetir o bloco de perguntas abaixo (pode ser configurado como
uma "seção" separada por tarefa no Google Forms):

6. **Consegui concluir esta tarefa sem ajuda.**
   (Escala Likert 1–5: 1 = Discordo totalmente, 5 = Concordo totalmente)

7. **Esta tarefa foi fácil de realizar.**
   (Escala Likert 1–5)

8. **As informações na tela eram claras o suficiente para entender o que fazer.**
   (Escala Likert 1–5)

9. **Se você teve dificuldade nesta tarefa, descreva o que aconteceu.** (Texto livre, opcional)

---

## Seção 4 — Avaliação geral do aplicativo

10. **De modo geral, o aplicativo é fácil de usar.**
    (Escala Likert 1–5)

11. **O visual do aplicativo (cores, textos, ícones) é agradável e claro.**
    (Escala Likert 1–5)

12. **Eu confiaria nas informações de risco de alagamento mostradas pelo aplicativo.**
    (Escala Likert 1–5)

13. **Eu usaria este aplicativo se ele estivesse disponível na loja de aplicativos, com dados reais.**
    - Sim, certamente
    - Provavelmente sim
    - Não sei
    - Provavelmente não
    - Certamente não

14. **O que você mais gostou no aplicativo?** (Texto livre)

15. **O que você mudaria ou melhoraria?** (Texto livre)

16. **Você notou algum erro, travamento ou comportamento inesperado durante o uso?**
    (Texto livre; se sim, descrever a tela e o que aconteceu — alimenta o registro de
    defeitos do Fluxo de Teste, coluna "ID Defeito")

17. **Comentários adicionais.** (Texto livre, opcional)

---

## Seção 5 — Encerramento

> Texto final do Forms: "Muito obrigado por participar! Suas respostas serão usadas
> exclusivamente para fins acadêmicos, na validação do protótipo desenvolvido para o TCC.
> Nenhum dado pessoal identificável foi coletado neste formulário além do que você
> informou voluntariamente no TCLE em separado."

---

## Preparação do ambiente antes de cada sessão (para o grupo, não faz parte do Forms)

Atualizado em 03/10/2026, depois do primeiro teste do app contra a API real:

1. **API e banco no ar**, acessíveis pelo aparelho de teste: `docker compose up -d` no
   notebook com Docker. No emulador desse notebook, o endereço padrão
   (`http://10.0.2.2:8000/`) já funciona. Num celular físico, o `API_BASE_URL` do
   `android/local.properties` deve apontar para um endereço que o celular alcance (IP
   Tailscale do notebook com o app Tailscale no celular, ou hospedagem definitiva) — o APK
   precisa ser gerado de novo depois de mudar esse valor.
2. **Ocorrências de demonstração carregadas**: `python -m dados_demo` (em `backend/`). Elas
   têm datas relativas ao momento da carga; para as tarefas com filtro "Últimas 24 h"
   mostrarem resultados, recarregar no dia da sessão (`python -m dados_demo --limpar` e
   depois `python -m dados_demo`).
3. **Chave do Google Maps** no `android/local.properties` (`MAPS_API_KEY=...`) **e liberada
   para o certificado que assina o APK**: a chave do projeto é restrita a apps Android
   cadastrados no Google Cloud (SHA-1 do certificado + `com.example.alagamentos`). Se o APK
   for gerado numa máquina cujo certificado não esteja cadastrado, o mapa aparece em branco
   ("Authorization failure" no logcat) e as **Tarefas 4 e 5 não podem ser feitas**. O SHA-1
   do certificado de depuração de cada máquina sai com
   `keytool -list -v -keystore %USERPROFILE%\.android\debug.keystore -storepass android`.
4. **Chave do OpenWeather** no `.env` (`OPENWEATHER_API_KEY=...`) para a opção "Automático"
   do nível de risco na Tarefa 2. Sem ela, o app mostra "Risco automático indisponível" e o
   participante precisa escolher Baixo, Médio ou Alto — anotar isso na observação da tarefa
   se acontecer.
5. **Depois da sessão**: as ocorrências cadastradas pelos participantes ficam no banco com o
   `id_usuario` do aparelho de teste; apagar antes da próxima sessão para cada participante
   começar do mesmo estado.

## Notas de rastreabilidade (para o grupo, não faz parte do Forms)

- Perguntas 6–9 (por tarefa) alimentam os campos "Resultado Obtido" e "Observações" dos
  casos de teste de usabilidade no Fluxo de Teste (`CT-CAD-001`, `CT-LST-001/002`,
  `CT-MAP-001/002`, `CT-DET-001`, `CT-LOG-001`, `CT-CFG-001`, `CT-NOT-001`).
- O critério de aprovação definido no Plano de Teste (seção "Critério geral de aprovação")
  usa a média das perguntas de escala Likert (6, 7, 8, 10, 11, 12) como o indicador de
  "percepção de facilidade de uso" — limiar sugerido: média ≥ 4.
- Respostas da pergunta 16 (erros/travamentos) devem ser triadas pelo responsável de cada
  módulo (ver coluna "Responsável" da aba Plano de Teste) e, se confirmadas, registradas
  como defeito (`BUG-001`, `BUG-002`, ...) no Fluxo de Teste.
