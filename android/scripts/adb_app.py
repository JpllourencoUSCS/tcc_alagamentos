"""
Automação simples do app no emulador via adb (03/10/2026) — usada para testar o
app contra a API real e gerar as capturas de tela do relatório sem depender de
Android Studio.

Uso como biblioteca (ver roteiro_capturas.py) ou pela linha de comando:

    python adb_app.py ids                      # lista resource-ids/textos da tela
    python adb_app.py toque-id btn_entrar      # toca no elemento pelo id
    python adb_app.py toque-texto Alertas      # toca no elemento pelo texto
    python adb_app.py digitar edt_login_usuario "Maria"
    python adb_app.py captura saida.png

Requer o adb do Android SDK (padrão: %LOCALAPPDATA%\\Android\\Sdk\\platform-tools).
"""

import os
import re
import subprocess
import sys
import time
import xml.etree.ElementTree as ET
from pathlib import Path

PACOTE = "com.example.alagamentos"
ADB = os.environ.get(
    "ADB", str(Path(os.environ.get("LOCALAPPDATA", "")) / "Android/Sdk/platform-tools/adb.exe")
)


def adb(*args: str, binario: bool = False):
    resultado = subprocess.run([ADB, *args], capture_output=True, check=True)
    return resultado.stdout if binario else resultado.stdout.decode("utf-8", "replace")


def tela() -> ET.Element:
    adb("shell", "uiautomator", "dump", "/sdcard/ui.xml")
    return ET.fromstring(adb("shell", "cat", "/sdcard/ui.xml"))


def _centro(no: ET.Element) -> tuple[int, int]:
    x1, y1, x2, y2 = map(int, re.findall(r"\d+", no.get("bounds")))
    return (x1 + x2) // 2, (y1 + y2) // 2


def achar(id_: str | None = None, texto: str | None = None, contem: bool = False) -> ET.Element | None:
    for no in tela().iter("node"):
        if id_ and no.get("resource-id") == f"{PACOTE}:id/{id_}":
            return no
        if texto is not None:
            valor = no.get("text") or no.get("content-desc") or ""
            if (texto in valor) if contem else (valor == texto):
                return no
    return None


def tocar(id_: str | None = None, texto: str | None = None, contem: bool = False, espera: float = 1.5) -> None:
    no = achar(id_, texto, contem)
    if no is None:
        raise SystemExit(f"elemento não encontrado: id={id_} texto={texto}")
    adb("shell", "input", "touchscreen", "tap", *map(str, _centro(no)))
    time.sleep(espera)


def tocar_xy(x: int, y: int, espera: float = 1.5) -> None:
    adb("shell", "input", "touchscreen", "tap", str(x), str(y))
    time.sleep(espera)


def digitar(id_: str, texto: str) -> None:
    tocar(id_, espera=0.5)
    # input text não aceita espaço literal nem acentos: espaço vira %s
    adb("shell", "input", "text", texto.replace(" ", "%s"))
    time.sleep(0.5)


def fechar_teclado(espera: float = 1.0) -> None:
    """ESC, não BACK: o BACK às vezes fecha a tela junto com o teclado."""
    if "mInputShown=true" in adb("shell", "dumpsys", "input_method"):
        adb("shell", "input", "keyevent", "KEYCODE_ESCAPE")
        time.sleep(espera)


def voltar(espera: float = 1.5) -> None:
    adb("shell", "input", "keyevent", "KEYCODE_BACK")
    time.sleep(espera)


def rolar(de_y: int = 1800, ate_y: int = 600, espera: float = 1.0) -> None:
    adb("shell", "input", "touchscreen", "swipe", "540", str(de_y), "540", str(ate_y), "300")
    time.sleep(espera)


def captura(caminho: str | Path) -> Path:
    caminho = Path(caminho)
    caminho.parent.mkdir(parents=True, exist_ok=True)
    caminho.write_bytes(adb("exec-out", "screencap", "-p", binario=True))
    return caminho


def ids() -> list[str]:
    saida = []
    for no in tela().iter("node"):
        rid = (no.get("resource-id") or "").replace(f"{PACOTE}:id/", "")
        txt = no.get("text") or no.get("content-desc") or ""
        if rid.startswith("android:") or not (rid or txt):
            continue
        saida.append(f"{rid or '-':<32} {txt[:60]!r:<64} {no.get('bounds')}")
    return saida


if __name__ == "__main__":
    comando, *args = sys.argv[1:] or ["ids"]
    if comando == "ids":
        print("\n".join(ids()))
    elif comando == "toque-id":
        tocar(id_=args[0])
    elif comando == "toque-texto":
        tocar(texto=args[0], contem=True)
    elif comando == "digitar":
        digitar(args[0], args[1])
    elif comando == "captura":
        print(captura(args[0]))
    else:
        raise SystemExit(__doc__)
