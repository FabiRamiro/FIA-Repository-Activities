"""Pruebas de protección, programación genética y curvas de resultados."""

import math
import random
import unittest
from unittest.mock import patch
from app import app
from arithmetic import EvaluationPolicy
from expression_tree import ExpressionTree
from interpreter import ExpressionError, Node, Parser, interpret
from sampling import sample_expressions

PROTECTED = {"mode": "protected", "epsilon": 1e-9, "max_value": 1e12}


class ProtectedArithmeticTests(unittest.TestCase):
    def result(self, source):
        result = interpret(source, policy=PROTECTED)
        self.assertIsNone(result["evaluation"]["error"], result)
        self.assertTrue(math.isfinite(result["evaluation"]["value"]))
        self.assertLessEqual(abs(result["evaluation"]["value"]), 1e12)
        return result

    def test_division_preserves_sign_and_respects_threshold(self):
        for source, value in [("1/0", 1e9), ("1/-1e-12", -1e9), ("0/0", 0), ("1/1e-8", 1e8)]:
            with self.subTest(source=source):
                self.assertAlmostEqual(self.result(source)["evaluation"]["value"], value, delta=1e-6)
        self.assertTrue(self.result("1/0")["corrections"])
        self.assertFalse(self.result("1/1e-8")["corrections"])

    def test_epsilon_is_configurable(self):
        self.assertEqual(interpret("1/0", policy={**PROTECTED, "epsilon": .001})["evaluation"]["value"], 1000)

    def test_negative_roots(self):
        for source, value in [("sqrt(-9)", 3), ("root(-27,3)", -3), ("root(-16,2)", 4), ("root(-27,-3)", -1/3)]:
            with self.subTest(source=source):
                self.assertAlmostEqual(self.result(source)["evaluation"]["value"], value)
        self.assertFalse(self.result("root(-27,3)")["corrections"])

    def test_logs_power_and_trigonometric_domains(self):
        for source in ("ln(0)", "log(-8,-2)", "log(4,1)", "(-4)^.5", "0^-2", "root(2,0)", "acos(2)", "asin(-3)", "1%0"):
            with self.subTest(source=source):
                self.assertTrue(self.result(source)["corrections"])

    def test_saturation_and_large_intermediate_results(self):
        for source in ("exp(10000)", "sinh(-10000)", "cosh(10000)", "10^1000", "1e90*1e90", "170!", "(-3.2)!", "1e999", "tan(pi/2)"):
            with self.subTest(source=source):
                self.assertTrue(self.result(source)["corrections"])
        self.assertLess(self.result("sinh(-10000)")["evaluation"]["value"], 0)

    def test_strict_mode_remains_unchanged(self):
        for source in ("sqrt(-9)", "1/0", "ln(0)", "acos(2)"):
            with self.subTest(source=source):
                result = interpret(source, policy={"mode": "strict"})
                self.assertIsNone(result["evaluation"]["value"])
                self.assertTrue(result["evaluation"]["error"])
                self.assertFalse(result["corrections"])

    def test_missing_variables_are_not_fabricated(self):
        result = interpret("x/0", policy=PROTECTED)
        self.assertIsNone(result["evaluation"]["value"])
        self.assertIn("x", result["evaluation"]["error"])

    def test_evaluation_clears_old_corrections(self):
        tree = ExpressionTree("1/x", PROTECTED)
        self.assertTrue(tree.report({"x": 0})["corrections"])
        self.assertFalse(tree.report({"x": 2})["corrections"])

    def test_invalid_policy(self):
        for policy in ([], {"mode": "complex"}, {"epsilon": 0}, {"epsilon": float("nan")}, {"max_value": True}, {"max_value": -1}, {"epsilon": None}, {"bad": 1}):
            with self.subTest(policy=policy), self.assertRaises(ExpressionError):
                interpret("1+1", policy=policy)


class ExpressionTreeTests(unittest.TestCase):
    def test_parse_once_evaluate_many_times(self):
        tree = ExpressionTree("x^2+x+1")
        with patch.object(Parser, "parse", side_effect=AssertionError("No se debe reanalizar")):
            self.assertEqual(tree.predict([{"x": 0}, {"x": 1}, {"x": 2}]), [1, 3, 7])

    def test_fitness_and_penalties(self):
        tree = ExpressionTree("x^2+x+1")
        rows = [{"x": 0}, {"x": 1}, {"x": 2}]
        self.assertEqual(tree.fitness(rows, [1, 3, 7]), 0)
        self.assertEqual(ExpressionTree("x").fitness(rows, [1, 2, 3]), 1)
        self.assertEqual(ExpressionTree("1/x").fitness(rows, [1, 2, 3]), 1e100)
        with self.assertRaises(ExpressionError):
            tree.fitness(rows, [])

    def test_serialization_preserves_semantics_and_policy(self):
        tree = ExpressionTree("sqrt(-x)+1/0", PROTECTED)
        restored = ExpressionTree.from_dict(tree.to_dict())
        self.assertEqual(restored.evaluate({"x": 4}), tree.evaluate({"x": 4}))
        self.assertEqual(restored.policy, tree.policy)
        self.assertEqual(restored.variables, ["x"])

    def test_clone_and_subtree_replacement_leave_parent_unchanged(self):
        parent = ExpressionTree("x+1")
        before = parent.to_dict()
        child = parent.replace_subtree((1,), ExpressionTree("2*x"))
        self.assertEqual(child.evaluate({"x": 3}), 9)
        self.assertEqual(parent.to_dict(), before)
        self.assertIsNot(child.root, parent.root)
        self.assertEqual(parent.clone().evaluate({"x": 2}), 3)
        with self.assertRaises(ExpressionError):
            parent.replace_subtree((-1,), child)

    def test_random_trees_are_reproducible(self):
        first = ExpressionTree.random(rng=random.Random(42), policy=PROTECTED)
        second = ExpressionTree.random(rng=random.Random(42), policy=PROTECTED)
        self.assertEqual(first.to_expression(), second.to_expression())
        self.assertLessEqual(first.depth, 4)

    def test_crossover_and_mutation_invariants(self):
        rng = random.Random(19)
        parents = [ExpressionTree("sqrt(x)+2", PROTECTED), ExpressionTree("x*x-1", PROTECTED)]
        originals = [parent.to_dict() for parent in parents]
        for _ in range(30):
            children = parents[0].crossover(parents[1], rng=rng, max_depth=6, max_nodes=40)
            for child in children:
                mutated = child.mutate(rng=rng, max_depth=6, max_nodes=40)
                self.assertLessEqual(mutated.depth, 6)
                self.assertLessEqual(mutated.size, 40)
                self.assertEqual(len({mutated.subtree(path).id for path in mutated.paths()}), mutated.size)
                self.assertTrue(all(value is not None and math.isfinite(value) for value in mutated.predict([{"x": -2}, {"x": 0}, {"x": 3}])))
        self.assertEqual([parent.to_dict() for parent in parents], originals)

    def test_negative_numeric_leaf_round_trip(self):
        tree = ExpressionTree.from_root(Node("", "^", "operator", [Node("", "-3", "number"), Node("", "2", "number")]))
        self.assertEqual(ExpressionTree(tree.to_expression()).evaluate(), 9)

    def test_invalid_serialized_trees_and_limits(self):
        cyclic = Node("", "+", "operator")
        cyclic.children = [cyclic, Node("", "1", "number")]
        with self.assertRaises(ExpressionError):
            ExpressionTree.from_root(cyclic)
        for payload in ({"kind": "function", "label": "open"}, {"kind": "operator", "label": "+", "children": []}, {"kind": "variable", "label": "sqrt"}, {"kind": "number", "label": "nan"}):
            with self.subTest(payload=payload), self.assertRaises(ExpressionError):
                ExpressionTree.from_dict(payload)
        for depth in (0, 13, True):
            with self.assertRaises(ExpressionError):
                ExpressionTree.random(max_depth=depth)

    def test_all_registered_primitives_can_be_used(self):
        from interpreter import FUNCTIONS
        for name in FUNCTIONS:
            tree = ExpressionTree.random(max_depth=3, primitives=(name,), rng=random.Random(2), policy=PROTECTED)
            self.assertTrue(math.isfinite(tree.evaluate({"x": -2})), name)


class SamplingTests(unittest.TestCase):
    def test_domain_is_inclusive(self):
        result = sample_expressions(["x^2"], start=0, end=1, points=5)
        self.assertEqual(result["x"], [0, .25, .5, .75, 1])
        self.assertEqual(result["series"][0]["y"], [0, .0625, .25, .5625, 1])

    def test_multiple_curves_and_fixed_variables(self):
        result = sample_expressions(["x+y", "x^2", "sin(x)"], start=0, end=1, points=3, variables={"x": 999, "y": 4})
        self.assertEqual(result["series"][0]["y"], [4, 4.5, 5])
        self.assertEqual(result["fixed_variables"], {"y": 4})

    def test_constant_curve(self):
        self.assertEqual(sample_expressions(["2"], points=3)["series"][0]["y"], [2, 2, 2])

    def test_strict_gaps_and_protected_counts(self):
        strict = sample_expressions(["sqrt(x)", "1/x"], start=-1, end=1, points=5)
        self.assertEqual(strict["series"][0]["y"][:2], [None, None])
        self.assertIsNone(strict["series"][1]["y"][2])
        protected = sample_expressions(["sqrt(x)", "1/x"], start=-1, end=1, points=5, policy=PROTECTED)
        self.assertEqual(protected["series"][0]["stats"]["corrected"], 2)
        self.assertEqual(protected["series"][1]["stats"]["corrected"], 1)
        self.assertTrue(all(value is not None for value in protected["series"][1]["y"]))

    def test_poles_between_samples_break_the_line(self):
        result = sample_expressions(["1/x"], start=-1, end=1, points=4)
        self.assertTrue(result["series"][0]["break_before"][2])
        tangent = sample_expressions(["tan(x)"], start=1, end=2, points=4)
        self.assertTrue(any(tangent["series"][0]["break_before"]))

    def test_invalid_domain_and_missing_fixed_variables(self):
        for options in ({"start": 1, "end": 1}, {"start": 2, "end": 1}, {"points": 100002}, {"points": 3.5}, {"points": True}, {"variable": "pi"}, {"start": float("nan")}):
            with self.subTest(options=options), self.assertRaises(ExpressionError):
                sample_expressions(["x"], **options)
        with self.assertRaises(ExpressionError):
            sample_expressions(["x+y"])
        with self.assertRaises(ExpressionError):
            sample_expressions(["x"] * 5)

    def test_extremely_narrow_domain_is_reported(self):
        with self.assertRaises(ExpressionError):
            sample_expressions(["x"], start=1, end=math.nextafter(1, 2), points=201)


class ExtensionApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_protected_api_and_sampling_share_rules(self):
        tree = self.client.post("/api/parse", json={"expression": "sqrt(-x)/0", "variables": {"x": 4}, "policy": PROTECTED})
        curve = self.client.post("/api/sample", json={"expressions": ["sqrt(-x)/0"], "start": 4, "end": 5, "points": 2, "policy": PROTECTED})
        self.assertEqual(tree.status_code, 200)
        self.assertEqual(curve.status_code, 200)
        self.assertEqual(tree.json["evaluation"]["value"], curve.json["series"][0]["y"][0])

    def test_sampling_api_rejects_invalid_requests(self):
        for payload in ([], {}, {"expressions": ["x"], "points": None}, {"expressions": ["x"], "end": "1"}, {"expressions": ["x"], "policy": {"mode": "magic"}}):
            with self.subTest(payload=payload):
                result = self.client.post("/api/sample", json=payload)
                self.assertEqual(result.status_code, 400)
                self.assertIn("error", result.json)


if __name__ == "__main__":
    unittest.main()
