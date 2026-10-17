# Roteiro da Apresentação para a Banca (rascunho)

*Semana 16 do cronograma (Marlon, com apoio do Guilherme). Rascunho de estrutura montado em
03/10/2026 a partir dos resultados já medidos — os números abaixo são os do repositório
nesta data; conferir antes de fechar os slides. Duração sugerida: 15–20 min + perguntas.
Cada slide traz a mensagem principal (o que a banca deve guardar) e o material de apoio.*

---

**1. Título** — Sistema de Monitoramento Colaborativo de Risco de Alagamento em São
Caetano do Sul. Equipe, orientador, USCS, data.

**2. Problema** — Alagamentos urbanos recorrentes no ABC; informação dispersa entre órgãos e
sem a percepção de quem está na rua. *Mensagem:* falta um indicador local, atualizado e que
inclua o cidadão.

**3. Objetivo** — Um sistema que combina fontes climáticas públicas com relatos dos
moradores num indicador de risco único, entregue por um app.

**4. Respostas aos pontos do TCC I** — tabela de uma linha por ponto do orientador
(latência, mais fontes, complexidade do banco, XML em vez de Compose, diferencial, título
sem "baixo custo") apontando o slide onde cada um é respondido.

**5. Arquitetura** — diagrama app → API → serviços (fusão, colaborativo, AHP) → PostGIS +
fontes externas (T16_secao_arquitetura, figura 3.W.1 redesenhada).

**6. Fontes de dados** — OpenWeather + Open-Meteo (fundidas), INMET (previsão e avisos oficiais, no lugar do
CPTEC, fora do ar desde 03/10) e relatos dos usuários; CEMADEN e o dado de estação em tempo
real do INMET descartados por proteção contra automação (achado metodológico). *Mensagem:* integrar dado
público brasileiro é difícil, e o sistema foi desenhado para isso.

**7. Diferencial: o modelo AHP** — 3 critérios, pesos 54/30/16 (autovetor, sem ajuste), CR = 0,0079 (< 0,10),
escala de intensidade de chuva, redistribuição de peso para fonte ausente.

**8. Dado colaborativo** — relatos a até 1 km nas últimas 3 h, ponderados por proximidade
no tempo e no espaço; mínimo de 2 relatos. *Mensagem:* é a fonte que só este sistema tem.

**9. Robustez do modelo** — análise de sensibilidade: ±10% em um peso muda a classe em no
máximo 7,1% de 280 cenários (±20%: 12,9%). Tabela de T15, seção 8.2.

**10. Complexidade do banco: o benchmark** — gráfico
`backend/benchmark/resultados/grafico_consulta_espacial.png`. 100 mil registros:
14,65 ms → 0,18 ms (81,6×). *Mensagem:* O(n) sem índice, sublinear com GiST.

**11. O que o benchmark ensinou além da teoria** — em 1 milhão, o custo vira o tamanho do
resultado (O(log n + k)); `CLUSTER` reduz até 5×; o otimizador nem sempre escolhe o GiST
quando também ordena por data.

**12. Latência** — critérios de Nielsen (0,1 s / 1 s / 10 s) → RNF de T19. Leituras com
p95 < 17 ms mesmo com 1 milhão de registros; cadastro com risco automático ~0,5 s sem
cache e ~50 ms com cache.

**13. O app (demonstração ou capturas)** — `docs/capturas/`: mapa com as ocorrências e o
painel da ocorrência selecionada, alertas com filtros, detalhes, cadastro com o local no
mapa, aba de risco com as fontes do cálculo e os avisos do INMET, ajustes e perfil. Se possível, demonstração ao vivo do
cadastro com risco automático (ter as capturas como plano B). *Legendar como dados de
demonstração.*

**14. Qualidade e testes** — 114 testes automatizados no backend, 10 no app, CI no GitHub;
plano PT-001 com 29 casos; defeitos encontrados na integração real e corrigidos.

**15. Usabilidade** — *preencher após as sessões:* participantes, taxa de conclusão, média
Likert vs. limiar de 4, principais ajustes.

**16. Limitações** — sem pluviômetro físico (ANA e estação da USCS retiradas por falta de acesso), CPTEC fora do ar (substituído pelo INMET), pesos não calibrados com
especialistas, dados de demonstração, hospedagem não definitiva.

**17. Trabalhos futuros** — pluviômetro físico (ANA ou estação da USCS), calibração com histórico e Defesa
Civil, notificações push, hospedagem em nuvem, reputação dos relatos.

**18. Conclusão** — retomar a pergunta do slide 3 e as respostas do slide 4.

## Perguntas prováveis da banca (preparar resposta)

- Por que esses pesos? → matriz pareada, CR, análise de sensibilidade (slide 9).
- E se um usuário mentir? → mínimo de 2 relatos, peso de só 16%, decaimento no tempo.
- Por que tirar a ANA? → o cadastro nunca foi aprovado; o critério nunca teve dado real.
  No lugar, a Open-Meteo permite fundir duas medidas da mesma variável.
- E se as fontes discordarem? → vale a maior (conservador) e a divergência é registrada;
  exemplo real de 16/10 (OpenWeather 1,0 × Open-Meteo 2,0 mm/h → 2,0; Baixo, 18,9).
- Por que PostGIS e não um banco NoSQL? → índice espacial nativo e o benchmark.
- De onde vêm os limiares de chuva? → **conferir antes** (ver
  `docs/referencias_consolidadas.md`, pendência 1).
