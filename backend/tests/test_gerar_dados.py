"""
Testes da geração de massa de dados sintética (Semana 7 — Henrique).

Cobre só a parte pura (benchmark/gerar_dados.py) — a parte que fala com o
banco (benchmark/popular_banco.py) não tem como ser testada nesta máquina,
sem Postgres/PostGIS disponível (ver CRONOGRAMA_STATUS.md).
"""

import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

from benchmark.config import BBOX_REGIAO_PILOTO, JANELA_DIAS
from benchmark.gerar_dados import gerar_ocorrencias_sinteticas
from constants import FonteDado, NivelRisco


def test_gera_quantidade_exata():
    for quantidade in (0, 1, 1_000, 10_000):
        assert len(gerar_ocorrencias_sinteticas(quantidade)) == quantidade


def test_coordenadas_dentro_do_bbox():
    lat_min, lon_min, lat_max, lon_max = BBOX_REGIAO_PILOTO
    linhas = gerar_ocorrencias_sinteticas(5_000)
    for linha in linhas:
        assert lat_min <= linha["latitude"] <= lat_max
        assert lon_min <= linha["longitude"] <= lon_max


def test_fonte_e_nivel_risco_sempre_validos():
    linhas = gerar_ocorrencias_sinteticas(5_000)
    for linha in linhas:
        assert linha["fonte"] in list(FonteDado)
        assert linha["nivel_risco"] in list(NivelRisco)


def test_data_hora_dentro_da_janela_configurada():
    agora = datetime.now(timezone.utc)
    limite_inferior = agora - timedelta(days=JANELA_DIAS, minutes=1)  # folga p/ tempo de execução
    linhas = gerar_ocorrencias_sinteticas(2_000)
    for linha in linhas:
        assert limite_inferior <= linha["data_hora"] <= agora


def test_mesma_semente_e_referencia_geram_mesmo_dataset():
    referencia = datetime(2026, 8, 18, 12, 0, 0, tzinfo=timezone.utc)
    a = gerar_ocorrencias_sinteticas(500, semente=7, referencia=referencia)
    b = gerar_ocorrencias_sinteticas(500, semente=7, referencia=referencia)
    assert a == b


def test_mesma_semente_sem_referencia_fixa_pode_variar_em_data_hora():
    # Documenta o comportamento padrão (referencia=None -> datetime.now()):
    # só a semente não basta para reprodutibilidade byte a byte. Achado do
    # teste anterior (18/08) — ver docstring de gerar_ocorrencias_sinteticas.
    a = gerar_ocorrencias_sinteticas(50, semente=7)
    b = gerar_ocorrencias_sinteticas(50, semente=7)
    mesma_estrutura = all(
        {k: v for k, v in la.items() if k != "data_hora"}
        == {k: v for k, v in lb.items() if k != "data_hora"}
        for la, lb in zip(a, b)
    )
    assert mesma_estrutura


def test_sementes_diferentes_geram_datasets_diferentes():
    referencia = datetime(2026, 8, 18, 12, 0, 0, tzinfo=timezone.utc)
    a = gerar_ocorrencias_sinteticas(500, semente=1, referencia=referencia)
    b = gerar_ocorrencias_sinteticas(500, semente=2, referencia=referencia)
    assert a != b


def test_campos_preenchidos_condicionalmente_por_fonte():
    linhas = gerar_ocorrencias_sinteticas(3_000)

    usuarios = [l for l in linhas if l["fonte"] == FonteDado.USUARIO]
    assert usuarios, "esperava pelo menos um registro fonte=usuario na amostra"
    for linha in usuarios:
        assert linha["descricao"] is not None
        assert linha["id_usuario"] is not None
        assert linha["chuva_mm"] is None

    climaticas = [
        l for l in linhas if l["fonte"] in (FonteDado.OPENWEATHER, FonteDado.ANA)
    ]
    assert climaticas, "esperava pelo menos um registro openweather/ana na amostra"
    for linha in climaticas:
        assert linha["chuva_mm"] is not None
        assert linha["temperatura"] is not None
        assert linha["descricao"] is None
