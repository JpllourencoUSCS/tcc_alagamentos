# Monitoramento Colaborativo de Alagamentos — São Caetano do Sul

Trabalho de Conclusão de Curso de Ciência da Computação da USCS (Universidade Municipal de
São Caetano do Sul), sob orientação do Prof. Dr. Marcos Alberto Bussab. Equipe: Henrique,
João, Marlon e Guilherme.

O sistema classifica o risco de alagamento em São Caetano do Sul combinando dados
meteorológicos de fontes públicas com relatos dos próprios moradores. É formado por um
aplicativo Android e por uma API que consulta as fontes, calcula o risco por um modelo AHP
(*Analytic Hierarchy Process*) e guarda as ocorrências num banco geoespacial.

> As ocorrências que aparecem nas capturas e nos testes são **dados de demonstração**
> (`backend/dados_demo.py`), não alagamentos reais.

## Como funciona

- **Aplicativo Android** (Kotlin, layouts XML): mapa das ocorrências, lista com filtros,
  cadastro de ocorrência (por endereço, toque no mapa ou localização do aparelho, só dentro
  do município), risco de alagamento atual com os avisos oficiais do INMET, notificações e
  perfil. Capturas em [`docs/capturas/`](docs/capturas/).
- **API REST** (Python, FastAPI): `POST`/`GET /ocorrencias`, `GET /ocorrencias/{id}` e
  `GET /risco`. Documentação interativa em `/docs` com a API no ar.
- **Classificação de risco**: modelo AHP com quatro critérios — chuva atual (35%),
  pluviômetro local (25%), previsão (25%) e relatos de usuários próximos (15%). Fontes sem
  dado têm o peso redistribuído entre as demais, e avisos de chuva do INMET funcionam como
  piso da classe. Fundamentação em [`docs/T15_algoritmo_risco_fundamentacao.md`](docs/T15_algoritmo_risco_fundamentacao.md).
- **Banco de dados**: PostgreSQL 16 com PostGIS 3.4 e índice espacial GiST; o benchmark de
  indexação espacial está em [`backend/benchmark/`](backend/benchmark/).
- **Fontes de dados**: OpenWeather (chuva atual e previsão), ANA (pluviômetro; acesso ainda
  não liberado) e INMET (previsão textual e avisos oficiais). As decisões sobre fontes estão
  em [`docs/T_arquitetura_fontes_dados_final.md`](docs/T_arquitetura_fontes_dados_final.md).

## Estrutura do repositório

| Pasta | Conteúdo |
|---|---|
| `backend/` | API, fusão das fontes climáticas, modelo AHP, banco (`db/`), testes (`tests/`) e benchmark |
| `android/` | Aplicativo Android (projeto Android Studio) e scripts de automação por adb (`scripts/`) |
| `docs/` | Documentação do projeto: cronograma, decisões técnicas, rascunhos das seções do relatório (`T16_secao_*.md`), plano de testes, capturas e evidências |
| `testes-api/` | Scripts usados para testar cada fonte de dados externa |

## Como rodar

### API e banco (Docker)

Pré-requisito: Docker com Docker Compose.

```bash
cp .env.example .env            # preencha a senha do banco e a chave do OpenWeather
docker compose up -d            # sobe o banco (PostGIS) e a API em http://localhost:8000
docker exec -i alagamentos_db psql -U alagamentos -d alagamentos < backend/db/schema.sql
docker compose exec api python -m dados_demo   # opcional: 30 ocorrências de demonstração
```

Sem a chave do OpenWeather, o cálculo automático de risco responde 503 e o app pede que o
nível seja escolhido à mão. Bancos criados antes de 07/10/2026 precisam também de
`backend/db/migracao_2026-10-07_fonte_inmet.sql`.

### Testes do backend

```bash
python -m venv .venv && .venv/bin/pip install -r requirements.txt   # Windows: .venv\Scripts\
cd backend
python -m pytest tests/
```

Os testes de integração rodam contra um PostgreSQL/PostGIS real quando a variável
`DATABASE_URL` está definida; sem ela, são pulados e os demais rodam com implementações em
memória.

### Aplicativo Android

Pré-requisitos: JDK 21 ou mais recente e Android SDK. No arquivo `android/local.properties`
(não versionado):

```properties
MAPS_API_KEY=<chave do Google Maps SDK for Android>
API_BASE_URL=http://10.0.2.2:8000/   # endereço da API visto pelo emulador (padrão)
```

```bash
cd android
./gradlew assembleDebug testDebugUnitTest
```

A chave do Google Maps é restrita a certificados Android cadastrados no Google Cloud: o
APK precisa ser assinado por um certificado cujo SHA-1 esteja nas restrições da chave, senão
o mapa aparece em branco.

## Integração contínua

A cada push, o GitHub Actions ([`.github/workflows/ci.yml`](.github/workflows/ci.yml)) roda
os testes do backend contra um PostGIS real e compila o app com os testes de JVM.
