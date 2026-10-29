"""
Capturas de tela do app para o relatório (Semana 14 — Guilherme), geradas no emulador
contra a API real (03/10/2026; refeitas e ampliadas em 07/10/2026, com o mapa liberado e
os avisos do INMET na aba Previsão).

Pré-requisitos:
- Emulador ligado (`adb devices` lista um aparelho) com o app instalado (APK de depuração,
  para o `run-as` que grava o nome do perfil) e já com a entrada feita, em pt-BR e no fuso de São Paulo. Conferir com `adb shell date`: a cada boot o emulador pode
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
demonstração". Desde 29/10/2026 o perfil das capturas é "João Pedro" (gravado direto nas
preferências do app, porque o `input text` do adb não digita acentos) e a tela de entrada não
tem mais senha.
"""

import re
import tempfile
import sys
import time
from pathlib import Path

import adb_app as a

CENTRO_SCS = ("-46.5548", "-23.6229")  # longitude, latitude (ordem do "geo fix")
# Marcador vermelho (oeste, perto da Cerâmica) no enquadramento das ocorrências de demonstração
# das últimas 24 h (o mapa só mostra essas desde 07/10/2026); dados_demo usa semente fixa. Posição
# refeita em 29/10/2026, depois da correção dos centros de bairro em dados_demo.py
MARCADOR_DEMO = (226, 1236)
NOME_PERFIL = "João Pedro"
OCORRENCIA_DETALHES = "(Boa Vista)"  # risco alto, últimas 24 h, na lista filtrada
ENDERECO_DEMO = "Rua Alegre, 100"  # em São Caetano do Sul; sem acentos (o "input text" do adb não aceita)


def definir_nome_perfil(nome: str) -> None:
    """Grava o nome no perfil (SharedPreferences "perfil") com o app parado; tira o e-mail."""
    a.adb("shell", "am", "force-stop", a.PACOTE)
    xml = a.adb("exec-out", "run-as", a.PACOTE, "cat", "shared_prefs/perfil.xml")
    xml = re.sub(r'\s*<string name="(nome|email)">.*?</string>', "", xml, flags=re.S)
    xml = xml.replace("<map>", f'<map>\n    <string name="nome">{nome}</string>', 1)
    # O exec-in com run-as não grava (testado em 29/10/2026): o arquivo vai para /data/local/tmp
    # e o run-as copia para a pasta do app
    with tempfile.TemporaryDirectory() as tmp:
        local = Path(tmp) / "perfil.xml"
        local.write_text(xml, encoding="utf-8")
        a.adb("push", str(local), "/data/local/tmp/perfil.xml")
    a.adb("shell", "chmod", "644", "/data/local/tmp/perfil.xml")
    a.adb("shell", "run-as", a.PACOTE, "cp", "/data/local/tmp/perfil.xml", "shared_prefs/perfil.xml")
    a.adb("shell", "rm", "/data/local/tmp/perfil.xml")


def main(destino: Path) -> None:
    destino.mkdir(parents=True, exist_ok=True)
    a.adb("emu", "geo", "fix", *CENTRO_SCS)
    definir_nome_perfil(NOME_PERFIL)
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

    # Detalhes de uma ocorrência cujo endereço (geocodificador do Android) confirma o bairro da
    # descrição: perto das divisas, o Android às vezes atribui o bairro vizinho (29/10/2026)
    a.tocar(texto=OCORRENCIA_DETALHES, contem=True, espera=6)
    foto("04_detalhes")
    a.voltar()
    a.tocar("chip_todos", espera=0.5)
    a.tocar("chip_periodo_todo", espera=0.5)
    a.tocar("chip_regiao_todas", espera=1)

    a.tocar("nav_mapa", espera=2)
    a.tocar("fab_registrar", espera=4)
    a.digitar("edt_busca_endereco", ENDERECO_DEMO)  # busca por endereço (07/10/2026)
    a.fechar_teclado()
    a.tocar(texto="Buscar endereço", espera=5)      # lupa do campo
    a.tocar("chip_risco_alto", espera=0.5)
    foto("05_cadastro")
    a.voltar()

    a.tocar("nav_previsao", espera=1)
    foto("06_previsao_risco", espera=12)  # risco, avisos do INMET e fontes do cálculo
    a.tocar(texto="Sobre: Chuva agora", espera=1)  # cartão ⓘ: fontes, regra de fusão e valores
    foto("10_previsao_info_fonte", espera=1)
    a.tocar(texto="Entendi", espera=1)

    a.tocar("nav_ajustes", espera=1)
    foto("07_ajustes")

    a.tocar("card_perfil", espera=2)
    foto("09_perfil")

    # Sai e entra de novo, para capturar a entrada sem perder a sessão do roteiro
    a.rolar()                           # "Sair" fica no fim da tela de perfil
    a.tocar("btn_sair", espera=3)       # a entrada já vem com o nome do perfil
    a.fechar_teclado()
    foto("00_login", espera=1)
    a.tocar("btn_entrar", espera=3)


if __name__ == "__main__":
    main(Path(sys.argv[1] if len(sys.argv) > 1 else "capturas"))
