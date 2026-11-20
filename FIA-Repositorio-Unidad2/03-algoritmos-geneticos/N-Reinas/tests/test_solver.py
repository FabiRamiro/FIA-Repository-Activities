"""Propiedades del algoritmo genético y resultados repetibles, sin dependencias."""

import itertools
import random
import unittest
from unittest.mock import patch

from solver import (GeneticConfig, count_conflicts, diagonal_counts, evolve_n_queens,
                    mutate, ordered_crossover, solve_n_queens, swap_delta, validate)


def brute_conflicts(genes):
    return sum(abs(genes[a] - genes[b]) == b - a
               for a in range(len(genes)) for b in range(a + 1, len(genes)))


class GeneticSolverTests(unittest.TestCase):
    def test_fitness_matches_independent_pair_count(self):
        rng = random.Random(7)
        for n in [1, 2, 4, 8, 16, 40]:
            for _ in range(20):
                genes = rng.sample(range(n), n)
                self.assertEqual(count_conflicts(genes), brute_conflicts(genes))

    def test_crossover_and_mutation_preserve_permutations(self):
        rng = random.Random(31)
        for n in [1, 4, 8, 32, 100]:
            for _ in range(30):
                a, b = rng.sample(range(n), n), rng.sample(range(n), n)
                original_a, original_b = a.copy(), b.copy()
                child = ordered_crossover(a, b, rng)
                self.assertEqual(sorted(child), list(range(n)))
                mutate(child, rng, 1.0)
                self.assertEqual(sorted(child), list(range(n)))
                self.assertEqual(a, original_a)
                self.assertEqual(b, original_b)

    def test_swap_delta_matches_full_recalculation(self):
        rng = random.Random(12)
        for n in [2, 4, 12, 50]:
            for _ in range(40):
                genes = rng.sample(range(n), n)
                before, down, up = diagonal_counts(genes)
                a, b = rng.sample(range(n), 2)
                delta = swap_delta(genes, a, b, down, up)
                genes[a], genes[b] = genes[b], genes[a]
                self.assertEqual(before + delta, brute_conflicts(genes))

    def test_genetic_search_solves_beyond_twelve(self):
        for n in [4, 8, 16, 32, 64, 100]:
            with self.subTest(n=n):
                result = solve_n_queens(n, GeneticConfig(seed=42, time_limit=10))
                self.assertTrue(result["solved"])
                self.assertEqual(result["status"], "solved")
                self.assertEqual(brute_conflicts(result["positions"]), 0)
                self.assertEqual(sorted(result["positions"]), list(range(n)))

    def test_trace_is_real_and_elitism_never_loses_best_fitness(self):
        result = solve_n_queens(32, GeneticConfig(seed=42))
        scores = []
        for index, frame in enumerate(result["trace"]):
            self.assertEqual(frame["generation"], index)
            self.assertEqual(frame["conflicts"], brute_conflicts(frame["positions"]))
            self.assertAlmostEqual(frame["fitness"], 1 / (1 + frame["conflicts"]))
            self.assertEqual(sorted(frame["positions"]), list(range(32)))
            scores.append(frame["conflicts"])
        self.assertEqual(scores, sorted(scores, reverse=True))
        self.assertEqual(result["trace"][-1]["positions"], result["positions"])

    def test_seed_repeats_genetic_experiment(self):
        a = solve_n_queens(32, GeneticConfig(seed=11))
        b = solve_n_queens(32, GeneticConfig(seed=11))
        self.assertEqual([f["positions"] for f in a["trace"]], [f["positions"] for f in b["trace"]])

    def test_trivial_and_impossible_cases(self):
        self.assertEqual(solve_n_queens(1)["positions"], [0])
        for n in [2, 3]:
            result = solve_n_queens(n)
            self.assertFalse(result["solved"])
            self.assertEqual(result["status"], "impossible")

    def test_generation_exhaustion_does_not_claim_impossibility(self):
        result = solve_n_queens(1000, GeneticConfig(population_size=4, max_generations=1, seed=3))
        self.assertFalse(result["solved"])
        self.assertEqual(result["generation"], 1)
        self.assertEqual(result["status"], "generation_limit")

    def test_time_budget_returns_best_candidate(self):
        ticks = itertools.count(step=0.02)
        with patch("solver.perf_counter", side_effect=lambda: next(ticks)):
            result = solve_n_queens(100, GeneticConfig(seed=42, time_limit=.05))
        self.assertEqual(result["status"], "time_limit")
        self.assertEqual(result["conflicts"], brute_conflicts(result["positions"]))

    def test_positive_n_without_fixed_upper_bound_and_resource_budget(self):
        validate(100000, GeneticConfig(population_size=4))
        with self.assertRaisesRegex(ValueError, "memoria"):
            validate(100000000, GeneticConfig())
        for n in [0, -1, 4.5, "8", True, None]:
            with self.subTest(n=n), self.assertRaises(ValueError):
                solve_n_queens(n)

    def test_event_stream_finishes_with_result(self):
        events = list(evolve_n_queens(16, GeneticConfig(seed=42)))
        self.assertTrue(all(event["type"] == "generation" for event in events[:-1]))
        self.assertEqual(events[-1]["type"], "result")
        self.assertEqual(events[-1]["algorithm"], "genetic")


if __name__ == "__main__":
    unittest.main()
