"""Exportación con la biblioteca estándar, independiente de Qt y NumPy."""
from dataclasses import asdict
import csv
import io
import json
import math
import zipfile
from .trees import evaluate


def csv_text(header, rows):
    output = io.StringIO(newline="")
    writer = csv.writer(output)
    writer.writerow(header)
    writer.writerows(rows)
    return output.getvalue()


def json_safe(value):
    """JSON estándar: las métricas indefinidas se exportan como null, nunca NaN."""
    if isinstance(value, dict): return {key: json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple)): return [json_safe(item) for item in value]
    if isinstance(value, float) and not math.isfinite(value): return None
    return value


def write_experiment(path, data, config, history, selected):
    # Se copia el historial para que el ZIP sea una instantánea consistente.
    history = tuple(history)
    chosen = history[selected]
    result = {
        "dataset": data.name, "config": asdict(config), "selected_generation": selected,
        "last_generation": history[-1].generation, "expression": chosen.best.tree.expression(),
        "metrics": asdict(chosen.best.metrics), "tree": asdict(chosen.best.tree),
        "metric_convention": "NMSE=sum((y-pred)^2)/sum(y^2); R2=1-sum((y-pred)^2)/sum((y-mean(y))^2); RMSE=sqrt(MSE); undefined ratios => null",
        "protected_operators": "a/b: divisor=1 if abs(b)<1e-9; sqrt= sqrt(abs(a)); log=ln(1+abs(a)); operations clipped to +/-1e6",
        "evaluation": "Fit on all CSV points; no independent validation split.",
    }
    with zipfile.ZipFile(path, "w", zipfile.ZIP_DEFLATED) as archive:
        archive.writestr("resultado.json", json.dumps(json_safe(result), indent=2, ensure_ascii=False, allow_nan=False))
        archive.writestr("datos.csv", csv_text(["x", "y"], zip(data.x, data.y)))
        archive.writestr("predicciones.csv", csv_text(["x", "y", "prediccion", "residuo"],
            ((x, y, p, y-p) for x, y, p in zip(data.x, data.y, evaluate(chosen.best.tree, data.x)))))
        archive.writestr("generaciones.csv", csv_text(["generacion", "mse", "nmse", "r2", "rmse", "nodos", "profundidad", "diversidad", "formula"],
            ((s.generation, s.best.metrics.mse, s.best.metrics.nmse, s.best.metrics.r2, s.best.metrics.rmse,
              s.best.tree.size, s.best.tree.depth, s.diversity, s.best.tree.expression()) for s in history)))
        archive.writestr("historial.json", json.dumps(json_safe([asdict(s) for s in history]), ensure_ascii=False, allow_nan=False))


