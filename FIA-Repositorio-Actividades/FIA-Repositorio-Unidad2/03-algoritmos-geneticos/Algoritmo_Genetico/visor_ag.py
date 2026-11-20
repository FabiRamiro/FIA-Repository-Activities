"""
visor_ag.py
-----------
Ventana comun (PySide6 + matplotlib) para ver un algoritmo genetico
generacion por generacion. La usan:
    proyecto1/app_proyecto1.py   (AG binario: v1, v2 y v3)
    proyecto2/app_proyecto2.py   (AG real con 4 tipos de cruce)

Cada aplicacion hereda de VentanaAG, agrega sus parametros al formulario
y define ejecutar(params, progreso), que corre el AG y devuelve un Resultado.

La ventana tiene:
  - Panel izquierdo: parametros, boton Ejecutar, barra de progreso,
    datos de la generacion actual y resultado final.
  - Pestaña "Visualizador":
        arriba     la funcion y los individuos de la generacion actual
                   (1 variable: curva; 2 variables: curvas de nivel;
                    3 o mas: valor de cada variable de cada individuo)
        abajo izq. evolucion del mejor y la media (linea = generacion actual)
        abajo der. histograma de f(x) de la generacion actual
        controles  |<  <  Play/Pausa  >  >|, barra de generaciones, velocidad
                   teclado: flechas izquierda/derecha y espacio
  - Pestaña "Individuos": tabla de la generacion actual ordenada del mejor al peor.
"""

import sys
import traceback
from dataclasses import dataclass

import numpy as np
import matplotlib

matplotlib.use("QtAgg")
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg  # noqa: E402
from matplotlib.figure import Figure  # noqa: E402
from PySide6.QtCore import Qt, QThread, QTimer, Signal  # noqa: E402
from PySide6.QtGui import QColor, QKeySequence, QPalette, QShortcut  # noqa: E402
from PySide6.QtWidgets import (  # noqa: E402
    QApplication, QCheckBox, QFileDialog, QFormLayout, QFrame, QGridLayout, QHBoxLayout,
    QHeaderView, QLabel, QMainWindow, QMessageBox, QProgressBar, QPushButton, QScrollArea,
    QSlider, QTableWidget, QTableWidgetItem, QTabWidget, QVBoxLayout, QWidget,
)

# ---------------------------------------------------------------------------
# Tema (oscuro, como las interfaces de la carpeta Algoritmos)
# ---------------------------------------------------------------------------
BG, PANEL, LINE, INK, MUTED = "#0c0d0f", "#121315", "#2b2d32", "#e8e9ec", "#9ca3af"
ACENTO = "#4ade80"

# colores de las graficas
FONDO_FIG, FONDO_AX, REJILLA = "#121315", "#16181b", "#2b2d32"
C_FUNCION, C_INDIV, C_MEJOR = "#60a5fa", "#fb923c", "#facc15"
C_MEDIA, C_ABS, C_ESTELA = "#9ca3af", "#4ade80", "#6b7280"

STYLE = f"""
QMainWindow {{ background: {BG}; }}
QWidget {{ color: {INK}; font-family: 'Segoe UI'; font-size: 13px; }}
QLabel {{ background: transparent; }}
QFrame#rail {{ background: #101113; border-right: 1px solid {LINE}; }}
QFrame#card {{ background: {PANEL}; border: 1px solid {LINE}; border-radius: 8px; }}
QLabel#titulo {{ font-size: 17px; font-weight: 700; }}
QLabel#subtitulo {{ color: {MUTED}; font-size: 11px; }}
QLabel#eyebrow {{ color: {MUTED}; font-size: 10px; font-weight: 700; letter-spacing: 1px; }}
QLabel#clave {{ color: {MUTED}; font-size: 12px; }}
QLabel#valor {{ font-size: 12px; font-weight: 600; }}
QLabel#info {{ color: #c5c9d0; font-size: 12px; background: #16181b; border: 1px solid {LINE};
               border-radius: 6px; padding: 8px; }}
QLabel#aviso {{ color: #fbbf24; font-size: 11px; }}
QPushButton {{ background: #1e2024; border: 1px solid #35383e; border-radius: 7px;
               padding: 7px 12px; font-size: 12px; }}
QPushButton:hover {{ background: #2b2e34; border-color: {ACENTO}; }}
QPushButton:pressed {{ background: #151619; }}
QPushButton:disabled {{ color: #62656d; background: #141518; border-color: #292b30; }}
QPushButton#primary {{ background: #24543a; border: 1px solid {ACENTO}; font-weight: 700;
                       padding: 10px; font-size: 13px; }}
QPushButton#primary:hover {{ background: #306b49; }}
QComboBox, QSpinBox, QDoubleSpinBox {{ background: #1a1c20; color: {INK}; border: 1px solid {LINE};
                                       border-radius: 6px; padding: 5px 8px; }}
QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled {{ color: #55585f; }}
QComboBox QAbstractItemView {{ background: #1a1c20; color: {INK}; selection-background-color: #24543a; }}
QCheckBox {{ color: #c5c9d0; spacing: 7px; font-size: 12px; }}
QCheckBox::indicator {{ width: 13px; height: 13px; border: 1px solid #5b5e67; border-radius: 3px;
                        background: #16171a; }}
QCheckBox::indicator:checked {{ background: {ACENTO}; border: 3px solid #24543a; }}
QProgressBar {{ background: #1a1c20; border: 1px solid {LINE}; border-radius: 5px; height: 14px;
                text-align: center; font-size: 10px; }}
QProgressBar::chunk {{ background: #2f7a50; border-radius: 4px; }}
QSlider::groove:horizontal {{ background: #303239; height: 4px; border-radius: 2px; }}
QSlider::sub-page:horizontal {{ background: {ACENTO}; border-radius: 2px; }}
QSlider::handle:horizontal {{ background: #bbf7d0; width: 14px; height: 14px; margin: -5px 0;
                              border-radius: 7px; }}
QTabWidget::pane {{ background: {PANEL}; border: 1px solid {LINE}; border-radius: 6px; }}
QTabBar::tab {{ color: {MUTED}; padding: 9px 16px; font-size: 12px; border-bottom: 2px solid transparent; }}
QTabBar::tab:selected {{ color: {INK}; border-bottom: 2px solid {ACENTO}; }}
QTableWidget {{ background: {PANEL}; alternate-background-color: #191b1f; color: {INK}; border: none;
                gridline-color: #222429; }}
QTableWidget::item:selected {{ background: #24543a; }}
QHeaderView::section {{ background: #1e2025; color: {MUTED}; padding: 6px 4px; border: none; font-size: 11px; }}
QTableCornerButton::section {{ background: #1e2025; border: none; }}
QScrollArea {{ border: none; background: transparent; }}
QScrollBar:vertical {{ background: #16171a; width: 8px; }}
QScrollBar::handle:vertical {{ background: #474b54; min-height: 28px; border-radius: 4px; }}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QToolTip {{ background: #202227; color: {INK}; border: 1px solid #3c3f47; padding: 6px; }}
"""

matplotlib.rcParams.update({
    "figure.facecolor": FONDO_FIG, "axes.facecolor": FONDO_AX, "savefig.facecolor": FONDO_FIG,
    "axes.edgecolor": LINE, "axes.labelcolor": "#c5c9d0", "text.color": INK,
    "xtick.color": MUTED, "ytick.color": MUTED, "grid.color": REJILLA, "grid.alpha": 0.8,
    "axes.grid": True, "axes.spines.top": False, "axes.spines.right": False,
    "legend.facecolor": "#1a1c20", "legend.edgecolor": LINE, "legend.fontsize": 8,
    "font.size": 9, "axes.titlesize": 10,
})


def aplicar_tema(app):
    paleta = QPalette()
    for rol, tinta in [(QPalette.ColorRole.Window, BG), (QPalette.ColorRole.WindowText, INK),
                       (QPalette.ColorRole.Base, PANEL), (QPalette.ColorRole.AlternateBase, "#191b1e"),
                       (QPalette.ColorRole.Text, INK), (QPalette.ColorRole.Button, "#24262b"),
                       (QPalette.ColorRole.ButtonText, INK), (QPalette.ColorRole.Highlight, "#24543a"),
                       (QPalette.ColorRole.HighlightedText, INK)]:
        paleta.setColor(rol, QColor(tinta))
    app.setPalette(paleta)
    app.setStyleSheet(STYLE)


def fmt(v, dec=6):
    """Formato corto para numeros (o vectores) en las tarjetas."""
    if v is None:
        return "—"
    if np.ndim(v) > 0:
        v = list(v)
        txt = ", ".join(f"{a:.4f}" for a in v[:3])
        return f"[{txt}{', …' if len(v) > 3 else ''}]"
    return f"{v:.{dec}f}"


# ---------------------------------------------------------------------------
# Resultado de una ejecucion del AG (lo que la ventana necesita para graficar)
# ---------------------------------------------------------------------------
@dataclass
class Resultado:
    titulo: str          # titulo de la grafica (acepta mathtext de matplotlib)
    funcion: object      # f(np.array con una entrada por variable) -> float
    x_min: list
    x_max: list
    maximizar: bool
    poblaciones: list    # por generacion: matriz tam_pob x n (fenotipos)
    valores: list        # por generacion: f(x) de cada individuo
    optimo: float = None
    x_opt: list = None

    def __post_init__(self):
        self.poblaciones = [np.asarray(p, dtype=float).reshape(len(p), -1) for p in self.poblaciones]
        self.valores = [np.asarray(v, dtype=float) for v in self.valores]
        self.n = self.poblaciones[0].shape[1]
        self.num_gen = len(self.poblaciones) - 1
        elegir = np.argmax if self.maximizar else np.argmin
        self.pos_mejor = np.array([int(elegir(v)) for v in self.valores])
        self.mejor = np.array([v[i] for v, i in zip(self.valores, self.pos_mejor)])
        self.peor = np.array([v.min() if self.maximizar else v.max() for v in self.valores])
        self.media = np.array([v.mean() for v in self.valores])
        self.desv = np.array([v.std() for v in self.valores])
        acum = np.maximum.accumulate if self.maximizar else np.minimum.accumulate
        self.mejor_abs = acum(self.mejor)
        # generacion en la que aparece por primera vez el mejor absoluto final
        self.gen_mejor = int(np.argmax(self.mejor == self.mejor_abs[-1]))
        self.x_mejor = self.poblaciones[self.gen_mejor][self.pos_mejor[self.gen_mejor]]
        self.f_mejor = self.mejor_abs[-1]


# ---------------------------------------------------------------------------
# Hilo para correr el AG sin congelar la ventana
# ---------------------------------------------------------------------------
class Trabajador(QThread):
    progreso = Signal(int)
    listo = Signal(object)
    fallo = Signal(str)

    def __init__(self, fn, *args):
        super().__init__()
        self.fn, self.args = fn, args

    def run(self):
        try:
            res = self.fn(*self.args, lambda frac: self.progreso.emit(int(100 * frac)))
            self.listo.emit(res)
        except Exception:
            self.fallo.emit(traceback.format_exc())


class Tarjeta(QFrame):
    """Recuadro con un titulo y pares clave / valor."""

    def __init__(self, titulo, claves):
        super().__init__()
        self.setObjectName("card")
        lay = QVBoxLayout(self)
        lay.setContentsMargins(12, 10, 12, 10)
        lay.setSpacing(6)
        eyebrow = QLabel(titulo.upper())
        eyebrow.setObjectName("eyebrow")
        lay.addWidget(eyebrow)
        grid = QGridLayout()
        grid.setHorizontalSpacing(10)
        grid.setVerticalSpacing(4)
        self.valores = {}
        for i, clave in enumerate(claves):
            k = QLabel(clave)
            k.setObjectName("clave")
            v = QLabel("—")
            v.setObjectName("valor")
            v.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            v.setWordWrap(True)
            grid.addWidget(k, i, 0, Qt.AlignmentFlag.AlignTop)
            grid.addWidget(v, i, 1)
            self.valores[clave] = v
        grid.setColumnStretch(1, 1)
        lay.addLayout(grid)

    def poner(self, clave, texto, tooltip=None):
        self.valores[clave].setText(texto)
        self.valores[clave].setToolTip(tooltip or "")


def lienzo(figsize=(10, 7)):
    fig = Figure(figsize=figsize, layout="constrained")
    canvas = FigureCanvasQTAgg(fig)
    return fig, canvas


# ---------------------------------------------------------------------------
# Panel con las graficas y los controles de reproduccion
# ---------------------------------------------------------------------------
class PanelGraficas(QWidget):
    generacion_cambiada = Signal(int)

    def __init__(self):
        super().__init__()
        self.r = None
        self.gen = 0

        lay = QVBoxLayout(self)
        lay.setContentsMargins(6, 6, 6, 6)
        self.fig, self.canvas = lienzo()
        lay.addWidget(self.canvas, 1)

        barra = QHBoxLayout()
        barra.setSpacing(6)
        self.btn_inicio = self._boton("|◀", "Primera generación", lambda: self.ir_a(0))
        self.btn_atras = self._boton("◀", "Generación anterior (←)", lambda: self.ir_a(self.gen - 1))
        self.btn_play = self._boton("▶  Play", "Reproducir / pausar (espacio)", self.play_pausa)
        self.btn_play.setMinimumWidth(95)
        self.btn_adelante = self._boton("▶", "Generación siguiente (→)", lambda: self.ir_a(self.gen + 1))
        self.btn_fin = self._boton("▶|", "Última generación", lambda: self.ir_a(self.r.num_gen))
        for b in (self.btn_inicio, self.btn_atras, self.btn_play, self.btn_adelante, self.btn_fin):
            barra.addWidget(b)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.slider.valueChanged.connect(self.mostrar)
        barra.addWidget(self.slider, 1)
        self.lbl_gen = QLabel("Gen 0 / 0")
        self.lbl_gen.setMinimumWidth(95)
        barra.addWidget(self.lbl_gen)

        barra.addWidget(QLabel("Velocidad"))
        self.vel = QSlider(Qt.Orientation.Horizontal)
        self.vel.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.vel.setRange(1, 30)
        self.vel.setValue(10)
        self.vel.setFixedWidth(90)
        self.vel.setToolTip("Generaciones por segundo")
        self.vel.valueChanged.connect(lambda v: self.timer.setInterval(int(1000 / v)))
        barra.addWidget(self.vel)

        self.chk_estela = QCheckBox("Gen. anterior")
        self.chk_estela.setToolTip("Mostrar en gris dónde estaban los individuos en la generación anterior")
        self.chk_estela.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        self.chk_estela.setChecked(True)
        self.chk_estela.toggled.connect(lambda _: self.mostrar(self.gen))
        barra.addWidget(self.chk_estela)
        barra.addWidget(self._boton("Guardar imagen", "Guardar la figura como PNG", self.guardar))
        lay.addLayout(barra)

        self.timer = QTimer(self)
        self.timer.setInterval(100)
        self.timer.timeout.connect(self._paso)
        self._habilitar(False)

    def _boton(self, texto, tip, accion):
        b = QPushButton(texto)
        b.setToolTip(tip)
        b.setFocusPolicy(Qt.FocusPolicy.NoFocus)
        b.clicked.connect(accion)
        return b

    def _habilitar(self, si):
        for w in (self.btn_inicio, self.btn_atras, self.btn_play, self.btn_adelante, self.btn_fin,
                  self.slider):
            w.setEnabled(si)

    # ------------------------------------------------------------ construir
    def cargar(self, r):
        self.timer.stop()
        self.btn_play.setText("▶  Play")
        self.r = r
        fig = self.fig
        fig.clear()
        gs = fig.add_gridspec(2, 2, height_ratios=[1.45, 1], width_ratios=[1.75, 1])
        self.ax = fig.add_subplot(gs[0, :])
        self.ax_ev = fig.add_subplot(gs[1, 0])
        self.ax_h = fig.add_subplot(gs[1, 1])
        fig.suptitle(r.titulo, fontsize=11.5, fontweight="bold")

        self._dibujar_funcion()
        self._dibujar_evolucion()
        self._dibujar_histograma()

        self.slider.blockSignals(True)
        self.slider.setRange(0, r.num_gen)
        self.slider.setValue(0)
        self.slider.blockSignals(False)
        self._habilitar(True)
        self.mostrar(0)

    def _dibujar_funcion(self):
        ax, r = self.ax, self.r
        kw_ind = dict(s=30, color=C_INDIV, edgecolor="#1a1206", lw=0.5, zorder=3, label="Individuos")
        kw_est = dict(s=16, color=C_ESTELA, alpha=0.45, lw=0, zorder=2, label="Generación anterior")
        if r.n == 1:
            xs = np.linspace(r.x_min[0], r.x_max[0], 2500)
            ys = np.array([r.funcion(np.array([x])) for x in xs])
            ax.plot(xs, ys, color=C_FUNCION, lw=1.3, zorder=1, label="f(x)")
            if r.x_opt is not None and r.x_min[0] <= r.x_opt[0] <= r.x_max[0]:
                ax.axvline(r.x_opt[0], color=INK, ls=":", lw=0.9, alpha=0.6, label="Óptimo (libro)")
            ax.set_xlim(r.x_min[0], r.x_max[0])
            ax.set_xlabel("x")
            ax.set_ylabel("f(x)")
            self.estela = ax.scatter([], [], **kw_est)
            self.puntos = ax.scatter([], [], **kw_ind)
            self.estrella, = ax.plot([], [], "*", ms=17, color=C_MEJOR, markeredgecolor="black",
                                     zorder=4, label="Mejor de la generación")
        elif r.n == 2:
            g1 = np.linspace(r.x_min[0], r.x_max[0], 170)
            g2 = np.linspace(r.x_min[1], r.x_max[1], 170)
            X, Y = np.meshgrid(g1, g2)
            Z = np.array([[r.funcion(np.array([a, b])) for a, b in zip(fa, fb)]
                          for fa, fb in zip(X, Y)])
            # zonas buenas en claro: al maximizar los valores altos, al minimizar los bajos
            cs = ax.contourf(X, Y, Z, levels=30, cmap="Blues_r" if r.maximizar else "Blues", zorder=1)
            cb = self.fig.colorbar(cs, ax=ax, fraction=0.035, pad=0.01)
            cb.set_label("f(x1, x2)")
            cb.outline.set_edgecolor(LINE)
            ax.grid(False)
            if r.x_opt is not None:
                ax.plot(r.x_opt[0], r.x_opt[1], "X", ms=11, color="#f43f5e", markeredgecolor="white",
                        zorder=5, label="Óptimo (libro)")
            ax.set_xlim(r.x_min[0], r.x_max[0])
            ax.set_ylim(r.x_min[1], r.x_max[1])
            ax.set_xlabel("x1")
            ax.set_ylabel("x2")
            kw_ind["edgecolor"] = "white"
            kw_est["color"] = "#374151"
            kw_est["alpha"] = 0.55
            self.estela = ax.scatter([], [], **kw_est)
            self.puntos = ax.scatter([], [], **kw_ind)
            self.estrella, = ax.plot([], [], "*", ms=19, color=C_MEJOR, markeredgecolor="black",
                                     zorder=6, label="Mejor de la generación")
        else:
            # 3 o mas variables: cada columna es una variable, cada punto un individuo
            ax.set_xlim(0.4, r.n + 0.6)
            ax.set_ylim(min(r.x_min), max(r.x_max))
            ax.set_xticks(range(1, r.n + 1))
            ax.set_xticklabels([f"x{i}" for i in range(1, r.n + 1)])
            ax.set_ylabel("Valor de la variable")
            ax.grid(axis="x", alpha=0)
            if r.x_opt is not None:
                ax.plot(range(1, r.n + 1), r.x_opt, "_", ms=28, mew=2, color="#f43f5e", zorder=5,
                        label="Óptimo (libro)")
            kw_ind.update(s=16, alpha=0.7, lw=0)
            self.estela = ax.scatter([], [], **dict(kw_est, s=10))
            self.puntos = ax.scatter([], [], **kw_ind)
            self.estrella, = ax.plot([], [], "*-", ms=13, color=C_MEJOR, markeredgecolor="black",
                                     lw=1.2, zorder=6, label="Mejor de la generación")
        # con 2 variables la leyenda va arriba a la derecha; si no, donde estorbe menos
        ax.legend(loc="upper right" if r.n == 2 else "best", framealpha=0.9)

    def _dibujar_evolucion(self):
        ax, r = self.ax_ev, self.r
        gens = np.arange(r.num_gen + 1)
        ax.plot(gens, r.media, color=C_MEDIA, lw=1.2, label="Media de la población")
        ax.plot(gens, r.mejor, color=C_INDIV, lw=1, ls="--", label="Mejor de la generación")
        ax.plot(gens, r.mejor_abs, color=C_ABS, lw=2.4, label="Mejor absoluto")
        if r.optimo is not None:
            ax.axhline(r.optimo, color=INK, ls=":", lw=0.9, alpha=0.7, label="Óptimo (libro)")
        self.linea_gen = ax.axvline(0, color=INK, lw=1.1)
        self.punto_gen, = ax.plot([], [], "o", ms=6, color=C_ABS, markeredgecolor="black", zorder=5)
        ax.set_xlim(0, max(1, r.num_gen))
        ax.set_xlabel("Generación")
        ax.set_ylabel("f(x)")
        ax.set_title("Evolución", loc="left")
        ax.legend(loc="best", framealpha=0.9)

    def _dibujar_histograma(self):
        ax, r = self.ax_h, self.r
        todos = np.concatenate(r.valores)
        todos = todos[np.isfinite(todos)]
        lo, hi = float(todos.min()), float(todos.max())
        if hi - lo < 1e-12:
            lo, hi = lo - 0.5, hi + 0.5
        bordes = np.linspace(lo, hi, 31)
        self.conteos = np.array([np.histogram(v, bins=bordes)[0] for v in r.valores])
        centros = (bordes[:-1] + bordes[1:]) / 2
        self.barras = ax.bar(centros, self.conteos[0], width=(bordes[1] - bordes[0]) * 0.92,
                             color=C_FUNCION, alpha=0.85)
        self.linea_mejor_h = ax.axvline(r.mejor[0], color=C_MEJOR, lw=1.5, label="Mejor")
        self.linea_media_h = ax.axvline(r.media[0], color=C_MEDIA, lw=1.2, ls="--", label="Media")
        ax.set_ylim(0, self.conteos.max() * 1.08)
        ax.set_xlim(lo, hi)
        ax.set_xlabel("f(x)")
        ax.set_ylabel("Individuos")
        ax.set_title("Distribución de f(x) en la generación", loc="left")
        ax.legend(loc="upper right", framealpha=0.9)

    # ------------------------------------------------------------ mostrar
    def mostrar(self, g):
        if self.r is None:
            return
        r = self.r
        g = int(np.clip(g, 0, r.num_gen))
        self.gen = g
        p, fv, im = r.poblaciones[g], r.valores[g], r.pos_mejor[g]
        estela = self.chk_estela.isChecked() and g > 0
        pa, fa = (r.poblaciones[g - 1], r.valores[g - 1]) if g > 0 else (p, fv)

        if r.n == 1:
            self.puntos.set_offsets(np.column_stack([p[:, 0], fv]))
            self.estela.set_offsets(np.column_stack([pa[:, 0], fa]))
            self.estrella.set_data([p[im, 0]], [fv[im]])
        elif r.n == 2:
            self.puntos.set_offsets(p[:, :2])
            self.estela.set_offsets(pa[:, :2])
            self.estrella.set_data([p[im, 0]], [p[im, 1]])
        else:
            def tira(m, semilla):
                cols = np.tile(np.arange(1, r.n + 1), len(m))
                jit = (np.random.default_rng(semilla).random(len(cols)) - 0.5) * 0.35
                return np.column_stack([cols + jit, m.ravel()])
            self.puntos.set_offsets(tira(p, g))
            self.estela.set_offsets(tira(pa, g + 100000))
            self.estrella.set_data(np.arange(1, r.n + 1), p[im])
        self.estela.set_visible(estela)

        self.linea_gen.set_xdata([g, g])
        self.punto_gen.set_data([g], [r.mejor_abs[g]])
        for barra, h in zip(self.barras, self.conteos[g]):
            barra.set_height(h)
        self.linea_mejor_h.set_xdata([fv[im]] * 2)
        self.linea_media_h.set_xdata([fv.mean()] * 2)
        self.ax.set_title(f"Generación {g} de {r.num_gen}   ·   mejor de la generación  f = {fv[im]:.6f}"
                          f"   ·   media  {fv.mean():.4f}", loc="left")
        self.canvas.draw_idle()

        self.lbl_gen.setText(f"Gen {g} / {r.num_gen}")
        if self.slider.value() != g:
            self.slider.blockSignals(True)
            self.slider.setValue(g)
            self.slider.blockSignals(False)
        self.generacion_cambiada.emit(g)

    # ------------------------------------------------------------ controles
    def ir_a(self, g):
        if self.r is not None:
            self.mostrar(g)

    def play_pausa(self):
        if self.r is None:
            return
        if self.timer.isActive():
            self.timer.stop()
            self.btn_play.setText("▶  Play")
        else:
            if self.gen >= self.r.num_gen:
                self.mostrar(0)
            self.timer.start()
            self.btn_play.setText("❚❚  Pausa")

    def _paso(self):
        if self.gen >= self.r.num_gen:
            self.play_pausa()
        else:
            self.mostrar(self.gen + 1)

    def guardar(self):
        archivo, _ = QFileDialog.getSaveFileName(self, "Guardar imagen", f"generacion_{self.gen}.png",
                                                 "Imagen PNG (*.png)")
        if archivo:
            self.fig.savefig(archivo, dpi=150)


# ---------------------------------------------------------------------------
# Ventana principal (cada proyecto la extiende)
# ---------------------------------------------------------------------------
class VentanaAG(QMainWindow):
    """Subclases: agregan filas a self.form en construir_parametros() y definen
    leer_parametros() -> dict  y  ejecutar(params, progreso) -> Resultado."""

    def __init__(self, titulo, subtitulo):
        super().__init__()
        self.setWindowTitle(titulo)
        self.resultado = None
        self.trabajador = None

        raiz = QWidget()
        self.setCentralWidget(raiz)
        h = QHBoxLayout(raiz)
        h.setContentsMargins(0, 0, 0, 0)
        h.setSpacing(0)

        # ---- panel izquierdo
        rail = QFrame()
        rail.setObjectName("rail")
        lay = QVBoxLayout(rail)
        lay.setContentsMargins(16, 16, 16, 16)
        lay.setSpacing(10)
        t = QLabel(titulo)
        t.setObjectName("titulo")
        t.setWordWrap(True)
        s = QLabel(subtitulo)
        s.setObjectName("subtitulo")
        s.setWordWrap(True)
        lay.addWidget(t)
        lay.addWidget(s)

        eyebrow = QLabel("PARÁMETROS")
        eyebrow.setObjectName("eyebrow")
        lay.addWidget(eyebrow)
        self.form = QFormLayout()
        self.form.setLabelAlignment(Qt.AlignmentFlag.AlignLeft)
        self.form.setHorizontalSpacing(10)
        self.form.setVerticalSpacing(7)
        lay.addLayout(self.form)
        self.lbl_info = QLabel()
        self.lbl_info.setObjectName("info")
        self.lbl_info.setWordWrap(True)
        lay.addWidget(self.lbl_info)
        self.lbl_aviso = QLabel()
        self.lbl_aviso.setObjectName("aviso")
        self.lbl_aviso.setWordWrap(True)
        self.lbl_aviso.hide()
        lay.addWidget(self.lbl_aviso)

        self.btn_ejecutar = QPushButton("Ejecutar algoritmo genético")
        self.btn_ejecutar.setObjectName("primary")
        self.btn_ejecutar.clicked.connect(self.correr)
        lay.addWidget(self.btn_ejecutar)
        self.barra = QProgressBar()
        self.barra.setRange(0, 100)
        self.barra.setValue(0)
        lay.addWidget(self.barra)

        self.card_gen = Tarjeta("Generación actual", ["Generación", "Mejor f", "x del mejor",
                                                      "Media", "Peor", "Desv. est."])
        self.card_fin = Tarjeta("Resultado final", ["Mejor f", "En x", "Hallado en gen.",
                                                    "Óptimo libro", "Error"])
        lay.addWidget(self.card_gen)
        lay.addWidget(self.card_fin)
        lay.addStretch(1)

        scroll = QScrollArea()
        scroll.setWidget(rail)
        scroll.setWidgetResizable(True)
        scroll.setFixedWidth(390)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        h.addWidget(scroll)

        # ---- pestañas
        self.tabs = QTabWidget()
        self.panel = PanelGraficas()
        self.panel.generacion_cambiada.connect(self._al_cambiar_generacion)
        self.tabs.addTab(self.panel, "Visualizador")
        self.tabla = QTableWidget()
        self.tabla.setAlternatingRowColors(True)
        self.tabla.verticalHeader().setVisible(False)
        self.tabla.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.tabs.addTab(self.tabla, "Individuos")
        self.tabs.currentChanged.connect(lambda _: self._llenar_tabla())
        cont = QWidget()
        lc = QVBoxLayout(cont)
        lc.setContentsMargins(10, 10, 10, 10)
        lc.addWidget(self.tabs)
        h.addWidget(cont, 1)

        # ---- teclado
        for tecla, accion in [(Qt.Key.Key_Right, lambda: self.panel.ir_a(self.panel.gen + 1)),
                              (Qt.Key.Key_Left, lambda: self.panel.ir_a(self.panel.gen - 1)),
                              (Qt.Key.Key_Space, self.panel.play_pausa),
                              (Qt.Key.Key_Home, lambda: self.panel.ir_a(0)),
                              (Qt.Key.Key_End, lambda: self.panel.ir_a(10 ** 9))]:
            QShortcut(QKeySequence(tecla), self, activated=accion)

        self.construir_parametros()
        # se ejecuta una vez al abrir para que la ventana no aparezca vacia
        QTimer.singleShot(150, self.correr)

    # ---- lo que definen las subclases
    def construir_parametros(self):
        raise NotImplementedError

    def leer_parametros(self):
        raise NotImplementedError

    def ejecutar(self, params, progreso):
        raise NotImplementedError

    # ---- utilidades para las subclases
    def info(self, texto):
        self.lbl_info.setText(texto)

    def aviso(self, texto):
        self.lbl_aviso.setText(texto)
        self.lbl_aviso.setVisible(bool(texto))

    def lanzar(self, fn, args, al_terminar):
        """Corre fn(*args, progreso) en un hilo y llama al_terminar(resultado)."""
        if self.trabajador is not None and self.trabajador.isRunning():
            return
        self.btn_ejecutar.setEnabled(False)
        self.barra.setValue(0)
        self.trabajador = Trabajador(fn, *args)
        self.trabajador.progreso.connect(self.barra.setValue)
        self.trabajador.listo.connect(al_terminar)
        self.trabajador.fallo.connect(self._error)
        self.trabajador.finished.connect(lambda: self.btn_ejecutar.setEnabled(True))
        self.trabajador.start()

    def _error(self, texto):
        QMessageBox.critical(self, "Error al ejecutar", texto[-1500:])

    # ---- flujo principal
    def correr(self):
        try:
            params = self.leer_parametros()
        except ValueError as e:
            QMessageBox.warning(self, "Parámetros inválidos", str(e))
            return
        self.lanzar(self.ejecutar, (params,), self._mostrar_resultado)

    def _mostrar_resultado(self, r):
        self.resultado = r
        self.barra.setValue(100)
        self.card_fin.poner("Mejor f", fmt(r.f_mejor))
        self.card_fin.poner("En x", fmt(r.x_mejor if r.n > 1 else r.x_mejor[0]),
                            ", ".join(f"{v:.6f}" for v in r.x_mejor))
        self.card_fin.poner("Hallado en gen.", str(r.gen_mejor))
        self.card_fin.poner("Óptimo libro", fmt(r.optimo))
        self.card_fin.poner("Error", "—" if r.optimo is None else f"{abs(r.f_mejor - r.optimo):.6g}")
        self.panel.cargar(r)

    def _al_cambiar_generacion(self, g):
        r = self.resultado
        if r is None:
            return
        im = r.pos_mejor[g]
        x = r.poblaciones[g][im]
        self.card_gen.poner("Generación", f"{g} de {r.num_gen}")
        self.card_gen.poner("Mejor f", fmt(r.mejor[g]))
        self.card_gen.poner("x del mejor", fmt(x if r.n > 1 else x[0]), ", ".join(f"{v:.6f}" for v in x))
        self.card_gen.poner("Media", fmt(r.media[g], 4))
        self.card_gen.poner("Peor", fmt(r.peor[g], 4))
        self.card_gen.poner("Desv. est.", fmt(r.desv[g], 4))
        self._llenar_tabla()

    def _llenar_tabla(self):
        # solo se llena si la pestaña esta visible (para que el Play vaya fluido)
        r = self.resultado
        if r is None or self.tabs.currentWidget() is not self.tabla:
            return
        g = self.panel.gen
        p, fv = r.poblaciones[g], r.valores[g]
        orden = np.argsort(-fv if r.maximizar else fv)
        columnas = ["Rango", "Individuo"] + [f"x{i + 1}" for i in range(r.n)] + ["f(x)"]
        self.tabla.setColumnCount(len(columnas))
        self.tabla.setHorizontalHeaderLabels(columnas)
        self.tabla.setRowCount(len(orden))
        for fila, i in enumerate(orden):
            datos = [str(fila + 1), str(i)] + [f"{v:.6f}" for v in p[i]] + [f"{fv[i]:.6f}"]
            for c, d in enumerate(datos):
                item = QTableWidgetItem(d)
                item.setTextAlignment(Qt.AlignmentFlag.AlignRight | Qt.AlignmentFlag.AlignVCenter)
                if fila == 0:
                    item.setForeground(QColor(C_MEJOR))
                self.tabla.setItem(fila, c, item)
        self.tabla.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)


def iniciar(clase_ventana):
    app = QApplication.instance() or QApplication(sys.argv)
    aplicar_tema(app)
    w = clase_ventana()
    w.resize(1450, 880)
    w.show()
    sys.exit(app.exec())
