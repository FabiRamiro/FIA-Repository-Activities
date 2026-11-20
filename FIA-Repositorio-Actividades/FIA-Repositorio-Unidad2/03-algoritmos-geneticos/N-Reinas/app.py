"""Servidor local y API de evolución genética transmitida por generaciones."""

import argparse
import json
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlsplit

from solver import GeneticConfig, evolve_n_queens, solve_n_queens, validate

STATIC_DIRECTORY = Path(__file__).resolve().parent / "static"


class QueensHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(STATIC_DIRECTORY), **kwargs)

    def send_json(self, data, status=200):
        payload = json.dumps(data, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(payload)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(payload)

    def read_parameters(self, query):
        parameters = parse_qs(query, keep_blank_values=True)

        def value(name, default):
            values = parameters.get(name, [str(default)])
            if len(values) != 1 or not values[0].strip():
                raise ValueError(f"Envía un único valor válido para {name}.")
            return values[0]

        try:
            n = int(value("n", 8))
            config = GeneticConfig(population_size=int(value("population", 80)),
                                   max_generations=int(value("generations", 2000)),
                                   mutation_rate=float(value("mutation", 0.65)),
                                   time_limit=float(value("seconds", 15)),
                                   seed=int(value("seed", 0)) if "seed" in parameters else None)
        except (ValueError, OverflowError):
            raise ValueError("Revisa los parámetros: N, población, generaciones y semilla "
                             "deben ser enteros; mutación y tiempo deben ser números.") from None
        validate(n, config)
        return n, config

    def do_GET(self):
        url = urlsplit(self.path)
        if url.path == "/api/health":
            self.send_json({"status": "ok", "engine": "Python", "algorithm": "genetic"})
        elif url.path in ("/api/solve", "/api/evolve", "/api/validate"):
            try:
                n, config = self.read_parameters(url.query)
            except ValueError as error:
                self.send_json({"error": str(error)}, status=400)
                return
            if url.path == "/api/validate":
                self.send_json({"n": n, "valid": True})
                return
            if url.path == "/api/solve":
                self.send_json(solve_n_queens(n, config))
                return
            self.send_response(200)
            self.send_header("Content-Type", "application/x-ndjson; charset=utf-8")
            self.send_header("Cache-Control", "no-store")
            self.send_header("X-Content-Type-Options", "nosniff")
            self.end_headers()
            # Cada línea contiene una generación; al cancelar la conexión,
            # dejamos de producir eventos y termina también el cálculo.
            try:
                for event in evolve_n_queens(n, config):
                    self.wfile.write(json.dumps(event, separators=(",", ":")).encode("utf-8") + b"\n")
                    self.wfile.flush()
            except (BrokenPipeError, ConnectionResetError, ConnectionAbortedError):
                pass
        elif url.path.startswith("/api/"):
            self.send_json({"error": "Ruta no encontrada."}, status=404)
        else:
            super().do_GET()


def main():
    parser = argparse.ArgumentParser(description="Sakura Queens · Evolución genética 3D")
    parser.add_argument("--port", type=int, default=8000)
    parser.add_argument("--host", default="127.0.0.1")
    args = parser.parse_args()
    server = ThreadingHTTPServer((args.host, args.port), QueensHandler)
    print(f"Sakura Queens: http://{args.host}:{args.port}", flush=True)
    print("Motor: algoritmo genético. Pulsa Ctrl+C para detener.", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\nServidor detenido.")
    finally:
        server.server_close()


if __name__ == "__main__":
    main()
