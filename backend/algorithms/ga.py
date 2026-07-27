"""
ga.py — Genetic Algorithm (Navi Reference Optimizer Architecture)
------------------------------------------------------------------
Standard real-valued Genetic Algorithm with tournament selection, SBX crossover,
polynomial mutation, elitism, and optional Lamarckian local search fine-tuning.

Refactored to inherit from BaseOptimizer as Navi's reference optimizer template.
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
    TournamentSelection,
    SimulatedBinaryCrossover,
    PolynomialMutation,
    LamarckianLocalSearch,
)

DIM = 35


class GeneticAlgorithm(BaseOptimizer):
    """
    Real-Valued Genetic Algorithm Kernel.

    Responsibilities
    ----------------
    1. Real-coded EA evolutionary search over [0,1]^35 fuzzy parameter space.
    2. Modular operator delegation (Selection, SBX Crossover, Polynomial Mutation, Elitism).
    3. State-machine iterative execution via initialize() and step().
    4. Optional post-search fine-tuning via Lamarckian Local Search.

    ASM & Reference Optimizer Integration
    --------------------------------------
    - Step-Level Control: ASM can pause after any call to step() to re-allocate budget.
    - Diversity Telemetry: Exposes population spatial variance via get_population().
    - State Export: Fully serializes search state for multi-kernel switching.
    """

    def __init__(
        self,
        dim: int = DIM,
        bounds: Tuple[float, float] = (0.0, 1.0),
        budget: int = 10000,
        pop_size: int = 30,
        cx_prob: float = 0.85,
        mut_prob: float = 0.15,
        eta_c: float = 15.0,
        eta_m: float = 20.0,
        tournament_k: int = 5,
        enable_local_search: bool = True,
        local_search_steps: int = 100,
        seed: int = 42,
        verbose: bool = True,
    ):
        super().__init__(
            name="GA",
            dim=dim,
            bounds=bounds,
            budget=budget,
            seed=seed,
            verbose=verbose,
        )
        self.pop_size = pop_size
        self.cx_prob = cx_prob
        self.mut_prob = mut_prob
        self.eta_c = eta_c
        self.eta_m = eta_m
        self.enable_local_search = enable_local_search

        # Operators
        self.selector = TournamentSelection(k=tournament_k)
        self.crossovers = SimulatedBinaryCrossover(cx_prob=cx_prob, eta_c=eta_c, bounds=bounds)
        self.mutator = PolynomialMutation(mut_prob=mut_prob, eta_m=eta_m, bounds=bounds)
        self.local_searcher = LamarckianLocalSearch(n_steps=local_search_steps, bounds=bounds)

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
        
        # Initial population sampling
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
            metadata={"cx_prob": self.cx_prob, "mut_prob": self.mut_prob},
        )

        return self.state

    def step(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
    ) -> PopulationState:
        """
        Execute exactly one generation step of the Genetic Algorithm.
        """
        if self.state is None:
            raise RuntimeError("Optimizer not initialized. Call initialize() first.")

        pop = self.state.population
        scores = self.state.fitness
        best_f = self.state.best_fitness
        best_ind = self.state.best_solution

        new_pop_list = []
        while len(new_pop_list) < self.pop_size:
            p1 = self.selector.select(pop, scores, self.rng)
            p2 = self.selector.select(pop, scores, self.rng)

            c1, c2 = self.crossovers.cross(p1, p2, self.rng)
            
            c1 = self.mutator.mutate(c1, self.rng)
            new_pop_list.append(c1)
            
            if len(new_pop_list) < self.pop_size:
                c2 = self.mutator.mutate(c2, self.rng)
                new_pop_list.append(c2)

        current_pop = np.array(new_pop_list[: self.pop_size])
        current_scores = self.evaluate_population(current_pop, fitness_fn)

        # Elitism replacement
        gen_best_idx = int(np.argmax(current_scores))
        if current_scores[gen_best_idx] > best_f:
            best_f = float(current_scores[gen_best_idx])
            best_ind = current_pop[gen_best_idx].copy()
        else:
            worst_idx = int(np.argmin(current_scores))
            current_pop[worst_idx] = best_ind.copy()
            current_scores[worst_idx] = best_f

        self.generation += 1

        # Calculate population diversity (std across dimensions)
        diversity = float(np.mean(np.std(current_pop, axis=0)))

        # Update state
        self.state = PopulationState(
            population=current_pop,
            fitness=current_scores,
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
            mean_fitness=float(np.mean(current_scores)),
            worst_fitness=float(np.min(current_scores)),
            diversity_index=diversity,
        )

        return self.state

    def optimize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        pop_size: Optional[int] = None,
        iterations: int = 50,
    ) -> OptimizationResult:
        """
        Run full evolutionary search and optional Lamarckian local search fine-tuning.
        """
        p_size = pop_size if pop_size is not None else self.pop_size
        self.initialize(fitness_fn, pop_size=p_size)
        self.logger.start(initial_fitness=self.state.best_fitness)

        for _ in range(iterations):
            if self.is_budget_exhausted():
                break
            self.step(fitness_fn)

        best_ind = self.get_best_solution()
        best_f = self.state.best_fitness

        # Optional Lamarckian Local Search Fine-Tuning
        if self.enable_local_search:
            if self.verbose:
                print(f"  [GA] Evolutionary search complete. Fine-tuning {best_f:.6f} ...")
            
            def eval_wrapper(cand):
                return self.evaluate_candidate(cand, fitness_fn)

            refined_ind, refined_f, _ = self.local_searcher.search(
                champion=best_ind,
                champion_fitness=best_f,
                eval_fn=eval_wrapper,
                rng=self.rng,
            )
            
            if refined_f >= best_f:
                best_ind = refined_ind
                best_f = refined_f

        # Final simulation evaluation for complete dictionary output
        best_fitness, best_result = fitness_fn(best_ind)
        stats = self.get_statistics()

        return OptimizationResult(
            algorithm=self.name,
            best_solution=best_ind,
            fitness=best_fitness,
            green_times=best_result.get("green_times", []),
            cycle_time=best_result.get("cycle_time", 120),
            avg_speed=best_result.get("avg_speed", 0.0),
            avg_density=best_result.get("avg_density", 0.0),
            avg_wait_time=best_result.get("avg_wait_time", 0.0),
            total_flow=best_result.get("total_flow", 0.0),
            avg_queue_length=best_result.get("avg_queue_length", 0.0),
            congestion_pressure=best_result.get("congestion_pressure", 0.0),
            speed_density_ratio=best_result.get("speed_density_ratio", 0.0),
            convergence_history=self.get_history(),
            simulation_steps=best_result.get("simulation_steps", []),
            statistics=stats,
        )


# ─────────────────────────────────────────────────────────────────────────────
# Backward-Compatible Wrapper Function
# ─────────────────────────────────────────────────────────────────────────────
def run_ga(
    csv_path: str = "vanet.csv",
    pop_size: int = 30,
    n_gen: int = 50,
    cx_prob: float = 0.85,
    mut_prob: float = 0.15,
    eta_c: float = 15.0,
    eta_m: float = 20.0,
    seed: int = 42,
) -> dict:
    """
    Backward-compatible wrapper function for Genetic Algorithm.

    Preserves function signature expected by main.py, run_algo_graphs.py, and external callers.
    """
    def fitness_fn(cand):
        return evaluate_fitness(cand, csv_path=csv_path, seed=seed)

    ga = GeneticAlgorithm(
        pop_size=pop_size,
        cx_prob=cx_prob,
        mut_prob=mut_prob,
        eta_c=eta_c,
        eta_m=eta_m,
        seed=seed,
        verbose=True,
    )

    res = ga.optimize(fitness_fn=fitness_fn, pop_size=pop_size, iterations=n_gen)
    return res.to_dict()
