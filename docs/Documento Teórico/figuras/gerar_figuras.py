"""Figuras do documento teórico (arquitetura, fluxo do risco, DER, Gantt e painéis de telas).

Rodar a partir da raiz do repositório:
    .venv\\Scripts\\python.exe "docs/Documento Teórico/figuras/gerar_figuras.py"

As telas do app vêm de docs/capturas/ (ocorrências de demonstração, não alagamentos reais).
"""
from datetime import date
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.dates as mdates  # noqa: E402
import matplotlib.pyplot as plt  # noqa: E402
from matplotlib.patches import FancyArrowPatch, FancyBboxPatch, Patch  # noqa: E402
from PIL import Image, ImageDraw, ImageFont  # noqa: E402

RAIZ = Path(__file__).resolve().parents[3]
SAIDA = Path(__file__).resolve().parent
CAPTURAS = RAIZ / "docs" / "capturas"

plt.rcParams.update({"font.family": "Arial", "font.size": 10})

AZUL = "#dbe8f6"
VERDE = "#e0f0e3"
LARANJA = "#fbe9d7"
CINZA = "#eeeeee"
VERMELHO = "#f8dcdc"
BORDA = "#333333"
ESC = {"v": 1.0}


def caixa(ax, x, y, w, h, titulo, linhas=(), cor=AZUL, tam=9, negrito=True):
    ax.add_patch(FancyBboxPatch((x, y), w, h, boxstyle="round,pad=0.02,rounding_size=0.08",
                                fc=cor, ec=BORDA, lw=1))
    if linhas:
        ax.text(x + w / 2, y + h - 0.18, titulo, ha="center", va="top", fontsize=(tam + 1) * ESC["v"],
                fontweight="bold" if negrito else "normal")
        ax.text(x + w / 2, y + h - 0.55, "\n".join(linhas), ha="center", va="top", fontsize=tam * ESC["v"],
                linespacing=1.35)
    else:
        ax.text(x + w / 2, y + h / 2, titulo, ha="center", va="center", fontsize=tam * ESC["v"],
                fontweight="bold" if negrito else "normal", linespacing=1.3)


def seta(ax, a, b, texto=None, estilo="-|>", cor=BORDA, tracejada=False, desloc=(0, 0.12), tam=8,
         ha="center"):
    ax.add_patch(FancyArrowPatch(a, b, arrowstyle=estilo, mutation_scale=12, color=cor, lw=1.1,
                                 linestyle="--" if tracejada else "-"))
    if texto:
        ax.text((a[0] + b[0]) / 2 + desloc[0], (a[1] + b[1]) / 2 + desloc[1], texto, ha=ha,
                va="bottom", fontsize=tam, color=cor)


def salvar(fig, nome):
    fig.savefig(SAIDA / nome, dpi=200, bbox_inches="tight", facecolor="white")
    plt.close(fig)
    print("ok", nome)


def arquitetura():
    ESC["v"] = 1.1
    fig, ax = plt.subplots(figsize=(10, 6.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 6.2)
    ax.axis("off")

    caixa(ax, 0.1, 2.0, 2.4, 2.9, "Aplicativo Android",
          ["Kotlin + XML (Views)", "Google Maps SDK", "Retrofit (HTTP/JSON)",
           "Geocodificador do Android", "SharedPreferences", "(perfil e preferências)"], cor=VERDE)

    ax.add_patch(FancyBboxPatch((2.95, 0.9), 4.1, 5.0, boxstyle="round,pad=0.02,rounding_size=0.1",
                                fc="white", ec=BORDA, lw=1, ls="--"))
    ax.text(5.0, 5.75, "Contêiner Docker", ha="center", fontsize=8, style="italic")
    caixa(ax, 3.1, 4.45, 3.8, 1.05, "API REST (FastAPI)",
          ["POST/GET /ocorrencias · GET /risco", "validação Pydantic · OpenAPI em /docs"])
    caixa(ax, 3.1, 2.65, 3.8, 1.6, "Serviços de domínio",
          ["classificação de risco (orquestração)", "agregação colaborativa (1 km, 3 h)",
           "fusão climática + cache de 10 min", "algoritmo AHP (54/30/16) + piso INMET"])
    caixa(ax, 3.1, 1.1, 3.8, 1.3, "Repositório de dados",
          ["SQLAlchemy + GeoAlchemy2", "interface substituível nos testes"])

    caixa(ax, 7.5, 0.3, 2.4, 1.6, "Banco de dados",
          ["PostgreSQL 16 + PostGIS 3.4", "pontos em SRID 4326", "índice GiST em geom"], cor=CINZA, tam=8)
    caixa(ax, 7.5, 2.2, 2.4, 3.9, "Serviços externos",
          ["OpenWeather", "chuva atual e previsão", "(chave de API)", "",
           "Open-Meteo", "chuva atual e previsão", "(sem chave)", "",
           "INMET (apiprevmet3)", "previsão textual e avisos", "",
           "5 chamadas em paralelo,", "limite de 10 s cada"], cor=LARANJA)

    seta(ax, (2.5, 3.9), (3.1, 4.9))
    seta(ax, (3.1, 4.65), (2.5, 3.6))
    ax.text(2.45, 4.45, "HTTP/JSON", fontsize=8.5, rotation=58)
    seta(ax, (5.0, 4.45), (5.0, 4.2))
    seta(ax, (5.0, 2.75), (5.0, 2.45))
    seta(ax, (6.9, 1.6), (7.5, 1.2))
    ax.text(7.2, 1.55, "SQL", fontsize=8.5, ha="center")
    seta(ax, (6.9, 3.5), (7.5, 4.0))
    ax.text(7.2, 3.95, "HTTPS", fontsize=8.5, ha="center")
    salvar(fig, "fig_arquitetura.png")


def fluxo_risco():
    ESC["v"] = 1.2
    fig, ax = plt.subplots(figsize=(10, 7.8))
    ax.set_xlim(0, 10)
    ax.set_ylim(-0.6, 7.2)
    ax.axis("off")
    w, h, x = 5.35, 0.62, 0.0
    etapas = [
        ("1. Coleta em paralelo (cache de 10 min por célula de ~1 km)\nOpenWeather atual e previsão · Open-Meteo\nINMET previsão e avisos", AZUL),
        ("2. Unidades comuns\nchuva atual em mm/h · previsão: maior acumulado\nde 3 h nas próximas 24 h", AZUL),
        ("3. Fusão OpenWeather × Open-Meteo\nvale o MAIOR valor · divergência registrada", AZUL),
        ("4. Conversão para escala 0–100\nfaixas de intensidade de chuva", AZUL),
        ("5. Componente colaborativo\nrelatos a até 1 km, últimas 3 h, mínimo de 2", VERDE),
        ("6. AHP: score = 0,54·P + 0,30·F + 0,16·C\nsem relatos: 64,3% · 35,7%", AZUL),
        ("7. Classe: Baixo < 30 ≤ Médio < 60 ≤ Alto", AZUL),
        ("8. Piso dos avisos do INMET vigentes\nPerigo → mín. Médio · Grande Perigo → Alto", LARANJA),
    ]
    ys = [6.45 - i * 0.84 for i in range(len(etapas))]
    for (t, c), y in zip(etapas, ys):
        caixa(ax, x, y, w, h, t, cor=c, tam=8, negrito=False)
    for y0, y1 in zip(ys, ys[1:]):
        seta(ax, (x + w / 2, y0), (x + w / 2, y1 + h))
    caixa(ax, x + 0.775, ys[-1] - 0.85, 3.8, 0.55, "Resposta: score, classe, componentes,\nfusão e aviso aplicado",
          cor=CINZA, tam=8, negrito=False)
    seta(ax, (x + w / 2, ys[-1]), (x + w / 2, ys[-1] - 0.25))

    ex, ew = 5.55, 4.3
    caixa(ax, ex, ys[2] + 0.35, ew, 0.62,
          "Só uma das duas fontes respondeu\n→ usa a disponível (cálculo continua)", cor=VERDE, tam=8, negrito=False)
    caixa(ax, ex, ys[2] - 0.55, ew, 0.75,
          "Nenhuma das duas respondeu → HTTP 503;\no app pede que o usuário informe\no nível manualmente", cor=VERMELHO, tam=8, negrito=False)
    caixa(ax, ex, ys[4], ew, 0.62,
          "Menos de 2 relatos na vizinhança\n→ componente ausente; peso redistribuído", cor=VERDE, tam=8, negrito=False)
    caixa(ax, ex, ys[7], ew, 0.62,
          "INMET indisponível\n→ classificação sem piso (não interrompe)", cor=VERDE, tam=8, negrito=False)
    seta(ax, (x + w, ys[2] + h / 2), (ex, ys[2] + 0.66), tracejada=True)
    seta(ax, (x + w, ys[2] + h / 2), (ex, ys[2] - 0.17), tracejada=True)
    seta(ax, (x + w, ys[4] + h / 2), (ex, ys[4] + 0.31), tracejada=True)
    seta(ax, (x + w, ys[7] + h / 2), (ex, ys[7] + 0.31), tracejada=True)
    ax.text(ex + ew / 2, 6.85, "Caminhos de falha (tracejado)", ha="center", fontsize=11.5, fontweight="bold")
    salvar(fig, "fig_fluxo_risco.png")


def der():
    ESC["v"] = 1.1
    fig, ax = plt.subplots(figsize=(10, 4.2))
    ax.set_xlim(0, 10)
    ax.set_ylim(1.3, 5.6)
    ax.axis("off")

    def tabela(x, y_topo, nome, colunas, largura=3.0):
        lh = 0.27
        alt = lh * (len(colunas) + 1) + 0.1
        ax.add_patch(plt.Rectangle((x, y_topo - alt), largura, alt, fc="white", ec=BORDA))
        ax.add_patch(plt.Rectangle((x, y_topo - lh - 0.05), largura, lh + 0.05, fc=AZUL, ec=BORDA))
        ax.text(x + largura / 2, y_topo - lh / 2 - 0.02, nome, ha="center", va="center", fontweight="bold",
                fontsize=9 * ESC["v"])
        for i, (c, t) in enumerate(colunas):
            yy = y_topo - lh * (i + 1.5) - 0.07
            ax.text(x + 0.08, yy, c, va="center", fontsize=7.6 * ESC["v"])
            ax.text(x + largura - 0.08, yy, t, va="center", ha="right", fontsize=6.8 * ESC["v"], color="#555555")
        return alt

    tabela(3.3, 5.4, "ocorrencias", [
        ("PK id", "BIGSERIAL"), ("latitude, longitude", "DOUBLE"), ("geom (GiST)", "Point, 4326"),
        ("data_hora (B-tree)", "TIMESTAMPTZ"), ("descricao", "TEXT"), ("nivel_risco", "Baixo|Médio|Alto"),
        ("fonte (B-tree)", "usuario|..."), ("chuva_mm", "DOUBLE"), ("descricao_clima", "TEXT"),
        ("temperatura, umidade", "DOUBLE, INT"), ("id_usuario", "TEXT (pseudônimo)"),
        ("FK id_estacao_ref", "BIGINT"),
    ], largura=3.2)
    tabela(0.1, 5.4, "estacoes_referencia", [
        ("PK id", "BIGSERIAL"), ("codigo_externo, nome", "TEXT"), ("fonte", "ana"),
        ("latitude, longitude", "DOUBLE"), ("geom (GiST)", "Point, 4326"),
    ], largura=2.9)
    tabela(6.75, 5.4, "reportes_colaborativos_agregado", [
        ("PK id", "BIGSERIAL"), ("geom_area (GiST)", "Polygon, 4326"), ("janela_inicio, _fim", "TIMESTAMPTZ"),
        ("score", "0–100"), ("quantidade_reportes", "INT"), ("calculado_em", "TIMESTAMPTZ"),
    ], largura=3.25)
    seta(ax, (3.3, 2.05), (3.0, 3.8), estilo="-", cor=BORDA)
    ax.text(3.05, 2.95, "0..1 : N\n(opcional; sem\nuso desde 16/10)", fontsize=8.5, ha="right")
    seta(ax, (6.5, 3.6), (6.75, 3.6), estilo="-", cor=BORDA, tracejada=True)
    ax.text(6.75, 2.95, "agrega relatos com fonte = 'usuario'\n(relação lógica, sem FK; registrado\nna mesma transação da ocorrência)",
            fontsize=8.5, ha="left")
    ax.text(0.1, 1.55, "Gatilho trg_sync_geom: geom = ST_SetSRID(ST_MakePoint(longitude, latitude), 4326) "
            "em toda inclusão ou alteração de coordenadas.", fontsize=8.5, style="italic")
    salvar(fig, "fig_der.png")


def gantt():
    d = date
    # (atividade, responsável, início, fim, a_confirmar)
    atividades = [
        ("Replanejamento: saída do Compose, XML e AHP", "Todos", d(2026, 7, 1), d(2026, 7, 14), False),
        ("Fundamentação de indexação espacial (GiST)", "Henrique", d(2026, 7, 1), d(2026, 7, 5), False),
        ("Modelagem PostgreSQL/PostGIS", "Henrique", d(2026, 7, 6), d(2026, 7, 12), False),
        ("Levantamento e testes das fontes de dados", "João", d(2026, 7, 6), d(2026, 8, 16), False),
        ("Endpoints REST e repositório (FastAPI)", "Henrique", d(2026, 7, 13), d(2026, 8, 9), False),
        ("Algoritmo AHP e fusão climática", "João", d(2026, 7, 13), d(2026, 8, 17), False),
        ("Telas XML: mapa, listagem, detalhes, perfil", "Marlon", d(2026, 7, 6), d(2026, 9, 6), False),
        ("Telas XML: login, cadastro, filtros, notificações", "Guilherme", d(2026, 7, 6), d(2026, 8, 16), False),
        ("Massa sintética e scripts de benchmark", "Henrique", d(2026, 8, 10), d(2026, 9, 6), False),
        ("Testes automatizados e integração com PostGIS", "João", d(2026, 8, 31), d(2026, 9, 6), False),
        ("Plano de testes PT-001 e roteiro de usabilidade", "Guilherme", d(2026, 9, 7), d(2026, 9, 13), False),
        ("Integração do app com a API real", "Marlon", d(2026, 9, 28), d(2026, 10, 7), False),
        ("Execução do benchmark, latência e testes do app", "Henrique", d(2026, 9, 28), d(2026, 10, 7), False),
        ("Ajustes de escopo: INMET, Open-Meteo, AHP 3 critérios", "João", d(2026, 10, 6), d(2026, 10, 16), False),
        ("Formulário de usabilidade (Google Forms)", "Marlon", d(2026, 10, 5), d(2026, 10, 16), True),
        ("Redação do documento e da apresentação", "Todos", d(2026, 9, 28), d(2026, 10, 30), False),
    ]
    cores = {"Henrique": "#4c78a8", "João": "#f58518", "Marlon": "#54a24b", "Guilherme": "#b279a2",
             "Todos": "#7f7f7f"}
    fig, ax = plt.subplots(figsize=(10, 7.4))
    for i, (nome, resp, ini, fim, conf) in enumerate(atividades):
        ini_n, fim_n = mdates.date2num(ini), mdates.date2num(fim) + 1
        ax.barh(i, fim_n - ini_n, left=ini_n, color=cores[resp], edgecolor="black", lw=0.5,
                hatch="//" if conf else None, alpha=0.55 if conf else 1)
    ax.set_yticks(range(len(atividades)))
    ax.set_yticklabels([f"{a[0]}" for a in atividades], fontsize=11)
    ax.invert_yaxis()
    ax.xaxis.set_major_locator(mdates.WeekdayLocator(byweekday=mdates.MO, interval=2))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%d/%m"))
    ax.tick_params(axis="x", labelsize=10.5)
    ax.set_xlim(mdates.date2num(d(2026, 6, 29)), mdates.date2num(d(2026, 11, 2)))
    ax.grid(axis="x", ls=":", lw=0.6)
    for x, rot in [(d(2026, 7, 13), "Fase 2"), (d(2026, 8, 10), "Fase 3"), (d(2026, 9, 14), "Fase 4")]:
        ax.axvline(mdates.date2num(x), color="#999999", lw=0.8)
        ax.text(mdates.date2num(x) + 1, -0.9, rot, fontsize=10, color="#555555")
    ax.text(mdates.date2num(d(2026, 7, 1)) + 1, -0.9, "Fase 1", fontsize=10, color="#555555")
    legenda = [Patch(fc=c, ec="black", lw=0.5, label=r) for r, c in cores.items()]
    legenda.append(Patch(fc="white", ec="black", hatch="//", label="período a confirmar"))
    ax.legend(handles=legenda, loc="upper center", bbox_to_anchor=(0.3, -0.06), fontsize=10, ncol=3, frameon=False)
    ax.set_ylim(len(atividades) - 0.5, -1.2)
    salvar(fig, "fig_gantt.png")


def painel(arquivos, rotulos, nome, largura_tela=540):
    fonte = None
    for f in ("arial.ttf", "C:/Windows/Fonts/arial.ttf"):
        try:
            fonte = ImageFont.truetype(f, 34)
            break
        except OSError:
            continue
    telas = [Image.open(CAPTURAS / a).convert("RGB") for a in arquivos]
    telas = [t.resize((largura_tela, int(t.height * largura_tela / t.width)), Image.LANCZOS) for t in telas]
    margem, legenda = 30, 60
    w = len(telas) * largura_tela + (len(telas) + 1) * margem
    h = telas[0].height + 2 * margem + legenda
    img = Image.new("RGB", (w, h), "white")
    draw = ImageDraw.Draw(img)
    for i, (t, r) in enumerate(zip(telas, rotulos)):
        x = margem + i * (largura_tela + margem)
        img.paste(t, (x, margem))
        draw.rectangle([x - 1, margem - 1, x + largura_tela, margem + t.height], outline="#888888")
        tw = draw.textlength(r, font=fonte)
        draw.text((x + (largura_tela - tw) / 2, margem + t.height + 14), r, fill="black", font=fonte)
    img.save(SAIDA / nome, optimize=True)
    print("ok", nome)


if __name__ == "__main__":
    arquitetura()
    fluxo_risco()
    der()
    gantt()
    painel(["00_login.png", "01_mapa.png", "08_mapa_selecionada.png"], ["(a)", "(b)", "(c)"], "fig_telas_mapa.png")
    painel(["02_alertas.png", "03_alertas_filtrados.png", "04_detalhes.png"], ["(a)", "(b)", "(c)"],
           "fig_telas_alertas.png")
    painel(["05_cadastro.png", "06_previsao_risco.png", "10_previsao_info_fonte.png"], ["(a)", "(b)", "(c)"],
           "fig_telas_cadastro_previsao.png")
    painel(["07_ajustes.png", "09_perfil.png"], ["(a)", "(b)"], "fig_telas_ajustes.png")
