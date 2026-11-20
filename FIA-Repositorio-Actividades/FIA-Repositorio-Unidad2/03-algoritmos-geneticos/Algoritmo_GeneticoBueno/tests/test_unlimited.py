"""Evolución sin límite de generaciones, evaluación incremental y mutación del élite."""
import random
import unittest

from genetic_lab.data import generate_dataset
from genetic_lab.evolution import Config, Evolution
from genetic_lab.trees import Node, mutate_constant


class UnlimitedEvolutionTests(unittest.TestCase):
    def test_unlimited_run_stops_when_target_r2_is_reached(self):
        data = generate_dataset("Recta · 2x + 3", count=40)
        history = list(Evolution(data, Config(population=40, generations=0, target_r2=0.99)).run())
        self.assertGreaterEqual(history[-1].best.metrics.r2, 0.99)
        self.assertTrue(all(s.best.metrics.r2 < 0.99 for s in history[:-1]))

    def test_unlimited_run_continues_until_cancelled(self):
        data = generate_dataset("Recta · 2x + 3", count=20)
        seen = []
        for snapshot in Evolution(data, Config(population=20, generations=0)).run(lambda: len(seen) >= 12):
            seen.append(snapshot)
        self.assertEqual(len(seen), 12)

    def test_incremental_window_grows_and_reports_full_data_metrics(self):
        data = generate_dataset("Parábola · x² + x + 1", count=400, low=-4, high=4)
        config = Config(population=60, generations=40, incremental=True, start_window=0.2, seed=3)
        history = list(Evolution(data, config).run())
        windows = [s.window for s in history]
        self.assertIsNotNone(windows[0])
        self.assertAlmostEqual(windows[0][1], 0.8)
        widths = [(w[1] - w[0]) if w else 8.0 for w in windows]
        self.assertEqual(widths, sorted(widths))
        self.assertGreater(widths[-1], widths[0])

    def test_elite_constant_mutation_changes_only_one_constant(self):
        tree = Node("+", (Node("const", value=2.0), Node("*", (Node("const", value=3.0), Node("x")))))
        child, detail = mutate_constant(tree, random.Random(1))
        self.assertIsNotNone(detail)
        before = [2.0, 3.0]
        after = [child.children[0].value, child.children[1].children[0].value]
        self.assertEqual(sum(a != b for a, b in zip(before, after)), 1)
        self.assertEqual(mutate_constant(Node("x"), random.Random(1)), (Node("x"), None))


if __name__ == "__main__":
    unittest.main()
