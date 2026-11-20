"""Contratos del motor nativo y de la selección del método de error."""
from pathlib import Path
import subprocess
import sys
import unittest

from genetic_lab.data import generate_dataset, validate_dataset
from genetic_lab.evolution import Config, Evolution
from genetic_lab.metrics import METRICS, calculate_metrics, metric_loss
from genetic_lab.refinement import refine_affine
from genetic_lab.trees import Node, evaluate


class NativeBackendTests(unittest.TestCase):
    def test_core_and_export_work_without_site_packages(self):
        # -S excluye site-packages: fallaría si el backend importara NumPy o Qt.
        code = """
import io, sys, zipfile, json
from genetic_lab.data import PRESETS, generate_dataset
from genetic_lab.evolution import Config, Evolution
from genetic_lab.exporting import write_experiment
data = generate_dataset(list(PRESETS)[1], count=15)
config = Config(population=20, generations=2, metric='rmse')
history = list(Evolution(data, config).run())
output = io.BytesIO()
write_experiment(output, data, config, history, 2)
with zipfile.ZipFile(output) as archive:
    assert json.loads(archive.read('resultado.json'))['config']['metric'] == 'rmse'
assert len(history) == 3
assert isinstance(data.x, tuple)
assert 'numpy' not in sys.modules
assert 'matplotlib' not in sys.modules
assert 'PySide6' not in sys.modules
print('native-ok')
"""
        result = subprocess.run([sys.executable, "-S", "-c", code],
                                cwd=Path(__file__).resolve().parents[1],
                                capture_output=True, text=True, timeout=20)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertIn("native-ok", result.stdout)

    def test_mean_is_not_optimal_when_better_curve_exists(self):
        expected = [-1, 1, -1, 1]
        mean = calculate_metrics(expected, [0, 0, 0, 0])
        perfect = calculate_metrics(expected, expected)
        self.assertEqual(mean.mse, 1)
        self.assertEqual(mean.r2, 0)
        for metric in METRICS:
            self.assertLess(metric_loss(perfect, metric), metric_loss(mean, metric))

    def test_four_criteria_rank_the_same_candidates(self):
        expected = [-1, 1, -1, 1]
        predictions = [[0, 0, 0, 0], expected, [2, -2, 2, -2], [-0.5, 0.5, -0.5, 0.5]]
        candidates = [calculate_metrics(expected, values) for values in predictions]
        for metric in METRICS:
            order = sorted(range(4), key=lambda i: metric_loss(candidates[i], metric))
            self.assertEqual(order, [1, 3, 0, 2])

    def test_selected_metric_elite_never_worsens(self):
        data = generate_dataset("Parábola · x² + x + 1", count=25)
        for metric in METRICS:
            history = list(Evolution(data, Config(population=30, generations=5, metric=metric)).run())
            losses = [metric_loss(s.best.metrics, metric) for s in history]
            self.assertTrue(all(next_loss <= previous for previous, next_loss in zip(losses, losses[1:])))
            self.assertTrue(all(s.metric == metric for s in history))

    def test_undefined_selection_metric_requires_valid_choice(self):
        constant = validate_dataset([0, 1, 2], [3, 3, 3], "constante")
        zero = validate_dataset([0, 1, 2], [0, 0, 0], "cero")
        for data, metric in [(constant, "r2"), (zero, "r2"), (zero, "nmse")]:
            with self.assertRaisesRegex(ValueError, "no está definido"):
                Evolution(data, Config(metric=metric))

    def test_stagnation_raises_mutation_and_preserves_elite(self):
        data = generate_dataset("Recta · 2x + 3", count=12)
        config = Config(population=20, generations=9, crossover_rate=0,
                        mutation_rate=0, immigration_rate=0, refine_constants=False)
        history = list(Evolution(data, config).run())
        self.assertEqual(history[8].stagnant_generations, 8)
        self.assertEqual(history[9].mutation_rate, 0.2)
        self.assertLessEqual(history[9].best.metrics.mse, history[8].best.metrics.mse)

    def test_refinement_fits_scale_and_offset_from_data(self):
        x = [-2, -1, 0, 1, 2]
        expected = [3 + 2 * value for value in x]
        refined, changed = refine_affine(Node("x"), x, expected, max_depth=3)
        self.assertTrue(changed)
        self.assertEqual(evaluate(refined, x), expected)
        self.assertLessEqual(refined.depth, 3)

    def test_refinement_keeps_depth_limit_and_validates_real_error(self):
        tree = Node("sin", (Node("x"),))
        x = [0, 1, 2]
        refused, changed = refine_affine(tree, x, [1, 2, 3], max_depth=2)
        self.assertFalse(changed)
        self.assertEqual(refused, tree)
        expected = evaluate(tree, x)
        same, changed = refine_affine(tree, x, expected, max_depth=4)
        self.assertFalse(changed)
        self.assertEqual(same, tree)

    def test_optional_refinement_is_logged_only_when_enabled(self):
        data = generate_dataset("Recta · 2x + 3", count=15)
        enabled = list(Evolution(data, Config(population=30, generations=3)).run())
        disabled = list(Evolution(data, Config(population=30, generations=3, refine_constants=False)).run())
        self.assertGreater(sum(s.counts.get("ajustes de constantes", 0) for s in enabled), 0)
        self.assertEqual(sum(s.counts.get("ajustes de constantes", 0) for s in disabled), 0)


if __name__ == "__main__":
    unittest.main()
