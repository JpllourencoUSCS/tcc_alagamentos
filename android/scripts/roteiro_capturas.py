"""
Capturas de tela do app para o relatório (Semana 14 — Guilherme), geradas no emulador
contra a API real (03/10/2026).

Pré-requisitos:
- Emulador ligado (`adb devices` lista um aparelho) com o app instalado e já com login feito.
- API e banco no ar (`docker compose up -d`) com as ocorrências de demonstração carregadas
  (`python -m dados_demo` em backend/) — recarregar no dia, para "Últimas 24 h" ter dados.
- **MAPS_API_KEY no android/local.properties** antes de gerar o APK, senão o mapa sai em
  branco.
- Para a aba Previsão com dados: OPENWEATHER_API_KEY no .env (senão ela mostra o aviso de
  dados indisponíveis).

Uso (de android/scripts/):

    python roteiro_capturas.py ../../docs/capturas

Gera um PNG por tela. Nas legendas do relatório, identificar as ocorrências como "dados de
demonstração".
"""

import sys
import time
from pathlib import Path

import adb_app as a

CENTRO_SCS = ("-46.5548", "-23.6229")  # longitude, latitude (ordem do "geo fix")


def main(destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    a.adb("emu", "geo", "fix", *CENTRO_SCS)
    a.adb("shell", "am", "force-stop", a.PACOTE)
    a.adb("shell", "am", "start", "-n", f"{a.PACOTE}/.LoginActivity")
    time.sleep(5)

    def foto(nome: str, espera: float = 2.0) -> None:
        time.sleep(espera)
        print(a.captura(destino / f"{nome}.png"))

    a.tocar("nav_mapa", espera=1)
    foto("01_mapa", espera=4)          # tempo para os blocos do mapa carregarem

    a.tocar("nav_alertas", espera=1)
    foto("02_alertas")
    a.tocar("chip_regiao_cidade", espera=1)
    a.tocar("chip_periodo_24h", espera=1)
    a.tocar("chip_alto", espera=1)
    foto("03_alertas_filtrados")
    a.tocar("chip_todos", espera=0.5)
    a.tocar("chip_periodo_todo", espera=0.5)
    a.tocar("chip_regiao_todas", espera=1)

    a.tocar("alerta_titulo", espera=2)  # primeira ocorrência da lista
    foto("04_detalhes")
    a.voltar()

    a.tocar("fab_registrar", espera=2)
    a.tocar("btn_minha_localizacao", espera=4)
    a.tocar("chip_risco_alto", espera=0.5)
    foto("05_cadastro")
    a.voltar()

    a.tocar("nav_previsao", espera=1)
    foto("06_previsao_risco", espera=5)

    a.tocar("nav_ajustes", espera=1)
    foto("07_ajustes")


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "capturas"))
