"""
Agregador de reportes colaborativos (componente C4 do AHP, 15% — pendência
aberta em 17/08/2026 no CRONOGRAMA_STATUS.md, implementada em 03/10/2026).

Transforma os reportes brutos de usuários (`ocorrencias.fonte = 'usuario'`)
perto de um ponto, numa janela de tempo recente, no score 0-100 que
`algoritmo_risco.calcular_risco` espera em `reportes_colaborativos_score`.

Regras (ver docs/T15_algoritmo_risco_fundamentacao.md, seção 6.4):

- **Vizinhança**: reportes a até RAIO_METROS do ponto avaliado, nas últimas
  JANELA_HORAS. Alagamento é um fenômeno local e transitório — reporte de
  outro bairro ou de ontem não diz nada sobre o risco aqui e agora.
- **Valor de cada reporte**: o nível informado pelo usuário vira o ponto médio
  da faixa correspondente da própria escala do AHP (Baixo 0-30 -> 15,
  Médio 30-60 -> 45, Alto 60-100 -> 80), mantendo o componente na mesma
  escala dos outros três.
- **Peso de cada reporte**: decai linearmente com a idade (1 no instante do
  reporte, 0 no fim da janela) e com a distância (1 no ponto, 0 na borda do
  raio) — reportes mais recentes e mais próximos pesam mais, a mesma ideia da
  ponderação pelo inverso da distância usada em interpolação espacial.
- **Mínimo de reportes**: com menos de MINIMO_REPORTES, devolve None (não
  0.0), acionando o fail-safe 2 do algoritmo (redistribuição do peso de C4).
  Um único reporte isolado não basta para mover o score — reduz o efeito de
  reporte equivocado ou mal-intencionado.
"""

import math
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from sqlalchemy import func, select
from sqlalchemy.orm import Session

from constants import FonteDado, NivelRisco
from db.models import Ocorrencia, ReporteColaborativoAgregado

RAIO_METROS = 1_000
JANELA_HORAS = 3
MINIMO_REPORTES = 2

SCORE_POR_NIVEL = {
    NivelRisco.BAIXO.value: 15.0,
    NivelRisco.MEDIO.value: 45.0,
    NivelRisco.ALTO.value: 80.0,
}

# Metros por grau de latitude — usado só para o pré-filtro por bbox (que
# aproveita o índice GiST); a distância exata vem de ST_Distance em geography.
_METROS_POR_GRAU = 111_320


@dataclass
class ReporteProximo:
    nivel_risco: str
    data_hora: datetime
    distancia_m: float


@dataclass
class ScoreColaborativo:
    score: float
    quantidade_reportes: int
    janela_inicio: datetime
    janela_fim: datetime


def peso_reporte(
    reporte: ReporteProximo,
    agora: datetime,
    raio_m: float = RAIO_METROS,
    janela_horas: float = JANELA_HORAS,
) -> float:
    """Pura — peso 0-1 do reporte (decaimento linear no tempo x na distância)."""
    idade_h = (agora - reporte.data_hora).total_seconds() / 3600
    peso_tempo = max(0.0, 1 - idade_h / janela_horas) if idade_h >= 0 else 1.0
    peso_distancia = max(0.0, 1 - reporte.distancia_m / raio_m)
    return peso_tempo * peso_distancia


def calcular_score_colaborativo(
    reportes: list[ReporteProximo],
    agora: datetime,
    raio_m: float = RAIO_METROS,
    janela_horas: float = JANELA_HORAS,
    minimo_reportes: int = MINIMO_REPORTES,
) -> ScoreColaborativo | None:
    """Pura — média ponderada dos valores dos reportes, ou None quando não há
    reportes suficientes (fail-safe 2 do AHP)."""
    considerados = [
        (SCORE_POR_NIVEL[r.nivel_risco], peso_reporte(r, agora, raio_m, janela_horas))
        for r in reportes
        if r.nivel_risco in SCORE_POR_NIVEL
    ]
    considerados = [(valor, peso) for valor, peso in considerados if peso > 0]
    if len(considerados) < minimo_reportes:
        return None

    soma_pesos = sum(peso for _, peso in considerados)
    score = sum(valor * peso for valor, peso in considerados) / soma_pesos
    return ScoreColaborativo(
        score=round(score, 1),
        quantidade_reportes=len(considerados),
        janela_inicio=agora - timedelta(hours=janela_horas),
        janela_fim=agora,
    )


def buscar_reportes_proximos(
    db: Session,
    lat: float,
    lon: float,
    agora: datetime,
    raio_m: float = RAIO_METROS,
    janela_horas: float = JANELA_HORAS,
) -> list[ReporteProximo]:
    """Reportes de usuário a até `raio_m` metros e dentro da janela de tempo.

    Duas etapas, padrão do PostGIS para busca por raio com índice: `&&` contra
    um bbox expandido (resolvido pelo GiST, ver T17) e depois ST_DWithin em
    geography para o raio exato em metros — o cast para geography sozinho não
    usaria o índice de `geom`.
    """
    ponto = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
    # Graus de longitude encolhem com a latitude (fator cos(lat)); usar o raio
    # medido em graus de longitude como margem única do bbox garante que ele
    # cobre o círculo inteiro também na direção norte-sul.
    margem_graus = raio_m / (_METROS_POR_GRAU * max(math.cos(math.radians(lat)), 0.1))
    distancia = func.ST_Distance(
        func.Geography(Ocorrencia.geom), func.Geography(ponto)
    ).label("distancia_m")

    stmt = (
        select(Ocorrencia.nivel_risco, Ocorrencia.data_hora, distancia)
        .where(Ocorrencia.fonte == FonteDado.USUARIO.value)
        .where(Ocorrencia.data_hora >= agora - timedelta(hours=janela_horas))
        .where(Ocorrencia.data_hora <= agora)
        .where(Ocorrencia.geom.op("&&")(func.ST_Expand(ponto, margem_graus)))
        .where(func.ST_DWithin(func.Geography(Ocorrencia.geom), func.Geography(ponto), raio_m))
    )
    return [
        ReporteProximo(nivel_risco=n, data_hora=d, distancia_m=float(dist))
        for n, d, dist in db.execute(stmt).all()
    ]


def obter_score_colaborativo(
    db: Session,
    lat: float,
    lon: float,
    agora: datetime | None = None,
    registrar: bool = True,
) -> ScoreColaborativo | None:
    """Busca os reportes próximos, calcula o score e, se houver score, registra
    o agregado em `reportes_colaborativos_agregado` (tabela reservada desde a
    modelagem da Semana 2, T18 seção 4) — fica o histórico de qual valor do
    componente colaborativo entrou em cada classificação. O registro entra na
    sessão sem commit: é gravado junto com a ocorrência que o motivou."""
    agora = agora or datetime.now(timezone.utc)
    resultado = calcular_score_colaborativo(buscar_reportes_proximos(db, lat, lon, agora), agora)
    if resultado is not None and registrar:
        ponto = func.ST_SetSRID(func.ST_MakePoint(lon, lat), 4326)
        db.add(ReporteColaborativoAgregado(
            geom_area=func.ST_Buffer(func.Geography(ponto), RAIO_METROS).cast(
                ReporteColaborativoAgregado.geom_area.type
            ),
            janela_inicio=resultado.janela_inicio,
            janela_fim=resultado.janela_fim,
            score=resultado.score,
            quantidade_reportes=resultado.quantidade_reportes,
        ))
    return resultado
