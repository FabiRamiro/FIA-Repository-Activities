"""Métricas separadas del algoritmo para poder contrastarlas con la clase."""
from dataclasses import dataclass
import math

METRICS = {"mse": "MSE", "nmse": "NMSE", "r2": "R²", "rmse": "RMSE"}


@dataclass(frozen=True)
class Metrics:
    mse: float
    nmse: float
    r2: float
    rmse: float


class ErrorEvaluator:
    """Guarda los denominadores del CSV para no repetirlos por individuo.

    math.fsum suma con mayor precisión que una acumulación ordinaria.
    Tanto las fórmulas como los recorridos usan Python estándar.
    """
    def __init__(self, expected):
        self.expected = tuple(float(value) for value in expected)
        if not self.expected or not all(math.isfinite(value) for value in self.expected):
            raise ValueError("Las métricas requieren una serie no vacía de valores finitos.")
        self.count = len(self.expected)
        self.mean = math.fsum(self.expected) / self.count
        self.energy = math.fsum(value * value for value in self.expected)
        self.centered_sum = math.fsum((value - self.mean)**2 for value in self.expected)
        self.variance = self.centered_sum / self.count

    def measure(self, predicted):
        if len(predicted) != self.count:
            raise ValueError("Las series deben tener el mismo tamaño y no estar vacías.")
        if not all(math.isfinite(value) for value in predicted):
            raise ValueError("Las métricas requieren valores finitos.")
        squared_error = math.fsum((y - prediction)**2 for y, prediction in zip(self.expected, predicted))
        mse = squared_error / self.count
        nmse = squared_error / self.energy if self.energy > 0 else math.nan
        r2 = 1 - squared_error / self.centered_sum if self.centered_sum > 0 else math.nan
        return Metrics(mse, nmse, r2, math.sqrt(mse))


def calculate_metrics(expected, predicted):
    return ErrorEvaluator(expected).measure(tuple(float(value) for value in predicted))


def metric_loss(metrics, metric):
    """Para maximizar R² minimizamos 1-R². Las demás métricas se minimizan."""
    if metric not in METRICS:
        raise ValueError("Selecciona MSE, NMSE, R² o RMSE.")
    value = getattr(metrics, metric)
    if not math.isfinite(value):
        raise ValueError(f"{METRICS[metric]} no está definido para estos datos. Usa MSE o RMSE.")
    return 1 - value if metric == "r2" else value
