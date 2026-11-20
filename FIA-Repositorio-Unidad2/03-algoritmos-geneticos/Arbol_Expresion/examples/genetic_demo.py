"""Regresión simbólica mínima: busca una fórmula cercana a x²+x+1.

Ejecuta: python -m examples.genetic_demo
La programación genética usa árboles como individuos del algoritmo evolutivo.
"""

import argparse
import random
from arithmetic import EvaluationPolicy
from expression_tree import ExpressionTree


def evolve(seed=7, generations=12, population_size=40):
    rng = random.Random(seed)
    policy = EvaluationPolicy(mode="protected")
    rows = [{"x": index / 10} for index in range(-10, 11)]
    targets = [row["x"] ** 2 + row["x"] + 1 for row in rows]
    population = [ExpressionTree.random(rng=rng, policy=policy, primitives=("+", "-", "*", "/")) for _ in range(population_size)]
    history = []

    for generation in range(generations + 1):
        # Fitness: el error cuadrático medio. Menor significa mejor candidato.
        ranked = sorted(((tree.fitness(rows, targets), index, tree) for index, tree in enumerate(population)), key=lambda item: item[0])
        best_error, _, best = ranked[0]
        history.append(best_error)
        print(f"Generación {generation:02d} | MSE {best_error:.8g} | {best.to_expression()}")
        if best_error < 1e-12 or generation == generations:
            return best, history

        def tournament():
            return min(rng.sample(ranked, min(3, len(ranked))), key=lambda item: item[0])[2]

        # Elitismo: guardamos los dos mejores para no perder lo ya aprendido.
        next_population = [ranked[0][2].clone(), ranked[1][2].clone()]
        while len(next_population) < population_size:
            first, second = tournament(), tournament()
            children = first.crossover(second, rng=rng, max_depth=8, max_nodes=100) if rng.random() < .7 else (first.clone(), second.clone())
            for child in children:
                if rng.random() < .3:
                    child = child.mutate(rng=rng, max_depth=8, max_nodes=100, primitives=("+", "-", "*", "/"))
                next_population.append(child)
                if len(next_population) == population_size:
                    break
        population = next_population


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed", type=int, default=7)
    parser.add_argument("--generations", type=int, default=12)
    parser.add_argument("--population", type=int, default=40)
    options = parser.parse_args()
    if not 0 <= options.generations <= 1000 or not 4 <= options.population <= 500:
        parser.error("Usa de 0 a 1000 generaciones y de 4 a 500 individuos.")
    winner, _history = evolve(options.seed, options.generations, options.population)
    print("\nPega la expresión ganadora en Arboria para ver su árbol y su curva:")
    print(winner.to_expression())
