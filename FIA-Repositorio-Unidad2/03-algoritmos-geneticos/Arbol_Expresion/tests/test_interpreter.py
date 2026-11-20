"""Pruebas de reglas matemáticas y contratos del servidor.

Ejecuta: python -m unittest discover -s tests -v
"""

import math
import unittest
from app import app
from interpreter import ExpressionError, interpret


class InterpreterTests(unittest.TestCase):
    def assertValue(self, expression, expected, variables=None):
        result = interpret(expression, variables)
        self.assertIsNone(result["evaluation"]["error"], result["evaluation"])
        self.assertAlmostEqual(result["evaluation"]["value"], expected)
        return result

    def test_precedence_and_parentheses(self):
        for expression, value in [("2+3*4", 14), ("(2+3)*4", 20), ("8/4/2", 1), ("8-4-2", 2)]:
            with self.subTest(expression=expression):
                self.assertValue(expression, value)

    def test_right_associative_powers(self):
        self.assertValue("2^3^2", 512)
        self.assertValue("2**3**2", 512)

    def test_unary_signs(self):
        for expression, value in [("-2^2", -4), ("(-2)^2", 4), ("2^-2", .25), ("--3", 3), ("2*-3", -6)]:
            with self.subTest(expression=expression):
                self.assertValue(expression, value)

    def test_sqrt_structure_and_values(self):
        result = self.assertValue("sqrt(x^2 + y^2)", 5, {"x": 3, "y": 4})
        self.assertEqual(result["tree"]["label"], "sqrt")
        self.assertEqual(result["tree"]["children"][0]["label"], "+")
        self.assertEqual(result["stats"], {"nodes": 8, "depth": 4, "leaves": 4, "operations": 4})

    def test_implicit_multiplication(self):
        for expression, value in [("2x(x+1)", 24), ("(x+1)(x-1)", 8), ("2sin(pi/2)", 2), ("2pi", 2*math.pi), ("2 e", 2*math.e)]:
            with self.subTest(expression=expression):
                self.assertValue(expression, value, {"x": 3})

    def test_identifiers_are_whole_names(self):
        self.assertValue("xy + x2", 9, {"xy": 4, "x2": 5})

    def test_unicode_aliases(self):
        for expression in ("√(16)", "raiz(16)", "raíz(16)"):
            with self.subTest(expression=expression):
                self.assertValue(expression, 4)
        self.assertValue("sen(π/2) × 4 − 2 ÷ 2", 3)

    def test_scientific_notation_and_decimals(self):
        self.assertValue("1.2e3 + .5 - 2.5E-1", 1200.25)

    def test_function_arguments(self):
        self.assertValue("root(27, 3)+log(8,2)", 6)
        self.assertValue("root(-27,3)", -3)
        self.assertValue("max(1,min(4,8),3)", 4)
        self.assertValue("hypot(3,4)", 5)
        self.assertValue("ln(e)+log10(100)+abs(-2)", 5)

    def test_factorial(self):
        self.assertValue("0!+4!", 25)
        self.assertValue("-3!", -6)
        self.assertValue("2^3!", 64)

    def test_traversals_visit_every_node_once(self):
        result = interpret("max(1+2,3,4^2)")
        for order in result["traversals"].values():
            self.assertEqual(len(order), result["stats"]["nodes"])
            self.assertEqual(len(order), len(set(order)))
        self.assertEqual(result["traversals"]["preorder"][0], result["tree"]["id"])
        self.assertEqual(result["traversals"]["postorder"][-1], result["tree"]["id"])
        simple = interpret("2+3*4")
        self.assertEqual(simple["notation"]["prefix"], "+ 2 * 3 4")
        self.assertEqual(simple["notation"]["postfix"], "2 3 4 * +")

    def test_invalid_syntax(self):
        for expression in ("", "2+", "(2+3", "2+3)", "sqrt()", "sqrt(1,2)", "misterio(2)", "sin x", "x=2", "2@3", "max(1)", "min(1,)", "2 3", "1.2.3"):
            with self.subTest(expression=expression), self.assertRaises(ExpressionError):
                interpret(expression)

    def test_domain_errors_keep_the_tree(self):
        for expression in ("sqrt(-1)", "1/0", "1%0", "ln(0)", "root(1,0)", "root(-2,2)", "(-1)!", "3.5!", "171!", "2^1001", "exp(1000)", "1e999", "pow(-2,.5)"):
            with self.subTest(expression=expression):
                result = interpret(expression)
                self.assertIsNone(result["evaluation"]["value"])
                self.assertTrue(result["evaluation"]["error"])
                self.assertTrue(result["tree"]["id"])

    def test_missing_variable_does_not_destroy_sibling_values(self):
        result = interpret("x + 2^3")
        self.assertIn("x", result["evaluation"]["error"])
        self.assertEqual(result["tree"]["children"][1]["value"], 8)

    def test_invalid_variable_values(self):
        for value in (True, "3", float("nan"), float("inf"), 10**1000):
            with self.subTest(value=str(value)[:30]), self.assertRaises(ExpressionError):
                interpret("x", {"x": value})
        for variables in ([], [1], "x"):
            with self.subTest(variables=variables), self.assertRaises(ExpressionError):
                interpret("x", variables)

    def test_limits(self):
        for expression in ("1"*513, "("*60+"1"+")"*60, "+".join(["1"]*100)):
            with self.subTest(length=len(expression)), self.assertRaises(ExpressionError):
                interpret(expression)

    def test_input_is_never_executed(self):
        for expression in ("__import__('os')", "open('file')", "x.__class__", "[1,2]", "lambda: 1"):
            with self.subTest(expression=expression), self.assertRaises(ExpressionError):
                interpret(expression)


class ApiTests(unittest.TestCase):
    def setUp(self):
        self.client = app.test_client()

    def test_static_files(self):
        for path in ("/", "/static/styles.css", "/static/app.js", "/static/scene.js", "/static/vendor/three.module.js"):
            with self.subTest(path=path):
                response = self.client.get(path)
                self.assertEqual(response.status_code, 200)
                response.close()

    def test_parse_endpoint(self):
        response = self.client.post("/api/parse", json={"expression": "sqrt(x^2+y^2)", "variables": {"x": 3, "y": 4}})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json["evaluation"]["value"], 5)

    def test_syntax_error_has_position(self):
        response = self.client.post("/api/parse", json={"expression": "2+"})
        self.assertEqual(response.status_code, 400)
        self.assertIsInstance(response.json["position"], int)

    def test_invalid_json_and_types(self):
        for data in (None, [], 3, {}, {"expression": 42}, {"expression": "x", "variables": []}, {"expression": "x", "variables": {"x": 10**1000}}):
            with self.subTest(data=str(data)[:50]):
                response = self.client.post("/api/parse", json=data)
                self.assertEqual(response.status_code, 400)

    def test_size_limit(self):
        response = self.client.post("/api/parse", data='{"expression":"' + "1"*17000 + '"}', content_type="application/json")
        self.assertEqual(response.status_code, 413)
        self.assertIn("error", response.json)

    def test_function_catalog(self):
        response = self.client.get("/api/functions")
        self.assertEqual(response.status_code, 200)
        self.assertIn("sqrt", [item["name"] for item in response.json["functions"]])
        self.assertEqual(response.json["aliases"]["raiz"], "sqrt")


if __name__ == "__main__":
    unittest.main()
