"""Métricas independientes de la web, reutilizables para programación genética."""

import math
from interpreter import ExpressionError, checked_number


def regression_metrics(targets, predictions):
    """NMSE = MSE / varianza poblacional del objetivo. Nunca omite filas inválidas."""
    targets, predictions = list(targets), list(predictions)
    if not targets or len(targets) != len(predictions):
        raise ExpressionError("Las métricas necesitan dos listas no vacías de igual longitud.")
    invalid = sum(a is None or b is None for a, b in zip(targets, predictions))
    result = {"n": len(targets), "invalid": invalid, "mse": None, "rmse": None,
              "nmse": None, "r2": None, "note": None}
    if invalid:
        result["note"] = f"Hay {invalid} pares sin resultado. No se omiten para favorecer al candidato."
        return result
    for value in targets + predictions:
        checked_number(value)
    n = len(targets)
    mse = math.fsum((a - b) ** 2 / n for a, b in zip(targets, predictions))
    mean = math.fsum(value / n for value in targets)
    variance = math.fsum((value - mean) ** 2 / n for value in targets)
    result.update(mse=mse, rmse=math.sqrt(mse))
    # La varianza de una lista constante es cero aunque su media redondee.
    if all(value == targets[0] for value in targets) or variance == 0:
        result["note"] = "Objetivo constante: NMSE y R² no están definidos (varianza cero)."
    else:
        nmse = mse / variance
        if math.isfinite(nmse):
            result.update(nmse=nmse, r2=1 - nmse)
        else:
            result["note"] = "NMSE y R² exceden la precisión numérica disponible."
    return result


def compare_series(series):
    return [{"series_index": index, "expression": item["expression"],
             **regression_metrics(series[0]["y"], item["y"])}
            for index, item in enumerate(series) if index > 0]
