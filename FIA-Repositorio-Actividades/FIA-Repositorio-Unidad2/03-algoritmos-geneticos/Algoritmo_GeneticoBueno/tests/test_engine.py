"""Pruebas de contratos matemáticos y de los operadores genéticos."""
import math
from pathlib import Path
import random
import tempfile
import unittest
import numpy as np
from genetic_lab.data import generate_dataset, load_csv, save_csv, validate_dataset, PRESETS
from genetic_lab.metrics import calculate_metrics
from genetic_lab.trees import Node, evaluate, repair, simplify, crossover, mutate, random_tree
from genetic_lab.evolution import Config, Evolution


class MetricTests(unittest.TestCase):
    def test_hand_calculated_example(self):
        result = calculate_metrics([1, 2, 5], [0, 1, 4])
        self.assertAlmostEqual(result.mse, 1)
        self.assertAlmostEqual(result.nmse, 0.1)
        self.assertAlmostEqual(result.r2, 17/26)
        self.assertAlmostEqual(result.rmse, 1)
        self.assertNotAlmostEqual(result.r2, 1 - result.nmse)

    def test_perfect_and_negative_r2(self):
        self.assertEqual(calculate_metrics([1, 2, 3], [1, 2, 3]).r2, 1)
        self.assertLess(calculate_metrics([1, 2, 3], [100, 100, 100]).r2, 0)

    def test_constant_target_only_r2_is_undefined(self):
        result = calculate_metrics([3, 3, 3], [3, 3, 3])
        self.assertEqual(result.mse, 0)
        self.assertEqual(result.nmse, 0)
        self.assertTrue(math.isnan(result.r2))
        self.assertEqual(result.rmse, 0)

    def test_zero_target_has_two_undefined_ratios(self):
        result = calculate_metrics([0, 0, 0], [1, 1, 1])
        self.assertEqual(result.mse, 1)
        self.assertEqual(result.rmse, 1)
        self.assertTrue(math.isnan(result.nmse))
        self.assertTrue(math.isnan(result.r2))

    def test_rmse_is_root_mse_not_root_nmse(self):
        result = calculate_metrics([10, 20, 30], [8, 18, 28])
        self.assertEqual(result.mse, 4)
        self.assertEqual(result.rmse, 2)
        self.assertAlmostEqual(result.nmse, 12 / 1400)

    def test_invalid_predictions_rejected(self):
        with self.assertRaises(ValueError): calculate_metrics([1, 2], [math.nan, 2])
        with self.assertRaises(ValueError): calculate_metrics([1, 2], [1])


class TreeTests(unittest.TestCase):
    def test_expression_evaluation(self):
        tree = Node("+", (Node("*", (Node("x"), Node("x"))), Node("const", value=1)))
        np.testing.assert_allclose(evaluate(tree, np.array([-2, 0, 2])), [5, 1, 5])
        self.assertEqual(tree.depth, 3)
        self.assertEqual(tree.size, 5)

    def test_protected_operators(self):
        x = np.array([-3., 0., 2.])
        division = Node("/", (Node("x"), Node("const", value=0)))
        np.testing.assert_allclose(evaluate(division, x), x)
        np.testing.assert_allclose(evaluate(Node("sqrt", (Node("x"),)), x), np.sqrt(np.abs(x)))
        np.testing.assert_allclose(evaluate(Node("log", (Node("x"),)), x), np.log1p(np.abs(x)))

    def test_repair_arity_constants_and_depth(self):
        rng = random.Random(1)
        tree = Node("+", (Node("sin", (Node("sin", (Node("x"),)),)),))
        fixed, count = repair(tree, 2, rng)
        self.assertLessEqual(fixed.depth, 2)
        self.assertEqual(len(fixed.children), 2)
        self.assertGreater(count, 0)
        bad, count = repair(Node("const", value=math.inf), 3, rng)
        self.assertEqual(bad.value, 0)
        self.assertEqual(count, 1)
        unknown, count = repair(Node("unknown"), 3, rng)
        self.assertIn(unknown.op, ("x", "const"))

    def test_pruning_preserves_protected_semantics(self):
        rng = random.Random(91)
        x = np.array([-1e6, -1, 0, 1, 1e6])
        for _ in range(100):
            tree = random_tree(rng, 5, ("+", "-", "*", "/", "sin", "cos", "sqrt", "log"))
            pruned, _ = simplify(tree)
            np.testing.assert_allclose(evaluate(tree, x), evaluate(pruned, x), rtol=1e-12, atol=1e-12)
            self.assertLessEqual(pruned.size, tree.size)

    def test_genetic_operators_do_not_change_parents(self):
        rng = random.Random(12)
        a = Node("+", (Node("x"), Node("const", value=1)))
        b = Node("*", (Node("x"), Node("x")))
        original_a, original_b = a.expression(), b.expression()
        for _ in range(50):
            child, _ = crossover(a, b, rng)
            child, _ = mutate(child, rng, 5, ("+", "-", "*"))
            child, _ = repair(child, 5, rng)
            self.assertLessEqual(child.depth, 5)
        self.assertEqual(a.expression(), original_a)
        self.assertEqual(b.expression(), original_b)


class DataTests(unittest.TestCase):
    def test_csv_round_trip(self):
        data = generate_dataset(next(iter(PRESETS)), count=15, noise=0.1)
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            path = Path(folder) / "points.csv"
            save_csv(data, path)
            loaded = load_csv(path)
        np.testing.assert_allclose(data.x, loaded.x)
        np.testing.assert_allclose(data.y, loaded.y)

    def test_bom_semicolon_and_sort(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            path = Path(folder) / "points.csv"
            path.write_text("\ufeff X ; Y \n2;5\n0;1\n1;2\n", encoding="utf-8")
            loaded = load_csv(path)
        np.testing.assert_allclose(loaded.x, [0, 1, 2])

    def test_bad_csv_has_line_number(self):
        with tempfile.TemporaryDirectory(dir=Path(__file__).resolve().parent) as folder:
            path = Path(folder) / "bad.csv"
            path.write_text("x,y\n1,no\n2,4\n3,5\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "Fila 2"):
                load_csv(path)

    def test_invalid_data(self):
        with self.assertRaises(ValueError): validate_dataset([1, 1, 1], [2, 3, 4], "bad")
        with self.assertRaises(ValueError): validate_dataset([1, 2, 3], [1, np.nan, 2], "bad")
        with self.assertRaises(ValueError): validate_dataset([1, 2], [1, 2], "bad")


class EvolutionTests(unittest.TestCase):
    def test_reproducibility_and_elitism(self):
        data = generate_dataset("Parábola · x² + x + 1", count=30)
        config = Config(population=70, generations=12, max_depth=5, seed=42)
        first = list(Evolution(data, config).run())
        second = list(Evolution(data, config).run())
        self.assertEqual(len(first), 13)
        self.assertEqual([s.best.tree for s in first], [s.best.tree for s in second])
        errors = [s.best.metrics.mse for s in first]
        self.assertTrue(all(b <= a for a, b in zip(errors, errors[1:])))
        self.assertTrue(all(s.best.tree.depth <= config.max_depth for s in first))
        self.assertLess(errors[-1], errors[0])
        self.assertTrue(any(s.counts.get("cruzas", 0) for s in first))
        self.assertTrue(any(s.counts.get("mutaciones", 0) for s in first))
        self.assertTrue(any(s.counts.get("podas", 0) for s in first))
        self.assertTrue(any(s.counts.get("reparaciones", 0) for s in first))
        for snapshot in first[1:]:
            self.assertEqual(snapshot.counts["reconstrucciones"],
                             snapshot.counts["cruzas"] + snapshot.counts["mutaciones"])
            self.assertTrue(any(event.kind == "Reconstrucción" for event in snapshot.events))

    def test_constant_target(self):
        data = generate_dataset("Constante · 3", count=15)
        snapshots = list(Evolution(data, Config(population=20, generations=3)).run())
        self.assertTrue(all(math.isfinite(s.best.score) for s in snapshots))

    def test_cancel_before_initial_generation(self):
        data = generate_dataset(next(iter(PRESETS)))
        self.assertEqual(list(Evolution(data, Config()).run(lambda: True)), [])

    def test_invalid_config(self):
        for config in [Config(population=10, elitism=10), Config(mutation_rate=2), Config(operators=()),
                       Config(max_depth=20), Config(parsimony=-1)]:
            with self.assertRaises(ValueError): config.validate()


if __name__ == "__main__":
    unittest.main()
