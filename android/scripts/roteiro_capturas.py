"""
Capturas de tela do app para o relatório (Semana 14 — Guilherme), geradas no emulador
contra a API real (03/10/2026; refeitas e ampliadas em 07/10/2026, com o mapa liberado e
os avisos do INMET na aba Previsão).

Pré-requisitos:
- Emulador ligado (`adb devices` lista um aparelho) com o app instalado e já com login feito,
  em pt-BR e no fuso de São Paulo. Conferir com `adb shell date`: a cada boot o emulador pode
  voltar para GMT (horas 3 h adiantadas). Para corrigir, inclusive o relógio da barra de status:
  `adb root`, `adb shell settings put global auto_time_zone 0` e
  `adb shell cmd time_zone_detector suggest_manual_time_zone --zone_id America/Sao_Paulo`.
- API e banco no ar (`docker compose up -d`) com as ocorrências de demonstração carregadas
  (`python -m dados_demo` em backend/) — recarregar no dia, para "Últimas 24 h" ter dados.
- **MAPS_API_KEY no android/local.properties** antes de gerar o APK, e o SHA-1 do certificado
  que assina o APK cadastrado nas restrições da chave no Google Cloud — senão o mapa sai em
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
# Marcador vermelho (norte, Av. do Estado) no enquadramento das ocorrências de demonstração das
# últimas 24 h (o mapa só mostra essas desde 07/10/2026); dados_demo usa semente fixa
MARCADOR_DEMO = (454, 868)
SENHA_FICTICIA = "teste123"  # o login não valida credenciais (CT-LOG-001)
ENDERECO_DEMO = "Rua Alegre, 100"  # em São Caetano do Sul; sem acentos (o "input text" do adb não aceita)


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

    a.tocar_xy(*MARCADOR_DEMO, espera=1)
    if a.achar("txt_sel_titulo") is not None:
        foto("08_mapa_selecionada")
    else:
        print("08_mapa_selecionada: nenhum marcador no ponto previsto, captura pulada")

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

    a.tocar("nav_mapa", espera=2)
    a.tocar("fab_registrar", espera=4)
    a.digitar("edt_busca_endereco", ENDERECO_DEMO)  # busca por endereço (07/10/2026)
    a.fechar_teclado()
    a.tocar(texto="Buscar endereço", espera=5)      # lupa do campo
    a.tocar("chip_risco_alto", espera=0.5)
    foto("05_cadastro")
    a.voltar()

    a.tocar("nav_previsao", espera=1)
    foto("06_previsao_risco", espera=5)  # risco, avisos do INMET e fontes do cálculo
    a.tocar(texto="Sobre: Pluviômetro local", espera=1)  # cartão ⓘ com a origem do dado
    foto("10_previsao_info_fonte", espera=1)
    a.tocar(texto="Entendi", espera=1)

    a.tocar("nav_ajustes", espera=1)
    foto("07_ajustes")

    a.tocar("card_perfil", espera=2)
    foto("09_perfil")

    # Sai e entra de novo, para capturar o login sem perder a sessão do roteiro
    a.rolar()                           # "Sair" fica no fim da tela de perfil
    a.tocar("btn_sair", espera=3)
    a.digitar("edt_login_senha", SENHA_FICTICIA)
    a.fechar_teclado()
    foto("00_login", espera=1)
    a.tocar("btn_entrar", espera=3)


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "capturas"))
