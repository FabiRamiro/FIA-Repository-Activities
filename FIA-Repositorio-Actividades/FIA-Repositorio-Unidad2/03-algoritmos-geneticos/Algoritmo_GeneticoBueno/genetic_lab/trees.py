"""Árboles inmutables: cada operación recibe sus argumentos como hijos.

La inmutabilidad evita que una mutación modifique accidentalmente a los padres
o a los árboles que guardamos en el historial.
"""
from dataclasses import dataclass
import math
import random

ARITY = {"+": 2, "-": 2, "*": 2, "/": 2, "sin": 1, "cos": 1,
         "sqrt": 1, "log": 1, "x": 0, "const": 0}
LIMIT = 1_000_000.0


@dataclass(frozen=True)
class Node:
    op: str
    children: tuple["Node", ...] = ()
    value: float = 0.0

    @property
    def size(self):
        return 1 + sum(child.size for child in self.children)

    @property
    def depth(self):
        return 1 + max((child.depth for child in self.children), default=0)

    def expression(self):
        if self.op == "x":
            return "x"
        if self.op == "const":
            return f"{self.value:.15g}"
        if len(self.children) == 1:
            return f"{self.op}({self.children[0].expression()})"
        return f"({self.children[0].expression()} {self.op} {self.children[1].expression()})"


def evaluate(node, x):
    """Recorre el árbol con listas y math de Python estándar; nunca eval().

    Cada rama produce una lista. Los ciclos aplican la operación a cada punto.
    Se protegen división, raíz, logaritmo y magnitud de los resultados.
    """
    inputs = [float(value) for value in x]

    def visit(current):
        if current.op == "x": return inputs
        if current.op == "const": return [current.value] * len(inputs)
        args = [visit(child) for child in current.children]
        a = args[0]
        if current.op == "+": result = [left + right for left, right in zip(a, args[1])]
        elif current.op == "-": result = [left - right for left, right in zip(a, args[1])]
        elif current.op == "*": result = [left * right for left, right in zip(a, args[1])]
        elif current.op == "/":
            result = [left if abs(right) < 1e-9 else left / right for left, right in zip(a, args[1])]
        elif current.op == "sin": result = [math.sin(value) for value in a]
        elif current.op == "cos": result = [math.cos(value) for value in a]
        elif current.op == "sqrt": result = [math.sqrt(abs(value)) for value in a]
        elif current.op == "log": result = [math.log1p(abs(value)) for value in a]
        else: raise ValueError(f"Operador desconocido: {current.op}")
        return [value if -LIMIT <= value <= LIMIT else
                (0.0 if math.isnan(value) else (LIMIT if value > 0 else -LIMIT))
                for value in result]

    return visit(node)


def terminal(rng):
    if rng.random() < 0.55:
        return Node("x")
    # Enteros y reales permiten explorar coeficientes decimales desde el inicio.
    value = float(rng.randint(-12, 12)) if rng.random() < 0.5 else round(rng.uniform(-12, 12), 4)
    return Node("const", value=value)


def random_tree(rng, max_depth, operators, full=False):
    """Grow mezcla hojas y operaciones; full completa hasta la profundidad indicada."""
    if max_depth <= 1 or (not full and rng.random() < 0.3):
        return terminal(rng)
    op = rng.choice(operators)
    return Node(op, tuple(random_tree(rng, max_depth - 1, operators, full)
                          for _ in range(ARITY[op])))


def paths(node, prefix=()):
    """Direcciones de subárboles. Ejemplo: (1, 0) = segundo hijo, primer nieto."""
    result = [prefix]
    for index, child in enumerate(node.children):
        result.extend(paths(child, prefix + (index,)))
    return result


def subtree(node, path):
    for index in path:
        node = node.children[index]
    return node


def replace(node, path, replacement):
    """Reconstruye el camino hasta la raíz, conservando las ramas no afectadas."""
    if not path:
        return replacement
    children = list(node.children)
    children[path[0]] = replace(children[path[0]], path[1:], replacement)
    return Node(node.op, tuple(children), node.value)


def repair(node, max_depth, rng):
    """Repara operador, aridad y constantes; poda ramas que excedan el límite."""
    changes = 0
    if node.op not in ARITY:
        return terminal(rng), 1
    if node.op == "const":
        if not math.isfinite(node.value):
            return Node("const", value=0.0), 1
        value = min(LIMIT, max(-LIMIT, node.value))
        return Node("const", value=value), int(value != node.value or bool(node.children))
    if node.op == "x":
        return Node("x"), int(bool(node.children))
    if max_depth <= 1:
        return terminal(rng), 1
    expected = ARITY[node.op]
    children = list(node.children[:expected])
    changes += abs(len(node.children) - expected)
    while len(children) < expected:
        children.append(terminal(rng))
    fixed = []
    for child in children:
        child, count = repair(child, max_depth - 1, rng)
        fixed.append(child)
        changes += count
    return Node(node.op, tuple(fixed)), changes


def simplify(node):
    """Poda algebraica conservadora: elimina ramas que no aportan al resultado."""
    if not node.children:
        return node, 0
    children, count = [], 0
    for child in node.children:
        child, changed = simplify(child)
        children.append(child)
        count += changed
    result = Node(node.op, tuple(children), node.value)
    if all(child.op == "const" for child in children):
        return Node("const", value=evaluate(result, [0.0])[0]), count + 1
    if len(children) == 2:
        a, b = children
        is_const = lambda n, v: n.op == "const" and n.value == v
        if node.op in ("+", "-") and is_const(b, 0): return a, count + 1
        if node.op == "+" and is_const(a, 0): return b, count + 1
        if node.op in ("*", "/") and is_const(b, 1): return a, count + 1
        if node.op == "*" and is_const(a, 1): return b, count + 1
        if node.op == "*" and (is_const(a, 0) or is_const(b, 0)):
            return Node("const", value=0.0), count + 1
    return result, count


def crossover(parent_a, parent_b, rng):
    point_a, point_b = rng.choice(paths(parent_a)), rng.choice(paths(parent_b))
    child = replace(parent_a, point_a, subtree(parent_b, point_b))
    return child, f"Se reemplazó la rama {point_a or 'raíz'} de A por la rama {point_b or 'raíz'} de B."


def mutate(node, rng, max_depth, operators):
    point = rng.choice(paths(node))
    chosen = subtree(node, point)
    if chosen.op == "const" and rng.random() < 0.6:
        scale = rng.choice((0.00001, 0.001, 0.05, 0.5, 2.0))
        replacement = Node("const", value=round(chosen.value + rng.gauss(0, scale), 8))
        detail = f"Mutación de constante mediante una perturbación aleatoria de escala {scale:g}."
    else:
        replacement = random_tree(rng, min(3, max(1, max_depth - len(point))), operators)
        detail = f"Se regeneró la rama {point or 'raíz'} con un subárbol aleatorio."
    return replace(node, point, replacement), detail


def mutate_constant(node, rng):
    """Mueve una sola constante con una perturbación de escala aleatoria (fina o gruesa)."""
    constants = [path for path in paths(node) if subtree(node, path).op == "const"]
    if not constants:
        return node, None
    point = rng.choice(constants)
    scale = rng.choice((0.00001, 0.0001, 0.001, 0.01, 0.1))
    value = subtree(node, point).value + rng.gauss(0, scale) * max(1.0, abs(subtree(node, point).value))
    detail = f"Se perturbó la constante {point or 'raíz'} con escala {scale:g}."
    return replace(node, point, Node("const", value=value)), detail
