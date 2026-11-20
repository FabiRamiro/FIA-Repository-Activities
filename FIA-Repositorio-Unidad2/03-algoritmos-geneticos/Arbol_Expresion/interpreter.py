"""Intérprete matemático: símbolos → árbol → evaluación, sin ejecutar código del usuario.

El analizador Pratt utiliza una prioridad por operador para decidir qué operación
agrupar primero. Cada llamada devuelve un Nodo: una pequeña parte del árbol.
"""

from dataclasses import dataclass, field
import math
import re
from arithmetic import Arithmetic, EvaluationPolicy


class ExpressionError(ValueError):
    """Error comprensible, con posición opcional dentro de la expresión."""

    def __init__(self, message, position=None):
        super().__init__(message)
        self.position = position


@dataclass
class Node:
    id: str
    label: str
    kind: str
    children: list = field(default_factory=list)
    value: float | None = None
    error: str | None = None
    warnings: list = field(default_factory=list)

    def to_dict(self):
        return {
            "id": self.id, "label": self.label, "kind": self.kind,
            "children": [child.to_dict() for child in self.children],
            "value": self.value, "error": self.error, "warnings": self.warnings,
        }


def real_root(value, degree=2):
    if degree == 0:
        raise ValueError("El índice de una raíz no puede ser cero.")
    if value < 0:
        if not float(degree).is_integer() or int(degree) % 2 == 0:
            raise ValueError("Esta raíz no tiene resultado real.")
        return -math.pow(-value, 1 / degree)
    return math.pow(value, 1 / degree)


# Para agregar una función: registra (implementación, mínimo y máximo de argumentos).
# El frontend consulta este registro para mostrar la ayuda actualizada.
FUNCTIONS = {
    "sqrt": (math.sqrt, 1, 1), "root": (real_root, 2, 2),
    "sin": (math.sin, 1, 1), "cos": (math.cos, 1, 1), "tan": (math.tan, 1, 1),
    "asin": (math.asin, 1, 1), "acos": (math.acos, 1, 1), "atan": (math.atan, 1, 1),
    "sinh": (math.sinh, 1, 1), "cosh": (math.cosh, 1, 1), "tanh": (math.tanh, 1, 1),
    "ln": (math.log, 1, 1), "log": (math.log, 1, 2), "log10": (math.log10, 1, 1),
    "exp": (math.exp, 1, 1), "abs": (abs, 1, 1),
    "floor": (math.floor, 1, 1), "ceil": (math.ceil, 1, 1),
    "round": (round, 1, 1), "min": (min, 2, 12), "max": (max, 2, 12),
    "pow": (math.pow, 2, 2), "hypot": (math.hypot, 2, 12),
}
ALIASES = {"raiz": "sqrt", "raíz": "sqrt", "sen": "sin", "tg": "tan"}
CONSTANTS = {"pi": math.pi, "π": math.pi, "e": math.e, "tau": math.tau, "τ": math.tau}
TOKEN = re.compile(r"\s*(?:(\d+(?:\.\d*)?(?:[eE][+-]?\d+)?|\.\d+(?:[eE][+-]?\d+)?)|([^\W\d]\w*)|(\*\*|[+\-*/^%(),!√×÷−]))", re.UNICODE)


class Parser:
    # (prioridad izquierda, prioridad derecha). ^ es asociativo a la derecha:
    # 2^3^2 significa 2^(3^2), mientras 8/4/2 significa (8/4)/2.
    BINDING = {"+": (10, 11), "-": (10, 11), "*": (20, 21), "/": (20, 21), "%": (20, 21), "^": (30, 30)}

    def __init__(self, source):
        if not isinstance(source, str) or not source.strip():
            raise ExpressionError("Escribe una expresión para comenzar.", 0)
        if len(source) > 512:
            raise ExpressionError("La expresión admite hasta 512 caracteres.")
        self.tokens = []
        position = 0
        while position < len(source):
            if not source[position:].strip():
                break
            match = TOKEN.match(source, position)
            if not match:
                raise ExpressionError(f"Símbolo no reconocido: {source[position]!r}.", position)
            number, name, operator = match.groups()
            text = number or name or operator
            actual_position = match.start() + len(match.group()) - len(text)
            text = {"**": "^", "×": "*", "÷": "/", "−": "-", "√": "sqrt"}.get(text, text)
            self.tokens.append(("number" if number else "name" if name or operator == "√" else "operator", text, actual_position))
            position = match.end()
        if len(self.tokens) > 256:
            raise ExpressionError("La expresión tiene demasiados elementos (máximo 256).")
        self.tokens.append(("end", "", len(source)))
        self.cursor = 0
        self.count = 0

    def current(self):
        return self.tokens[self.cursor]

    def take(self):
        token = self.current()
        self.cursor += 1
        return token

    def expect(self, symbol):
        if self.current()[1] != symbol:
            raise ExpressionError(f"Se esperaba '{symbol}'.", self.current()[2])
        self.take()

    def node(self, label, kind, children=None):
        self.count += 1
        if self.count > 160:
            raise ExpressionError("El árbol admite hasta 160 nodos.")
        return Node(f"n{self.count}", label, kind, children or [])

    def parse(self):
        root = self.expression()
        if self.current()[0] != "end":
            raise ExpressionError(f"Elemento inesperado: '{self.current()[1]}'.", self.current()[2])
        if tree_depth(root) > 48:
            raise ExpressionError("El árbol admite hasta 48 niveles.")
        return root

    def expression(self, minimum=0, depth=0):
        if depth > 48:
            raise ExpressionError("Hay demasiados niveles de anidación.", self.current()[2])
        kind, text, position = self.take()
        if kind == "number":
            left = self.node(text, "number")
        elif text in ("+", "-"):
            # Una potencia se agrupa antes que el signo: -2^2 = -(2^2).
            operand = self.expression(25, depth + 1)
            if operand.kind == "number":
                # Un signo sobre un literal forma una constante con signo. Así,
                # guardar/cargar un árbol generado conserva su altura y aridades.
                if text == "-":
                    operand.label = operand.label[1:] if operand.label.startswith("-") else "-" + operand.label
                left = operand
            else:
                left = self.node("neg" if text == "-" else "pos", "unary", [operand])
        elif text == "(":
            left = self.expression(0, depth + 1)
            self.expect(")")
        elif kind == "name":
            name = ALIASES.get(text.lower(), text.lower())
            if name in FUNCTIONS:
                self.expect("(")
                arguments = []
                if self.current()[1] != ")":
                    while True:
                        arguments.append(self.expression(0, depth + 1))
                        if self.current()[1] != ",":
                            break
                        self.take()
                self.expect(")")
                _, low, high = FUNCTIONS[name]
                if not low <= len(arguments) <= high:
                    expected = str(low) if low == high else f"{low} a {high}"
                    raise ExpressionError(f"{name} necesita {expected} argumento(s).", position)
                left = self.node(name, "function", arguments)
            elif self.current()[1] == "(" and len(text) > 1 and name not in CONSTANTS:
                raise ExpressionError(f"Función desconocida: '{text}'. Usa una función de la guía.", position)
            else:
                left = self.node(name if name in CONSTANTS else text, "constant" if name in CONSTANTS else "variable")
        else:
            raise ExpressionError("Falta un número, una variable o un paréntesis de apertura.", position)

        while True:
            next_kind, operator, _ = self.current()
            if next_kind == "number" and self.tokens[self.cursor - 1][0] == "number":
                raise ExpressionError("Falta un operador entre los números.", self.current()[2])
            if operator == "!":
                if 40 < minimum:
                    break
                self.take()
                left = self.node("!", "unary", [left])
                continue
            # 2x y 2(x+1) se interpretan como multiplicaciones explícitas en el árbol.
            implicit = next_kind in ("number", "name") or operator == "("
            if implicit:
                operator = "*"
            if operator not in self.BINDING:
                break
            left_priority, right_priority = self.BINDING[operator]
            if left_priority < minimum:
                break
            if not implicit:
                self.take()
            right = self.expression(right_priority, depth + 1)
            left = self.node(operator, "operator", [left, right])
        return left


def tree_depth(node):
    return 1 + max((tree_depth(child) for child in node.children), default=0)


def checked_number(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ExpressionError("Los valores de las variables deben ser números reales.")
    # Comparamos primero para rechazar enteros gigantes sin convertirlos a float.
    if abs(value) > 1e100 or not math.isfinite(value):
        raise ExpressionError("El resultado supera el rango permitido (±1e100).")
    return float(value)


def validate_variables(variables):
    variables = {} if variables is None else variables
    if not isinstance(variables, dict):
        raise ExpressionError("Las variables deben enviarse como un objeto de nombre y valor.")
    for name, value in variables.items():
        if not isinstance(name, str):
            raise ExpressionError("Los nombres de variables deben ser texto.")
        checked_number(value)
    return variables


def evaluate(node, variables, policy=None):
    """Evalúa en postorden y registra correcciones locales, sin reanalizar."""
    variables = validate_variables(variables)
    try:
        arithmetic = Arithmetic(policy)
    except ValueError as error:
        raise ExpressionError(str(error)) from error

    def visit(current):
        values = [visit(child) for child in current.children]
        current.warnings = []
        current.error = None
        current.value = None
        try:
            if any(child.error for child in current.children):
                raise ExpressionError(next(child.error for child in current.children if child.error))
            if current.kind == "number":
                value = float(current.label)
            elif current.kind == "constant":
                value = CONSTANTS[current.label]
            elif current.kind == "variable":
                if current.label not in variables:
                    raise ExpressionError(f"Asigna un valor a la variable '{current.label}'.")
                value = variables[current.label]
            else:
                function = FUNCTIONS[current.label][0] if current.kind == "function" else None
                value, current.warnings = arithmetic.apply(current.kind, current.label, values, function)
            value = arithmetic.bounded(value, current.warnings)
            current.value = checked_number(value)
        except (ValueError, ZeroDivisionError, OverflowError, TypeError) as error:
            if isinstance(error, ExpressionError):
                current.error = str(error)
            elif isinstance(error, ZeroDivisionError):
                current.error = "No se puede dividir entre cero."
            elif isinstance(error, OverflowError):
                current.error = "El resultado es demasiado grande."
            else:
                current.error = f"'{current.label}' no está definida para estos valores reales."
        return current.value

    return visit(node)


def traversal(node, order):
    children = [traversal(child, order) for child in node.children]
    descendants = [item for group in children for item in group]
    if order == "preorder":
        return [node.id] + descendants
    if order == "postorder":
        return descendants + [node.id]
    if not children:
        return [node.id]
    # En funciones usamos el nombre antes de sus argumentos, igual que sqrt(x).
    if node.kind == "function" or node.label in ("neg", "pos"):
        return [node.id] + descendants
    return children[0] + [node.id] + [item for group in children[1:] for item in group]


def infix(node):
    if not node.children:
        return f"({node.label})" if node.kind == "number" and node.label.startswith("-") else node.label
    parts = [infix(child) for child in node.children]
    if node.kind == "function":
        return f"{node.label}({', '.join(parts)})"
    if node.kind == "unary":
        return f"({parts[0]}!)" if node.label == "!" else f"({'-' if node.label == 'neg' else '+'}{parts[0]})"
    return f"({parts[0]} {node.label} {parts[1]})"


def interpret(source, variables=None, policy=None):
    root = Parser(source).parse()
    evaluate(root, variables, policy)
    return describe_tree(root, source, policy)


def describe_tree(root, source, policy=None):
    nodes = []

    def collect(node):
        nodes.append(node)
        for child in node.children:
            collect(child)

    collect(root)
    orders = {order: traversal(root, order) for order in ("preorder", "inorder", "postorder")}
    lookup = {node.id: node.label for node in nodes}
    return {
        "expression": source, "tree": root.to_dict(),
        "variables": sorted({node.label for node in nodes if node.kind == "variable"}),
        "evaluation": {"value": root.value, "error": root.error},
        "policy": EvaluationPolicy.from_value(policy).to_dict(),
        "corrections": [{"node_id": node.id, "label": node.label, "messages": node.warnings} for node in nodes if node.warnings],
        "stats": {"nodes": len(nodes), "depth": tree_depth(root), "leaves": sum(not node.children for node in nodes), "operations": sum(bool(node.children) for node in nodes)},
        "traversals": orders,
        "notation": {"infix": infix(root), "prefix": " ".join(lookup[key] for key in orders["preorder"]), "postfix": " ".join(lookup[key] for key in orders["postorder"])},
    }
