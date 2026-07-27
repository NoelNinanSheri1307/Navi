"""
de.py — Differential Evolution (Navi Framework Optimizer Architecture)
-----------------------------------------------------------------------
Classic DE/rand/1/bin strategy refactored to inherit from BaseOptimizer.

Optimises the 35-dim fuzzy parameter vector while maintaining 100% backward
compatibility and deterministic seed reproducibility.
"""

from typing import Callable, Dict, Any, Tuple, Optional
import numpy as np

from evaluation.fitness import evaluate_fitness
from algorithms.base import (
    BaseOptimizer,
    PopulationState,
    OptimizationResult,
)
from algorithms.operators import (
    DEMutation,
    DECrossover,
    DESelection,
)

DIM = 35


class DifferentialEvolution(BaseOptimizer):
    """
    Differential Evolution Optimizer Kernel.

    Responsibilities
    ----------------
    1. Continuous global optimization over [0,1]^35 fuzzy parameter space.
    2. Modular operator delegation (DE Mutation, DE Binomial Crossover, Greedy Selection).
    3. State-machine iterative execution via initialize() and step().
    4. Flexible mutation strategy configuration (default 'rand/1', extensible to 'best/1').

    ASM & Reference Optimizer Integration
    --------------------------------------
    - Step-Level Control: ASM can pause after any call to step() to inspect metrics.
    - Diversity Telemetry: Exposes population spatial variance via get_population().
    - State Serialization: Export and restore search state across strategy switches.
    """

    def __init__(
        self,
        dim: int = DIM,
        bounds: Tuple[float, float] = (0.0, 1.0),
        budget: int = 10000,
        pop_size: int = 30,
        F: float = 0.8,
        CR: float = 0.9,
        strategy: str = "rand/1",
        seed: int = 42,
        verbose: bool = True,
    ):
        super().__init__(
            name="DE",
            dim=dim,
            bounds=bounds,
            budget=budget,
            seed=seed,
            verbose=verbose,
        )
        self.pop_size = pop_size
        self.F = F
        self.CR = CR
        self.strategy = strategy

        # Modular Operators
        self.mutator = DEMutation(F=F, strategy=strategy, bounds=bounds)
        self.crossovers = DECrossover(CR=CR)
        self.selector = DESelection()

    def initialize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        pop_size: Optional[int] = None,
    ) -> PopulationState:
        """
        Initialize uniform random population and compute baseline fitness scores.
        """
        if pop_size is not None:
            self.pop_size = pop_size

        self.reset()

        pop = self.rng.uniform(self.bounds[0], self.bounds[1], (self.pop_size, self.dim))
        scores = self.evaluate_population(pop, fitness_fn)

        best_idx = int(np.argmax(scores))
        best_ind = pop[best_idx].copy()
        best_f = float(scores[best_idx])

        self.state = PopulationState(
            population=pop,
            fitness=scores,
            best_solution=best_ind,
            best_fitness=best_f,
            evaluation_count=self.evaluations_used,
            generation=0,
            metadata={"F": self.F, "CR": self.CR, "strategy": self.strategy},
        )

        return self.state

    def step(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
    ) -> PopulationState:
        """
        Execute exactly one generation step of Differential Evolution.
        """
        if self.state is None:
            raise RuntimeError("Optimizer not initialized. Call initialize() first.")

        pop = self.state.population
        scores = self.state.fitness
        best_f = self.state.best_fitness
        best_ind = self.state.best_solution.copy()

        for i in range(self.pop_size):
            if self.is_budget_exhausted():
                break

            # 1. Mutation
            mutant = self.mutator.mutate(
                target_idx=i,
                population=pop,
                best_individual=best_ind,
                rng=self.rng,
            )

            # 2. Crossover
            trial = self.crossovers.cross(
                target=pop[i],
                mutant=mutant,
                rng=self.rng,
            )

            # 3. Evaluation
            f_trial, _ = self.evaluate_candidate(trial, fitness_fn)

            # 4. Selection
            chosen_ind, chosen_f, replaced = self.selector.select(
                target_individual=pop[i],
                target_fitness=scores[i],
                trial_individual=trial,
                trial_fitness=f_trial,
            )

            pop[i] = chosen_ind
            scores[i] = chosen_f

            if chosen_f > best_f:
                best_f = chosen_f
                best_ind = chosen_ind.copy()

        self.generation += 1

        # Calculate population spatial diversity
        diversity = float(np.mean(np.std(pop, axis=0)))

        # Update state
        self.state = PopulationState(
            population=pop,
            fitness=scores,
            best_solution=best_ind,
            best_fitness=best_f,
            evaluation_count=self.evaluations_used,
            generation=self.generation,
            metadata={"diversity": diversity},
        )

        # Telemetry logging
        self.logger.log_step(
            generation=self.generation,
            evaluation_count=self.evaluations_used,
            best_fitness=best_f,
            mean_fitness=float(np.mean(scores)),
            worst_fitness=float(np.min(scores)),
            diversity_index=diversity,
        )

        return self.state


# ─────────────────────────────────────────────────────────────────────────────
# Backward-Compatible Wrapper Function
# ─────────────────────────────────────────────────────────────────────────────
def run_de(
    csv_path: str = "vanet.csv",
    pop_size: int = 30,
    n_gen: int = 50,
    F: float = 0.8,
    CR: float = 0.9,
    seed: int = 42,
) -> dict:
    """
    Backward-compatible wrapper function for Differential Evolution (DE/rand/1/bin).

    Preserves function signature expected by main.py, run_algo_graphs.py, and external callers.
    """
    def fitness_fn(cand):
        return evaluate_fitness(cand, csv_path=csv_path, seed=seed)

    de = DifferentialEvolution(
        pop_size=pop_size,
        F=F,
        CR=CR,
        strategy="rand/1",
        seed=seed,
        verbose=True,
    )

    res = de.optimize(fitness_fn=fitness_fn, pop_size=pop_size, iterations=n_gen)
    return res.to_dict()
