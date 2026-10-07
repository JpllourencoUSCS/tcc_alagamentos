"""
Testes da integração com o INMET (apiprevmet3), que substituiu o CPTEC em 06/10/2026
como validação cruzada qualitativa (fora do AHP). As respostas simuladas seguem a
estrutura real observada em 06/10/2026 para São Caetano do Sul (código IBGE 3548807),
sem os ícones em base64.
"""

import sys
from datetime import datetime, timezone
from pathlib import Path
from unittest.mock import MagicMock, patch

sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

import pytest
import requests

import fusao_climatica as fc

SCS = "3548807"


def _turno(resumo):
    return {"resumo": resumo, "temp_max": 20, "temp_min": 17, "entidade": "São Caetano do Sul", "uf": "SP"}


DIAS = {
    "06/10/2026": {"manha": _turno("Pancadas de chuva e trovoadas isoladas"),
                   "tarde": _turno("Muitas nuvens com chuva"),
                   "noite": _turno("Chuva fraca")},
    "07/10/2026": {"manha": _turno("Muitas nuvens"), "tarde": _turno("Nublado"),
                   "noite": _turno("Muitas nuvens com chuva isolada")},
    "08/10/2026": _turno("Muitas nuvens com chuva isolada"),  # dia 3+: resumo único
}

AVISOS_BRUTO = {
    "hoje": [
        {"descricao": "Tempestade", "severidade": "Perigo Potencial", "aviso_cor": "#FFFE00",
         "inicio": "2026-10-06 08:52", "fim": "2026-10-06 23:59",
         "riscos": ["Chuva entre 20 e 30 mm/h ou até 50 mm/dia.", "Baixo risco de alagamentos."],
         "geocodes": "3547809,3548807,3548708", "poligono": "{...}"},
        {"descricao": "Chuvas Intensas", "severidade": "Perigo", "aviso_cor": "#F96602",
         "inicio": "2026-10-06 10:00", "fim": "2026-10-07 10:00", "riscos": "x",
         "geocodes": "2300101,2900108"},  # outro estado
    ],
    "futuro": [
        {"descricao": "Tempestade", "severidade": "Perigo Potencial", "aviso_cor": "#FFFE00",
         "inicio": "2026-10-07 00:00", "fim": "2026-10-07 23:59", "riscos": ["y"],
         "geocodes": " 3548807 "},
    ],
}


def _brasilia(dia, hora):
    return datetime(2026, 10, dia, hora, 0, tzinfo=fc.FUSO_BRASILIA)


@pytest.fixture(autouse=True)
def _cache_limpo():
    fc.limpar_cache()
    yield
    fc.limpar_cache()


# ---------- Previsão (puras) ----------

@pytest.mark.parametrize("hora, turno", [(6, "manha"), (11, "manha"), (12, "tarde"),
                                         (17, "tarde"), (18, "noite"), (23, "noite"), (3, "noite")])
def test_turno_por_hora(hora, turno):
    assert fc.turno_inmet(hora) == turno


def test_resumo_do_turno_atual():
    assert fc.resumo_previsao_inmet(DIAS, _brasilia(6, 9)) == "Pancadas de chuva e trovoadas isoladas"
    assert fc.resumo_previsao_inmet(DIAS, _brasilia(6, 15)) == "Muitas nuvens com chuva"
    assert fc.resumo_previsao_inmet(DIAS, _brasilia(7, 20)) == "Muitas nuvens com chuva isolada"


def test_resumo_usa_horario_de_brasilia_mesmo_com_instante_em_utc():
    # 02:00 UTC de 07/10 = 23:00 de 06/10 em Brasília -> noite de 06/10
    agora_utc = datetime(2026, 10, 7, 2, 0, tzinfo=timezone.utc)
    assert fc.resumo_previsao_inmet(DIAS, agora_utc) == "Chuva fraca"


def test_madrugada_usa_a_noite_do_dia_anterior():
    assert fc.resumo_previsao_inmet(DIAS, _brasilia(7, 3)) == "Chuva fraca"


def test_dia_sem_turnos_usa_resumo_unico():
    assert fc.resumo_previsao_inmet(DIAS, _brasilia(8, 15)) == "Muitas nuvens com chuva isolada"


def test_data_fora_da_resposta_usa_o_primeiro_dia_disponivel():
    assert fc.resumo_previsao_inmet(DIAS, _brasilia(5, 9)) == "Pancadas de chuva e trovoadas isoladas"


def test_resposta_vazia():
    assert fc.resumo_previsao_inmet({}, _brasilia(6, 9)) is None


# ---------- Avisos (puras) ----------

def test_filtra_avisos_do_municipio_em_hoje_e_futuro():
    avisos = fc.filtrar_avisos_inmet(AVISOS_BRUTO, SCS)
    assert [a["inicio"] for a in avisos] == ["2026-10-06 08:52", "2026-10-07 00:00"]
    assert avisos[0] == {
        "evento": "Tempestade", "severidade": "Perigo Potencial", "cor": "#FFFE00",
        "inicio": "2026-10-06 08:52", "fim": "2026-10-06 23:59",
        "riscos": "Chuva entre 20 e 30 mm/h ou até 50 mm/dia. Baixo risco de alagamentos.",
    }
    assert "poligono" not in avisos[0]


def test_avisos_em_lista_simples_e_sem_aviso_para_o_municipio():
    assert fc.filtrar_avisos_inmet(AVISOS_BRUTO["hoje"], "1111111") == []
    assert len(fc.filtrar_avisos_inmet(AVISOS_BRUTO["hoje"], SCS)) == 1


# ---------- Piso da classificação pelos avisos (07/10/2026) ----------

def _aviso(evento="Tempestade", severidade="Perigo", inicio="2026-10-07 12:00", fim="2026-10-07 23:59",
           riscos="Chuva entre 30 e 60 mm/h. Risco de alagamentos."):
    return {"evento": evento, "severidade": severidade, "cor": "#F96602",
            "inicio": inicio, "fim": fim, "riscos": riscos}


AGORA = _brasilia(7, 15)  # 07/10 15:00 em Brasília


@pytest.mark.parametrize("severidade, piso", [
    ("Perigo Potencial", None),   # INMET: "baixo risco de alagamentos"
    ("Perigo", "Médio"),          # "risco de alagamentos"
    ("Grande Perigo", "Alto"),    # "grande risco de grandes alagamentos"
])
def test_piso_segue_a_severidade_do_aviso(severidade, piso):
    resultado = fc.piso_por_avisos([_aviso(severidade=severidade)], AGORA)
    assert (resultado["nivel"] if resultado else None) == piso


@pytest.mark.parametrize("evento", ["Tempestade", "Chuvas Intensas", "Acumulado de Chuva"])
def test_avisos_de_chuva_impoem_piso(evento):
    assert fc.piso_por_avisos([_aviso(evento=evento)], AGORA)["evento"] == evento


def test_aviso_que_nao_e_de_chuva_nao_impoe_piso():
    aviso = _aviso(evento="Baixa Umidade", severidade="Grande Perigo",
                   riscos="Umidade relativa do ar abaixo de 12%. Grande risco à saúde.")
    assert fc.piso_por_avisos([aviso], AGORA) is None


def test_evento_desconhecido_que_menciona_alagamento_conta_como_chuva():
    assert fc.piso_por_avisos([_aviso(evento="Ciclone", riscos="Risco de alagamentos")], AGORA)["nivel"] == "Médio"


def test_so_avisos_vigentes_contam():
    amanha = _aviso(inicio="2026-10-08 00:00", fim="2026-10-08 23:59")
    ontem = _aviso(inicio="2026-10-06 00:00", fim="2026-10-06 23:59")
    assert fc.piso_por_avisos([amanha, ontem], AGORA) is None
    # 23:30 em Brasília = 02:30 UTC do dia seguinte: o aviso até 23:59 ainda vale
    assert fc.piso_por_avisos([_aviso()], datetime(2026, 10, 8, 2, 30, tzinfo=timezone.utc)) is not None


def test_com_varios_avisos_vale_o_maior_piso():
    piso = fc.piso_por_avisos([_aviso(severidade="Perigo"), _aviso(evento="Acumulado de Chuva",
                                                                    severidade="Grande Perigo")], AGORA)
    assert piso == {"nivel": "Alto", "evento": "Acumulado de Chuva", "severidade": "Grande Perigo"}


def test_aviso_com_datas_invalidas_e_ignorado():
    assert fc.piso_por_avisos([_aviso(inicio=None)], AGORA) is None


@pytest.mark.parametrize("classe, piso, esperado", [
    ("Baixo", "Médio", "Médio"), ("Baixo", "Alto", "Alto"),
    ("Alto", "Médio", "Alto"),    # piso nunca reduz
    ("Médio", None, "Médio"),
])
def test_aplicar_piso(classe, piso, esperado):
    assert fc.aplicar_piso(classe, {"nivel": piso} if piso else None) == esperado


def test_classificar_risco_eleva_a_classe_mas_nao_o_score():
    seco = fc.DadosClimaticosConsolidados(
        lat=-23.62, lon=-46.55, precipitacao_atual_mm_h=0.0, pico_previsto_mm_3h=0.0,
        fonte_precipitacao_atual="OpenWeather", fonte_previsao="OpenWeather",
        avisos_inmet=[_aviso(severidade="Perigo")],
    )
    sem_aviso = fc.classificar_risco(fc.DadosClimaticosConsolidados(
        lat=-23.62, lon=-46.55, precipitacao_atual_mm_h=0.0, pico_previsto_mm_3h=0.0,
        fonte_precipitacao_atual="OpenWeather", fonte_previsao="OpenWeather"), agora=AGORA)
    com_aviso = fc.classificar_risco(seco, agora=AGORA)

    assert sem_aviso["classificacao"] == sem_aviso["classificacao_indice"] == "Baixo"
    assert sem_aviso["piso_aviso_inmet"] is None
    assert com_aviso["classificacao_indice"] == "Baixo"
    assert com_aviso["classificacao"] == "Médio"
    assert com_aviso["score_final"] == sem_aviso["score_final"]
    assert com_aviso["piso_aviso_inmet"]["severidade"] == "Perigo"


# ---------- Busca (rede simulada) ----------

def _resposta(json_):
    r = MagicMock()
    r.json.return_value = json_
    r.raise_for_status.return_value = None
    return r


def test_busca_previsao_envia_user_agent_e_extrai_resumo():
    with patch.object(fc.requests, "get", return_value=_resposta({SCS: DIAS})) as get:
        resumo = fc._buscar_inmet_previsao(SCS, agora=_brasilia(6, 20))
    assert resumo == "Chuva fraca"
    assert get.call_args.kwargs["headers"]["User-Agent"].startswith("Mozilla/5.0")
    assert get.call_args.args[0].endswith(f"/previsao/{SCS}")


@pytest.mark.parametrize("erro", [requests.exceptions.ConnectionError("fora"),
                                  requests.exceptions.HTTPError("403")])
def test_falha_do_inmet_vira_none_fail_safe(erro):
    with patch.object(fc.requests, "get", side_effect=erro):
        assert fc._buscar_inmet_previsao(SCS) is None
        assert fc._buscar_inmet_avisos(SCS) is None


def test_previsao_fica_em_cache_por_municipio_por_10_min():
    with patch.object(fc.requests, "get", return_value=_resposta({SCS: DIAS})) as get:
        assert fc._buscar_inmet_previsao(SCS, agora=_brasilia(6, 9), instante=0) == "Pancadas de chuva e trovoadas isoladas"
        # mesmo dado em cache, mas o turno é recalculado para o novo horário
        assert fc._buscar_inmet_previsao(SCS, agora=_brasilia(6, 20), instante=300) == "Chuva fraca"
        assert get.call_count == 1
        fc._buscar_inmet_previsao(SCS, instante=fc.CACHE_TTL_S + 1)
        assert get.call_count == 2


def test_lista_de_avisos_fica_em_cache_por_10_min():
    with patch.object(fc.requests, "get", return_value=_resposta(AVISOS_BRUTO)) as get:
        fc._buscar_inmet_avisos(SCS, agora=0)
        fc._buscar_inmet_avisos(SCS, agora=300)
        assert get.call_count == 1
        fc._buscar_inmet_avisos(SCS, agora=fc.CACHE_TTL_S + 1)
        assert get.call_count == 2
