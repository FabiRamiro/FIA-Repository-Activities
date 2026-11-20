"""Pruebas de integración Qt sin abrir una ventana en el escritorio."""
import os
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
import json
from pathlib import Path
import tempfile
import time
import unittest
import zipfile
from PySide6.QtWidgets import QApplication
from genetic_lab.app import MainWindow, STYLE, write_experiment
from genetic_lab.data import validate_dataset


class ApplicationTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.app = QApplication.instance() or QApplication([])
        cls.app.setStyle("Fusion")
        cls.app.setStyleSheet(STYLE)

    def setUp(self):
        self.window = MainWindow()
        self.window.fields["population"].setValue(30)
        self.window.fields["generations"].setValue(3)
        self.window.fields["max_depth"].setValue(4)
        self.window.show()
        self.app.processEvents()

    def tearDown(self):
        self.window.close()
        self.app.processEvents()

    def wait_until(self, predicate, timeout=15):
        deadline = time.monotonic() + timeout
        while not predicate() and time.monotonic() < deadline:
            self.app.processEvents()
            time.sleep(0.01)
        self.assertTrue(predicate(), "El hilo de evolución no respondió a tiempo")

    def test_step_pause_history_tabs_and_export(self):
        w = self.window
        w.start_run()
        w.playing = False
        self.wait_until(lambda: len(w.history) == 1)
        # El motor no avanza mientras no se concede otro permiso.
        end = time.monotonic() + 0.2
        while time.monotonic() < end: self.app.processEvents()
        self.assertEqual(len(w.history), 1)
        w.step()
        self.wait_until(lambda: len(w.history) == 2)
        self.assertEqual(w.history[-1].generation, 1)
        for index in range(w.tabs.count()):
            w.tabs.setCurrentIndex(index)
            self.app.processEvents()
        w.first_generation()
        self.assertEqual(w.timeline.value(), 0)
        w.step()
        self.assertEqual(w.timeline.value(), 1)
        w.step()
        self.wait_until(lambda: len(w.history) == 3)
        w.step()
        self.wait_until(lambda: not w.worker.isRunning())
        self.app.processEvents()
        self.assertEqual(len(w.history), 4)
        self.assertTrue(w.start_button.isEnabled())
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            path = Path(folder) / "run.zip"
            write_experiment(path, w.data, w.run_config, w.history, 1)
            with zipfile.ZipFile(path) as archive:
                self.assertEqual(len(archive.namelist()), 5)
                result = json.loads(archive.read("resultado.json"))
                self.assertEqual(result["selected_generation"], 1)
                self.assertEqual(len(json.loads(archive.read("historial.json"))), 4)
                self.assertEqual(result["config"]["seed"], 42)

    def test_stop_and_restart(self):
        w = self.window
        w.start_run()
        self.wait_until(lambda: bool(w.history))
        w.stop_run()
        self.wait_until(lambda: not w.worker.isRunning())
        self.app.processEvents()
        w.start_run()
        w.playing = False
        self.wait_until(lambda: len(w.history) == 1)
        self.assertEqual(w.history[0].generation, 0)

    def test_zoom_survives_steps_and_metric_history_is_independent(self):
        w = self.window
        w.metric_choice.setCurrentIndex(w.metric_choice.findData("r2"))
        w.set_view(-0.75, 0.75)
        w.start_run()
        w.playing = False
        self.wait_until(lambda: len(w.history) == 1)
        self.assertEqual(w.run_config.metric, "r2")
        self.assertFalse(w.metric_choice.isEnabled())
        w.step()
        self.wait_until(lambda: len(w.history) == 2)
        self.assertEqual(w.view_limits, (-0.75, 0.75))
        self.assertEqual(tuple(w.fit_plot.axes.get_xlim()), (-0.75, 0.75))
        metrics = w.history[-1].best.metrics
        w.set_view(0.1, 0.2)
        self.assertEqual(w.history[-1].best.metrics, metrics)
        w.history_metric.setCurrentIndex(w.history_metric.findData("rmse"))
        self.assertEqual(w.run_config.metric, "r2")
        w.first_generation()
        self.assertEqual(w.view_limits, (0.1, 0.2))
        self.assertEqual(w.timeline.value(), 0)

    def test_invalid_metric_does_not_start_worker(self):
        w = self.window
        w.data = validate_dataset([0, 1, 2], [3, 3, 3], "constante")
        w.refresh_data()
        w.metric_choice.setCurrentIndex(w.metric_choice.findData("r2"))
        errors = []
        w.error = errors.append
        w.start_run()
        self.assertIsNone(w.worker)
        self.assertIn("no está definido", errors[0])


if __name__ == "__main__":
    unittest.main()
