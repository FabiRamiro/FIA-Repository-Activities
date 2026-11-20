"""Generación libre de fórmulas desde una biblioteca de operaciones con aridad."""

import random
import re

from arithmetic import EvaluationPolicy
from expression_tree import ExpressionTree
from interpreter import ALIASES, CONSTANTS, FUNCTIONS, ExpressionError, Node, checked_number
from operations import OPERATIONS, OPERATIONS_BY_ID
from sampling import sample_expressions


class ExpressionGenerator:
    """Construye primero el árbol; la expresión de texto se deriva del árbol."""

    def __init__(self, operations=None, policy=None, seed=None):
        if operations is None:
            operations = [item.id for item in OPERATIONS]
        if not isinstance(operations, (tuple, list)) or not operations or any(not isinstance(item, str) or item not in OPERATIONS_BY_ID for item in operations):
            raise ExpressionError("Selecciona al menos una operación válida de la biblioteca.")
        self.operations = tuple(OPERATIONS_BY_ID[key] for key in dict.fromkeys(operations))
        if seed is not None and (isinstance(seed, bool) or not isinstance(seed, int) or not -(2**53 - 1) <= seed <= 2**53 - 1):
            raise ExpressionError("La semilla debe ser un entero entre −9007199254740991 y 9007199254740991, o null.")
        self.seed = seed
        self.rng = random.Random(seed)
        try:
            self.policy = EvaluationPolicy.from_value({"mode": "protected"} if policy is None else policy)
        except ValueError as error:
            raise ExpressionError(str(error)) from error

    def generate(self, variable="x", max_height=5, constants=True, constant_min=-5, constant_max=5):
        ExpressionTree._limits(max_height)
        if not isinstance(variable, str) or len(variable) > 64 or not re.fullmatch(r"[^\W\d]\w*", variable) or variable.lower() in {*FUNCTIONS, *CONSTANTS, *ALIASES}:
            raise ExpressionError("La variable debe tener un nombre válido, no reservado, de hasta 64 caracteres.")
        if not isinstance(constants, bool):
            raise ExpressionError("constants debe ser true o false.")
        for value in (constant_min, constant_max):
            checked_number(value)
        if not -1000 <= constant_min <= constant_max <= 1000:
            raise ExpressionError("El rango de constantes debe estar ordenado y dentro de [-1000, 1000].")

        def terminal():
            if not constants or self.rng.random() < .6:
                return Node("", variable, "variable")
            # Un número negativo sigue siendo una hoja, no una operación extra.
            return Node("", str(round(self.rng.uniform(constant_min, constant_max), 3)), "number")

        def grow(level, budget):
            if level == max_height or budget == 1 or level > 1 and self.rng.random() < .3:
                return terminal()
            available = [operation for operation in self.operations if operation.arity + 1 <= budget]
            if not available:
                return terminal()
            operation = self.rng.choice(available)
            remaining = budget - 1
            budgets = []
            for index in range(operation.arity - 1):
                reserved = operation.arity - index - 1
                share = self.rng.randint(1, remaining - reserved)
                budgets.append(share)
                remaining -= share
            budgets.append(remaining)
            return Node("", operation.label, operation.kind, [grow(level + 1, share) for share in budgets])

        for _ in range(80):
            try:
                root = grow(1, 160)
                tree = ExpressionTree.from_root(root, self.policy)
                # f(x) siempre contiene x, aunque algebraicamente pueda cancelarse.
                if variable not in tree.variables:
                    leaves = [path for path in tree.paths() if not tree.subtree(path).children]
                    tree = tree.replace_subtree(self.rng.choice(leaves), Node("", variable, "variable"))
                # El texto que verá y editará el usuario debe reconstruir exactamente
                # la misma estructura, sin añadir operaciones fuera de la biblioteca.
                reparsed = ExpressionTree(tree.to_expression(), self.policy)
                if reparsed.depth <= max_height and reparsed.size <= 160 and self._valid_operations(reparsed):
                    return reparsed
            except ExpressionError:
                continue
        raise ExpressionError("No se encontró una fórmula dentro de los límites de tamaño. Reduce la altura o la biblioteca y vuelve a intentar.")

    def _valid_operations(self, tree):
        allowed = {(item.kind, item.label): item.arity for item in self.operations}
        for path in tree.paths():
            node = tree.subtree(path)
            if node.children and allowed.get((node.kind, node.label)) != len(node.children):
                return False
        return True


def generate_expression(operations=None, variable="x", max_height=5, seed=None, constants=True,
                        constant_min=-5, constant_max=5, variables=None, policy=None,
                        start=0, end=1, points=201, step=None):
    generator = ExpressionGenerator(operations, policy, seed)
    tree = generator.generate(variable, max_height, constants, constant_min, constant_max)
    # El árbol y la curva usan la misma fórmula y la misma política de evaluación.
    curve = sample_expressions([tree.to_expression()], variable, start, end, points, variables, generator.policy, step)
    values = {} if variables is None else dict(variables)
    values.setdefault(variable, start)
    report = tree.report(values)
    report["generation"] = {
        "formula": f"f({variable}) = {tree.to_expression()}",
        "variable": variable, "max_height": max_height, "actual_height": tree.depth,
        "initial_value": values[variable],
        "height_convention": "levels", "seed": seed, "constants": constants,
        "constant_min": constant_min, "constant_max": constant_max,
        "operations": [item.to_dict() for item in generator.operations],
    }
    report["curve"] = curve
    return report
