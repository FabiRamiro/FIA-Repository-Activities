"""Pruebas HTTP: el navegador recibe páginas y resultados reales de Python."""

import json
import threading
import unittest
from http.client import HTTPConnection
from http.server import ThreadingHTTPServer

from app import QueensHandler


class QuietHandler(QueensHandler):
    def log_message(self, *args):
        pass


class ServerTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.server = ThreadingHTTPServer(("127.0.0.1", 0), QuietHandler)
        cls.thread = threading.Thread(target=cls.server.serve_forever, daemon=True)
        cls.thread.start()

    @classmethod
    def tearDownClass(cls):
        cls.server.shutdown()
        cls.server.server_close()
        cls.thread.join()

    def request(self, path):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        connection.request("GET", path)
        response = connection.getresponse()
        body = response.read()
        status = response.status
        connection.close()
        return status, body

    def test_page_and_local_assets(self):
        for path in ["/", "/app.js", "/scene.js", "/style.css", "/assets/sakura-sanctuary.png",
                     "/vendor/three.module.js", "/vendor/OrbitControls.js", "/assets/dm-sans.ttf"]:
            with self.subTest(path=path):
                status, body = self.request(path)
                self.assertEqual(status, 200)
                self.assertTrue(body)

    def test_solver_endpoint(self):
        status, body = self.request("/api/solve?n=32&seed=42")
        self.assertEqual(status, 200)
        data = json.loads(body)
        self.assertEqual(data["algorithm"], "genetic")
        self.assertEqual(data["conflicts"], 0)
        self.assertTrue(data["solved"])
        self.assertEqual(data["n"], 32)

    def test_invalid_query(self):
        for query in ["n=0", "n=-1", "n=hola", "n=4.5", "n=", "n=4&n=8", "n=100000000",
                      "mutation=nan", "seconds=inf", "population=3", "generations=0"]:
            with self.subTest(query=query):
                status, body = self.request("/api/solve?" + query)
                self.assertEqual(status, 400)
                self.assertIn("error", json.loads(body))

    def test_ndjson_stream_contains_generations_and_result(self):
        connection = HTTPConnection("127.0.0.1", self.server.server_port, timeout=5)
        connection.request("GET", "/api/evolve?n=16&seed=42")
        response = connection.getresponse()
        self.assertEqual(response.status, 200)
        self.assertIn("application/x-ndjson", response.getheader("Content-Type"))
        first = json.loads(response.readline())
        self.assertEqual(first["generation"], 0)
        self.assertEqual(first["type"], "generation")
        rest = [json.loads(line) for line in response]
        self.assertEqual(rest[-1]["type"], "result")
        self.assertTrue(rest[-1]["solved"])
        connection.close()

    def test_validate_accepts_large_n_without_running_search(self):
        status, body = self.request("/api/validate?n=10000&population=4")
        self.assertEqual(status, 200)
        self.assertEqual(json.loads(body), {"n": 10000, "valid": True})

    def test_unknown_api_route(self):
        self.assertEqual(self.request("/api/missing")[0], 404)

    def test_python_source_is_not_served(self):
        for path in ["/app.py", "/solver.py", "/../app.py", "/%2e%2e/solver.py"]:
            with self.subTest(path=path):
                self.assertEqual(self.request(path)[0], 404)


if __name__ == "__main__":
    unittest.main()
