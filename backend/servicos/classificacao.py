"""
Wrapper fino sobre fusao_climatica (Semana 5 — Henrique, reconstruído em
18/08/2026): isola o endpoint de criação de ocorrências da chamada real às
APIs externas (OpenWeather/ANA/CPTEC), pelo mesmo motivo de
db/repository.py isolar o SQLAlchemy — fusao_climatica.obter_dados_consolidados
faz requests HTTP de verdade, o que não pode rodar em teste automatizado sem
rede e credenciais (ANA_IDENTIFICADOR/ANA_SENHA).

03/10/2026: passa a usar o cache de dados climáticos (~1 km / 10 min) e o
agregador de reportes colaborativos (servicos/colaborativo.py) — até então o
componente colaborativo (15%) entrava sempre como None no AHP.
"""

from typing import Protocol

from sqlalchemy.orm import Session

from fusao_climatica import classificar_risco, obter_dados_consolidados_em_cache
from servicos.colaborativo import obter_score_colaborativo


class ClassificadorRiscoProtocol(Protocol):
    def classificar(self, lat: float, lon: float) -> dict: ...
    def avaliar(self, lat: float, lon: float) -> dict: ...


class ClassificadorRiscoReal:
    """Implementação real: fusão de fontes + reportes colaborativos + AHP.

    Devolve só o que o endpoint precisa gravar (classificação e a precipitação
    atual usada no cálculo), mais o score final e o colaborativo para quem
    quiser registrar/inspecionar — o resto do resultado da fusão (previsão,
    fontes, validação CPTEC) não é persistido em `ocorrencias` hoje.

    Lança fusao_climatica.FonteClimaticaIndisponivel se o OpenWeather (fonte
    principal) falhar — a API traduz em 503.
    """

    def __init__(self, db: Session | None = None):
        self.db = db

    def classificar(self, lat: float, lon: float) -> dict:
        dados, _ = obter_dados_consolidados_em_cache(lat, lon)
        colaborativo = obter_score_colaborativo(self.db, lat, lon) if self.db is not None else None
        resultado = classificar_risco(
            dados,
            reportes_colaborativos_score=colaborativo.score if colaborativo else None,
        )
        return {
            "classificacao": resultado["classificacao"],
            "chuva_mm": dados.precipitacao_atual_mm_h,
            # Previsão textual do INMET gravada como contexto da ocorrência (06/10/2026)
            "descricao_clima": dados.previsao_inmet,
            "score_final": resultado["score_final"],
            "score_colaborativo": colaborativo.score if colaborativo else None,
        }

    def avaliar(self, lat: float, lon: float) -> dict:
        """Avaliação completa do risco num ponto, sem gravar nada (GET /risco,
        03/10/2026): classificação, score, cada componente do AHP e os dados
        brutos usados — o que a aba "Previsão" do app mostra."""
        dados, do_cache = obter_dados_consolidados_em_cache(lat, lon)
        colaborativo = (
            obter_score_colaborativo(self.db, lat, lon, registrar=False)
            if self.db is not None else None
        )
        resultado = classificar_risco(
            dados,
            reportes_colaborativos_score=colaborativo.score if colaborativo else None,
        )
        # algoritmo_risco devolve texto ("N/A (...)") para componente ausente;
        # na API, ausência é null
        componentes = {
            nome: valor if isinstance(valor, (int, float)) else None
            for nome, valor in resultado["componentes"].items()
        }
        return {
            "latitude": lat,
            "longitude": lon,
            "classificacao": resultado["classificacao"],
            # Classe do AHP antes do piso dos avisos do INMET, e o aviso que elevou (se algum)
            "classificacao_indice": resultado["classificacao_indice"],
            "piso_aviso_inmet": resultado["piso_aviso_inmet"],
            "score_final": resultado["score_final"],
            "componentes": componentes,
            "precipitacao_atual_mm_h": dados.precipitacao_atual_mm_h,
            "pico_previsto_mm_3h": dados.pico_previsto_mm_3h,
            "pluviometro_local_mm_h": dados.pluviometro_local_mm_h,
            "reportes_colaborativos": colaborativo.quantidade_reportes if colaborativo else 0,
            "previsao_inmet": dados.previsao_inmet,
            "avisos_inmet": dados.avisos_inmet,
            "fontes": resultado["fontes"],
            "dados_em_cache": do_cache,
        }
