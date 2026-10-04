"""
Endpoint de consulta do risco atual num ponto (03/10/2026).

Até aqui a classificação AHP só era usada dentro do POST /ocorrencias (quando
o usuário não informa o nível). GET /risco expõe a mesma avaliação para
leitura — fusão das fontes climáticas + reportes colaborativos vizinhos + AHP,
com cada componente separado — sem gravar nada. É o que a aba "Previsão" do
app mostra.
"""

from fastapi import APIRouter, Depends, HTTPException, Query

from api.ocorrencias import get_classificador_risco
from api.schemas import RiscoOut
from fusao_climatica import FonteClimaticaIndisponivel
from servicos.classificacao import ClassificadorRiscoProtocol

router = APIRouter(prefix="/risco", tags=["risco"])


@router.get("", response_model=RiscoOut)
def obter_risco(
    latitude: float = Query(ge=-90, le=90),
    longitude: float = Query(ge=-180, le=180),
    classificador: ClassificadorRiscoProtocol = Depends(get_classificador_risco),
) -> RiscoOut:
    try:
        avaliacao = classificador.avaliar(latitude, longitude)
    except FonteClimaticaIndisponivel:
        raise HTTPException(
            status_code=503,
            detail="Dados climáticos indisponíveis no momento; não foi possível calcular o risco.",
        )
    return RiscoOut.model_validate(avaliacao)
