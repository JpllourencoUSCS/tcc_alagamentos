# Referências Consolidadas do Relatório Final

*Semana 15 do cronograma (Guilherme — organização de referências). Consolidado em
03/10/2026 a partir das seções de fundamentação (T15, T17, T19) e da documentação técnica
usada no projeto. Formato ABNT NBR 6023. **Antes de fechar o relatório:** conferir cada
item na fonte original, completar os campos marcados com [confirmar] e manter só as
referências efetivamente citadas no texto final.*

## Referências bibliográficas

AMERICAN METEOROLOGICAL SOCIETY. Rain. *In*: **Glossary of Meteorology**. Boston: AMS.
Disponível em: https://glossary.ametsoc.org/wiki/Rain. Acesso em: 03 out. 2026.

CARD, S. K.; ROBERTSON, G. G.; MACKINLAY, J. D. The information visualizer, an
information workspace. *In*: CONFERENCE ON HUMAN FACTORS IN COMPUTING SYSTEMS (CHI '91),
1991, New Orleans. **Proceedings** [...]. New York: ACM, 1991. p. 181–188.

DEAN, J.; BARROSO, L. A. The tail at scale. **Communications of the ACM**, New York,
v. 56, n. 2, p. 74–80, 2013.

GUTTMAN, A. R-trees: a dynamic index structure for spatial searching. *In*: ACM SIGMOD
INTERNATIONAL CONFERENCE ON MANAGEMENT OF DATA, 1984, Boston. **Proceedings** [...].
New York: ACM, 1984. p. 47–57.

HELLERSTEIN, J. M.; NAUGHTON, J. F.; PFEFFER, A. Generalized search trees for database
systems. *In*: INTERNATIONAL CONFERENCE ON VERY LARGE DATA BASES (VLDB), 21., 1995,
Zurich. **Proceedings** [...]. San Francisco: Morgan Kaufmann, 1995. p. 562–573.

INTERNATIONAL ORGANIZATION FOR STANDARDIZATION. **ISO/IEC 25010:2011**: systems and
software engineering — systems and software quality requirements and evaluation
(SQuaRE) — system and software quality models. Geneva: ISO, 2011.

MILLER, R. B. Response time in man-computer conversational transactions. *In*: AFIPS
FALL JOINT COMPUTER CONFERENCE, 1968, San Francisco. **Proceedings** [...]. Washington:
Thompson, 1968. v. 33, p. 267–277.

NIELSEN, J. **Usability engineering**. San Francisco: Morgan Kaufmann, 1993.

OBE, R. O.; HSU, L. S. **PostGIS in action**. 3. ed. Shelter Island: Manning, 2021.

SAATY, T. L. **The analytic hierarchy process**: planning, priority setting, resource
allocation. New York: McGraw-Hill, 1980.

SAATY, T. L. Decision making with the analytic hierarchy process. **International
Journal of Services Sciences**, v. 1, n. 1, p. 83–98, 2008.

WORLD METEOROLOGICAL ORGANIZATION. **Guide to instruments and methods of observation**
(WMO-No. 8). Geneva: WMO, 2018. [confirmar edição e capítulo da classificação de
intensidade de precipitação]

## Documentação técnica e fontes de dados

AGÊNCIA NACIONAL DE ÁGUAS E SANEAMENTO BÁSICO (ANA). **HidroWebService**: manual técnico
de acesso aos dados das estações telemétricas. Versão 20.02.2026. Brasília: ANA, 2026.
[confirmar título exato e URL do manual]

ANDROID DEVELOPERS. **Android developer documentation**. Mountain View: Google.
Disponível em: https://developer.android.com/docs. Acesso em: 03 out. 2026.

CENTRO DE PREVISÃO DE TEMPO E ESTUDOS CLIMÁTICOS (CPTEC/INPE). **Serviços web em XML**:
previsão de tempo para cidades. Cachoeira Paulista: INPE. Disponível em:
http://servicos.cptec.inpe.br/XML/. Acesso em: 05 ago. 2026.

INSTITUTO NACIONAL DE METEOROLOGIA (INMET). **Previsão do tempo** e **Avisos
meteorológicos**: API de previsão por município (`apiprevmet3`). Brasília: INMET.
Disponível em: https://apiprevmet3.inmet.gov.br e https://avisos.inmet.gov.br. Acesso em:
06 out. 2026. [API sem documentação oficial; citar também o portal
https://portal.inmet.gov.br e, se usado, o feed RSS de avisos, cuja licença permite
reprodução com citação da fonte]

FASTAPI. **FastAPI documentation**. Disponível em: https://fastapi.tiangolo.com/.
Acesso em: 03 out. 2026.

GOOGLE. **Maps SDK for Android**. Disponível em:
https://developers.google.com/maps/documentation/android-sdk. Acesso em: 03 out. 2026.

GOOGLE. **Measure performance with the RAIL model**. web.dev. Disponível em:
https://web.dev/articles/rail. Acesso em: 03 out. 2026.

OPENSTREETMAP FOUNDATION. **Nominatim API documentation**. Disponível em:
https://nominatim.org/release-docs/latest/api/Overview/. Acesso em: 03 out. 2026.

OPENWEATHER. **Current weather data** e **5 day / 3 hour forecast**: API documentation.
Disponível em: https://openweathermap.org/api. Acesso em: 03 out. 2026.

POSTGIS PROJECT. **PostGIS documentation**: spatial indexes. Disponível em:
https://postgis.net/docs/. Acesso em: 03 out. 2026.

POSTGRESQL GLOBAL DEVELOPMENT GROUP. **PostgreSQL 16 documentation**: using EXPLAIN;
CLUSTER. Disponível em: https://www.postgresql.org/docs/16/. Acesso em: 03 out. 2026.

SQLALCHEMY. **Joining a session into an external transaction (such as for test
suites)**. *In*: SQLAlchemy 2.0 documentation. Disponível em:
https://docs.sqlalchemy.org/en/20/orm/session_transaction.html. Acesso em: 03 out. 2026.

## Pendências de verificação

1. **Limiares de intensidade de chuva do modelo AHP.** `algoritmo_risco.py` e T15 atribuem
   à OMM a classificação leve < 2,5 mm/h, moderada 2,5–7,6 mm/h, forte 7,6–50 mm/h e
   violenta > 50 mm/h. O limite de 7,6 mm/h corresponde à definição do *Glossary of
   Meteorology* da American Meteorological Society; o guia da OMM (WMO-No. 8) usa, até
   onde a equipe deve confirmar, 10 mm/h como limite entre moderada e forte e 50 mm/h para
   violenta. **Não é preciso mudar o modelo** — só citar corretamente: por exemplo,
   "limiares baseados na classificação da American Meteorological Society (leve, moderada
   e forte) e da OMM (violenta)". Conferir nas duas fontes antes de escrever.
2. **Manual da ANA:** título exato, versão e URL.
3. **Referências do levantamento de APIs (T05–T07, T12):** os documentos citam testes e
   documentação de cada fonte, mas não trazem referências formais; incluir aqui as que
   forem citadas no texto final.
