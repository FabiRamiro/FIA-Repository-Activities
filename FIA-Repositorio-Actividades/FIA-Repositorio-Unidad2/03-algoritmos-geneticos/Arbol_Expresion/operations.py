"""Biblioteca cerrada de primitivas del generador de expresiones.

La aridad es el número exacto de hijos. Las implementaciones numéricas siguen
centralizadas en arithmetic.py y en el registro FUNCTIONS del intérprete.
"""

from dataclasses import asdict, dataclass


@dataclass(frozen=True)
class Operation:
    id: str
    name: str
    symbol: str
    label: str
    kind: str
    arity: int

    def to_dict(self):
        return asdict(self)


OPERATIONS = (
    Operation("add", "Suma", "+", "+", "operator", 2),
    Operation("sub", "Resta", "−", "-", "operator", 2),
    Operation("mul", "Multiplicación", "×", "*", "operator", 2),
    Operation("div", "División", "÷", "/", "operator", 2),
    Operation("mod", "Módulo", "%", "%", "operator", 2),
    Operation("sqrt", "Raíz cuadrada", "√", "sqrt", "function", 1),
    Operation("sin", "Seno", "sin", "sin", "function", 1),
    Operation("cos", "Coseno", "cos", "cos", "function", 1),
    Operation("tan", "Tangente", "tan", "tan", "function", 1),
    Operation("pow", "Potencia", "aⁿ", "^", "operator", 2),
    Operation("log", "Logaritmo natural", "ln", "ln", "function", 1),
)
OPERATIONS_BY_ID = {operation.id: operation for operation in OPERATIONS}
