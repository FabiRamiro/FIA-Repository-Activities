"""La biblioteca, el árbol reconstruido y la curva deben cumplir el mismo contrato."""

import math
import unittest

from app import app
from expression_tree import ExpressionTree
from generator import ExpressionGenerator, generate_expression
from interpreter import ExpressionError, Parser, infix
from operations import OPERATIONS
from sampling import build_domain, sample_expressions


class LibraryTests(unittest.TestCase):
    def test_exact_requested_library_and_arities(self):
        self.assertEqual(len(OPERATIONS), 11)
        binary = {"add", "sub", "mul", "div", "mod", "pow"}
        unary = {"sqrt", "sin", "cos", "tan", "log"}
        self.assertEqual({item.id for item in OPERATIONS}, binary | unary)
        for operation in OPERATIONS:
            self.assertEqual(operation.arity, 2 if operation.id in binary else 1)
        self.assertEqual(ExpressionTree.DEFAULT_PRIMITIVES, tuple(item.label for item in OPERATIONS))

    def test_catalog_matches_interpreter(self):
        for operation in OPERATIONS:
            expression = f"(x {operation.label} 2)" if operation.kind == "operator" else f"{operation.label}(x)"
            root = Parser(expression).parse()
            self.assertEqual((root.kind, root.label, len(root.children)), (operation.kind, operation.label, operation.arity))


class GeneratorTests(unittest.TestCase):
    def test_height_library_and_arity_invariants_over_many_seeds(self):
        allowed = {(item.kind, item.label): item.arity for item in OPERATIONS}
        for height in (1, 2, 3, 5, 8, 12):
            for seed in range(25):
                with self.subTest(height=height, seed=seed):
                    tree = ExpressionGenerator(seed=seed).generate(max_height=height)
                    self.assertLessEqual(tree.depth, height)
                    self.assertLessEqual(tree.size, 160)
                    self.assertIn("x", tree.variables)
                    for path in tree.paths():
                        node = tree.subtree(path)
                        if node.children:
                            self.assertIn((node.kind, node.label), allowed)
                            self.assertEqual(len(node.children), allowed[(node.kind, node.label)])
                        else:
                            self.assertIn(node.kind, ("number", "variable"))
                    restored = ExpressionTree(tree.to_expression(), tree.policy)
                    self.assertEqual(restored.depth, tree.depth)
                    self.assertEqual(restored.size, tree.size)
                    self.assertTrue(all(value is not None and math.isfinite(value) for value in restored.predict([{"x": -1}, {"x": 0}, {"x": 1}])))

    def test_selected_operations_only_and_no_constants(self):
        for seed in range(20):
            tree = ExpressionGenerator(["sin", "mul"], seed=seed).generate(constants=False)
            for path in tree.paths():
                node = tree.subtree(path)
                if node.children:
                    self.assertIn(node.label, ("sin", "*"))
                else:
                    self.assertEqual((node.kind, node.label), ("variable", "x"))

    def test_every_operation_can_be_selected_alone(self):
        for operation in OPERATIONS:
            with self.subTest(operation=operation.id):
                tree = ExpressionGenerator([operation.id], seed=2).generate(max_height=2, constants=False)
                self.assertEqual(tree.root.label, operation.label)
                self.assertEqual(tree.depth, 2)
                self.assertEqual(len(tree.root.children), operation.arity)

    def test_reproducibility(self):
        self.assertEqual(ExpressionGenerator(seed=7).generate().to_expression(), ExpressionGenerator(seed=7).generate().to_expression())
        expressions = {ExpressionGenerator(seed=seed).generate().to_expression() for seed in range(20)}
        self.assertGreater(len(expressions), 10)

    def test_negative_constants_are_leaves_after_reparsing(self):
        found = False
        for seed in range(10):
            tree = ExpressionGenerator(["add"], seed=seed).generate(max_height=2, constant_min=-4, constant_max=-4)
            for path in tree.paths():
                node = tree.subtree(path)
                if node.kind == "number":
                    self.assertLess(float(node.label), 0)
                    found = True
            self.assertEqual(tree.depth, 2)
            self.assertNotIn("unary", [tree.subtree(path).kind for path in tree.paths()])
        self.assertTrue(found)

    def test_one_level_tree_and_custom_variable(self):
        tree = ExpressionGenerator(seed=1).generate(variable="tiempo", max_height=1)
        self.assertEqual(tree.depth, 1)
        self.assertEqual(tree.size, 1)
        self.assertEqual(tree.root.label, "tiempo")

    def test_invalid_configuration(self):
        for operations in ([], "sin", ["exp"], ["root"], [None], [{}]):
            with self.subTest(operations=operations), self.assertRaises(ExpressionError):
                ExpressionGenerator(operations)
        for seed in (True, 1.1, "7", 2**53):
            with self.assertRaises(ExpressionError):
                ExpressionGenerator(seed=seed)
        for settings in ({"max_height": 0}, {"max_height": 13}, {"max_height": True}, {"variable": "pi"}, {"variable": "1x"}, {"variable": "a"*65}, {"constants": "yes"}, {"constant_min": 5, "constant_max": -5}):
            with self.subTest(settings=settings), self.assertRaises(ExpressionError):
                ExpressionGenerator().generate(**settings)

    def test_report_tree_and_curve_are_the_same_expression(self):
        result = generate_expression(seed=17, max_height=5, start=-1, end=1, step=.2, variables={"x": .25})
        self.assertEqual(result["curve"]["series"][0]["expression"], result["expression"])
        self.assertEqual(result["generation"]["actual_height"], result["stats"]["depth"])
        self.assertEqual(infix(Parser(result["expression"]).parse()), result["notation"]["infix"])
        tree = ExpressionTree(result["expression"], result["policy"])
        self.assertEqual(result["evaluation"]["value"], tree.evaluate({"x": .25}))
        self.assertEqual(result["curve"]["series"][0]["y"], tree.predict([{"x": x} for x in result["curve"]["x"]]))


class StepSamplingTests(unittest.TestCase):
    def test_decimal_step_and_endpoints(self):
        xs, metadata = build_domain(0, 1, step=.1)
        self.assertEqual(xs, [0, .1, .2, .3, .4, .5, .6, .7, .8, .9, 1])
        self.assertFalse(metadata["short_final_interval"])

    def test_non_divisible_domain_preserves_requested_step(self):
        xs, metadata = build_domain(0, 1, step=.3)
        self.assertEqual(xs, [0, .3, .6, .9, 1])
        self.assertTrue(metadata["short_final_interval"])
        self.assertEqual(build_domain(-1, 1, step=.5)[0], [-1, -.5, 0, .5, 1])
        self.assertEqual(build_domain(0, 1, step=2)[0], [0, 1])

    def test_upper_limit_and_bad_steps(self):
        self.assertEqual(len(build_domain(0, 1, step=.00001)[0]), 100001)
        for step in (0, -1, True, "0.1", float("nan"), .000001, 1e-300):
            with self.subTest(step=step), self.assertRaises(ExpressionError):
                build_domain(0, 1, step=step)

    def test_step_can_be_used_for_several_curves(self):
        data = sample_expressions(["x", "x^2"], step=.3)
        self.assertEqual(data["points"], 5)
        self.assertEqual(data["sampling"]["mode"], "step")
        self.assertEqual(data["series"][0]["y"], data["x"])
        self.assertEqual(data["series"][1]["y"], [x*x for x in data["x"]])

    def test_signed_literal_preserves_power_precedence(self):
        for source, expected in [("-2^2", -4), ("(-2)^2", 4), ("2^-2", .25), ("2^-2^2", .0625), ("-3!", -6)]:
            with self.subTest(source=source):
                self.assertEqual(ExpressionTree(source).evaluate(), expected)
        negative = Parser("(-3)").parse()
        self.assertEqual((negative.kind, negative.label, negative.children), ("number", "-3", []))


class GeneratorApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_library_endpoint(self):
        result = self.client.get("/api/operations")
        self.assertEqual(result.status_code, 200)
        self.assertEqual(len(result.json["operations"]), 11)
        self.assertEqual(result.json["height_convention"], "levels")

    def test_generate_endpoint(self):
        result = self.client.post("/api/generate", json={"operations": ["sin", "add", "pow"], "max_height": 4, "seed": 7, "domain": {"start": 0, "end": 1, "step": .1}})
        self.assertEqual(result.status_code, 200)
        self.assertLessEqual(result.json["stats"]["depth"], 4)
        self.assertEqual(result.json["curve"]["points"], 11)
        self.assertEqual(result.json["policy"]["mode"], "protected")

    def test_invalid_requests(self):
        for payload in ([], {"operations": []}, {"operations": ["open"]}, {"max_height": None}, {"seed": True}, {"domain": []}, {"domain": {"start": 2, "end": 1}}, {"domain": {"step": 0}}, {"policy": {"mode": "invalid"}}):
            with self.subTest(payload=payload):
                response = self.client.post("/api/generate", json=payload)
                self.assertEqual(response.status_code, 400)
                self.assertIn("error", response.json)

    def test_sample_endpoint_accepts_step(self):
        result = self.client.post("/api/sample", json={"expressions": ["x^2"], "start": 0, "end": 1, "step": .3})
        self.assertEqual(result.status_code, 200)
        self.assertEqual(result.json["x"], [0, .3, .6, .9, 1])


if __name__ == "__main__":
    unittest.main()
