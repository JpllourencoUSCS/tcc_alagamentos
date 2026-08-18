"""
Geração de massa de dados sintética para o benchmark (Semana 7 — Henrique,
reconstruído em 18/08/2026).

Separado da parte que fala com o banco (`popular_banco.py`) de propósito: esta
função é pura (sem I/O), então dá pra testar as três escalas (1k/10k/100k) sem
precisar de um Postgres/PostGIS disponível — o que falta nesta máquina hoje.
"""

import random
import uuid
from datetime import datetime, timedelta, timezone

from benchmark.config import BBOX_REGIAO_PILOTO, JANELA_DIAS, SEMENTE_PADRAO
from constants import FonteDado, NivelRisco

_DESCRICOES_USUARIO = [
    "Água na altura do meio-fio, trânsito lento.",
    "Alagamento total da pista, carros parados.",
    "Bueiro entupido, começando a acumular água.",
    "Rua intransitável para pedestres.",
    "Nível da água subindo rápido, atenção.",
]


def _gerar_uma(rng: random.Random, agora: datetime) -> dict:
    lat_min, lon_min, lat_max, lon_max = BBOX_REGIAO_PILOTO
    fonte = rng.choice(list(FonteDado))
    data_hora = agora - timedelta(
        seconds=rng.uniform(0, JANELA_DIAS * 24 * 3600)
    )

    linha = {
        "latitude": rng.uniform(lat_min, lat_max),
        "longitude": rng.uniform(lon_min, lon_max),
        "data_hora": data_hora,
        "nivel_risco": rng.choice(list(NivelRisco)),
        "fonte": fonte,
        "descricao": None,
        "chuva_mm": None,
        "descricao_clima": None,
        "temperatura": None,
        "umidade": None,
        "id_usuario": None,
    }

    # Preenchimento condicional por fonte, só pra não gerar um dataset
    # sintético onde todas as colunas são preenchidas em todas as linhas de
    # forma implausível (o que nenhuma fonte real faz) — não é crítico para o
    # benchmark em si (que mede tempo de consulta, não qualidade do dado), mas
    # deixa o dataset mais honesto caso seja usado de exemplo no relatório.
    if fonte == FonteDado.USUARIO:
        linha["descricao"] = rng.choice(_DESCRICOES_USUARIO)
        linha["id_usuario"] = f"user-{uuid.UUID(int=rng.getrandbits(128))}"
    elif fonte in (FonteDado.OPENWEATHER, FonteDado.ANA):
        linha["chuva_mm"] = round(rng.expovariate(1 / 4), 1)  # maioria baixa, cauda longa
        linha["temperatura"] = round(rng.uniform(15, 32), 1)
        linha["umidade"] = rng.randint(40, 100)
    elif fonte == FonteDado.CPTEC:
        linha["descricao_clima"] = rng.choice(
            ["Chuvoso", "Parcialmente Nublado", "Pancadas de Chuva", "Céu Claro"]
        )

    return linha


def gerar_ocorrencias_sinteticas(
    quantidade: int,
    semente: int = SEMENTE_PADRAO,
    referencia: datetime | None = None,
) -> list[dict]:
    """Gera `quantidade` linhas prontas para inserir em `ocorrencias`
    (dicts com as mesmas chaves de db.models.Ocorrencia, exceto `id`/`geom` —
    `geom` fica por conta do trigger do banco, ver schema.sql).

    Determinística para uma dada `semente` — dataset reproduzível entre
    execuções, relevante para comparar o benchmark antes/depois do índice
    (Semana 9) sobre exatamente os mesmos dados. Isso exige também fixar o
    ponto de referência de `data_hora`: por padrão é `datetime.now()`, então
    duas chamadas com a mesma `semente` em instantes reais diferentes geram
    `data_hora` levemente diferentes (bug encontrado pelo teste de
    reprodutibilidade em 18/08 — corrigido tornando `referencia` explícita).
    Passe `referencia` fixa quando precisar de igualdade byte a byte entre
    execuções (é o que os testes fazem).
    """
    rng = random.Random(semente)
    agora = referencia or datetime.now(timezone.utc)
    return [_gerar_uma(rng, agora) for _ in range(quantidade)]
