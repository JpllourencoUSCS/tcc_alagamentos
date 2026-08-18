# T17 — Fundamentação Técnica: Indexação Espacial (GiST/R-tree) em PostGIS

*Responsável: Henrique | Semana 1 do cronograma (reconstruído em 18/08/2026 após perda dos
arquivos originais) | Base teórica para o ambiente de benchmark (Semanas 7–9) e para a
resposta ao ponto do orientador sobre "complexidade computacional do BD georreferenciado"*

## 1. Objetivo

Documentar a fundamentação teórica sobre indexação espacial em bancos de dados relacionais,
como base para justificar — com literatura, não apenas empiricamente — o ganho de desempenho
que será medido no benchmark comparativo (consultas geoespaciais com e sem índice GiST, sobre
massas de 1k/10k/100k registros, Semanas 7–9).

## 2. O problema: por que um índice B-tree não serve para dados espaciais

O índice padrão de bancos relacionais (B-tree) assume uma ordem total sobre valores
unidimensionais (ex.: um inteiro ou uma data). Coordenadas geográficas são bidimensionais
(latitude, longitude), e as consultas relevantes para este projeto não são de igualdade ou
intervalo simples, mas espaciais:

- **Contém/intersecta**: "quais ocorrências estão dentro deste polígono (bairro, bacia)?"
- **Proximidade (KNN)**: "quais as 10 ocorrências mais próximas deste ponto?"
- **Bounding box**: "quais pontos estão dentro desta janela de mapa visível?"

Sem um índice espacial, o banco precisa avaliar a função de distância/contenção contra
**cada linha da tabela** (*sequential scan*) — custo O(n). Para a tabela `ocorrencias`
crescendo com o uso do app (reportes de usuário + leituras automáticas das APIs), isso se
torna o gargalo mais provável em consultas de mapa (a operação mais frequente do app).

## 3. R-tree (Guttman, 1984)

O R-tree é a estrutura de indexação espacial de referência, proposta por Antonin Guttman em
*"R-trees: A Dynamic Index Structure for Spatial Searching"* (ACM SIGMOD, 1984). Ideia central:

- Cada objeto espacial é aproximado por seu **MBR** (*Minimum Bounding Rectangle* — o menor
  retângulo alinhado aos eixos que o contém). Para os pontos deste projeto (lat/lon de uma
  ocorrência), o MBR degenera num retângulo de área zero, mas o mesmo mecanismo se aplica.
- MBRs são agrupados hierarquicamente em uma árvore balanceada: cada nó interno guarda o MBR
  que envolve todos os MBRs de seus filhos. A raiz envolve o dataset inteiro.
- Uma busca por região (`ST_Intersects`, `ST_Contains`, `ST_DWithin`) desce a árvore podando
  ramos cujo MBR não intersecta a região de busca — não precisa visitar as folhas fora da área
  de interesse. Complexidade média **O(log n)** por busca, contra O(n) do scan sequencial.
- Diferença central para uma B-tree: os MBRs de nós irmãos **podem se sobrepor**. Isso é o que
  permite indexar objetos 2D sem impor uma ordem total artificial, mas também é a razão de o
  algoritmo de inserção precisar de heurísticas (ex.: minimizar aumento de área) para manter a
  árvore eficiente — não há uma "posição correta única" como numa B-tree.

## 4. GiST — o mecanismo que o PostgreSQL/PostGIS usa

O PostgreSQL não implementa R-tree como estrutura própria; ele implementa **GiST**
(*Generalized Search Tree*, Hellerstein, Naughton & Pfeffer, 1995) — um framework de índice
genérico e extensível, que fornece a árvore balanceada, o algoritmo de busca com poda e os
pontos de extensão (`consistent`, `union`, `penalty`, `picksplit`), deixando o tipo de dado
definir sua própria noção de "contenção" e "proximidade".

O PostGIS registra uma **implementação de R-tree sobre o framework GiST** para o tipo
`geometry`/`geography`. Na prática, para este projeto isso significa:

```sql
CREATE INDEX idx_ocorrencias_geom
    ON ocorrencias
    USING GIST (geom);
```

Esse índice acelera qualquer predicado espacial do PostGIS baseado no operador `&&`
(sobreposição de bounding box) por baixo dos panos — incluindo `ST_Intersects`,
`ST_Contains`, `ST_DWithin` e `ST_Distance` combinado com `ORDER BY` (KNN via GiST desde o
PostgreSQL 9.1+/PostGIS 2.0+).

## 5. Por que GiST/R-tree e não outra estrutura

Alternativas existentes e por que não foram adotadas:

| Estrutura | Observação |
|---|---|
| **Quadtree** | Divide o espaço recursivamente em quadrantes fixos; bom para dados uniformemente distribuídos, mas degrada com dados concentrados (o caso deste projeto: ocorrências tendem a se agrupar em áreas urbanas de risco). Não é o padrão nativo do PostGIS. |
| **SP-GiST** | Estrutura de particionamento do espaço (não balanceada por conteúdo), eficiente para dados com distribuição bem definida (ex.: pontos em grade). PostGIS oferece suporte experimental, mas GiST é a opção madura e documentada oficialmente para uso geral. |
| **BRIN** | Muito mais leve, mas assume correlação física entre a ordem de inserção e o valor indexado — não se sustenta para coordenadas geográficas inseridas em qualquer ordem (reportes de usuários chegam em ordem temporal, não espacial). |
| **GiST/R-tree** | Escolhida: é a opção oficial e recomendada pela documentação do PostGIS para a coluna `geometry`, suporta todos os predicados espaciais usados neste projeto (contém, intersecta, KNN) e é a que a literatura de referência (Obe & Hsu, *PostGIS in Action*) usa como baseline em benchmarks comparáveis ao que este TCC pretende reproduzir. |

## 6. Hipótese a validar no benchmark (Semanas 7–9)

Com base na literatura, a hipótese que o benchmark deve confirmar empiricamente:

- Sem índice espacial, o tempo de consulta geoespacial cresce **linearmente** com o volume de
  dados (O(n)).
- Com índice GiST, o crescimento esperado é **logarítmico** (O(log n)), tornando-se a diferença
  mais perceptível justamente na maior massa de teste (100k registros) — o que também
  fundamenta teoricamente por que o desenho do benchmark usa três ordens de grandeza (1k, 10k,
  100k) em vez de um único volume: o ganho relativo do índice só fica visível ao comparar a
  taxa de crescimento entre volumes, não um volume isolado.

## 7. Referências

- GUTTMAN, A. *R-trees: A Dynamic Index Structure for Spatial Searching*. ACM SIGMOD, 1984.
- HELLERSTEIN, J. M.; NAUGHTON, J. F.; PFEFFER, A. *Generalized Search Trees for Database
  Systems*. VLDB, 1995.
- OBE, R.; HSU, L. *PostGIS in Action*. 3rd ed. Manning, 2021 — cap. sobre indexação espacial.
- Documentação oficial do PostGIS — *Spatial Indexes*:
  https://postgis.net/docs/using_postgis_dbmanagement.html#idm590
