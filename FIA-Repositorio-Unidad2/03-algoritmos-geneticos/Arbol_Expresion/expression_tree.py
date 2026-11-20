"""Árboles reutilizables como individuos de programación genética.

Este módulo no depende de Flask, Three.js ni del navegador. Se analiza una vez
y se evalúa muchas veces. Los operadores genéticos siempre devuelven copias.
"""

from copy import deepcopy
import random
import re

from arithmetic import EvaluationPolicy
from operations import OPERATIONS
from interpreter import (
    ALIASES, CONSTANTS, FUNCTIONS, ExpressionError, Node, Parser,
    checked_number, describe_tree, evaluate, infix, tree_depth,
)


class ExpressionTree:
    DEFAULT_PRIMITIVES = tuple(operation.label for operation in OPERATIONS)

    def __init__(self, expression, policy=None):
        self.root = Parser(expression).parse()
        self.source = expression
        try:
            self.policy = EvaluationPolicy.from_value(policy)
        except ValueError as error:
            raise ExpressionError(str(error)) from error

    @classmethod
    def from_root(cls, root, policy=None):
        # Validamos la estructura antes de copiarla para detectar ciclos y límites.
        count = 0
        seen = set()

        def copy_node(node, depth):
            nonlocal count
            if not isinstance(node, Node) or id(node) in seen:
                raise ExpressionError("El árbol contiene nodos compartidos o un ciclo.")
            seen.add(id(node))
            count += 1
            if count > 160 or depth > 48:
                raise ExpressionError("El árbol supera 160 nodos o 48 niveles.")
            if not isinstance(node.label, str) or not isinstance(node.children, list):
                raise ExpressionError("Cada nodo necesita etiqueta de texto y lista de hijos.")
            children = [copy_node(child, depth + 1) for child in node.children]
            label, kind = node.label, node.kind
            if kind == "operator":
                valid = label in Parser.BINDING and len(children) == 2
            elif kind == "unary":
                valid = label in ("neg", "pos", "!") and len(children) == 1
            elif kind == "function":
                valid = label in FUNCTIONS and FUNCTIONS[label][1] <= len(children) <= FUNCTIONS[label][2]
            elif kind == "constant":
                valid = label in CONSTANTS and not children
            elif kind == "variable":
                valid = bool(re.fullmatch(r"[^\W\d]\w*", label)) and label.lower() not in {*FUNCTIONS, *CONSTANTS, *ALIASES} and not children
            elif kind == "number":
                try:
                    valid = not children and bool(re.fullmatch(r"-?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][+-]?\d+)?", label))
                    checked_number(float(label))
                except (ValueError, OverflowError):
                    valid = False
            else:
                valid = False
            if not valid:
                raise ExpressionError(f"Nodo inválido: {kind!r}, {label!r}.")
            return Node("", label, kind, children)

        copied = copy_node(root, 1)
        source = infix(copied)
        if len(source) > 512:
            raise ExpressionError("La expresión del árbol supera los 512 caracteres.")
        instance = cls.__new__(cls)
        try:
            instance.policy = EvaluationPolicy.from_value(policy)
        except ValueError as error:
            raise ExpressionError(str(error)) from error
        instance.root, instance.source = copied, source
        for index, path in enumerate(instance.paths(), 1):
            instance.subtree(path).id = f"n{index}"
        return instance

    @classmethod
    def from_dict(cls, payload):
        if not isinstance(payload, dict):
            raise ExpressionError("El árbol serializado debe ser un objeto.")
        count = 0

        def load(data, depth):
            nonlocal count
            count += 1
            if count > 160 or depth > 48 or not isinstance(data, dict):
                raise ExpressionError("Estructura serializada inválida o demasiado grande.")
            children = data.get("children", [])
            if not isinstance(children, list):
                raise ExpressionError("Los hijos deben ser una lista.")
            return Node("", data.get("label"), data.get("kind"), [load(child, depth + 1) for child in children])

        return cls.from_root(load(payload.get("tree", payload), 1), payload.get("policy"))

    @property
    def variables(self):
        return sorted({self.subtree(path).label for path in self.paths() if self.subtree(path).kind == "variable"})

    @property
    def depth(self):
        return tree_depth(self.root)

    @property
    def size(self):
        return len(self.paths())

    def to_expression(self):
        return infix(self.root)

    def to_dict(self):
        return {"tree": self.root.to_dict(), "policy": self.policy.to_dict()}

    def clone(self):
        return self.from_root(self.root, self.policy)

    def simplify(self):
        """Pliega subárboles constantes sin errores ni correcciones; conserva el padre."""
        root = deepcopy(self.root)

        def fold(node):
            node.children = [fold(child) for child in node.children]
            if node.children and all(child.kind in ("number", "constant") for child in node.children):
                evaluate(node, {}, self.policy)
                if not node.error and not node.warnings and not any(child.error or child.warnings for child in node.children):
                    # repr conserva exactamente el float evaluado, sin redondearlo a 3 decimales.
                    return Node("", repr(node.value), "number")
            return node

        return self.from_root(fold(root), self.policy)

    def evaluate(self, variables=None):
        """Devuelve un número; si el modo estricto falla, lanza ExpressionError."""
        value = evaluate(self.root, variables, self.policy)
        if self.root.error:
            raise ExpressionError(self.root.error)
        return value

    def report(self, variables=None):
        evaluate(self.root, variables, self.policy)
        return describe_tree(self.root, self.source, self.policy)

    def predict(self, rows):
        """Evalúa muchas filas; los errores matemáticos estrictos se representan con None."""
        results = []
        for variables in rows:
            try:
                results.append(self.evaluate(variables))
            except ExpressionError:
                results.append(None)
        return results

    def fitness(self, rows, targets, invalid_penalty=1e100):
        """Error cuadrático medio (menor es mejor); penaliza candidatos inválidos."""
        rows, targets = list(rows), list(targets)
        if not rows or len(rows) != len(targets):
            raise ExpressionError("Fitness necesita datos y objetivos de igual longitud, no vacíos.")
        checked_number(invalid_penalty)
        if invalid_penalty <= 0:
            raise ExpressionError("La penalización debe ser positiva.")
        for target in targets:
            checked_number(target)
        predictions = self.predict(rows)
        if any(value is None for value in predictions):
            return float(invalid_penalty)
        errors = ((value - target) ** 2 / len(targets) for value, target in zip(predictions, targets))
        return min(sum(errors), invalid_penalty)

    def paths(self):
        result = []

        def visit(node, path):
            result.append(path)
            for index, child in enumerate(node.children):
                visit(child, path + (index,))

        visit(self.root, ())
        return result

    def subtree(self, path):
        node = self.root
        if not isinstance(path, (tuple, list)):
            raise ExpressionError("La ruta de un subárbol debe ser una lista de índices.")
        for index in path:
            if isinstance(index, bool) or not isinstance(index, int) or not 0 <= index < len(node.children):
                raise ExpressionError("Ruta de subárbol inválida.")
            node = node.children[index]
        return node

    def replace_subtree(self, path, replacement):
        self.subtree(path)  # Comprobamos la ruta antes de editar la copia.
        root = deepcopy(self.root)
        node = replacement.root if isinstance(replacement, ExpressionTree) else replacement
        if not path:
            root = node
        else:
            parent = root
            for index in path[:-1]:
                parent = parent.children[index]
            parent.children[path[-1]] = deepcopy(node)
        return self.from_root(root, self.policy)

    @staticmethod
    def _limits(max_depth, max_nodes=160):
        if isinstance(max_depth, bool) or not isinstance(max_depth, int) or not 1 <= max_depth <= 12:
            raise ExpressionError("La profundidad genética debe ser un entero entre 1 y 12.")
        if isinstance(max_nodes, bool) or not isinstance(max_nodes, int) or not 1 <= max_nodes <= 160:
            raise ExpressionError("El límite genético debe ser un entero entre 1 y 160 nodos.")

    @classmethod
    def random(cls, variables=("x",), max_depth=4, rng=None, policy=None, primitives=None):
        cls._limits(max_depth)
        rng = rng or random.Random()
        variables = tuple(variables)
        if not variables or any(not isinstance(name, str) or not re.fullmatch(r"[^\W\d]\w*", name) or name.lower() in {*FUNCTIONS, *CONSTANTS, *ALIASES} for name in variables):
            raise ExpressionError("Indica al menos un nombre de variable válido y no reservado.")
        primitives = cls.DEFAULT_PRIMITIVES if primitives is None else tuple(primitives)
        if not primitives or any(item not in Parser.BINDING and item not in FUNCTIONS for item in primitives):
            raise ExpressionError("Las primitivas deben ser operadores o funciones registrados.")

        def grow(depth):
            if depth == max_depth or rng.random() < .3:
                return Node("", rng.choice(variables), "variable") if rng.random() < .6 else Node("", str(round(rng.uniform(-5, 5), 3)), "number")
            label = rng.choice(primitives)
            kind = "operator" if label in Parser.BINDING else "function"
            arity = 2 if kind == "operator" else FUNCTIONS[label][1]
            return Node("", label, kind, [grow(depth + 1) for _ in range(arity)])

        for _ in range(30):
            try:
                return cls.from_root(grow(1), policy)
            except ExpressionError:
                continue
        raise ExpressionError("No se pudo generar un árbol dentro de los límites; reduce su profundidad.")

    def crossover(self, other, rng=None, max_depth=12, max_nodes=160):
        self._limits(max_depth, max_nodes)
        if not isinstance(other, ExpressionTree):
            raise ExpressionError("El cruce necesita otro ExpressionTree.")
        if max(self.depth, other.depth) > max_depth or max(self.size, other.size) > max_nodes:
            raise ExpressionError("Los padres ya superan los límites del cruce.")
        rng = rng or random.Random()
        for _ in range(30):
            first, second = rng.choice(self.paths()), rng.choice(other.paths())
            try:
                child_a = self.replace_subtree(first, other.subtree(second))
                child_b = other.replace_subtree(second, self.subtree(first))
                if max(child_a.depth, child_b.depth) <= max_depth and max(child_a.size, child_b.size) <= max_nodes:
                    return child_a, child_b
            except ExpressionError:
                continue
        return self.clone(), other.clone()

    def mutate(self, rng=None, variables=None, max_depth=8, max_nodes=160, primitives=None):
        self._limits(max_depth, max_nodes)
        if self.depth > max_depth or self.size > max_nodes:
            raise ExpressionError("El padre supera los límites de la mutación.")
        rng = rng or random.Random()
        for _ in range(30):
            path = rng.choice(self.paths())
            replacement = self.random(variables or self.variables or ("x",), min(3, max_depth - len(path)), rng, self.policy, primitives)
            try:
                child = self.replace_subtree(path, replacement)
                if child.depth <= max_depth and child.size <= max_nodes:
                    return child
            except ExpressionError:
                continue
        return self.clone()
