"""Servidor local de Arboria. Ejecuta: python app.py"""

import argparse
import json
from flask import Flask, jsonify, request
from werkzeug.exceptions import RequestEntityTooLarge
from interpreter import ALIASES, CONSTANTS, FUNCTIONS, ExpressionError, interpret
from sampling import sample_expressions
from generator import generate_expression
from operations import OPERATIONS
from csv_comparison import compare_csv
from expression_tree import ExpressionTree

app = Flask(__name__, static_folder="static")
app.config["MAX_CONTENT_LENGTH"] = 16 * 1024 * 1024
app.json.ensure_ascii = False


@app.before_request
def request_limit():
    # El archivo CSV necesita más espacio que las pequeñas peticiones JSON.
    if request.path != "/api/compare-csv" and request.content_length and request.content_length > 16 * 1024:
        raise RequestEntityTooLarge()


@app.get("/")
def index():
    return app.send_static_file("index.html")


@app.get("/api/functions")
def functions():
    return jsonify(functions=[{"name": name, "min_args": item[1], "max_args": item[2]} for name, item in FUNCTIONS.items()], aliases=ALIASES, constants=list(CONSTANTS))


@app.post("/api/parse")
def parse():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Envía un objeto JSON con expression y variables."), 400
    try:
        return jsonify(interpret(data.get("expression"), data.get("variables", {}), data.get("policy")))
    except ExpressionError as error:
        return jsonify(error=str(error), position=error.position), 400
    except RecursionError:
        return jsonify(error="La expresión tiene demasiados niveles de anidación."), 400


@app.get("/api/operations")
def operations():
    return jsonify(operations=[operation.to_dict() for operation in OPERATIONS], max_height=12, height_convention="levels")


@app.post("/api/generate")
def generate():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Envía un objeto JSON con la configuración del generador."), 400
    domain = data.get("domain", {})
    if not isinstance(domain, dict):
        return jsonify(error="El dominio debe ser un objeto con start, end, step o points."), 400
    try:
        return jsonify(generate_expression(
            operations=data.get("operations"), variable=data.get("variable", "x"),
            max_height=data.get("max_height", 5), seed=data.get("seed"),
            constants=data.get("constants", True), constant_min=data.get("constant_min", -5),
            constant_max=data.get("constant_max", 5), variables=data.get("variables"), policy=data.get("policy"),
            start=domain.get("start", 0), end=domain.get("end", 1), points=domain.get("points", 201), step=domain.get("step"),
        ))
    except ExpressionError as error:
        return jsonify(error=str(error), position=error.position), 400


@app.post("/api/sample")
def sample():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Envía un objeto JSON con expressions y dominio."), 400
    try:
        return jsonify(sample_expressions(
            data.get("expressions"), data.get("variable", "x"),
            data.get("start", 0), data.get("end", 1), data.get("points", 201),
            data.get("variables"), data.get("policy"), data.get("step"),
        ))
    except ExpressionError as error:
        return jsonify(error=str(error), position=error.position), 400
    except RecursionError:
        return jsonify(error="La expresión tiene demasiados niveles de anidación."), 400


@app.post("/api/compare-csv")
def compare_file():
    try:
        upload = request.files.get("file")
        if upload is None:
            raise ExpressionError("Selecciona un CSV con columnas de x y objetivo.")
        options = json.loads(request.form.get("options", "{}"))
        if not isinstance(options, dict):
            raise ExpressionError("La configuración debe ser un objeto.")
        result = compare_csv(upload.read().decode("utf-8-sig"), options.get("expressions"),
            variable=options.get("variable", "x"), variables=options.get("variables"),
            policy=options.get("policy"), x_column=options.get("x_column", ""), y_column=options.get("y_column", ""))
        return jsonify(result)
    except (ExpressionError, UnicodeError, json.JSONDecodeError) as error:
        return jsonify(error=str(error)), 400


@app.post("/api/simplify")
def simplify():
    data = request.get_json(silent=True)
    if not isinstance(data, dict):
        return jsonify(error="Envía expression, variables y policy."), 400
    try:
        original = ExpressionTree(data.get("expression"), data.get("policy"))
        simplified = original.simplify()
        result = simplified.report(data.get("variables"))
        result["simplification"] = {"before": original.size, "after": simplified.size, "original": original.source}
        return jsonify(result)
    except ExpressionError as error:
        return jsonify(error=str(error)), 400


@app.errorhandler(RequestEntityTooLarge)
def too_large(_error):
    limit = "16 MB" if request.path == "/api/compare-csv" else "16 KB"
    return jsonify(error=f"La solicitud supera los {limit} permitidos."), 413


if __name__ == "__main__":
    arguments = argparse.ArgumentParser(description="Arboria · laboratorio de expresiones")
    arguments.add_argument("--port", type=int, default=5000)
    options = arguments.parse_args()
    print(f"\n  Arboria está listo: http://127.0.0.1:{options.port}\n")
    app.run(host="127.0.0.1", port=options.port, debug=False)
