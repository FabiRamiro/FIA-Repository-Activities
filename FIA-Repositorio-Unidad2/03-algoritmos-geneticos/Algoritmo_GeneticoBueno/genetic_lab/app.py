"""Interfaz de escritorio. La evolución trabaja en un hilo y Qt dibuja en el principal."""
import csv
from pathlib import Path
import sys
import threading

import math
from PySide6.QtCore import Qt, QThread, Signal, QTimer, QAbstractTableModel, QModelIndex
from PySide6.QtGui import QFont, QFontDatabase, QColor, QPalette
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QFrame, QTabWidget, QScrollArea, QFormLayout, QSpinBox,
    QDoubleSpinBox, QComboBox, QCheckBox, QFileDialog, QMessageBox, QSlider,
    QTableView, QHeaderView, QTextBrowser, QSplitter,
    QAbstractItemView,
)
from .data import (PRESETS, DEFAULT_PRESET, DEFAULT_POINTS, DEFAULT_LOW, DEFAULT_HIGH,
                   MAX_POINTS, generate_dataset, load_csv, save_csv)
from .evolution import Config, Evolution
from .trees import evaluate
from .charts import FitPlot, OverviewPlot, HistoryPlot, ResidualPlot, TreeView
from .metrics import METRICS, ErrorEvaluator, metric_loss
from .exporting import write_experiment
from .guide import GUIDE

ROOT = Path(__file__).resolve().parent.parent

STYLE = """
QWidget { background: #0b1220; color: #e4ebf7; font-family: 'DejaVu Sans'; font-size: 12px; }
QMainWindow { background: #0b1220; }
QFrame#sidebar { background: #101a2b; border-right: 1px solid #25334a; }
QFrame#sidebar QLabel { background: transparent; }
QWidget#settingsContainer, QWidget#configPanel, QWidget#opsPanel { background: transparent; }
QLabel#brand { color: #49e0c3; font-size: 22px; font-weight: 800; }
QLabel#eyebrow { color: #748aa8; font-size: 10px; font-weight: 700; letter-spacing: 2px; }
QLabel#heading { font-size: 22px; font-weight: 700; }
QLabel#muted { color: #8f9fb9; }
QLabel#section { font-size: 11px; font-weight: 700; color: #91a5c4; padding-top: 14px; padding-bottom: 4px; }
QLabel#status { color: #4de0c3; background: #12352f; border: 1px solid #20584b; border-radius: 12px; padding: 6px 12px; }
QFrame#card { background: #111d30; border: 1px solid #263650; border-radius: 10px; }
QFrame#card QLabel { background: transparent; border: none; }
QLabel#metric { font-family: 'DejaVu Sans Mono'; font-size: 25px; font-weight: 700; color: #f0f6ff; }
QLabel#formula { background: #121f32; color: #52e1c7; font-family: 'DejaVu Sans Mono'; font-size: 14px; padding: 14px; border: 1px solid #28413e; border-radius: 8px; }
QPushButton { background: #1b2a41; border: 1px solid #34445f; border-radius: 6px; padding: 8px 12px; font-weight: 600; }
QPushButton:hover { background: #2a3c59; border-color: #729fff; }
QPushButton:pressed { background: #334d6e; }
QPushButton:disabled { color: #53627b; background: #131e30; border-color: #263248; }
QPushButton#primary { background: #3bdbb8; color: #062e28; border: none; padding: 11px; font-weight: 800; }
QPushButton#primary:hover { background: #70efce; }
QPushButton#primary:disabled { background: #1b5149; color: #73a599; }
QSpinBox, QDoubleSpinBox, QComboBox { background: #0c1525; border: 1px solid #31435e; border-radius: 5px; padding: 6px; min-height: 19px; selection-background-color: #237c75; }
QComboBox QAbstractItemView { background: #17263c; color: #e4ebf7; selection-background-color: #2d5272; }
QTabWidget::pane { background: #111a2b; border: 1px solid #263650; border-radius: 8px; }
QTabBar::tab { background: transparent; color: #93a5bf; padding: 12px 19px; border-bottom: 2px solid transparent; }
QTabBar::tab:selected { color: #4de0c3; border-bottom: 2px solid #4de0c3; background: #111f30; }
QTabBar::tab:hover { color: #d6e6fc; }
QSlider::groove:horizontal { height: 5px; background: #293a53; border-radius: 2px; }
QSlider::sub-page:horizontal { background: #3dc9b1; }
QSlider::handle:horizontal { background: #8cf2da; width: 13px; margin: -4px 0; border-radius: 6px; }
QProgressBar { background: #1b2940; border: none; border-radius: 4px; height: 5px; }
QCheckBox { spacing: 7px; }
QCheckBox::indicator { width: 14px; height: 14px; background: #0c1525; border: 1px solid #536b8e; border-radius: 3px; }
QCheckBox::indicator:checked { background: #39cfb1; border-color: #75f1d3; }
QScrollArea { border: none; background: transparent; }
QScrollBar:vertical { background: #111a2b; width: 8px; }
QScrollBar::handle:vertical { background: #344965; min-height: 25px; border-radius: 4px; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0; }
QTableView { background: #111a2b; alternate-background-color: #152238; gridline-color: #28394e; border: 1px solid #263650; selection-background-color: #224d5b; }
QHeaderView::section { background: #1b2a40; color: #a6bad6; border: none; padding: 8px; }
QTextBrowser { background: #111a2b; border: none; padding: 18px; font-size: 14px; }
QToolTip { background: #23364d; color: #f1f6ff; border: 1px solid #54708f; padding: 6px; }
QSplitter::handle { background: #263650; height: 3px; width: 3px; }
"""


def label(text, name=None):
    widget = QLabel(text)
    if name: widget.setObjectName(name)
    return widget


def button(text, action, primary=False):
    widget = QPushButton(text)
    if primary: widget.setObjectName("primary")
    widget.clicked.connect(action)
    return widget


def number(low, high, value, decimals=None):
    widget = QSpinBox() if decimals is None else QDoubleSpinBox()
    if decimals is not None:
        widget.setDecimals(decimals)
        widget.setSingleStep(0.05 if decimals < 4 else 0.0001)
    widget.setRange(low, high)
    widget.setValue(value)
    return widget


def format_metric(value):
    if not math.isfinite(value): return "N/D"
    if value == 0: return "0.0000"
    return f"{value:.3e}" if abs(value) < 0.0001 or abs(value) >= 10000 else f"{value:.4f}"


def configure_fonts():
    """Usa fuentes incluidas con Matplotlib incluso si Windows restringe sus fuentes."""
    from matplotlib import get_data_path
    if "DejaVu Sans" not in QFontDatabase.families():
        folder = Path(get_data_path()) / "fonts" / "ttf"
        for name in ("DejaVuSans.ttf", "DejaVuSans-Bold.ttf", "DejaVuSansMono.ttf", "DejaVuSansMono-Bold.ttf"):
            QFontDatabase.addApplicationFont(str(folder / name))


class EvolutionWorker(QThread):
    snapshot = Signal(object)
    failed = Signal(str)

    def __init__(self, data, config):
        super().__init__()
        self.data, self.config = data, config
        self.cancel = threading.Event()
        self.permit = threading.Event()

    def run(self):
        try:
            for snapshot in Evolution(self.data, self.config).run(self.cancel.is_set):
                if self.cancel.is_set(): break
                self.permit.clear()
                self.snapshot.emit(snapshot)
                if snapshot.generation == self.config.generations != 0: break
                if self.config.target_r2 and snapshot.best.metrics.r2 >= self.config.target_r2: break
                # Un permiso por generación: nunca se saltan generaciones por una cola rápida.
                while not self.permit.wait(0.1):
                    if self.cancel.is_set(): return
                if self.cancel.is_set(): return
        except Exception as error:
            self.failed.emit(f"{type(error).__name__}: {error}")

    def stop(self):
        self.cancel.set()
        self.permit.set()


class DatasetTableModel(QAbstractTableModel):
    """Qt pide solo las celdas visibles; no creamos 20 001 filas de widgets."""
    def __init__(self):
        super().__init__()
        self.dataset = None
        self.predicted = None

    def set_dataset(self, dataset, predicted=None):
        self.beginResetModel()
        self.dataset, self.predicted = dataset, predicted
        self.endResetModel()

    def rowCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() or self.dataset is None else len(self.dataset.x)

    def columnCount(self, parent=QModelIndex()):
        return 0 if parent.isValid() else 3

    def data(self, index, role=Qt.ItemDataRole.DisplayRole):
        if not index.isValid() or role != Qt.ItemDataRole.DisplayRole: return None
        row, col = index.row(), index.column()
        values = (self.dataset.x, self.dataset.y, self.predicted)
        return "—" if values[col] is None else f"{values[col][row]:.8g}"

    def headerData(self, section, orientation, role=Qt.ItemDataRole.DisplayRole):
        if role != Qt.ItemDataRole.DisplayRole: return None
        if orientation == Qt.Orientation.Horizontal:
            return ["x", "y objetivo", "Predicción del élite"][section]
        return str(section + 1)


class MainWindow(QMainWindow):
    def __init__(self):
        configure_fonts()
        super().__init__()
        self.setWindowTitle("EvoLab · Regresión simbólica")
        self.resize(1360, 900)
        self.setMinimumSize(980, 720)
        self.worker = None
        self.history = []
        self.run_config = None
        self.playing = False
        self.busy = False
        self.data = generate_dataset(DEFAULT_PRESET, count=DEFAULT_POINTS,
                                     low=DEFAULT_LOW, high=DEFAULT_HIGH)
        self.view_limits = (-1.5, 1.5)
        self.timer = QTimer(self)
        self.timer.setInterval(450)
        self.timer.timeout.connect(self.advance)
        self.timer.start()
        self.setCentralWidget(self.make_workspace())
        self.refresh_data()
        self.set_running(False)

    def make_settings(self):
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        self.config_panel = QWidget()
        outer = QHBoxLayout(self.config_panel)
        outer.setContentsMargins(30, 26, 30, 26)
        outer.setSpacing(50)
        left = QVBoxLayout()
        left.addWidget(label("Población y reproducción", "heading"))
        form = QFormLayout()
        form.setVerticalSpacing(15)
        self.fields = {
            "population": number(10, 2000, 180), "generations": number(0, 1000, 0),
            "max_depth": number(2, 9, 7), "tournament": number(2, 30, 5),
            "elitism": number(1, 100, 4), "seed": number(0, 999999, 42),
            "crossover_rate": number(0, 1, 0.85, 2),
            "mutation_rate": number(0, 1, 0.3, 2),
            "immigration_rate": number(0, 0.5, 0.1, 2),
            "parsimony": number(0, 1, 0, 4),
            "target_r2": number(0, 1, 0.999, 4),
            "elite_mutation_rate": number(0, 0.5, 0.1, 2),
        }
        self.fields["generations"].setSpecialValueText("Sin límite")
        self.fields["target_r2"].setSpecialValueText("Sin objetivo")
        names = ["Población", "Generaciones", "Profundidad máxima", "Tamaño del torneo",
                 "Élites", "Semilla aleatoria", "Probabilidad de cruza", "Probabilidad de mutación",
                 "Fracción de individuos nuevos", "Penalización por nodo", "R² objetivo", "Mutantes del élite"]
        tips = ["Fórmulas por generación.",
                "0 = sin límite: evoluciona hasta alcanzar el R² objetivo o hasta que pulses Detener.",
                "Niveles del árbol contando la raíz.", "Candidatos sorteados por selección.",
                "Individuos que sobreviven.", "Mismos datos y parámetros repiten el azar.",
                "Probabilidad de injertar una rama de otro padre.",
                "Probabilidad independiente de cambiar una rama o constante.",
                "0.10 introduce un 10% de árboles nuevos en cada generación para explorar.",
                "Cero prioriza el ajuste. Un valor positivo favorece árboles pequeños.",
                "La evolución termina sola cuando el élite alcanza este R² (1 = ajuste perfecto).",
                "Fracción de hijos que copian al élite con una constante ligeramente mutada."]
        for (key, field), name, tip in zip(self.fields.items(), names, tips):
            field.setMaximumWidth(190)
            field.setToolTip(tip)
            form.addRow(name, field)
        left.addLayout(form)
        left.addStretch()
        outer.addLayout(left, 1)
        right = QVBoxLayout()
        right.addWidget(label("Operaciones disponibles", "heading"))
        self.ops_panel = QWidget()
        ops = QVBoxLayout(self.ops_panel)
        ops.setContentsMargins(0, 5, 0, 5)
        self.op_checks = {}
        for text, operators in [("Aritmética   +  −  ×  ÷", ("+", "-", "*", "/")),
                                ("Trigonometría   sin / cos", ("sin", "cos")),
                                ("Raíz y logaritmo protegidos", ("sqrt", "log"))]:
            check = QCheckBox(text)
            check.setChecked("sqrt" not in operators)
            self.op_checks[operators] = check
            ops.addWidget(check)
        self.pruning = QCheckBox("Simplificar ramas redundantes (poda)")
        self.pruning.setChecked(True)
        ops.addWidget(self.pruning)
        self.adaptive = QCheckBox("Aumentar la mutación al estancarse")
        self.adaptive.setChecked(True)
        self.adaptive.setToolTip("Tras 8 generaciones sin mejora, sube 0.2 la probabilidad (máximo 1.0).")
        ops.addWidget(self.adaptive)
        self.refinement = QCheckBox("Afinar escala y desplazamiento (opcional)")
        self.refinement.setChecked(True)
        self.refinement.setToolTip("Ajusta a y b en a + b·g(x) con los puntos del CSV. Desactívalo para usar solo operadores genéticos.")
        ops.addWidget(self.refinement)
        self.incremental = QCheckBox("Evaluación incremental (ventana creciente)")
        self.incremental.setChecked(True)
        self.incremental.setToolTip("Mide el error primero cerca del centro y amplía el tramo cuando el élite "
                                    "lo ajusta con R² ≥ 0.98. Evita que una curva muy oscilante parezca una línea plana.")
        ops.addWidget(self.incremental)
        right.addWidget(self.ops_panel)
        right.addWidget(label("Cómo se elige una fórmula", "section"))
        explanation = label(
            "El método de error se selecciona arriba, antes de iniciar. "
            "El élite conserva el mejor ajuste de ese criterio.\n\n"
            "La selección por torneo usa la pérdida relativa al error de predecir el promedio, "
            "más la penalización por tamaño si la activas.\n\n"
            "Introducir individuos nuevos y variar las constantes ayuda a explorar; "
            "no garantiza descubrir la expresión exacta.", "muted")
        explanation.setWordWrap(True)
        right.addWidget(explanation)
        right.addStretch()
        outer.addLayout(right, 1)
        scroll.setWidget(self.config_panel)
        return scroll

    def make_workspace(self):
        workspace = QWidget()
        layout = QVBoxLayout(workspace)
        layout.setContentsMargins(22, 18, 22, 14)
        layout.setSpacing(10)
        top = QHBoxLayout()
        top.addWidget(label("◈  EvoLab", "brand"))
        top.addWidget(label("   DE PUNTOS A FÓRMULAS", "eyebrow"))
        top.addStretch()
        self.status = label("●  Listo", "status")
        top.addWidget(self.status)
        layout.addLayout(top)
        self.dataset_name = label("", "muted")
        self.dataset_name.setWordWrap(True)
        layout.addWidget(self.dataset_name)
        actions = QHBoxLayout()
        actions.addWidget(label("Optimizar con"))
        self.metric_choice = QComboBox()
        for key, text in METRICS.items():
            self.metric_choice.addItem(text + (" ↑" if key == "r2" else " ↓"), key)
        self.metric_choice.setToolTip("Se aplica a la próxima ejecución. El historial conserva su criterio original.")
        actions.addWidget(self.metric_choice)
        self.active_metric = label("Élite: —", "muted")
        actions.addWidget(self.active_metric)
        actions.addStretch()
        self.export_button = button("Exportar", self.export_run)
        self.start_button = button("▶  Iniciar evolución", self.start_run, True)
        actions.addWidget(self.export_button)
        actions.addWidget(self.start_button)
        layout.addLayout(actions)
        settings = self.make_settings()
        self.tabs = QTabWidget()
        self.tabs.addTab(self.evolution_tab(), "Comparación")
        self.tabs.addTab(self.statistics_tab(), "Errores")
        self.tabs.addTab(self.tree_tab(), "Árbol")
        self.tabs.addTab(self.operators_tab(), "Operadores")
        self.tabs.addTab(self.data_tab(), "Datos")
        self.tabs.addTab(settings, "Configuración")
        guide = QTextBrowser()
        guide.setHtml(GUIDE)
        self.tabs.addTab(guide, "Aprende")
        layout.addWidget(self.tabs, 1)
        self.formula = label("f(x) = ?   ·   Inicia la evolución para descubrir una fórmula.", "formula")
        self.formula.setWordWrap(True)
        self.formula.setMaximumHeight(65)
        self.formula.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
        layout.addWidget(self.formula)
        controls = QHBoxLayout()
        self.play_button = button("▶  Reproducir", self.toggle_play)
        self.step_button = button("Paso →", self.step)
        self.stop_button = button("■  Detener", self.stop_run)
        self.first_button = button("↤", self.first_generation)
        self.first_button.setToolTip("Volver a la generación 0")
        for item in (self.play_button, self.step_button, self.stop_button, self.first_button):
            controls.addWidget(item)
        self.timeline = QSlider(Qt.Orientation.Horizontal)
        self.timeline.setRange(0, 0)
        self.timeline.valueChanged.connect(self.scrub)
        controls.addWidget(self.timeline, 1)
        self.generation_label = label("GEN 000 / ∞", "muted")
        controls.addWidget(self.generation_label)
        self.speed = QComboBox()
        for title, interval in [("0.5×", 900), ("1×", 450), ("2×", 225), ("4×", 110), ("Máx.", 1)]:
            self.speed.addItem(title, interval)
        self.speed.setCurrentIndex(1)
        self.speed.currentIndexChanged.connect(lambda: self.timer.setInterval(self.speed.currentData()))
        self.speed.setToolTip("Intervalo mínimo entre generaciones; también se necesita tiempo de cálculo.")
        controls.addWidget(self.speed)
        layout.addLayout(controls)
        self.footer = label("La generación 0 es la población aleatoria.", "muted")
        layout.addWidget(self.footer)
        self.tabs.currentChanged.connect(self.render_active_tab)
        self.metric_choice.currentIndexChanged.connect(self.metric_changed)
        return workspace

    def evolution_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(10, 10, 10, 8)
        controls = QHBoxLayout()
        controls.addWidget(label("Vista de x"))
        self.view_low = number(-1e6, 1e6, -1.5, 5)
        self.view_high = number(-1e6, 1e6, 1.5, 5)
        for field in (self.view_low, self.view_high): field.setMaximumWidth(125)
        controls.addWidget(self.view_low)
        controls.addWidget(label("a"))
        controls.addWidget(self.view_high)
        controls.addWidget(button("Aplicar zoom", self.apply_view))
        controls.addWidget(button("Ver todo", self.full_view))
        controls.addStretch()
        self.show_predictions = QCheckBox("Marcar predicciones")
        self.show_predictions.setToolTip("Muestra las predicciones del élite en las mismas x de los puntos visibles.")
        self.show_predictions.toggled.connect(self.draw_comparison)
        controls.addWidget(self.show_predictions)
        controls.addWidget(button("PNG", self.save_plot))
        layout.addLayout(controls)
        self.fit_plot = FitPlot()
        self.fit_plot.view_requested.connect(self.set_view)
        layout.addWidget(self.fit_plot, 1)
        self.overview_plot = OverviewPlot()
        self.overview_plot.view_requested.connect(self.set_view)
        layout.addWidget(self.overview_plot)
        self.view_note = label("El zoom cambia la vista; el error usa todos los puntos del CSV.", "muted")
        layout.addWidget(self.view_note)
        return widget

    def statistics_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(16, 14, 16, 10)
        row = QHBoxLayout()
        self.metric_values = {}
        for key, text in METRICS.items():
            card = QFrame()
            card.setObjectName("card")
            col = QVBoxLayout(card)
            col.addWidget(label(text + (" ↑" if key == "r2" else " ↓"), "eyebrow"))
            value = label("—", "metric")
            col.addWidget(value)
            self.metric_values[key] = value
            row.addWidget(card)
        layout.addLayout(row)
        note = label("En un mismo CSV, estas cuatro métricas ordenan los ajustes de la misma manera. "
                     "Una recta en el promedio tiene R² = 0; un ajuste mejor tiene R² > 0.", "muted")
        note.setWordWrap(True)
        layout.addWidget(note)
        self.baseline_info = label("", "muted")
        self.baseline_info.setWordWrap(True)
        layout.addWidget(self.baseline_info)
        selector = QHBoxLayout()
        selector.addWidget(label("Ver historial de"))
        self.history_metric = QComboBox()
        for key, text in METRICS.items(): self.history_metric.addItem(text, key)
        self.history_metric.currentIndexChanged.connect(self.refresh_statistics)
        selector.addWidget(self.history_metric)
        selector.addStretch()
        layout.addLayout(selector)
        split = QSplitter(Qt.Orientation.Vertical)
        self.history_plot = HistoryPlot()
        self.residual_plot = ResidualPlot()
        split.addWidget(self.history_plot)
        split.addWidget(self.residual_plot)
        split.setSizes([280, 190])
        layout.addWidget(split, 1)
        return widget

    def tree_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        toolbar = QHBoxLayout()
        toolbar.addWidget(label("Candidato de la generación:"))
        self.candidate = QComboBox()
        self.candidate.currentIndexChanged.connect(self.show_candidate)
        toolbar.addWidget(self.candidate, 1)
        toolbar.addWidget(button("Ajustar vista", lambda: self.tree_view.fit_tree()))
        layout.addLayout(toolbar)
        self.tree_view = TreeView()
        layout.addWidget(self.tree_view, 1)
        self.tree_info = label("Los nodos verdes son operaciones; azul = x; oscuro = constante.", "muted")
        self.tree_info.setWordWrap(True)
        layout.addWidget(self.tree_info)
        layout.addWidget(label("Rueda: ampliar · Arrastrar: mover · Apunta a un nodo para ver su subexpresión", "muted"))
        return widget

    def operators_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        self.event_choice = QComboBox()
        self.event_choice.currentIndexChanged.connect(self.show_event)
        layout.addWidget(self.event_choice)
        self.event_detail = label("Aquí verás ejemplos reales de cruza, mutación, reconstrucción, poda y reparación.", "muted")
        self.event_detail.setWordWrap(True)
        layout.addWidget(self.event_detail)
        self.event_counts = label("La generación inicial todavía no tiene operadores aplicados.", "muted")
        self.event_counts.setWordWrap(True)
        layout.addWidget(self.event_counts)
        row = QSplitter(Qt.Orientation.Horizontal)
        self.event_trees = []
        for title in ("ANTES / PADRE A", "DONANTE / PADRE B", "DESPUÉS / HIJO"):
            panel = QWidget()
            col = QVBoxLayout(panel)
            col.addWidget(label(title, "eyebrow"))
            view = TreeView()
            self.event_trees.append(view)
            col.addWidget(view, 1)
            row.addWidget(panel)
        layout.addWidget(row, 1)
        layout.addWidget(label("Ejemplos de la transición hacia esta generación; pueden pertenecer a cualquier hijo.", "muted"))
        return widget

    def data_tab(self):
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(18, 16, 18, 16)
        header = QHBoxLayout()
        self.load_button = button("Importar CSV", self.import_csv)
        header.addWidget(self.load_button)
        header.addWidget(button("Guardar CSV", self.save_dataset))
        header.addStretch()
        header.addWidget(label("Columnas x,y · punto decimal · UTF-8", "muted"))
        layout.addLayout(header)
        self.generator_panel = QWidget()
        row = QHBoxLayout(self.generator_panel)
        row.setContentsMargins(0, 6, 0, 6)
        self.preset = QComboBox()
        self.preset.addItems(PRESETS)
        self.preset.setSizeAdjustPolicy(QComboBox.SizeAdjustPolicy.AdjustToMinimumContentsLengthWithIcon)
        self.preset.setMinimumContentsLength(20)
        self.preset.setToolTip(self.preset.currentText())
        self.preset.currentTextChanged.connect(self.preset.setToolTip)
        row.addWidget(self.preset, 2)
        self.point_count = number(3, MAX_POINTS, DEFAULT_POINTS)
        self.low = number(-1e6, 1e6, DEFAULT_LOW, 2)
        self.high = number(-1e6, 1e6, DEFAULT_HIGH, 2)
        self.noise = number(0, 100, 0, 2)
        for text, field in [("Puntos", self.point_count), ("x mín.", self.low),
                            ("x máx.", self.high), ("Ruido σ", self.noise)]:
            col = QVBoxLayout()
            col.addWidget(label(text, "muted"))
            col.addWidget(field)
            row.addLayout(col)
        row.addWidget(button("Generar", self.generate))
        layout.addWidget(self.generator_panel)
        self.data_table = QTableView()
        self.data_model = DatasetTableModel()
        self.data_table.setModel(self.data_model)
        self.data_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        self.data_table.setAlternatingRowColors(True)
        self.data_table.setEditTriggers(QAbstractItemView.EditTrigger.NoEditTriggers)
        layout.addWidget(self.data_table, 1)
        return widget

    def set_running(self, running):
        for widget in (self.config_panel, self.ops_panel, self.generator_panel, self.load_button, self.start_button, self.metric_choice):
            widget.setEnabled(not running)
        self.stop_button.setEnabled(running)
        has_history = bool(self.history)
        self.play_button.setEnabled(running or has_history)
        self.step_button.setEnabled(running or has_history)
        self.first_button.setEnabled(has_history)
        self.export_button.setEnabled(has_history)

    def start_run(self):
        if self.worker and self.worker.isRunning(): return
        try:
            config = Config(**{key: field.value() for key, field in self.fields.items()},
                            operators=tuple(op for ops, check in self.op_checks.items() if check.isChecked() for op in ops),
                            pruning=self.pruning.isChecked(), metric=self.metric_choice.currentData(),
                            adaptive_mutation=self.adaptive.isChecked(),
                            refine_constants=self.refinement.isChecked(),
                            incremental=self.incremental.isChecked())
            config.validate()
            metric_loss(self.baseline, config.metric)
        except ValueError as error:
            self.error(str(error))
            return
        self.clear_history()
        self.run_config = config
        self.history_metric.setCurrentIndex(self.history_metric.findData(config.metric))
        self.playing, self.busy = True, True
        self.play_button.setText("Ⅱ  Pausa")
        self.status.setText("●  Generando población…")
        self.tabs.setCurrentIndex(0)
        self.worker = EvolutionWorker(self.data, config)
        self.worker.snapshot.connect(self.receive_snapshot)
        self.worker.failed.connect(self.worker_error)
        self.worker.finished.connect(self.worker_finished)
        self.set_running(True)
        self.worker.start()

    def clear_history(self):
        self.playing, self.busy = False, False
        self.history.clear()
        self.run_config = None
        self.timeline.blockSignals(True)
        self.timeline.setRange(0, 0)
        self.timeline.setValue(0)
        self.timeline.blockSignals(False)
        self.play_button.setText("▶  Reproducir")
        self.generation_label.setText(f"GEN 000 / {self.generation_limit(self.fields['generations'].value())}")
        self.active_metric.setText("Élite: —")
        self.footer.setText("La generación 0 es la población aleatoria.")
        for value in self.metric_values.values(): value.setText("—")
        self.candidate.clear()
        self.event_choice.clear()
        self.tree_view.scene().clear()
        for view in self.event_trees: view.scene().clear()
        self.event_counts.setText("La generación inicial no tiene operadores aplicados.")
        self.event_detail.setText("Aquí verás ejemplos de la transición entre generaciones.")
        self.tree_info.setText("Operaciones, variable x y constantes del árbol.")
        self.formula.setText("f(x) = ?   ·   Inicia la evolución para descubrir una fórmula.")
        self.data_model.set_dataset(self.data)

        self.draw_comparison()

    def receive_snapshot(self, snapshot):
        selected = self.timeline.value()
        following = not self.history or selected == len(self.history) - 1
        self.history.append(snapshot)
        self.busy = False
        self.timeline.blockSignals(True)
        self.timeline.setMaximum(len(self.history) - 1)
        self.timeline.blockSignals(False)
        self.show_generation(len(self.history) - 1 if following else selected)
        self.first_button.setEnabled(True)
        self.export_button.setEnabled(True)
        self.status.setText("●  Evolucionando" if self.playing else "●  En pausa")

    def show_generation(self, index):
        if not 0 <= index < len(self.history): return
        snapshot = self.history[index]
        self.timeline.blockSignals(True)
        self.timeline.setValue(index)
        self.timeline.blockSignals(False)
        for key, value in self.metric_values.items():
            value.setText(format_metric(getattr(snapshot.best.metrics, key)))
        value = getattr(snapshot.best.metrics, snapshot.metric)
        self.active_metric.setText(f"Élite · {METRICS[snapshot.metric]} {format_metric(value)}")
        self.generation_label.setText(f"GEN {snapshot.generation:03d} / {self.generation_limit(self.run_config.generations)}")
        expression = snapshot.best.tree.expression()
        self.formula.setText("f(x) = " + (expression if len(expression) < 230 else expression[:227] + "…"))
        self.formula.setToolTip(expression)
        self.candidate.blockSignals(True)
        self.candidate.clear()
        for rank, individual in enumerate(snapshot.top, 1):
            self.candidate.addItem(f"#{rank} · {METRICS[snapshot.metric]} "
                f"{format_metric(getattr(individual.metrics, snapshot.metric))} · {individual.tree.size} nodos")
        self.candidate.blockSignals(False)
        self.event_choice.blockSignals(True)
        self.event_choice.clear()
        for event in snapshot.events: self.event_choice.addItem(event.kind)
        self.event_choice.blockSignals(False)
        self.event_counts.setText(" · ".join(f"{key}: {value}" for key, value in snapshot.counts.items())
                                  or "Generación 0: población aleatoria.")
        self.footer.setText(f"Diversidad {snapshot.diversity:.0%} · {snapshot.best.tree.size} nodos · "
                            f"Mutación aplicada {snapshot.mutation_rate:.0%} · "
                            f"{snapshot.stagnant_generations} generaciones sin mejora"
                            + (f" · Evaluando x ∈ [{snapshot.window[0]:.3g}, {snapshot.window[1]:.3g}]" if snapshot.window else ""))
        self.render_active_tab()

    @staticmethod
    def generation_limit(generations):
        return f"{generations:03d}" if generations else "∞"

    def current_snapshot(self):
        return self.history[self.timeline.value()] if self.history else None

    def render_active_tab(self, *_):
        if not hasattr(self, "timeline"): return
        index = self.tabs.currentIndex()
        snapshot = self.current_snapshot()
        if index == 0:
            self.draw_comparison()
        elif index == 1:
            self.refresh_statistics()
        elif index == 2:
            self.show_candidate(max(0, self.candidate.currentIndex()))
        elif index == 3:
            self.show_event(max(0, self.event_choice.currentIndex()))
        elif index == 4:
            predicted = evaluate(snapshot.best.tree, self.data.x) if snapshot else None
            self.data_model.set_dataset(self.data, predicted)

    def draw_comparison(self, *_):
        if not hasattr(self, "timeline"): return
        snapshot = self.current_snapshot()
        self.fit_plot.show_data(self.data, snapshot, self.view_limits, self.show_predictions.isChecked())
        self.overview_plot.set_view(self.view_limits)
        self.view_note.setText(
            f"Vista x ∈ [{self.view_limits[0]:.5g}, {self.view_limits[1]:.5g}] · "
            f"Las métricas mostradas usan los {len(self.data.x):,} puntos del CSV; "
            f"la selección usa el tramo evaluado (sombreado).")

    def set_view(self, low, high):
        low, high = max(min(self.data.x), low), min(max(self.data.x), high)
        if high - low <= 1e-8: return
        self.view_limits = (low, high)
        self.view_low.setValue(low)
        self.view_high.setValue(high)
        self.draw_comparison()

    def apply_view(self):
        if self.view_low.value() >= self.view_high.value():
            self.error("El límite inferior de la vista debe ser menor al superior.")
            return
        self.set_view(self.view_low.value(), self.view_high.value())

    def full_view(self):
        self.set_view(min(self.data.x), max(self.data.x))

    def metric_changed(self, *_):
        self.history_metric.setCurrentIndex(self.history_metric.findData(self.metric_choice.currentData()))

    def refresh_statistics(self, *_):
        if not hasattr(self, "timeline") or not hasattr(self, "baseline"): return
        metric = self.history_metric.currentData()
        self.history_plot.show_history(self.history, self.timeline.value(), metric, self.baseline)
        snapshot = self.current_snapshot()
        base = format_metric(getattr(self.baseline, metric))
        if snapshot:
            r2 = snapshot.best.metrics.r2
            comparison = ("El élite mejora al promedio." if r2 > 0 else
                          "El élite aún no supera predecir el promedio.") if math.isfinite(r2) else "R² no está definido para y constante."
            self.baseline_info.setText(f"Referencia: predecir y = {self.mean_y:.6g} da {METRICS[metric]} = {base}. {comparison}")
            self.residual_plot.show_residuals(self.data, snapshot)
        else:
            self.baseline_info.setText(f"Referencia: predecir y = {self.mean_y:.6g} da {METRICS[metric]} = {base}.")
            self.residual_plot.empty("Los residuos aparecerán al evaluar el primer élite.")

    def show_candidate(self, index):
        if not self.history or index < 0: return
        snapshot = self.history[self.timeline.value()]
        if index >= len(snapshot.top): return
        individual = snapshot.top[index]
        self.tree_view.show_tree(individual.tree)
        self.tree_info.setText(f"{individual.tree.size} nodos · {individual.tree.depth} niveles · "
                               f"Aptitud penalizada {individual.score:.6g}\n{individual.tree.expression()}")

    def show_event(self, index):
        for view in self.event_trees: view.scene().clear()
        if not self.history: return
        events = self.history[self.timeline.value()].events
        if not 0 <= index < len(events):
            self.event_detail.setText("No hay un ejemplo de operador en esta generación.")
            return
        event = events[index]
        self.event_detail.setText(event.detail)
        self.event_trees[0].show_tree(event.before)
        if event.donor: self.event_trees[1].show_tree(event.donor)
        self.event_trees[2].show_tree(event.after)

    def advance(self):
        if not self.playing: return
        self.advance_one()

    def advance_one(self):
        if self.busy: return
        index = self.timeline.value()
        if index < len(self.history) - 1:
            self.show_generation(index + 1)
        elif self.worker and self.worker.isRunning() and not self.worker.cancel.is_set():
            self.busy = True
            self.worker.permit.set()
        else:
            self.playing = False
            self.play_button.setText("▶  Reproducir")

    def toggle_play(self):
        self.playing = not self.playing
        self.play_button.setText("Ⅱ  Pausa" if self.playing else "▶  Reproducir")
        if self.playing and self.history and self.timeline.value() == len(self.history)-1 and not (self.worker and self.worker.isRunning()):
            self.show_generation(0)
        self.status.setText("●  Reproduciendo" if self.playing else "●  En pausa")

    def step(self):
        self.playing = False
        self.play_button.setText("▶  Reproducir")
        self.status.setText("●  Paso a paso")
        self.advance_one()

    def scrub(self, index):
        self.playing = False
        self.play_button.setText("▶  Reproducir")
        self.status.setText("●  Explorando historial")
        self.show_generation(index)

    def first_generation(self):
        self.scrub(0)

    def stop_run(self):
        self.playing = False
        self.play_button.setText("▶  Reproducir")
        if self.worker: self.worker.stop()
        self.status.setText("●  Deteniendo…")

    def worker_finished(self):
        self.busy = False
        self.playing = False
        self.play_button.setText("▶  Reproducir")
        self.set_running(False)
        last = self.history[-1] if self.history else None
        target = self.run_config.target_r2
        if last and target and last.best.metrics.r2 >= target:
            self.status.setText(f"●  Objetivo alcanzado · R² {last.best.metrics.r2:.4f}")
        elif last and last.generation == self.run_config.generations:
            self.status.setText("●  Evolución completada")
        else:
            self.status.setText("●  Ejecución detenida")

    def worker_error(self, message):
        self.error("No se pudo continuar la evolución:\n" + message)

    def error(self, message):
        QMessageBox.warning(self, "EvoLab · Revisa los datos", message)

    def import_csv(self):
        path, _ = QFileDialog.getOpenFileName(self, "Importar puntos objetivo", str(ROOT / "examples"), "CSV (*.csv)")
        if not path: return
        try:
            dataset = load_csv(path)
            self.data = dataset
            self.clear_history()
            self.refresh_data()
            self.set_running(False)
        except (ValueError, OSError, UnicodeError, csv.Error) as error:
            self.error(str(error))

    def generate(self):
        try:
            self.data = generate_dataset(self.preset.currentText(), self.point_count.value(), self.low.value(),
                                         self.high.value(), self.noise.value(), self.fields["seed"].value())
            self.clear_history()
            self.refresh_data()
            self.set_running(False)
        except ValueError as error:
            self.error(str(error))

    def refresh_data(self):
        self.dataset_name.setText(f"{self.data.name}   ·   {len(self.data.x):,} puntos   ·   "
                                  f"x ∈ [{min(self.data.x):.5g}, {max(self.data.x):.5g}]")
        evaluator = ErrorEvaluator(self.data.y)
        self.mean_y = evaluator.mean
        self.baseline = evaluator.measure([self.mean_y] * len(self.data.y))
        low, high = min(self.data.x), max(self.data.x)
        if self.data.name == DEFAULT_PRESET and low <= -1.5 and high >= 1.5:
            self.view_limits = (-1.5, 1.5)
        else:
            self.view_limits = (low, high)
        self.view_low.setValue(self.view_limits[0])
        self.view_high.setValue(self.view_limits[1])
        self.overview_plot.show_data(self.data, self.view_limits)
        self.data_model.set_dataset(self.data)
        self.draw_comparison()
        self.refresh_statistics()
        self.status.setText("●  Datos listos")

    def save_dataset(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar puntos CSV", str(ROOT / "puntos_objetivo.csv"), "CSV (*.csv)")
        if path:
            try: save_csv(self.data, path)
            except OSError as error: self.error(str(error))

    def save_plot(self):
        path, _ = QFileDialog.getSaveFileName(self, "Guardar gráfica", str(ROOT / "evolucion.png"), "PNG (*.png)")
        if path:
            try: self.fit_plot.figure.savefig(path, dpi=180, facecolor=self.fit_plot.figure.get_facecolor())
            except OSError as error: self.error(str(error))

    def export_run(self):
        if not self.history: return
        path, _ = QFileDialog.getSaveFileName(self, "Exportar experimento", str(ROOT / "experimento_evolab.zip"), "ZIP (*.zip)")
        if not path: return
        try:
            write_experiment(path, self.data, self.run_config, self.history, self.timeline.value())
            self.status.setText("●  Experimento exportado")
        except OSError as error:
            self.error(str(error))

    def closeEvent(self, event):
        if self.worker and self.worker.isRunning():
            self.worker.stop()
            # No se destruye un QThread mientras sigue ejecutándose.
            if not self.worker.wait(3000):
                self.status.setText("●  Terminando cálculo; vuelve a cerrar en un momento")
                event.ignore()
                return
        event.accept()



def main():
    app = QApplication(sys.argv)
    configure_fonts()
    app.setStyle("Fusion")
    app.setFont(QFont("DejaVu Sans", 10))
    palette = QPalette()
    palette.setColor(QPalette.ColorRole.Window, QColor("#0b1220"))
    palette.setColor(QPalette.ColorRole.WindowText, QColor("#e4ebf7"))
    palette.setColor(QPalette.ColorRole.Base, QColor("#111a2b"))
    palette.setColor(QPalette.ColorRole.Text, QColor("#e4ebf7"))
    palette.setColor(QPalette.ColorRole.Button, QColor("#1b2a41"))
    palette.setColor(QPalette.ColorRole.ButtonText, QColor("#e4ebf7"))
    palette.setColor(QPalette.ColorRole.Highlight, QColor("#237c75"))
    app.setPalette(palette)
    app.setStyleSheet(STYLE)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
