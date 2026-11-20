"""Ajuste opcional de dos constantes por mínimos cuadrados, sin bibliotecas externas.

La estructura g(x) sigue viniendo de los árboles aleatorios y sus operadores.
Solo estimamos a y b en a + b*g(x), usando exclusivamente los puntos del CSV.
"""
import math
from .trees import Node, LIMIT, evaluate, simplify


def refine_affine(tree, x, y, max_depth):
    """Devuelve un árbol mejorado solo si su MSE real disminuye.

    b = Σ((g-promedio(g))*(y-promedio(y))) / Σ(g-promedio(g))²
    a = promedio(y) - b*promedio(g)

    El límite de profundidad sigue vigente. Comprobamos el error después de
    aplicar las operaciones protegidas, porque estas pueden recortar valores.
    """
    body = tree
    # Si ya tiene la envoltura a + b*g(x), afinamos esa misma envoltura.
    if (tree.op == "+" and tree.children[0].op == "const"
            and tree.children[1].op == "*" and tree.children[1].children[0].op == "const"):
        body = tree.children[1].children[1]
    if body.depth + 2 > max_depth:
        return tree, False
    values = evaluate(body, x)
    count = len(values)
    mean_g = math.fsum(values) / count
    mean_y = math.fsum(y) / count
    variance_sum = math.fsum((value - mean_g)**2 for value in values)
    if variance_sum == 0:
        candidate = Node("const", value=mean_y)
    else:
        slope = math.fsum((g - mean_g)*(target - mean_y) for g, target in zip(values, y)) / variance_sum
        offset = mean_y - slope * mean_g
        if not all(math.isfinite(value) and abs(value) <= LIMIT for value in (slope, offset)):
            return tree, False
        candidate = Node("+", (Node("const", value=offset),
                               Node("*", (Node("const", value=slope), body))))
        candidate, _ = simplify(candidate)
    original = evaluate(tree, x)
    predicted = evaluate(candidate, x)
    old_error = math.fsum((target - value)**2 for target, value in zip(y, original))
    new_error = math.fsum((target - value)**2 for target, value in zip(y, predicted))
    if new_error < old_error:
        return candidate, True
    return tree, False
