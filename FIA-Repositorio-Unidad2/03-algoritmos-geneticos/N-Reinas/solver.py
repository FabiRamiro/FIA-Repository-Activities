"""N-Reinas mediante un algoritmo genético de permutaciones, sin backtracking."""

from dataclasses import dataclass
from random import Random
from time import perf_counter


@dataclass(frozen=True)
class GeneticConfig:
    population_size: int = 80
    max_generations: int = 2000
    mutation_rate: float = 0.65
    time_limit: float = 15.0
    seed: int | None = None
    memory_budget_mb: int = 256


def validate(n, config):
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise ValueError("N debe ser un entero positivo.")
    if not 4 <= config.population_size <= 1000:
        raise ValueError("La población debe tener entre 4 y 1000 individuos.")
    if not 1 <= config.max_generations <= 100000:
        raise ValueError("Usa entre 1 y 100000 generaciones.")
    if not 0 <= config.mutation_rate <= 1:
        raise ValueError("La probabilidad de mutación debe estar entre 0 y 1.")
    if not 0.05 <= config.time_limit <= 120:
        raise ValueError("El presupuesto de búsqueda debe estar entre 0.05 y 120 segundos.")
    # No hay máximo fijo para N. Estimamos listas, enteros, padres e hijos
    # antes de asignarlos para respetar un presupuesto de memoria por búsqueda.
    estimated_bytes = n * (config.population_size * 80 + 256)
    if estimated_bytes > config.memory_budget_mb * 1024 * 1024:
        raise ValueError("Esta combinación de N y población supera el presupuesto "
                         f"de memoria de {config.memory_budget_mb} MB. Reduce la población "
                         "o ajusta memory_budget_mb en GeneticConfig.")


def diagonal_counts(genes):
    """Una permutación ya evita repetir filas/columnas: faltan las diagonales."""
    n = len(genes)
    descending = [0] * (2 * n - 1)
    ascending = [0] * (2 * n - 1)
    conflicts = 0
    for row, column in enumerate(genes):
        down, up = row - column + n - 1, row + column
        conflicts += descending[down] + ascending[up]
        descending[down] += 1
        ascending[up] += 1
    return conflicts, descending, ascending


def count_conflicts(genes):
    """Número de pares en conflicto, no número de reinas amenazadas."""
    return diagonal_counts(genes)[0]


def ordered_crossover(parent_a, parent_b, rng):
    """Cruce de orden: hereda un fragmento y completa sin columnas duplicadas."""
    n = len(parent_a)
    if n < 2:
        return parent_a.copy()
    start, end = sorted(rng.sample(range(n + 1), 2))
    child = [-1] * n
    child[start:end] = parent_a[start:end]
    inherited = set(parent_a[start:end])
    remaining = (gene for gene in parent_b if gene not in inherited)
    for index in list(range(end, n)) + list(range(start)):
        child[index] = next(remaining)
    return child


def swap_delta(genes, first, second, descending, ascending):
    """Cambio de conflictos sin copiar el tablero: solo varían 2 reinas.

    Una diagonal con c reinas tiene c*(c-1)/2 pares en conflicto.
    Calculamos la diferencia al retirar esas reinas y añadirlas intercambiadas.
    """
    n = len(genes)
    changes = {}
    for row, column, sign in [(first, genes[first], -1), (second, genes[second], -1),
                               (first, genes[second], 1), (second, genes[first], 1)]:
        for key in [(0, row - column + n - 1), (1, row + column)]:
            changes[key] = changes.get(key, 0) + sign
    delta = 0
    for (direction, index), change in changes.items():
        count = (descending if direction == 0 else ascending)[index]
        delta += count * change + change * (change - 1) // 2
    return delta


def mutate(genes, rng, probability):
    """Mutación por intercambio guiada por conflictos, con exploración aleatoria.

    Este operador modifica un hijo del cruce genético; no usa otro solver.
    Intercambiar dos columnas conserva la permutación del cromosoma.
    """
    n = len(genes)
    if n < 2 or rng.random() >= probability:
        return genes
    if rng.random() < 0.12:
        first, second = rng.sample(range(n), 2)
    else:
        _, descending, ascending = diagonal_counts(genes)
        attacked = [row for row, column in enumerate(genes)
                    if descending[row - column + n - 1] > 1 or ascending[row + column] > 1]
        if not attacked:
            return genes
        first = rng.choice(attacked)
        candidates = [other for other in rng.sample(range(n), min(n, 14)) if other != first]
        if not candidates:
            return genes
        second = min(candidates, key=lambda other: swap_delta(
            genes, first, other, descending, ascending))
    genes[first], genes[second] = genes[second], genes[first]
    return genes


def evolve_n_queens(n, config=None):
    """Emite cada generación y un resultado. La semilla permite repetir la búsqueda."""
    config = config or GeneticConfig()
    validate(n, config)
    rng = Random(config.seed)
    started = perf_counter()
    evaluations = 0
    generation = 0
    best = list(range(n))
    best_score = count_conflicts(best)
    initial_score = best_score
    stagnation = 0
    status = "generation_limit"

    def snapshot(genes, score, rate):
        return {"type": "generation", "n": n, "generation": generation,
                "positions": genes.copy(), "conflicts": score, "fitness": 1 / (1 + score),
                "evaluations": evaluations, "mutation_rate": round(rate, 3),
                "duration_ms": round((perf_counter() - started) * 1000, 3)}

    if n in (1, 2, 3):
        # Casos matemáticos conocidos: no se finge una búsqueda aleatoria.
        best = [0] if n == 1 else ([0, 1] if n == 2 else [0, 2, 1])
        best_score = count_conflicts(best)
        initial_score = best_score
        evaluations = 1
        yield snapshot(best, best_score, config.mutation_rate)
        status = "solved" if n == 1 else "impossible"
    else:
        population = []
        for _ in range(config.population_size):
            genes = list(range(n))
            rng.shuffle(genes)
            population.append((count_conflicts(genes), genes))
            evaluations += 1
        population.sort(key=lambda individual: individual[0])
        best_score, best = population[0][0], population[0][1].copy()
        initial_score = best_score
        yield snapshot(best, best_score, config.mutation_rate)

        while best_score > 0 and generation < config.max_generations:
            if perf_counter() - started >= config.time_limit:
                status = "time_limit"
                break
            # Elitismo: los dos mejores sobreviven a la siguiente generación.
            next_population = [(score, genes.copy()) for score, genes in population[:2]]
            rate = min(0.98, config.mutation_rate + stagnation * 0.015)

            def select_parent():
                # Torneo: gana el de menos conflictos entre tres al azar.
                return min(rng.sample(population, 3), key=lambda individual: individual[0])[1]

            while len(next_population) < config.population_size:
                if perf_counter() - started >= config.time_limit:
                    break
                parent_a, parent_b = select_parent(), select_parent()
                child = (ordered_crossover(parent_a, parent_b, rng)
                         if rng.random() < 0.85 else parent_a.copy())
                mutate(child, rng, rate)
                if stagnation > 25 and rng.random() < 0.08:
                    rng.shuffle(child)  # Inmigración genética: nueva diversidad.
                next_population.append((count_conflicts(child), child))
                evaluations += 1

            population = sorted(next_population, key=lambda individual: individual[0])
            generation += 1
            champion_score = population[0][0]
            champions = [genes for score, genes in population if score == champion_score]
            champion = rng.choice(champions)
            if champion_score < best_score:
                stagnation = 0
            else:
                stagnation += 1
            best_score, best = champion_score, champion.copy()
            yield snapshot(best, best_score, rate)

        if best_score == 0:
            status = "solved"

    yield {"type": "result", "algorithm": "genetic", "n": n, "status": status,
           "solved": best_score == 0, "positions": best.copy(), "conflicts": best_score,
           "initial_conflicts": initial_score, "generation": generation,
           "evaluations": evaluations, "population_size": config.population_size,
           "max_generations": config.max_generations, "mutation_rate": config.mutation_rate,
           "seed": config.seed, "time_limit": config.time_limit,
           "duration_ms": round((perf_counter() - started) * 1000, 3)}


def solve_n_queens(n, config=None):
    """Versión no transmitida para pruebas y clientes simples de la API."""
    trace = []
    for event in evolve_n_queens(n, config):
        if event["type"] == "generation":
            trace.append(event)
        else:
            return {**event, "trace": trace}
