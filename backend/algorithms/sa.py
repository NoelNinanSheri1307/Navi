"""
sa.py — Simulated Annealing (Navi Trajectory Optimizer Architecture)
----------------------------------------------------------------------
Standard Metropolis-Hastings Simulated Annealing (Kirkpatrick et al., 1983)
with Gaussian perturbation neighbor generation and geometric temperature cooling.

Refactored to inherit from BaseOptimizer as Navi's reference trajectory optimizer.
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
    SANeighborGenerator,
    SATemperatureSchedule,
    SAAcceptanceCriterion,
)

DIM = 35


class SimulatedAnnealingOptimizer(BaseOptimizer):
    """
    Simulated Annealing Kernel.

    Responsibilities
    ----------------
    1. Single-trajectory stochastic global search over [0,1]^35 fuzzy parameter space.
    2. Modular operator delegation (Neighbor Generation, Geometric Cooling, Metropolis Acceptance).
    3. Iterative state-machine lifecycle via initialize() and step().
    4. Trajectory telemetry recording (temperature, acceptance probability, improvements).

    ASM & Framework Integration
    ---------------------------
    - Step-Level Control: ASM can pause after any single annealing step.
    - Persistent Trajectory State: Current solution vector, current score, best solution, and temperature stored in PopulationState.metadata.
    - State Serialization: Export and restore trajectory state across strategy switches.
    """

    def __init__(
        self,
        dim: int = DIM,
        bounds: Tuple[float, float] = (0.0, 1.0),
        budget: int = 10000,
        t_init: float = 1.0,
        cooling_rate: float = 0.95,
        step_size: float = 0.05,
        pop_size: Optional[int] = None,
        seed: int = 42,
        verbose: bool = True,
    ):
        super().__init__(
            name="SA",
            dim=dim,
            bounds=bounds,
            budget=budget,
            seed=seed,
            verbose=verbose,
        )
        self.t_init = t_init
        self.cooling_rate = cooling_rate
        self.step_size = step_size

        # Operators
        self.neighbor_op = SANeighborGenerator(bounds=bounds, step_size=step_size)
        self.temperature_op = SATemperatureSchedule(t_init=t_init, cooling_rate=cooling_rate)
        self.acceptance_op = SAAcceptanceCriterion()

        # Trajectory State Tensors
        self.current_solution: Optional[np.ndarray] = None
        self.current_score: float = -np.inf
        self.best_solution: Optional[np.ndarray] = None
        self.best_score: float = -np.inf
        self.temperature: float = t_init
        self.iterations_since_improvement: int = 0
        self.accepted_moves_count: int = 0

    def initialize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        t_init: Optional[float] = None,
        pop_size: Optional[int] = None,
    ) -> PopulationState:
        """
        Initialize uniform random single trajectory solution and reset temperature state.
        """
        if t_init is not None:
            self.t_init = t_init

        self.reset()
        self.temperature = self.t_init
        self.iterations_since_improvement = 0
        self.accepted_moves_count = 0

        # Trajectory sampling over [0, 1]^35
        self.current_solution = self.rng.uniform(self.bounds[0], self.bounds[1], self.dim)
        self.current_score, _ = self.evaluate_candidate(self.current_solution, fitness_fn)

        self.best_solution = self.current_solution.copy()
        self.best_score = float(self.current_score)

        # Encapsulate single-particle matrix for framework population compliance
        pop_matrix = np.expand_dims(self.current_solution, axis=0)
        fitness_arr = np.array([self.current_score], dtype=float)

        self.state = PopulationState(
            population=pop_matrix,
            fitness=fitness_arr,
            best_solution=self.best_solution.copy(),
            best_fitness=self.best_score,
            evaluation_count=self.evaluations_used,
            generation=0,
            metadata={
                "current_solution": self.current_solution.copy(),
                "current_score": self.current_score,
                "best_solution": self.best_solution.copy(),
                "best_score": self.best_score,
                "temperature": self.temperature,
                "acceptance_rate": 1.0,
                "cooling_rate": self.cooling_rate,
                "iterations_since_improvement": 0,
            },
        )

        return self.state

    def step(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
    ) -> PopulationState:
        """
        Execute exactly one iteration step of Simulated Annealing.
        """
        if self.state is None or self.current_solution is None:
            raise RuntimeError("Optimizer not initialized. Call initialize() first.")

        # 1. Generate neighbor solution
        neighbor = self.neighbor_op.generate_neighbor(self.current_solution, self.rng)

        # 2. Evaluate neighbor
        neighbor_score, _ = self.evaluate_candidate(neighbor, fitness_fn)
        delta_fitness = neighbor_score - self.current_score

        # 3. Metropolis acceptance decision
        accepted, prob = self.acceptance_op.accept_move(
            delta_fitness=delta_fitness,
            temperature=self.temperature,
            rng=self.rng,
        )

        is_improving = False
        if accepted:
            self.current_solution = neighbor.copy()
            self.current_score = float(neighbor_score)
            self.accepted_moves_count += 1

            if self.current_score > self.best_score:
                self.best_solution = self.current_solution.copy()
                self.best_score = float(self.current_score)
                self.iterations_since_improvement = 0
                is_improving = True
            else:
                self.iterations_since_improvement += 1
        else:
            self.iterations_since_improvement += 1

        # 4. Geometric temperature cooling
        self.temperature = self.temperature_op.cool(self.temperature)
        self.generation += 1

        acc_rate = float(self.accepted_moves_count / self.generation)
        pop_matrix = np.expand_dims(self.current_solution, axis=0)
        fitness_arr = np.array([self.current_score], dtype=float)

        self.state = PopulationState(
            population=pop_matrix,
            fitness=fitness_arr,
            best_solution=self.best_solution.copy(),
            best_fitness=self.best_score,
            evaluation_count=self.evaluations_used,
            generation=self.generation,
            metadata={
                "current_solution": self.current_solution.copy(),
                "current_score": self.current_score,
                "best_solution": self.best_solution.copy(),
                "best_score": self.best_score,
                "temperature": self.temperature,
                "acceptance_rate": acc_rate,
                "acceptance_prob": prob,
                "accepted_move": accepted,
                "improving_move": is_improving,
                "cooling_rate": self.cooling_rate,
                "iterations_since_improvement": self.iterations_since_improvement,
            },
        )

        # Telemetry logging
        self.logger.log_step(
            generation=self.generation,
            evaluation_count=self.evaluations_used,
            best_fitness=self.best_score,
            mean_fitness=self.current_score,
            worst_fitness=self.current_score,
            diversity_index=0.0,
        )

        return self.state

    def optimize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        n_iter: int = 50,
        **kwargs,
    ) -> OptimizationResult:
        """
        Execute full trajectory annealing run.
        """
        self.initialize(fitness_fn)
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
        """Export state dictionary including trajectory state tensors."""
        base_state = super().export_state()
        if self.current_solution is not None:
            base_state["current_solution"] = self.current_solution.copy()
            base_state["current_score"] = self.current_score
            base_state["best_solution"] = self.best_solution.copy()
            base_state["best_score"] = self.best_score
            base_state["temperature"] = self.temperature
            base_state["iterations_since_improvement"] = self.iterations_since_improvement
        return base_state

    def restore_state(self, state_dict: Dict[str, Any]) -> None:
        """Restore search state including trajectory tensors."""
        super().restore_state(state_dict)
        if "current_solution" in state_dict:
            self.current_solution = state_dict["current_solution"].copy()
            self.current_score = state_dict.get("current_score", -np.inf)
            self.best_solution = state_dict.get("best_solution", self.current_solution).copy()
            self.best_score = state_dict.get("best_score", self.current_score)
            self.temperature = state_dict.get("temperature", self.t_init)
            self.iterations_since_improvement = state_dict.get("iterations_since_improvement", 0)


# ─────────────────────────────────────────────────────────────────────────────
# Backward-Compatible Wrapper Function
# ─────────────────────────────────────────────────────────────────────────────
def run_sa(
    csv_path: str = "vanet.csv",
    t_init: float = 1.0,
    cooling_rate: float = 0.95,
    step_size: float = 0.05,
    n_iter: int = 50,
    seed: int = 42,
) -> dict:
    """
    Backward-compatible wrapper function for Simulated Annealing.

    Preserves function signature expected by main.py, run_algo_graphs.py, and external callers.
    """
    def fitness_fn(cand):
        return evaluate_fitness(cand, csv_path=csv_path, seed=seed)

    sa = SimulatedAnnealingOptimizer(
        t_init=t_init,
        cooling_rate=cooling_rate,
        step_size=step_size,
        seed=seed,
        verbose=True,
    )

    res = sa.optimize(fitness_fn=fitness_fn, n_iter=n_iter)
    return res.to_dict()
