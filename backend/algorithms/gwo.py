"""
gwo.py — Grey Wolf Optimizer (Navi Hierarchical Swarm Architecture)
---------------------------------------------------------------------
Standard Grey Wolf Optimizer (Mirjalili et al., 2014) with alpha, beta, and
delta leadership hierarchy and linear adaptive parameter decay a(t).

Refactored to inherit from BaseOptimizer as Navi's reference hierarchical optimizer.
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
    GWOLeadership,
    GWOEncircling,
    GWOPositionUpdate,
)

DIM = 35


class GreyWolfOptimizer(BaseOptimizer):
    """
    Grey Wolf Optimizer Kernel.

    Responsibilities
    ----------------
    1. Continuous global optimization over [0,1]^35 fuzzy parameter space.
    2. Modular operator delegation (Leadership Hierarchy, Encircling Vectors, Position Updates).
    3. Iterative state-machine lifecycle via initialize() and step().
    4. Hierarchical telemetry recording (Alpha, Beta, Delta fitness & adaptive decay parameter a).

    ASM & Framework Integration
    ---------------------------
    - Step-Level Control: ASM can pause after any iteration step.
    - Hierarchical State: Alpha, Beta, Delta positions and scores stored in PopulationState.metadata.
    - State Serialization: Export and restore hierarchy state across strategy switches.
    """

    def __init__(
        self,
        dim: int = DIM,
        bounds: Tuple[float, float] = (0.0, 1.0),
        budget: int = 10000,
        n_wolves: int = 30,
        pop_size: Optional[int] = None,
        seed: int = 42,
        verbose: bool = True,
    ):
        super().__init__(
            name="GWO",
            dim=dim,
            bounds=bounds,
            budget=budget,
            seed=seed,
            verbose=verbose,
        )
        self.n_wolves = pop_size if pop_size is not None else n_wolves
        self.total_iters = 50

        # Operators
        self.leadership = GWOLeadership()
        self.encircling = GWOEncircling()
        self.position_operator = GWOPositionUpdate(bounds=bounds)

        # Hierarchy Tensors
        self.alpha_pos: Optional[np.ndarray] = None
        self.alpha_score: float = -np.inf
        self.beta_pos: Optional[np.ndarray] = None
        self.beta_score: float = -np.inf
        self.delta_pos: Optional[np.ndarray] = None
        self.delta_score: float = -np.inf

    def initialize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        n_wolves: Optional[int] = None,
        pop_size: Optional[int] = None,
    ) -> PopulationState:
        """
        Initialize uniform random wolf pack, evaluate fitness, and extract leaders.
        """
        w_count = pop_size if pop_size is not None else n_wolves
        if w_count is not None:
            self.n_wolves = w_count

        self.reset()

        # Position sampling over [0, 1]^35
        wolves = self.rng.uniform(self.bounds[0], self.bounds[1], (self.n_wolves, self.dim))
        scores = self.evaluate_population(wolves, fitness_fn)

        # Extract Alpha, Beta, Delta leaders
        (
            self.alpha_pos,
            self.alpha_score,
            self.beta_pos,
            self.beta_score,
            self.delta_pos,
            self.delta_score,
        ) = self.leadership.identify_leaders(wolves, scores)

        self.state = PopulationState(
            population=wolves,
            fitness=scores,
            best_solution=self.alpha_pos.copy(),
            best_fitness=self.alpha_score,
            evaluation_count=self.evaluations_used,
            generation=0,
            metadata={
                "alpha_position": self.alpha_pos.copy(),
                "alpha_score": self.alpha_score,
                "beta_position": self.beta_pos.copy(),
                "beta_score": self.beta_score,
                "delta_position": self.delta_pos.copy(),
                "delta_score": self.delta_score,
                "a_parameter": 2.0,
            },
        )

        return self.state

    def step(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
    ) -> PopulationState:
        """
        Execute exactly one iteration step of Grey Wolf Optimizer.
        """
        if self.state is None or self.alpha_pos is None:
            raise RuntimeError("Optimizer not initialized. Call initialize() first.")

        wolves = self.state.population
        a_param = self.encircling.compute_adaptive_a(self.generation, self.total_iters)

        # Update each wolf position based on leadership vectors
        new_wolves = np.zeros_like(wolves)
        for i in range(self.n_wolves):
            _, X1 = self.encircling.calculate_leader_distances(
                wolf_position=wolves[i],
                leader_position=self.alpha_pos,
                a_param=a_param,
                rng=self.rng,
            )

            _, X2 = self.encircling.calculate_leader_distances(
                wolf_position=wolves[i],
                leader_position=self.beta_pos,
                a_param=a_param,
                rng=self.rng,
            )

            _, X3 = self.encircling.calculate_leader_distances(
                wolf_position=wolves[i],
                leader_position=self.delta_pos,
                a_param=a_param,
                rng=self.rng,
            )

            new_wolves[i] = self.position_operator.update_position(X1, X2, X3)

        # Evaluate new positions
        scores = self.evaluate_population(new_wolves, fitness_fn)

        # Update historical leaders
        (
            self.alpha_pos,
            self.alpha_score,
            self.beta_pos,
            self.beta_score,
            self.delta_pos,
            self.delta_score,
        ) = self.leadership.update_leaders(
            population=new_wolves,
            scores=scores,
            alpha_pos=self.alpha_pos,
            alpha_score=self.alpha_score,
            beta_pos=self.beta_pos,
            beta_score=self.beta_score,
            delta_pos=self.delta_pos,
            delta_score=self.delta_score,
        )

        self.generation += 1
        diversity = float(np.mean(np.std(new_wolves, axis=0)))

        # Update state
        self.state = PopulationState(
            population=new_wolves,
            fitness=scores,
            best_solution=self.alpha_pos.copy(),
            best_fitness=self.alpha_score,
            evaluation_count=self.evaluations_used,
            generation=self.generation,
            metadata={
                "alpha_position": self.alpha_pos.copy(),
                "alpha_score": self.alpha_score,
                "beta_position": self.beta_pos.copy(),
                "beta_score": self.beta_score,
                "delta_position": self.delta_pos.copy(),
                "delta_score": self.delta_score,
                "a_parameter": a_param,
                "diversity": diversity,
            },
        )

        # Telemetry logging
        self.logger.log_step(
            generation=self.generation,
            evaluation_count=self.evaluations_used,
            best_fitness=self.alpha_score,
            mean_fitness=float(np.mean(scores)),
            worst_fitness=float(np.min(scores)),
            diversity_index=diversity,
        )

        return self.state

    def optimize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        n_wolves: Optional[int] = None,
        n_iter: int = 50,
    ) -> OptimizationResult:
        """
        Execute full wolf pack optimization run.
        """
        self.total_iters = n_iter
        w_count = n_wolves if n_wolves is not None else self.n_wolves
        self.initialize(fitness_fn, n_wolves=w_count)
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
        """Export state dictionary including leadership hierarchy tensors."""
        base_state = super().export_state()
        if self.alpha_pos is not None:
            base_state["alpha_position"] = self.alpha_pos.copy()
            base_state["alpha_score"] = self.alpha_score
        if self.beta_pos is not None:
            base_state["beta_position"] = self.beta_pos.copy()
            base_state["beta_score"] = self.beta_score
        if self.delta_pos is not None:
            base_state["delta_position"] = self.delta_pos.copy()
            base_state["delta_score"] = self.delta_score
        return base_state

    def restore_state(self, state_dict: Dict[str, Any]) -> None:
        """Restore search state including leadership hierarchy tensors."""
        super().restore_state(state_dict)
        if "alpha_position" in state_dict:
            self.alpha_pos = state_dict["alpha_position"].copy()
            self.alpha_score = state_dict.get("alpha_score", -np.inf)
        if "beta_position" in state_dict:
            self.beta_pos = state_dict["beta_position"].copy()
            self.beta_score = state_dict.get("beta_score", -np.inf)
        if "delta_position" in state_dict:
            self.delta_pos = state_dict["delta_position"].copy()
            self.delta_score = state_dict.get("delta_score", -np.inf)


# ─────────────────────────────────────────────────────────────────────────────
# Backward-Compatible Wrapper Function
# ─────────────────────────────────────────────────────────────────────────────
def run_gwo(
    csv_path: str = "vanet.csv",
    n_wolves: int = 30,
    n_iter: int = 50,
    seed: int = 42,
) -> dict:
    """
    Backward-compatible wrapper function for Grey Wolf Optimizer.

    Preserves function signature expected by main.py, run_algo_graphs.py, and external callers.
    """
    def fitness_fn(cand):
        return evaluate_fitness(cand, csv_path=csv_path, seed=seed)

    gwo = GreyWolfOptimizer(
        n_wolves=n_wolves,
        seed=seed,
        verbose=True,
    )

    res = gwo.optimize(fitness_fn=fitness_fn, n_wolves=n_wolves, n_iter=n_iter)
    return res.to_dict()
