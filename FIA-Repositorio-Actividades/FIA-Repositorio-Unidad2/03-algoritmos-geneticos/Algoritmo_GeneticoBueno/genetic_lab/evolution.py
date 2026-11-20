"""Motor de programación genética independiente de la interfaz gráfica."""
from dataclasses import dataclass, field
import itertools
import math
import random
from statistics import median
from .metrics import ErrorEvaluator, Metrics, METRICS, metric_loss
from .trees import Node, evaluate, random_tree, crossover, mutate, mutate_constant, repair, simplify
from .refinement import refine_affine


@dataclass(frozen=True)
class Config:
    population: int = 180
    generations: int = 80  # 0 = sin límite: sigue hasta alcanzar target_r2 o detenerse
    max_depth: int = 6
    tournament: int = 5
    elitism: int = 4
    crossover_rate: float = 0.85
    mutation_rate: float = 0.3
    parsimony: float = 0.0
    metric: str = "mse"
    immigration_rate: float = 0.1
    elite_mutation_rate: float = 0.0  # fracción de hijos que son el élite con una constante perturbada
    adaptive_mutation: bool = True
    refine_constants: bool = True
    seed: int = 42
    operators: tuple[str, ...] = ("+", "-", "*", "/", "sin", "cos")
    pruning: bool = True
    target_r2: float = 0.0  # 0 desactiva el paro por objetivo
    # Evaluación incremental: el error se mide primero en una ventana central y se amplía
    # cuando el élite la ajusta con R² >= expand_r2, hasta cubrir todo el CSV.
    incremental: bool = False
    start_window: float = 0.08
    expand_r2: float = 0.98
    window_growth: float = 1.3

    def validate(self):
        from .trees import ARITY
        if not 10 <= self.population <= 2000: raise ValueError("Población: 10 a 2000.")
        if not 0 <= self.generations <= 1000: raise ValueError("Generaciones: 0 (sin límite) a 1000.")
        if not 0 <= self.target_r2 <= 1: raise ValueError("R² objetivo: 0 a 1.")
        if not 0 < self.start_window <= 1 or not 0 < self.expand_r2 <= 1 or self.window_growth <= 1:
            raise ValueError("Ventana inicial y R² para ampliar: entre 0 y 1.")
        if not 2 <= self.max_depth <= 9: raise ValueError("Profundidad: 2 a 9.")
        if not 1 <= self.elitism < self.population: raise ValueError("Elitismo fuera de rango.")
        if not 2 <= self.tournament <= self.population: raise ValueError("Torneo fuera de rango.")
        if not 0 <= self.crossover_rate <= 1 or not 0 <= self.mutation_rate <= 1:
            raise ValueError("Las probabilidades deben estar entre 0 y 1.")
        if not math.isfinite(self.parsimony) or self.parsimony < 0:
            raise ValueError("La penalización por complejidad debe ser finita y no negativa.")
        if self.metric not in METRICS: raise ValueError("Método de error inválido.")
        if not 0 <= self.immigration_rate <= 0.5: raise ValueError("Inmigración: 0 a 0.5.")
        if not 0 <= self.elite_mutation_rate <= 0.5: raise ValueError("Mutantes del élite: 0 a 0.5.")
        if not self.operators or any(op not in ARITY or ARITY[op] == 0 for op in self.operators):
            raise ValueError("Selecciona al menos una operación válida.")


@dataclass(frozen=True)
class Individual:
    tree: Node
    metrics: Metrics
    score: float


@dataclass(frozen=True)
class GeneticEvent:
    kind: str
    before: Node
    after: Node
    detail: str
    donor: Node | None = None


@dataclass(frozen=True)
class Snapshot:
    generation: int
    best: Individual
    top: tuple[Individual, ...]
    median_mse: float
    diversity: float
    events: tuple[GeneticEvent, ...] = ()
    counts: dict = field(default_factory=dict)
    metric: str = "mse"
    mutation_rate: float = 0.3
    stagnant_generations: int = 0
    window: tuple[float, float] | None = None  # tramo de x evaluado; None = todo el CSV


class Evolution:
    def __init__(self, dataset, config):
        config.validate()
        self.data, self.config = dataset, config
        self.rng = random.Random(config.seed)
        self.full_errors = ErrorEvaluator(dataset.y)
        self.full_cache = {}
        low, high = min(dataset.x), max(dataset.x)
        self.center, self.radius = (low + high) / 2, (high - low) / 2
        self.fraction = config.start_window if config.incremental else 1.0
        self.set_window()

    def set_window(self):
        """Selecciona los puntos con |x - centro| <= fracción·radio (mínimo 30 puntos)."""
        limit = self.fraction * self.radius
        points = [(a, b) for a, b in zip(self.data.x, self.data.y) if abs(a - self.center) <= limit]
        if self.fraction >= 1 or len(points) < 30:
            self.fraction, points = 1.0, list(zip(self.data.x, self.data.y))
        self.x, self.y = tuple(a for a, _ in points), tuple(b for _, b in points)
        self.cache = {}
        self.errors = ErrorEvaluator(self.y)
        self.baseline = self.errors.measure([self.errors.mean] * len(self.y))
        self.scale = metric_loss(self.baseline, self.config.metric) or 1.0

    @property
    def window(self):
        if self.fraction >= 1: return None
        return (self.center - self.fraction * self.radius, self.center + self.fraction * self.radius)

    def on_full_data(self, individual):
        """Las métricas mostradas siempre usan los puntos completos del CSV."""
        if self.fraction >= 1: return individual
        if individual.tree not in self.full_cache:
            self.full_cache[individual.tree] = self.full_errors.measure(evaluate(individual.tree, self.data.x))
        return Individual(individual.tree, self.full_cache[individual.tree], individual.score)

    def assess(self, tree):
        if tree not in self.cache:
            metrics = self.errors.measure(evaluate(tree, self.x))
            score = metric_loss(metrics, self.config.metric) / self.scale + self.config.parsimony * tree.size
            self.cache[tree] = Individual(tree, metrics, score)
        return self.cache[tree]

    def select(self, population):
        """Torneo: sorteamos k candidatos y elegimos el de menor aptitud penalizada."""
        return min(self.rng.sample(population, self.config.tournament), key=lambda item: item.score)

    def refine(self, child, events, counts):
        before = child
        child, changed = refine_affine(child, self.x, self.y, self.config.max_depth)
        if changed:
            counts["ajustes de constantes"] += 1
            if not any(event.kind == "Ajuste de constantes" for event in events):
                events.append(GeneticEvent("Ajuste de constantes", before, child,
                    "Se afinan a y b en a + b·g(x) mediante mínimos cuadrados escritos en Python. "
                    "Solo se acepta si mejora el error y respeta la profundidad máxima."))
        return child

    def run(self, cancelled=lambda: False):
        config, rng = self.config, self.rng
        trees = [random_tree(rng, rng.randint(2, config.max_depth), config.operators, full=i % 2 == 0)
                 for i in range(config.population)]
        events, counts = [], {}
        best_loss = math.inf
        stagnant = 0
        used_mutation = config.mutation_rate
        # Generación 0 = población aleatoria, seguida de N generaciones evolucionadas (o sin límite).
        for generation in itertools.count():
            if cancelled(): return
            population = []
            for tree in trees:
                if cancelled(): return
                population.append(self.assess(tree))
            ranked = sorted(population, key=lambda item: item.score)
            by_error = sorted(population, key=lambda item: (metric_loss(item.metrics, config.metric), item.tree.size))
            champion = by_error[0]
            loss = metric_loss(champion.metrics, config.metric)
            stagnant = stagnant + 1 if loss >= best_loss - 1e-12 else 0
            best_loss = min(best_loss, loss)
            top = tuple(self.on_full_data(item) for item in by_error[:8])
            window, window_r2 = self.window, champion.metrics.r2
            yield Snapshot(generation, top[0], top,
                           float(median(item.metrics.mse for item in population)),
                           len(set(trees)) / len(trees), tuple(events), counts.copy(),
                           config.metric, used_mutation, stagnant, window)
            if generation == config.generations != 0 or cancelled(): return
            if config.target_r2 and top[0].metrics.r2 >= config.target_r2: return
            expanded = None
            if window and window_r2 >= config.expand_r2:
                # El élite domina la ventana: la ampliamos y reevaluamos a toda la población.
                self.fraction = min(1.0, self.fraction * config.window_growth)
                self.set_window()
                population = [self.assess(item.tree) for item in population]
                ranked = sorted(population, key=lambda item: item.score)
                champion = min(population, key=lambda item: (metric_loss(item.metrics, config.metric), item.tree.size))
                best_loss, stagnant = math.inf, 0
                expanded = self.window or (min(self.data.x), max(self.data.x))
            # Conservamos al campeón del criterio elegido y otras élites por aptitud.
            trees = [champion.tree] + [item.tree for item in ranked[:config.elitism - 1]]
            events = []
            counts = {"cruzas": 0, "mutaciones": 0, "reconstrucciones": 0, "podas": 0, "reparaciones": 0,
                      "elites": config.elitism, "inmigrantes": 0, "ajustes de constantes": 0}
            if expanded:
                counts["ampliaciones de ventana"] = 1
                events.append(GeneticEvent("Ampliación de ventana", champion.tree, champion.tree,
                    f"El élite alcanzó R² ≥ {config.expand_r2:g} en el tramo evaluado; "
                    f"ahora el error se mide en x ∈ [{expanded[0]:.3g}, {expanded[1]:.3g}]."))
            immigrants = min(round(config.population * config.immigration_rate), config.population - config.elitism)
            used_mutation = min(1.0, config.mutation_rate + 0.2) if config.adaptive_mutation and stagnant >= 8 else config.mutation_rate
            elite_mutants = min(round(config.population * config.elite_mutation_rate),
                                config.population - immigrants - len(trees))
            for _ in range(elite_mutants):
                if cancelled(): return
                child, detail = mutate_constant(champion.tree, rng)
                if detail is None: break
                counts["mutaciones del élite"] = counts.get("mutaciones del élite", 0) + 1
                if not any(event.kind == "Mutación del élite" for event in events):
                    events.append(GeneticEvent("Mutación del élite", champion.tree, child,
                        detail + " Afina las constantes del mejor individuo sin cambiar su forma."))
                trees.append(child)
            while len(trees) < config.population - immigrants:
                if cancelled(): return
                parent = self.select(population).tree
                child = parent
                if rng.random() < config.crossover_rate:
                    donor = self.select(population).tree
                    child, detail = crossover(parent, donor, rng)
                    counts["cruzas"] += 1
                    counts["reconstrucciones"] += 1
                    if not any(event.kind == "Cruza" for event in events):
                        events.append(GeneticEvent("Cruza", parent, child, detail, donor))
                    if not any(event.kind == "Reconstrucción" for event in events):
                        events.append(GeneticEvent("Reconstrucción", parent, child,
                            "Al injertar la rama se reconstruye el camino hasta la raíz. "
                            "Es la reconstrucción usada en la cruza; el padre permanece intacto.", donor))
                if rng.random() < used_mutation:
                    before = child
                    child, detail = mutate(child, rng, config.max_depth, config.operators)
                    counts["mutaciones"] += 1
                    counts["reconstrucciones"] += 1
                    if not any(event.kind == "Mutación" for event in events):
                        events.append(GeneticEvent("Mutación", before, child, detail))
                    if not any(event.kind == "Reconstrucción" for event in events):
                        events.append(GeneticEvent("Reconstrucción", before, child,
                            "La sustitución de una rama reconstruye el camino hasta la raíz; "
                            "el árbol anterior permanece intacto. Es parte de esta mutación."))
                before = child
                child, changes = repair(child, config.max_depth, rng)
                counts["reparaciones"] += changes
                if changes and not any(event.kind == "Reparación" for event in events):
                    events.append(GeneticEvent("Reparación", before, child,
                                              f"{changes} correcciones de estructura o profundidad máxima."))
                if config.pruning:
                    before = child
                    child, changes = simplify(child)
                    counts["podas"] += changes
                    if changes and not any(event.kind == "Poda" for event in events):
                        events.append(GeneticEvent("Poda", before, child,
                                                  f"{changes} simplificaciones algebraicas; se conserva la función protegida."))
                if config.refine_constants and rng.random() < 0.25:
                    child = self.refine(child, events, counts)
                trees.append(child)
            for _ in range(immigrants):
                if cancelled(): return
                immigrant = random_tree(rng, rng.randint(2, config.max_depth), config.operators)
                if config.refine_constants:
                    immigrant = self.refine(immigrant, events, counts)
                trees.append(immigrant)
                counts["inmigrantes"] += 1
            # Cache acotada a individuos vivos: las ejecuciones largas no acumulan árboles.
            alive = set(trees)
            self.cache = {tree: item for tree, item in self.cache.items() if tree in alive}
            self.full_cache = {tree: item for tree, item in self.full_cache.items() if tree in alive}
