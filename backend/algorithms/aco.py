"""
aco.py — Ant Colony Optimization (Navi Memory-Based Swarm Architecture)
-------------------------------------------------------------------------
Continuous Ant Colony Optimization (ACOR - Socha & Dorigo, 2008) with continuous
solution archive pheromone model and Gaussian mixture sampling.

Refactored to inherit from BaseOptimizer as Navi's reference memory-based optimizer.
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
    ACORArchivePheromone,
    ACORTransition,
    ACORArchiveUpdate,
)

DIM = 35


class AntColonyOptimizer(BaseOptimizer):
    """
    Continuous Ant Colony Optimization (ACOR) Kernel.

    Responsibilities
    ----------------
    1. Continuous global search over [0,1]^35 fuzzy parameter space using a solution archive.
    2. Modular operator delegation (Pheromone Weights, Ant Sampling, Archive Update).
    3. Iterative state-machine lifecycle via initialize() and step().
    4. Colony telemetry recording (mean Gaussian sigma variance, archive best/mean fitness).

    ASM & Framework Integration
    ---------------------------
    - Step-Level Control: ASM can pause after any colony iteration step.
    - Persistent Colony State: Solution archive matrix and fitness scores stored in PopulationState.metadata.
    - State Serialization: Export and restore archive state across strategy switches.
    """

    def __init__(
        self,
        dim: int = DIM,
        bounds: Tuple[float, float] = (0.0, 1.0),
        budget: int = 10000,
        n_ants: int = 20,
        archive_size: int = 30,
        pop_size: Optional[int] = None,
        q: float = 0.1,
        xi: float = 0.85,
        seed: int = 42,
        verbose: bool = True,
    ):
        super().__init__(
            name="ACO",
            dim=dim,
            bounds=bounds,
            budget=budget,
            seed=seed,
            verbose=verbose,
        )
        self.n_ants = pop_size if pop_size is not None else n_ants
        self.archive_size = archive_size
        self.q = q
        self.xi = xi

        # Operators
        self.pheromone_op = ACORArchivePheromone(q=q, xi=xi)
        self.transition_op = ACORTransition(bounds=bounds)
        self.update_op = ACORArchiveUpdate()

        # Colony State Tensors
        self.archive: Optional[np.ndarray] = None
        self.archive_scores: Optional[np.ndarray] = None
        self.rank_weights: Optional[np.ndarray] = None

    def initialize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        n_ants: Optional[int] = None,
        pop_size: Optional[int] = None,
    ) -> PopulationState:
        """
        Initialize solution archive, evaluate initial candidates, and compute rank weights.
        """
        ant_count = pop_size if pop_size is not None else n_ants
        if ant_count is not None:
            self.n_ants = ant_count

        self.reset()

        # Archive position sampling over [0, 1]^35
        self.archive = self.rng.uniform(self.bounds[0], self.bounds[1], (self.archive_size, self.dim))
        scores = self.evaluate_population(self.archive, fitness_fn)

        # Sort archive descending by fitness
        order = np.argsort(scores)[::-1]
        self.archive = self.archive[order]
        self.archive_scores = scores[order]

        # Compute rank probabilities
        self.rank_weights = self.pheromone_op.compute_rank_weights(self.archive_size)

        self.state = PopulationState(
            population=self.archive.copy(),
            fitness=self.archive_scores.copy(),
            best_solution=self.archive[0].copy(),
            best_fitness=float(self.archive_scores[0]),
            evaluation_count=self.evaluations_used,
            generation=0,
            metadata={
                "archive": self.archive.copy(),
                "archive_scores": self.archive_scores.copy(),
                "rank_weights": self.rank_weights.copy(),
                "archive_size": self.archive_size,
                "q": self.q,
                "xi": self.xi,
            },
        )

        return self.state

    def step(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
    ) -> PopulationState:
        """
        Execute exactly one iteration step of Continuous Ant Colony Optimization.
        """
        if self.state is None or self.archive is None:
            raise RuntimeError("Optimizer not initialized. Call initialize() first.")

        # 1. Sample new ant candidate positions
        new_ants = np.zeros((self.n_ants, self.dim), dtype=float)
        for i in range(self.n_ants):
            ant_pos, _ = self.transition_op.sample_ant(
                archive=self.archive,
                weights=self.rank_weights,
                pheromone_op=self.pheromone_op,
                rng=self.rng,
            )
            new_ants[i] = ant_pos

        # 2. Evaluate newly sampled ant positions
        new_scores = self.evaluate_population(new_ants, fitness_fn)

        # 3. Merge and update solution archive
        self.archive, self.archive_scores = self.update_op.update_archive(
            archive=self.archive,
            archive_scores=self.archive_scores,
            new_ants=new_ants,
            new_scores=new_scores,
            archive_size=self.archive_size,
        )

        # 4. Re-calculate rank weights
        self.rank_weights = self.pheromone_op.compute_rank_weights(self.archive_size)

        self.generation += 1
        diversity = float(np.mean(np.std(self.archive, axis=0)))

        # Calculate mean Gaussian kernel sigma across dimensions for template 0
        sigmas_0 = self.pheromone_op.compute_dimension_sigmas(self.archive, 0)
        mean_sigma = float(np.mean(sigmas_0))

        # Update state
        self.state = PopulationState(
            population=self.archive.copy(),
            fitness=self.archive_scores.copy(),
            best_solution=self.archive[0].copy(),
            best_fitness=float(self.archive_scores[0]),
            evaluation_count=self.evaluations_used,
            generation=self.generation,
            metadata={
                "archive": self.archive.copy(),
                "archive_scores": self.archive_scores.copy(),
                "rank_weights": self.rank_weights.copy(),
                "diversity": diversity,
                "mean_sigma": mean_sigma,
                "pheromone_mean": float(np.mean(self.rank_weights)),
                "pheromone_var": float(np.var(self.rank_weights)),
            },
        )

        # Telemetry logging
        self.logger.log_step(
            generation=self.generation,
            evaluation_count=self.evaluations_used,
            best_fitness=float(self.archive_scores[0]),
            mean_fitness=float(np.mean(self.archive_scores)),
            worst_fitness=float(np.min(self.archive_scores)),
            diversity_index=diversity,
        )

        return self.state

    def optimize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        n_ants: Optional[int] = None,
        archive_size: Optional[int] = None,
        n_iter: int = 50,
    ) -> OptimizationResult:
        """
        Execute full ant colony optimization run.
        """
        if archive_size is not None:
            self.archive_size = archive_size
        ant_count = n_ants if n_ants is not None else self.n_ants

        self.initialize(fitness_fn, n_ants=ant_count)
        self.logger.start(initial_fitness=self.state.best_fitness)

        for _ in range(n_iter):
            if self.is_budget_exhausted():
                break
            self.step(fitness_fn)

        best_ind = self.get_best_solution()
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

    def export_state(self) -> Dict[str, Any]:
        """Export state dictionary including continuous solution archive tensors."""
        base_state = super().export_state()
        if self.archive is not None:
            base_state["archive"] = self.archive.copy()
            base_state["archive_scores"] = self.archive_scores.copy()
            base_state["rank_weights"] = self.rank_weights.copy()
        return base_state

    def restore_state(self, state_dict: Dict[str, Any]) -> None:
        """Restore search state including solution archive tensors."""
        super().restore_state(state_dict)
        if "archive" in state_dict:
            self.archive = state_dict["archive"].copy()
            self.archive_scores = state_dict["archive_scores"].copy()
            self.rank_weights = state_dict["rank_weights"].copy()


# ─────────────────────────────────────────────────────────────────────────────
# Backward-Compatible Wrapper Function
# ─────────────────────────────────────────────────────────────────────────────
def run_aco(
    csv_path: str = "vanet.csv",
    n_ants: int = 20,
    archive_size: int = 30,
    q: float = 0.1,
    xi: float = 0.85,
    n_iter: int = 50,
    seed: int = 42,
) -> dict:
    """
    Backward-compatible wrapper function for Ant Colony Optimization.

    Preserves function signature expected by main.py, run_algo_graphs.py, and external callers.
    """
    def fitness_fn(cand):
        return evaluate_fitness(cand, csv_path=csv_path, seed=seed)

    aco = AntColonyOptimizer(
        n_ants=n_ants,
        archive_size=archive_size,
        q=q,
        xi=xi,
        seed=seed,
        verbose=True,
    )

    res = aco.optimize(fitness_fn=fitness_fn, n_ants=n_ants, archive_size=archive_size, n_iter=n_iter)
    return res.to_dict()
