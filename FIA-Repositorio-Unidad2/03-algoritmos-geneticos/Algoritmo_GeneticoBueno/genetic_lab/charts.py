"""Presentación gráfica: NumPy se limita a preparar lo que dibuja Matplotlib."""
import numpy as np
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QColor, QPainter, QPen, QBrush, QFont
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
from matplotlib.figure import Figure
from matplotlib.ticker import SymmetricalLogLocator, MaxNLocator
from matplotlib.widgets import SpanSelector
from .trees import evaluate
from .metrics import METRICS

BG = "#111a2b"
FG = "#a2b1c8"
TEAL = "#40dec2"
BLUE = "#729fff"


class PlotCanvas(FigureCanvasQTAgg):
    def __init__(self, title="", height=3):
        self.figure = Figure(figsize=(7, height), facecolor=BG, layout="constrained")
        self.axes = self.figure.add_subplot(111)
        super().__init__(self.figure)
        self.title = title
        self.style()

    def style(self):
        ax = self.axes
        ax.set_facecolor(BG)
        ax.tick_params(colors=FG, labelsize=9)
        for spine in ax.spines.values(): spine.set_color("#28354b")
        ax.grid(True, color="#253249", linewidth=0.6, alpha=0.65)
        ax.set_axisbelow(True)
        ax.set_title(self.title, color="#e6edf7", fontsize=11, loc="left", pad=12)
        ax.xaxis.label.set_color(FG)
        ax.yaxis.label.set_color(FG)

    def clear(self):
        self.axes.clear()
        self.axes.set_axis_on()
        self.style()

    def legend(self):
        self.axes.legend(facecolor=BG, edgecolor="#28354b", labelcolor=FG,
                         fontsize=9, loc="upper left", framealpha=1.0)

    def empty(self, message):
        self.clear()
        self.axes.set_axis_off()
        self.axes.text(0.5, 0.5, message, transform=self.axes.transAxes,
                       ha="center", va="center", color=FG, fontsize=12)
        self.draw_idle()


class FitPlot(PlotCanvas):
    view_requested = Signal(float, float)

    def __init__(self):
        super().__init__("ÉLITE FRENTE AL OBJETIVO", 5)
        self.mpl_connect("scroll_event", self.zoom)

    def zoom(self, event):
        if event.inaxes is not self.axes or event.xdata is None: return
        low, high = self.axes.get_xlim()
        factor = 0.65 if event.button == "up" else 1 / 0.65
        self.view_requested.emit(event.xdata + (low-event.xdata)*factor,
                                 event.xdata + (high-event.xdata)*factor)

    def show_data(self, data, snapshot=None, view_range=None, show_predictions=False):
        self.clear()
        ax = self.axes
        low, high = view_range or (min(data.x), max(data.x))
        # Esta máscara cambia solo la vista. El motor evalúa el CSV completo.
        x, y = np.asarray(data.x), np.asarray(data.y)
        mask = (x >= low) & (x <= high)
        visible_x, visible_y = x[mask], y[mask]
        if len(visible_x):
            ax.plot(visible_x, visible_y, color=BLUE, linewidth=1.05,
                    alpha=0.8, label="Objetivo · CSV", zorder=2)
            ax.scatter(visible_x, visible_y, s=9 if len(visible_x) < 600 else 2,
                       color=BLUE, linewidths=0, alpha=0.8, zorder=3)
        all_y = [visible_y] if len(visible_y) else []
        if snapshot and snapshot.window:
            ax.axvspan(*snapshot.window, color=TEAL, alpha=0.07, zorder=1, label="Tramo evaluado")
        if snapshot:
            grid = np.linspace(low, high, max(800, len(visible_x)))
            curve = evaluate(snapshot.best.tree, grid)
            ax.plot(grid, curve, color=TEAL, linewidth=2.4, zorder=4,
                    label=f"Élite · generación {snapshot.generation}")
            all_y.append(np.asarray(curve))
            if show_predictions and len(visible_x):
                prediction = evaluate(snapshot.best.tree, visible_x)
                ax.scatter(visible_x, prediction, s=27 if len(visible_x) < 600 else 5,
                           facecolors="none", edgecolors=TEAL, linewidths=0.8, zorder=5,
                           label="Predicción en cada x")
        if all_y:
            values = np.concatenate(all_y)
            margin = max(float(np.ptp(values))*0.12, 0.5)
            ax.set_ylim(float(values.min()-margin), float(values.max()+margin))
        ax.set_xlim(low, high)
        ax.set_xlabel("x · rueda del ratón para ampliar")
        ax.set_ylabel("y")
        ax.yaxis.set_major_locator(MaxNLocator(6))
        if len(visible_x) or snapshot: self.legend()
        self.draw_idle()


class OverviewPlot(PlotCanvas):
    view_requested = Signal(float, float)

    def __init__(self):
        super().__init__("TODO EL INTERVALO · arrastra para elegir un tramo", 1.3)
        self.setMinimumHeight(115)
        self.setMaximumHeight(145)
        self.span = None
        self.highlight = None
        self.data = None

    def show_data(self, data, view_range):
        self.data = data
        if self.span: self.span.disconnect_events()
        self.clear()
        self.axes.plot(data.x, data.y, color=BLUE, linewidth=0.45, alpha=0.6)
        self.axes.set_xlim(min(data.x), max(data.x))
        self.axes.yaxis.set_major_locator(MaxNLocator(2))
        self.highlight = self.axes.axvspan(*view_range, color=TEAL, alpha=0.18)
        self.span = SpanSelector(self.axes, self.select, "horizontal", useblit=False,
                                 props={"facecolor": TEAL, "alpha": 0.25})
        self.draw_idle()

    def select(self, low, high):
        if high - low > 1e-8: self.view_requested.emit(low, high)

    def set_view(self, view_range):
        if self.highlight:
            self.highlight.remove()
            self.highlight = self.axes.axvspan(*view_range, color=TEAL, alpha=0.18)
            self.draw_idle()


class HistoryPlot(PlotCanvas):
    def __init__(self):
        super().__init__("EVOLUCIÓN DEL ERROR", 3)

    def show_history(self, history, selected, metric="mse", baseline=None):
        if not history:
            self.empty("Inicia una evolución para ver el historial de errores.")
            return
        self.title = f"HISTORIAL · {METRICS[metric]} " + ("↑ mayor es mejor" if metric == "r2" else "↓ menor es mejor")
        self.clear()
        values = [getattr(s.best.metrics, metric) for s in history]
        self.axes.plot([s.generation for s in history], values, color=TEAL,
                       linewidth=2, marker="." if len(history) < 40 else None, label="Élite")
        if metric == "mse":
            self.axes.plot([s.generation for s in history], [s.median_mse for s in history],
                           color=BLUE, linewidth=1, alpha=0.6, label="Mediana de la población")
        if baseline is not None and np.isfinite(getattr(baseline, metric)):
            self.axes.axhline(getattr(baseline, metric), color="#a1a9bc", linestyle="--",
                             linewidth=1, label="Predecir siempre el promedio")
        self.axes.axvline(selected, color="#f6c776", linewidth=1, linestyle=":")
        if metric != "r2":
            self.axes.set_yscale("symlog", linthresh=1e-6)
            locator = SymmetricalLogLocator(base=10, linthresh=1e-6)
            locator.set_params(numticks=6)
            self.axes.yaxis.set_major_locator(locator)
            self.axes.set_ylim(bottom=0)
        else:
            self.axes.yaxis.set_major_locator(MaxNLocator(6))
        self.axes.xaxis.set_major_locator(MaxNLocator(integer=True))
        self.axes.set_xlabel("Generación")
        self.axes.set_ylabel(METRICS[metric])
        self.legend()
        self.draw_idle()


class ResidualPlot(PlotCanvas):
    def __init__(self):
        super().__init__("RESIDUOS · y observado − y predicho", 3)

    def show_residuals(self, data, snapshot):
        self.clear()
        predictions = evaluate(snapshot.best.tree, data.x)
        errors = [y - prediction for y, prediction in zip(data.y, predictions)]
        self.axes.axhline(0, color=TEAL, alpha=0.8)
        self.axes.scatter(data.x, errors, color=BLUE, s=12 if len(data.x) < 1000 else 2,
                          alpha=0.65, linewidths=0)
        self.axes.set_xlabel("x")
        self.axes.set_ylabel("y − ŷ")
        self.draw_idle()


class TreeView(QGraphicsView):
    """Escena desplazable y ampliable. Cada nivel representa una operación anidada."""
    def __init__(self):
        super().__init__()
        self.setScene(QGraphicsScene(self))
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setBackgroundBrush(QColor(BG))
        self.setDragMode(QGraphicsView.DragMode.ScrollHandDrag)
        self.setMinimumHeight(260)
        self._auto_fit = True

    def show_tree(self, tree):
        scene = self.scene()
        scene.clear()
        self._auto_fit = True
        cursor = [0]

        def layout(node, depth):
            child_positions = [layout(child, depth + 1) for child in node.children]
            if child_positions:
                x = sum(pos[0] for pos in child_positions) / len(child_positions)
            else:
                x = cursor[0] * 86
                cursor[0] += 1
            y = depth * 95
            for cx, cy in child_positions:
                scene.addLine(x, y + 25, cx, cy - 25, QPen(QColor("#435578"), 2))
            color = "#3b82f6" if node.op == "x" else "#263a54" if node.op == "const" else "#167e73"
            scene.addEllipse(x - 28, y - 25, 56, 50,
                             QPen(QColor("#68b5c3"), 1), QBrush(QColor(color)))
            text = f"{node.value:.3g}" if node.op == "const" else node.op
            label = scene.addText(text, QFont("DejaVu Sans", 10, QFont.Weight.DemiBold))
            label.setDefaultTextColor(QColor("#f0f6ff"))
            label.setPos(x - label.boundingRect().width()/2, y - label.boundingRect().height()/2)
            label.setToolTip(node.expression())
            return x, y

        layout(tree, 0)
        scene.setSceneRect(scene.itemsBoundingRect().adjusted(-35, -35, 35, 35))
        self.fit_tree()

    def fit_tree(self):
        if not self.scene().items(): return
        self.fitInView(self.scene().sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)
        if self.transform().m11() > 1.3:
            self.resetTransform()
            self.scale(1.3, 1.3)

    def resizeEvent(self, event):
        super().resizeEvent(event)
        if self._auto_fit: self.fit_tree()

    def wheelEvent(self, event):
        self._auto_fit = False
        factor = 1.15 if event.angleDelta().y() > 0 else 1/1.15
        zoom = self.transform().m11() * factor
        if 0.02 <= zoom <= 5: self.scale(factor, factor)
        event.accept()
