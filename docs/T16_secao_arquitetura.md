# Seção: Arquitetura Final do Sistema

*Rascunho de seção do relatório final — Semana 14 do cronograma (Henrique). Redigido em
03/10/2026 a partir do código do repositório. A numeração "3.W" é provisória e deve ser
ajustada na montagem do relatório. A parte do algoritmo de risco está em
`T16_secao_algoritmo_risco.md` e a de fontes de dados em `T16_secao_relatorio_apis.md`;
esta seção mostra como as peças se conectam.*

---

## 3.W Arquitetura do Sistema

O sistema segue uma arquitetura cliente-servidor em três camadas: um **aplicativo
Android** (cliente), uma **API REST** (servidor de aplicação) e um **banco de dados
geoespacial**. O servidor também consulta três serviços climáticos externos.

### 3.W.1 Visão geral

```
┌────────────────────────┐        HTTP/JSON         ┌──────────────────────────────────────┐
│  Aplicativo Android    │  GET/POST /ocorrencias   │  API REST (FastAPI, Python)          │
│  Kotlin + XML Views    │ ───────────────────────▶ │                                      │
│  Google Maps SDK       │ ◀─────────────────────── │  api/        rotas e validação       │
│  Retrofit              │                          │  servicos/   classificação de risco  │
└────────────────────────┘                          │              agregação colaborativa  │
                                                    │  fusao_climatica  (4 chamadas em     │
                                                    │                    paralelo + cache) │
                                                    │  algoritmo_risco  (AHP)              │
                                                    │  db/         repositório (SQLAlchemy)│
                                                    └──────┬───────────────────┬───────────┘
                                                           │ SQL (PostGIS)     │ HTTPS
                                                           ▼                   ▼
                                            ┌──────────────────────┐  ┌────────────────────┐
                                            │ PostgreSQL 16        │  │ OpenWeather        │
                                            │ + PostGIS 3.4        │  │ ANA (HidroWebService)│
                                            │ índice GiST em geom  │  │ CPTEC/INPE         │
                                            └──────────────────────┘  └────────────────────┘
```

*(Figura 3.W.1 — redesenhar como diagrama na versão final do relatório.)*

### 3.W.2 Componentes

**Aplicativo Android.** Desenvolvido em Kotlin com layouts XML (Android Views), sem Jetpack
Compose, conforme decisão de replanejamento da Fase 1. Usa o Google Maps SDK para o mapa e
o Retrofit para consumir a API. Os detalhes estão na seção do aplicativo
(`T16_secao_app_android.md`).

**API REST.** Implementada com FastAPI, que gera a validação dos dados e a documentação
interativa (OpenAPI, em `/docs`) a partir dos contratos Pydantic (`api/schemas.py`).
Expõe três operações sobre ocorrências e uma de consulta de risco:

| Método e rota | Função |
|---|---|
| `POST /ocorrencias` | Registra uma ocorrência. Sem `nivel_risco`, o risco é calculado automaticamente. |
| `GET /ocorrencias` | Lista ocorrências, com filtros de fonte, nível de risco, período (`data_inicio`/`data_fim`) e região (bbox), paginação (`skip`/`limit`) e ordenação da mais recente para a mais antiga. |
| `GET /ocorrencias/{id}` | Detalhes de uma ocorrência. |
| `GET /risco` | Risco de alagamento calculado agora para uma coordenada, com o score de cada componente do AHP e os dados usados. Não grava nada. |

Valores fora do vocabulário (por exemplo, um nível de risco inexistente) são rejeitados
com HTTP 422. A falha da fonte climática principal durante o cálculo automático devolve
HTTP 503 com mensagem orientando o usuário a informar o nível manualmente.

**Camada de serviços.** Separa as rotas da lógica de domínio:
- `servicos/classificacao.py` orquestra o cálculo automático: obtém os dados climáticos,
  calcula o componente colaborativo e aplica o AHP.
- `servicos/colaborativo.py` agrega os reportes de usuários vizinhos (1 km, últimas 3 h)
  num score de 0 a 100 (T15, seção 6.4).
- `fusao_climatica.py` consulta OpenWeather (condição atual e previsão), ANA e CPTEC **em
  paralelo**, com timeout de 10 s por fonte, e guarda o resultado em **cache** por 10
  minutos para cada célula de ~1 km.
- `algoritmo_risco.py` implementa o modelo AHP, incluindo a redistribuição de pesos quando
  uma fonte está indisponível.

**Camada de dados.** O acesso ao banco passa por um repositório (`db/repository.py`) com
interface definida (`OcorrenciaRepositoryProtocol`). As rotas não usam o SQLAlchemy
diretamente, o que permite testá-las com uma implementação em memória. O modelo de dados
(`db/schema.sql`, `db/models.py`) tem três tabelas: `ocorrencias` (reportes de usuários e
leituras das fontes automáticas), `estacoes_referencia` (estações físicas da ANA) e
`reportes_colaborativos_agregado` (histórico dos scores colaborativos calculados). A
coluna `geom` (ponto PostGIS, SRID 4326) é mantida por *trigger* a partir de latitude e
longitude e indexada com GiST. O filtro de região usa o operador `&&` contra
`ST_MakeEnvelope`, que esse índice resolve.

**Vocabulário compartilhado.** Os valores válidos de nível de risco e fonte ficam num único
lugar (`constants.py`), reutilizado pelo modelo do banco (restrições `CHECK`) e pela API
(validação), evitando divergência entre camadas.

### 3.W.3 Fluxo do cadastro com risco automático

1. O usuário marca o local no mapa (ou usa o GPS) e envia o reporte sem escolher o nível.
2. O app faz `POST /ocorrencias` sem `nivel_risco`.
3. A API pede a classificação à camada de serviços, que:
   a. busca os dados climáticos da célula de ~1 km (do cache, se consultados há menos de
      10 minutos; senão, das quatro fontes em paralelo);
   b. calcula o score colaborativo a partir dos reportes vizinhos das últimas 3 horas;
   c. aplica o AHP e obtém o nível (Baixo, Médio ou Alto).
4. A ocorrência é gravada com o nível calculado e a precipitação usada, na mesma transação
   do registro do score colaborativo.
5. A API devolve a ocorrência criada, e o app abre a tela de detalhes com o risco
   calculado.

A consulta `GET /risco` usa o mesmo caminho (itens a a c), sem gravar ocorrência nem
registrar o score colaborativo, e alimenta a aba "Previsão" do aplicativo.

### 3.W.4 Implantação

O banco e a API são empacotados como contêineres (`docker-compose.yml` com os serviços
`db` e `api`; `Dockerfile` na raiz do repositório). As credenciais (senha do banco, chave
do OpenWeather, credenciais da ANA) vêm de variáveis de ambiente lidas de um arquivo `.env`
fora do controle de versão. Durante o desenvolvimento, o ambiente roda num notebook da
equipe e é compartilhado com os demais integrantes por VPN privada (Tailscale), sem expor
o banco na internet. A mesma imagem da API pode ser implantada em qualquer serviço de
hospedagem de contêineres, mudando só as variáveis de ambiente.

### 3.W.5 Qualidade e testes

O backend tem uma suíte automatizada (pytest) com 61 testes em 03/10/2026, em duas
categorias:
- **Testes de contrato**, que substituem banco e fontes externas por implementações em
  memória e verificam rotas, validação e regras.
- **Testes de integração**, que rodam contra um PostgreSQL/PostGIS real. Cada teste roda
  dentro de uma transação desfeita ao final, então nenhum dado de teste permanece no banco.

A metodologia completa está na seção de testes (`T16_secao_metodologia_testes.md`).

### 3.W.6 Decisões de arquitetura e justificativas

| Decisão | Justificativa |
|---|---|
| PostgreSQL + PostGIS | Tipos e índices espaciais nativos (GiST/R-tree), validados no benchmark (T16_secao_benchmark). |
| FastAPI | Validação e documentação OpenAPI geradas a partir dos tipos, e bom desempenho para uma API de leitura intensiva. |
| Repositório com interface | Rotas testáveis sem banco, e troca de implementação sem alterar as rotas. |
| Fusão climática em paralelo + cache | O tempo do cadastro com risco automático fica limitado à fonte mais lenta, e não à soma das quatro (RNF-03 e RNF-05 em T19). |
| Fail-safe por fonte | A indisponibilidade da ANA ou a falta de reportes colaborativos não derrubam a classificação nem subestimam o risco (T15, seção 6.3). |
| Contêineres + variáveis de ambiente | Mesmo artefato em desenvolvimento e hospedagem, sem credenciais no repositório. |

---

*Seção redigida com base no código de `backend/`, `docker-compose.yml` e `Dockerfile`
(estado de 03/10/2026).*
