"""Lee un objetivo CSV y evalúa candidatos exactamente en sus valores de x."""

import csv
import io
from interpreter import ExpressionError, checked_number
from sampling import MAX_SAMPLES, sample_expressions
from metrics import compare_series


def compare_csv(content, expressions, variable="x", variables=None, policy=None,
                x_column="", y_column=""):
    if not isinstance(content, str):
        raise ExpressionError("El CSV debe ser texto UTF-8.")
    if not isinstance(expressions, list) or not 1 <= len(expressions) <= 3:
        raise ExpressionError("Indica de una a tres expresiones candidatas para el CSV.")
    if not all(isinstance(name, str) for name in (x_column, y_column, variable)):
        raise ExpressionError("Los nombres de columnas y variable deben ser texto.")
    try:
        # Se admite coma o punto y coma, con decimales escritos con punto.
        delimiter = ";" if ";" in content.splitlines()[0] else ","
        reader = csv.DictReader(io.StringIO(content.lstrip("\ufeff")), delimiter=delimiter, strict=True)
        headers = reader.fieldnames or []
        if len(set(headers)) != len(headers):
            raise ExpressionError("El CSV tiene encabezados repetidos.")
        x_column = x_column or (variable if variable in headers else "x")
        y_column = y_column or next((name for name in ("y_objetivo", "y", "target") if name in headers), None)
        if not y_column:
            y_column = next((name for name in headers if name.startswith("f1:")), None)
        if x_column not in headers or y_column not in headers or x_column == y_column:
            raise ExpressionError("Selecciona columnas distintas de x y objetivo existentes en el CSV.")
        xs, ys = [], []
        for line, row in enumerate(reader, 2):
            if len(xs) >= MAX_SAMPLES:
                raise ExpressionError(f"El CSV supera {MAX_SAMPLES} filas.")
            try:
                if None in row:
                    raise ValueError("Columnas extra")
                x, y = float(row[x_column]), float(row[y_column])
                checked_number(x)
                checked_number(y)
            except (ValueError, TypeError, KeyError) as error:
                raise ExpressionError(f"Fila {line}: x y objetivo deben ser números finitos, con punto decimal.") from error
            xs.append(x)
            ys.append(y)
    except (csv.Error, IndexError) as error:
        raise ExpressionError("El archivo no es un CSV válido con encabezados.") from error
    curve = sample_expressions(expressions, variable=variable, variables=variables,
                               policy=policy, sample_x=xs)
    curve["series"].insert(0, {"expression": f"Objetivo CSV · {y_column}", "y": ys,
        "corrections": [0] * len(xs), "errors": [None] * len(xs), "break_before": [False] * len(xs),
        "stats": {"valid": len(xs), "invalid": 0, "corrected": 0, "min": min(ys), "max": max(ys)}})
    curve["metrics"] = compare_series(curve["series"])
    curve["reference"] = {"source": "csv", "x_column": x_column, "y_column": y_column}
    return curve
