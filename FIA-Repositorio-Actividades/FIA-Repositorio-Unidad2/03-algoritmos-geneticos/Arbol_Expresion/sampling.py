"""Muestreo de curvas sin dependencias de interfaz; analiza cada fórmula una vez."""

import math
import re
from decimal import Decimal, localcontext
from expression_tree import ExpressionTree
from interpreter import ALIASES, CONSTANTS, FUNCTIONS, ExpressionError, checked_number, validate_variables

MAX_SAMPLES = 100_001


def singularity_signature(tree, nodes=None):
    """Detecta cruces de polos conocidos; no une ramas a través de ellos."""
    result = {}
    for node in nodes if nodes is not None else (tree.subtree(path) for path in tree.paths()):
        if node.label in ("/", "%"):
            result[node.id] = node.children[1].value
        elif node.label == "tan" and node.children[0].value is not None:
            result[node.id] = math.cos(node.children[0].value)
        elif node.label in ("^", "pow") and node.children[1].value is not None and node.children[1].value < 0:
            result[node.id] = node.children[0].value
    return result


def build_domain(start=0, end=1, points=201, step=None):
    """Incluye ambos extremos; un paso no divisible deja un último tramo menor."""
    checked_number(start)
    checked_number(end)
    if start >= end:
        raise ExpressionError("El inicio del dominio debe ser menor que el final.")
    short_final_interval = False
    if step is not None:
        checked_number(step)
        if step <= 0:
            raise ExpressionError("El tamaño de paso debe ser positivo.")
        # Decimal evita acumular el error de sumar 0.1 una y otra vez.
        with localcontext() as context:
            context.prec = 50
            first, last, increment = (Decimal(str(value)) for value in (start, end, step))
            ratio = (last - first) / increment
            required = int(ratio) + 1 + (ratio != int(ratio))
            if required > MAX_SAMPLES:
                raise ExpressionError(f"El paso produce más de {MAX_SAMPLES} muestras. Aumenta el paso o reduce el dominio.")
            full_steps = int(ratio)
            decimals = [first + index * increment for index in range(full_steps + 1)]
            short_final_interval = decimals[-1] != last
            if short_final_interval:
                decimals.append(last)
            xs = [float(value) for value in decimals]
    else:
        if isinstance(points, bool) or not isinstance(points, int) or not 2 <= points <= MAX_SAMPLES:
            raise ExpressionError(f"El número de muestras debe ser un entero entre 2 y {MAX_SAMPLES}.")
        xs = [start * (1 - index / (points - 1)) + end * (index / (points - 1)) for index in range(points)]
    xs[0], xs[-1] = float(start), float(end)
    if any(right <= left for left, right in zip(xs, xs[1:])):
        raise ExpressionError("El dominio es demasiado estrecho para esas muestras con precisión flotante.")
    return xs, {"mode": "step" if step is not None else "points", "step": step, "short_final_interval": short_final_interval}


def sample_expressions(expressions, variable="x", start=0, end=1, points=201, variables=None, policy=None, step=None, sample_x=None):
    if not isinstance(expressions, list) or not 1 <= len(expressions) <= 4:
        raise ExpressionError("Envía de una a cuatro expresiones para graficar.")
    if sample_x is None:
        xs, sampling = build_domain(start, end, points, step)
    else:
        xs = list(sample_x)
        if not 2 <= len(xs) <= MAX_SAMPLES:
            raise ExpressionError(f"El CSV necesita entre 2 y {MAX_SAMPLES} muestras.")
        for x in xs:
            checked_number(x)
        if any(right <= left for left, right in zip(xs, xs[1:])):
            raise ExpressionError("Los valores de x del CSV deben estar ordenados y no repetidos.")
        start, end = xs[0], xs[-1]
        sampling = {"mode": "csv", "step": None, "short_final_interval": False}
    if not isinstance(variable, str) or not re.fullmatch(r"[^\W\d]\w*", variable) or variable.lower() in {*FUNCTIONS, *CONSTANTS, *ALIASES}:
        raise ExpressionError("Selecciona una variable válida para el dominio.")
    variables = validate_variables(variables)
    trees = [ExpressionTree(source, policy) for source in expressions]
    fixed_names = sorted({name for tree in trees for name in tree.variables if name != variable})
    missing = [name for name in fixed_names if name not in variables]
    if missing:
        raise ExpressionError(f"Asigna valores a las variables fijas: {', '.join(missing)}.")
    series = []
    for source, tree in zip(expressions, trees):
        ys, corrections, breaks, errors = [], [], [], []
        previous = {}
        corrected_count = invalid_count = 0
        nodes = [tree.subtree(path) for path in tree.paths()]
        values = {**variables}
        for x in xs:
            values[variable] = x
            try:
                value = tree.evaluate(values)
            except ExpressionError:
                value = None
            signature = singularity_signature(tree, nodes)
            split = False
            for key, boundary_value in signature.items():
                old = previous.get(key)
                if boundary_value is not None and old is not None and (old < 0 < boundary_value or boundary_value < 0 < old or (old == 0) != (boundary_value == 0)):
                    split = True
            correction_count = sum(bool(node.warnings) for node in nodes)
            ys.append(value)
            corrections.append(correction_count)
            errors.append(tree.root.error)
            breaks.append(split)
            corrected_count += correction_count > 0
            invalid_count += value is None
            previous = signature
        valid = [value for value in ys if value is not None]
        series.append({"expression": source, "y": ys, "corrections": corrections, "errors": errors, "break_before": breaks, "stats": {"valid": len(valid), "invalid": invalid_count, "corrected": corrected_count, "min": min(valid) if valid else None, "max": max(valid) if valid else None}})
    result = {"variable": variable, "start": start, "end": end, "points": len(xs), "sampling": sampling, "x": xs, "series": series, "policy": trees[0].policy.to_dict(), "fixed_variables": {name: variables[name] for name in fixed_names}}
    from metrics import compare_series
    result["metrics"] = compare_series(series)
    return result
