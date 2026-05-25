# Definição dos Dados Provenientes das APIs

**Responsável:** Aluno 3  
**Apoio:** Aluno 2

---

## Contexto

Com base no levantamento das APIs (Tarefas 6 e 9) e nos testes realizados pelo Aluno 2
com a OpenWeather (Tarefa 8), este documento define quais campos serão efetivamente
consumidos pelas APIs externas e como cada um se relaciona com as funcionalidades do sistema.

---

## 1. Dados provenientes da OpenWeather API (fonte primária)

| Campo da API | Caminho no JSON | Tipo | Uso no sistema |
|---|---|---|---|
| Precipitação última hora | `rain.1h` | float (mm) | **Cálculo de nível de risco** |
| Descrição do clima | `weather[0].description` | string | Exibição ao usuário |
| Temperatura atual | `main.temp` | float (°C) | Exibição informativa |
| Umidade relativa | `main.humidity` | int (%) | Exibição informativa |
| Cobertura de nuvens | `clouds.all` | int (%) | Dado auxiliar de risco |
| Data/hora da medição | `dt` | Unix timestamp | Registro temporal |
| Coordenadas (validação) | `coord.lat` / `coord.lon` | float | Confirmação da área consultada |

### Regra de classificação de risco baseada em `rain.1h`

| Faixa de precipitação (mm/h) | Classificação |
|---|---|
| 0 a 5 | Baixo |
| 5 a 25 | Médio |
| Acima de 25 | Alto |

> Referência: classificação baseada em critérios do CEMADEN e da Defesa Civil de São Paulo.

---

## 2. Dados provenientes da OpenWeather — Previsão (complementar)

Endpoint: `/data/2.5/forecast` — retorna 40 entradas em intervalos de 3h (5 dias).

| Campo | Caminho no JSON | Uso no sistema |
|---|---|---|
| Precipitação prevista | `list[n].rain.3h` | Alerta antecipado |
| Data/hora prevista | `list[n].dt_txt` | Exibição na linha do tempo |
| Descrição prevista | `list[n].weather[0].description` | Exibição ao usuário |

---

## 3. Dados provenientes do Nominatim / OpenStreetMap (geocoding)

Usado quando o usuário informar endereço textual em vez de coordenadas GPS.

| Campo | Caminho no JSON | Uso no sistema |
|---|---|---|
| Latitude | `lat` | Origem da consulta climática |
| Longitude | `lon` | Origem da consulta climática |
| Nome retornado | `display_name` | Confirmação visual para o usuário |

---

## 4. Dados do INMET e CEMADEN (reserva para versão futura)

Ambas as fontes foram avaliadas e permanecem como candidatas para **validação cruzada** dos
dados de precipitação em versões posteriores do sistema. Os campos equivalentes a `rain.1h`
são `CHUVA` (INMET) e `valorMedida` (CEMADEN).

---

## 5. Campos descartados nesta versão

| Campo | API | Motivo do descarte |
|---|---|---|
| `wind.speed` / `wind.deg` | OpenWeather | Sem relação direta com risco de alagamento no escopo atual |
| `main.pressure` | OpenWeather | Não utilizado nas regras de risco definidas |
| `sys.sunrise` / `sys.sunset` | OpenWeather | Não necessário para o protótipo |
| Dados horários completos | INMET | Acesso 403 em ambiente de desenvolvimento; cobertura irregular |
| Série histórica de chuva | CEMADEN | Endpoint instável; reservado para trabalho futuro |
