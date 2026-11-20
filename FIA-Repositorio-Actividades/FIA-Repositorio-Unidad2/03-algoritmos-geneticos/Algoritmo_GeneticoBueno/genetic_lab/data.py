"""Lectura y generación de CSV sin ejecutar expresiones proporcionadas por el usuario."""
import csv
from dataclasses import dataclass
from pathlib import Path
import math
import random

DEFAULT_PRESET = "Coseno cúbico · 6.87 + 11*cos(7.23*x³)"
DEFAULT_POINTS = 20_001
DEFAULT_LOW = -10.0
DEFAULT_HIGH = 10.0
MAX_POINTS = 50_001

PRESETS = {
    DEFAULT_PRESET: lambda x: 6.87 + 11 * math.cos(7.23 * x**3),
    "Parábola · x² + x + 1": lambda x: x*x + x + 1,
    "Onda · sin(x) + x": lambda x: math.sin(x) + x,
    "Cúbica · x³ − 2x": lambda x: x*x*x - 2*x,
    "Recta · 2x + 3": lambda x: 2*x + 3,
    "Constante · 3": lambda x: 3.0,
}


@dataclass(frozen=True)
class Dataset:
    x: tuple[float, ...]
    y: tuple[float, ...]
    name: str


def generate_dataset(preset, count=80, low=-4.0, high=4.0, noise=0.0, seed=42):
    if not 3 <= count <= MAX_POINTS or not -1e6 <= low < high <= 1e6 or not math.isfinite(noise) or noise < 0:
        raise ValueError("Usa al menos 3 puntos, un intervalo creciente entre ±1e6 y ruido no negativo.")
    rng = random.Random(seed)
    step = (high - low) / (count - 1)
    x = [low + index * step for index in range(count)]
    x[-1] = high
    y = [PRESETS[preset](value) + (rng.gauss(0, noise) if noise else 0) for value in x]
    return validate_dataset(x, y, preset)


def validate_dataset(x, y, name):
    try:
        x, y = tuple(float(value) for value in x), tuple(float(value) for value in y)
    except (TypeError, ValueError) as error:
        raise ValueError("x e y deben ser series de números.") from error
    if len(x) != len(y) or len(x) < 3:
        raise ValueError("El CSV necesita al menos 3 filas de pares numéricos x,y.")
    if len(x) > MAX_POINTS:
        raise ValueError(f"El límite es de {MAX_POINTS:,} puntos.")
    if not all(math.isfinite(value) for value in x + y):
        raise ValueError("No se permiten celdas vacías, NaN ni infinito.")
    if any(abs(value) > 1e6 for value in x + y):
        raise ValueError("Los datos deben estar entre −1 000 000 y 1 000 000.")
    if len(set(x)) < 2:
        raise ValueError("Se necesitan al menos dos valores de x diferentes.")
    pairs = sorted(zip(x, y), key=lambda pair: pair[0])
    return Dataset(tuple(pair[0] for pair in pairs), tuple(pair[1] for pair in pairs), name)


def load_csv(path):
    with Path(path).open("r", encoding="utf-8-sig", newline="") as handle:
        sample = handle.read(8192)
        handle.seek(0)
        delimiter = ";" if sample.splitlines() and ";" in sample.splitlines()[0] else ","
        reader = csv.DictReader(handle, delimiter=delimiter)
        headers = {name.strip().lower(): name for name in (reader.fieldnames or [])}
        if not {"x", "y"}.issubset(headers):
            raise ValueError("El encabezado debe contener las columnas x,y (también se acepta punto y coma).")
        x, y = [], []
        for line, row in enumerate(reader, 2):
            try:
                x.append(float(row[headers["x"]]))
                y.append(float(row[headers["y"]]))
            except (ValueError, TypeError, KeyError) as error:
                raise ValueError(f"Fila {line}: x e y deben ser números; usa punto decimal.") from error
            if len(x) > MAX_POINTS:
                raise ValueError(f"El CSV supera el límite de {MAX_POINTS:,} puntos.")
    return validate_dataset(x, y, Path(path).name)


def save_csv(dataset, path):
    with Path(path).open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle)
        writer.writerow(["x", "y"])
        writer.writerows(zip(dataset.x, dataset.y))
