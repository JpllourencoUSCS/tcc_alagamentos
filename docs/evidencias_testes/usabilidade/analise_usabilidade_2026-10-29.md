# Avaliação de usabilidade — análise das respostas (29/10/2026)

*Responsável pela análise: João (sessão de 29/10/2026). Respostas do formulário aplicado pelo
grupo (Google Forms), em `respostas_formulario_2026-10.csv` nesta pasta.*

## Como foi aplicada

- **Instrumento:** formulário do Google Forms com o termo de consentimento e as capturas das
  sete telas principais (entrada, mapa, alertas, detalhes, cadastro, previsão, ajustes). Para
  cada tela: quatro afirmações em escala de 1 a 5 (facilidade de uso, intuitividade, design,
  importância), uma pergunta específica de múltipla escolha e um campo de comentário. As
  perguntas estão no Apêndice B do documento teórico.
- **Diferença em relação ao roteiro planejado** (`docs/questionario_teste_usabilidade.md`):
  os participantes **não usaram o aplicativo**, só viram as telas; não houve tarefas guiadas
  nem perfil do participante. A avaliação mede compreensão e percepção da interface, não
  taxa de conclusão de tarefas.
- **Amostra:** de conveniência — familiares e amigos dos integrantes (informação do grupo).
- **Respostas consideradas:** só as **12** que aceitaram o termo (17 a 21/10/2026). O
  formulário recebeu 35 respostas; nas 23 anteriores a 17/10 a pergunta do termo ainda não
  existia, e o grupo decidiu (29/10/2026) não usá-las nem mencioná-las no documento. Elas não
  estão nesta pasta.
- **Critério de aprovação (PT-001):** média ≥ 4 nas perguntas em escala Likert.

## Resultados (12 participantes, 336 notas)

| Tela | Facilidade | Intuitividade | Design | Importância | Média |
|---|---|---|---|---|---|
| Entrada | 4,83 | 5,00 | 4,75 | 5,00 | 4,90 |
| Mapa | 4,58 | 4,58 | 4,83 | 4,92 | 4,73 |
| Alertas | 4,50 | 4,58 | 4,67 | 4,75 | 4,62 |
| Detalhes | 4,92 | 4,92 | 4,83 | 4,92 | 4,90 |
| Cadastro | 4,67 | 4,67 | 4,83 | 4,92 | 4,77 |
| Previsão | 4,83 | 4,75 | 4,75 | 4,75 | 4,77 |
| Ajustes | 4,83 | 4,83 | 4,83 | 4,83 | 4,83 |
| **Todas** | **4,74** | **4,76** | **4,79** | **4,87** | **4,79** |

- Distribuição das notas: 285 notas 5, 34 notas 4, 14 notas 3, 3 notas 2 (95% com 4 ou 5).
- 8 dos 12 participantes deram 5 em todos os itens (efeito da amostra de pessoas próximas).
- **Critério atendido:** todas as telas e todos os critérios com média ≥ 4.

## Perguntas específicas e melhorias aplicadas no app (29/10/2026)

| Tela | Respostas | Melhoria |
|---|---|---|
| Entrada — aviso "não há verificação de senha" claro? | 10 sim; 2 mais ou menos | Campo de senha retirado (`LoginActivity.kt`, `activity_login.xml`): entrada sem cadastro nem senha, nome opcional |
| Mapa — entendeu as cores e os marcadores mais apagados? | 10 tudo; 2 só as cores | Resumo "Situação atual" com o ponto de cada linha na cor do nível e a explicação dos esmaecidos (`MapaFragment.kt`, `strings.xml`) |
| Alertas — filtros fáceis de combinar? | 12 sim | — |
| Detalhes — informações suficientes? | 9 sim; 3 faltam | Endereço aproximado (rua e bairro) pelo geocodificador do aparelho (`DetalhesFragment.kt`, `fragment_detalhes.xml`) |
| Cadastro — diferença entre "Automático" e escolher o nível? | 9 sim; 2 em parte; 1 não | Explicação dos dois modos sempre visível; corrigido o texto que ainda citava pluviômetros (`CadastroFragment.kt`, `fragment_cadastro.xml`) |
| Previsão — "Baixo" com aviso de tempestade ficou claro? | 11 sim; 1 em dúvida | — |
| Ajustes — opções de alerta e de fonte de dados claras? | 11 sim; 1 em parte | — (o filtro de fontes já tinha saído em 16/10) |

Sugestões dos comentários: nome da região/bairro e indicação no mapa nos detalhes (endereço
incluído; mapa nos detalhes fica como trabalho futuro); mais destaque à descrição (já é o
título da tela); "Esqueceu a senha" (sem sentido depois da retirada da senha).

Verificação: build com 0 erros de lint e 11/11 testes de JVM; telas conferidas no emulador
contra a API real; capturas refeitas em `docs/capturas/` (29/10/2026). Não houve nova rodada
de avaliação com as telas alteradas.
