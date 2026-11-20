"""Reglas numéricas reutilizables para evaluación estricta y programación genética."""

from dataclasses import asdict, dataclass
import math


@dataclass(frozen=True)
class EvaluationPolicy:
    """Una política fija las convenciones; no modifica la expresión original."""

    mode: str = "strict"
    epsilon: float = 1e-9
    max_value: float = 1e12

    def __post_init__(self):
        if self.mode not in ("strict", "protected"):
            raise ValueError("El modo debe ser 'strict' o 'protected'.")
        for name, value, low, high in (("epsilon", self.epsilon, 1e-15, .01), ("max_value", self.max_value, 1, 1e100)):
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not low <= value <= high:
                raise ValueError(f"{name} debe ser un número entre {low:g} y {high:g}.")

    @classmethod
    def from_value(cls, value=None):
        if value is None:
            return cls()
        if isinstance(value, cls):
            return value
        if not isinstance(value, dict) or set(value) - {"mode", "epsilon", "max_value"}:
            raise ValueError("La política admite mode, epsilon y max_value.")
        return cls(**value)

    def to_dict(self):
        return asdict(self)


class Arithmetic:
    """Aplica operaciones y devuelve también las correcciones de ese nodo."""

    def __init__(self, policy=None):
        self.policy = EvaluationPolicy.from_value(policy)

    def bounded(self, value, notes):
        if self.policy.mode == "protected" and (abs(value) > self.policy.max_value or math.isinf(value)):
            notes.append(f"Resultado saturado a ±{self.policy.max_value:g}.")
            return math.copysign(self.policy.max_value, value)
        return value

    def denominator(self, value, notes):
        if abs(value) < self.policy.epsilon:
            replacement = math.copysign(self.policy.epsilon, value)
            notes.append(f"Divisor {value:g} sustituido por {replacement:g} (epsilon).")
            return replacement
        return value

    def positive(self, value, notes, label):
        replacement = max(abs(value), self.policy.epsilon)
        if replacement != value:
            notes.append(f"{label}: argumento {value:g} sustituido por {replacement:g}.")
        return replacement

    def power(self, base, exponent, notes):
        if abs(exponent) > 1000:
            exponent = math.copysign(1000, exponent)
            notes.append("Exponente limitado al intervalo [-1000, 1000].")
        if base < 0 and not float(exponent).is_integer():
            base = abs(base)
            notes.append("Potencia fraccionaria: se usó el valor absoluto de la base negativa.")
        if base == 0 and exponent < 0:
            base = self.denominator(base, notes)
        negative = base < 0 and float(exponent).is_integer() and int(exponent) % 2 != 0
        if base != 0 and exponent * math.log(abs(base)) > math.log(self.policy.max_value):
            notes.append(f"Potencia saturada a ±{self.policy.max_value:g}.")
            return -self.policy.max_value if negative else self.policy.max_value
        return math.pow(base, exponent)

    def apply(self, kind, label, values, function=None):
        values = list(values)
        notes = []
        protected = self.policy.mode == "protected"
        if protected:
            if label in ("/", "%"):
                values[1] = self.denominator(values[1], notes)
            elif label == "sqrt" and values[0] < 0:
                notes.append("Raíz cuadrada protegida: se calculó sqrt(abs(argumento)).")
                values[0] = abs(values[0])
            elif label in ("ln", "log", "log10"):
                values[0] = self.positive(values[0], notes, "Logaritmo protegido")
                if len(values) == 2:
                    values[1] = self.positive(values[1], notes, "Base protegida")
                    if abs(values[1] - 1) < self.policy.epsilon:
                        values[1] = 1 + self.policy.epsilon
                        notes.append("Base de logaritmo cercana a 1 sustituida por 1 + epsilon.")
            elif label in ("asin", "acos"):
                clipped = max(-1, min(1, values[0]))
                if clipped != values[0]:
                    notes.append("Argumento trigonométrico limitado a [-1, 1].")
                values[0] = clipped
            elif label in ("exp", "sinh", "cosh"):
                bound = math.log(self.policy.max_value) if label == "exp" else math.log(2 * self.policy.max_value)
                clipped = min(bound, values[0]) if label == "exp" else max(-bound, min(bound, values[0]))
                if clipped != values[0]:
                    notes.append("Argumento exponencial limitado para evitar desbordamiento.")
                values[0] = clipped
            elif label == "!":
                integer = min(170, int(round(abs(values[0]))))
                if integer != values[0]:
                    notes.append(f"Factorial protegido: se usó el entero {integer}.")
                values[0] = integer

        if label in ("^", "pow"):
            if protected:
                value = self.power(*values, notes)
            else:
                if abs(values[1]) > 1000:
                    raise ValueError("El exponente admite valores entre -1000 y 1000.")
                value = math.pow(*values)
        elif label == "root" and protected:
            radicand, degree = values
            degree = self.denominator(degree, notes)
            if radicand < 0 and float(degree).is_integer() and int(degree) % 2:
                value = -self.power(-radicand, 1 / degree, notes)
            else:
                if radicand < 0:
                    notes.append("Raíz protegida: se usó el valor absoluto del radicando negativo.")
                value = self.power(abs(radicand), 1 / degree, notes)
        elif kind == "function":
            value = function(*values)
        elif kind == "unary":
            if label == "!":
                if not float(values[0]).is_integer() or not 0 <= values[0] <= 170:
                    raise ValueError("El factorial requiere un entero de 0 a 170.")
                value = math.factorial(int(values[0]))
            else:
                value = -values[0] if label == "neg" else values[0]
        elif label == "+":
            value = values[0] + values[1]
        elif label == "-":
            value = values[0] - values[1]
        elif label == "*":
            value = values[0] * values[1]
        elif label == "/":
            value = values[0] / values[1]
        elif label == "%":
            value = values[0] % values[1]
        else:
            raise ValueError(f"Operación desconocida: {label}.")
        return self.bounded(value, notes), notes
