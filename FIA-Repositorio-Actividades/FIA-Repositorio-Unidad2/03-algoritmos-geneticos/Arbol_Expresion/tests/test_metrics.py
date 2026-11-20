"""Comprueba comparación, muestreo extenso y simplificación con casos conocidos."""

import io
import json
import math
import unittest
from unittest.mock import patch
from app import app
from csv_comparison import compare_csv
from expression_tree import ExpressionTree
from interpreter import ExpressionError, Parser
from metrics import regression_metrics
from sampling import build_domain, sample_expressions

FORMULA = "6.87 + 11 * cos(7.23 * x^3)"


class MetricsTests(unittest.TestCase):
    def test_hand_calculated_metrics(self):
        metrics = regression_metrics([1, 3], [2, 2])
        self.assertEqual([metrics[key] for key in ("mse", "rmse", "nmse", "r2")], [1, 1, 1, 0])
        perfect = regression_metrics([1, 3], [1, 3])
        self.assertEqual(perfect["mse"], 0)
        self.assertEqual(perfect["r2"], 1)
        self.assertLess(regression_metrics([1, 3], [10, 10])["r2"], 0)

    def test_invalid_pairs_are_not_silently_removed(self):
        result = regression_metrics([1, 3], [1, None])
        self.assertEqual(result["invalid"], 1)
        self.assertIsNone(result["mse"])
        with self.assertRaises(ExpressionError):
            regression_metrics([1], [1, 2])
        with self.assertRaises(ExpressionError):
            regression_metrics([float("nan")], [1])

    def test_constant_target_has_undefined_normalized_metrics(self):
        result = regression_metrics([2, 2], [2, 3])
        self.assertEqual(result["mse"], .5)
        self.assertIsNone(result["nmse"])
        self.assertIsNone(result["r2"])

    def test_requested_exercise_endpoints_values_and_metrics(self):
        result = sample_expressions([FORMULA, f"({FORMULA})+1"], start=-10, end=10, step=.001)
        self.assertEqual(result["points"], 20001)
        self.assertEqual((result["x"][0], result["x"][-1]), (-10, 10))
        self.assertEqual(result["series"][0]["y"][10000], 17.87)
        self.assertAlmostEqual(result["series"][0]["y"][0], 6.87 + 11 * math.cos(-7230))
        self.assertAlmostEqual(result["metrics"][0]["mse"], 1)
        self.assertAlmostEqual(result["metrics"][0]["rmse"], 1)
        self.assertTrue(all(abs((b - a) - .001) < 1e-12 for a, b in zip(result["x"], result["x"][1:])))

    def test_sampling_builds_one_tree_and_no_visual_reports(self):
        original = Parser.parse
        with patch.object(Parser, "parse", autospec=True, side_effect=original) as parser:
            with patch.object(ExpressionTree, "report", side_effect=AssertionError("No informes por muestra")):
                sample_expressions(["1/x"], start=-1, end=1, points=11)
        self.assertEqual(parser.call_count, 1)

    def test_limit_includes_short_final_interval(self):
        self.assertEqual(len(build_domain(0, 1, step=.00001)[0]), 100001)
        with self.assertRaises(ExpressionError):
            build_domain(0, 1.000001, step=.00001)


class CSVTests(unittest.TestCase):
    def test_csv_x_values_are_used_without_resampling(self):
        result = compare_csv("x,y\n0,1\n0.3,1.6\n1,3\n", ["2*x+1"])
        self.assertEqual(result["x"], [0, .3, 1])
        self.assertEqual(result["metrics"][0]["mse"], 0)
        self.assertEqual(result["sampling"]["mode"], "csv")

    def test_exported_headers_and_custom_columns(self):
        self.assertEqual(compare_csv('x,"f1: x^2",modo\n0,0,strict\n1,1,strict', ["x^2"])["metrics"][0]["mse"], 0)
        self.assertEqual(compare_csv("tiempo;medicion\n0;2\n1;3", ["x+2"], x_column="tiempo", y_column="medicion")["metrics"][0]["mse"], 0)

    def test_invalid_csv_is_rejected(self):
        for content in ("", "x,z\n0,1\n1,2", "x,y\n0,1\n0,2", "x,y\n1,1\n0,2", "x,y\n0,nan\n1,2", "x,y\n0,\n1,2", "x,y\n0,1", "x,y\n0,1,3\n1,2"):
            with self.subTest(content=content), self.assertRaises(ExpressionError):
                compare_csv(content, ["x"])

    def test_file_api_and_json_api(self):
        client = app.test_client()
        response = client.post("/api/compare-csv", data={"file": (io.BytesIO(b"x,y\n0,1\n1,3"), "objective.csv"), "options": json.dumps({"expressions": ["2*x+1"]})})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["metrics"][0]["r2"], 1)
        response = client.post("/api/sample", json={"expressions": [FORMULA], "start": -10, "end": 10, "step": .001})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["points"], 20001)


class SimplificationTests(unittest.TestCase):
    def test_folding_preserves_values_and_parent(self):
        tree = ExpressionTree("(2+3)*x + cos(0)")
        before = tree.to_expression()
        reduced = tree.simplify()
        self.assertLess(reduced.size, tree.size)
        self.assertEqual(tree.to_expression(), before)
        for x in (-1, 0, 5):
            self.assertEqual(tree.evaluate({"x": x}), reduced.evaluate({"x": x}))

    def test_simplification_preserves_errors_and_corrections(self):
        for source, policy in [("0*(1/0)", {"mode": "strict"}), ("sqrt(-9)+2", {"mode": "protected"}), ("1e90*1e90", {"mode": "protected"}), ("(pi+0)*x", {"mode": "protected", "max_value": 1})]:
            tree = ExpressionTree(source, policy)
            reduced = tree.simplify()
            self.assertEqual(tree.report()["evaluation"], reduced.report()["evaluation"])
            self.assertEqual(len(tree.report()["corrections"]), len(reduced.report()["corrections"]))

    def test_simplification_api(self):
        result = app.test_client().post("/api/simplify", json={"expression": "(2+3)*x", "variables": {"x": 2}})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json["evaluation"]["value"], 10)
        self.assertEqual(result.json["simplification"], {"before": 5, "after": 3, "original": "(2+3)*x"})
