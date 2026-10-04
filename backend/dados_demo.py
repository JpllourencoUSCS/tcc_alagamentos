"""
Dados de demonstração em São Caetano do Sul (03/10/2026) — para testar o app
contra a API real, conduzir os testes de usabilidade e tirar as capturas de
tela do relatório sem depender de chuva de verdade.

Não são dados reais: toda linha criada aqui leva `id_usuario = 'demo-seed'`
(marcador usado para removê-las) e deve ser apresentada como "dados de
demonstração" em qualquer captura usada no relatório.

Uso (de backend/, com DATABASE_URL apontando para o banco):

    python -m dados_demo            # insere (se ainda não houver dados demo)
    python -m dados_demo --limpar   # remove só as linhas demo
"""

import argparse
import random
from datetime import datetime, timedelta, timezone

from sqlalchemy import delete, func, select

from constants import FonteDado, NivelRisco
from db.models import Ocorrencia
from db.session import SessionLocal

MARCADOR = "demo-seed"

# Centro aproximado de bairros de São Caetano do Sul
BAIRROS = {
    "Centro": (-23.6229, -46.5548),
    "Barcelona": (-23.6262, -46.5634),
    "Santa Paula": (-23.6155, -46.5651),
    "Santa Maria": (-23.6309, -46.5728),
    "Cerâmica": (-23.6150, -46.5745),
    "Fundação": (-23.6098, -46.5594),
    "Nova Gerty": (-23.6359, -46.5634),
    "Oswaldo Cruz": (-23.6300, -46.5480),
    "Olímpico": (-23.6255, -46.5460),
    "Prosperidade": (-23.6175, -46.5440),
    "Mauá": (-23.6105, -46.5490),
    "Boa Vista": (-23.6210, -46.5700),
}

DESCRICOES = {
    NivelRisco.ALTO: [
        "Rua tomada pela água, carros não passam.",
        "Água acima do meio-fio entrando nas garagens.",
        "Alagamento total perto do córrego.",
    ],
    NivelRisco.MEDIO: [
        "Água acumulando na esquina, trânsito lento.",
        "Bueiro transbordando, pista parcialmente alagada.",
    ],
    NivelRisco.BAIXO: [
        "Poças grandes, mas dá para passar.",
        "Chuva fraca, sem acúmulo de água por enquanto.",
    ],
}

CLIMA = {
    NivelRisco.ALTO: ("Chuva forte", 28.0),
    NivelRisco.MEDIO: ("Chuva moderada", 6.5),
    NivelRisco.BAIXO: ("Chuva fraca", 0.8),
}


def gerar(agora: datetime, semente: int = 7) -> list[dict]:
    """Pura — ~30 ocorrências espalhadas nos últimos 10 dias, com um episódio
    de chuva forte nas últimas horas (para o mapa e os alertas terem o que
    mostrar em todas as faixas de período do filtro)."""
    rng = random.Random(semente)
    linhas = []
    for i in range(30):
        bairro, (lat, lon) = rng.choice(list(BAIRROS.items()))
        recente = i < 8  # 8 ocorrências nas últimas 6 h
        idade = timedelta(hours=rng.uniform(0.1, 6)) if recente else timedelta(days=rng.uniform(0.3, 10))
        nivel = rng.choices(
            list(NivelRisco), weights=[1, 3, 4] if recente else [4, 3, 1]
        )[0]
        fonte = rng.choices([FonteDado.USUARIO, FonteDado.OPENWEATHER], weights=[3, 1])[0]
        linha = {
            "latitude": round(lat + rng.uniform(-0.003, 0.003), 6),
            "longitude": round(lon + rng.uniform(-0.003, 0.003), 6),
            "data_hora": agora - idade,
            "nivel_risco": nivel.value,
            "fonte": fonte.value,
            "id_usuario": MARCADOR,
            "descricao": None,
            "chuva_mm": None,
            "descricao_clima": None,
            "temperatura": None,
            "umidade": None,
        }
        if fonte == FonteDado.USUARIO:
            linha["descricao"] = f"{rng.choice(DESCRICOES[nivel])} ({bairro})"
        else:
            descricao_clima, chuva = CLIMA[nivel]
            linha["descricao_clima"] = descricao_clima
            linha["chuva_mm"] = round(chuva * rng.uniform(0.7, 1.3), 1)
            linha["temperatura"] = round(rng.uniform(17, 24), 1)
            linha["umidade"] = rng.randint(80, 98)
        linhas.append(linha)
    return linhas


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limpar", action="store_true", help="Remove as linhas demo e sai.")
    args = parser.parse_args()

    with SessionLocal() as db:
        existentes = db.scalar(
            select(func.count()).select_from(Ocorrencia).where(Ocorrencia.id_usuario == MARCADOR)
        )
        if args.limpar:
            db.execute(delete(Ocorrencia).where(Ocorrencia.id_usuario == MARCADOR))
            db.commit()
            print(f"{existentes} ocorrências demo removidas.")
            return
        if existentes:
            print(f"Já existem {existentes} ocorrências demo (use --limpar para recriar).")
            return
        linhas = gerar(datetime.now(timezone.utc))
        db.add_all(Ocorrencia(**linha) for linha in linhas)
        db.commit()
        print(f"{len(linhas)} ocorrências demo inseridas em São Caetano do Sul.")


if __name__ == "__main__":
    main()
