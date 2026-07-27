"""
optimizer.py
------------
Abstract Base Optimizer class for the Navi optimization framework.

Defines the reusable architectural contract, budget management, random seed
control, evaluation accounting, state export/restore, and logging hooks
inherited by all current and future optimization algorithms (GA, PSO, GWO, DE,
ACO, SA, and ASM).
"""

from abc import ABC, abstractmethod
import time
from typing import Any, Callable, Dict, List, Optional, Tuple
import numpy as np

from .types import (
    IterationMetrics,
    OptimizationResult,
    OptimizerStatistics,
    PopulationState,
)
from .logger import ExecutionLogger


class BaseOptimizer(ABC):
    """
    Abstract Base Class for all Navi metaheuristic optimizers.

    Responsibilities
    ----------------
    1. Encapsulate common search state (budget, evaluations, bounds, seed, RNG).
    2. Manage population evaluation tracking and deterministic seed sequences.
    3. Expose standard lifecycle operations: initialize(), step(), optimize(), reset().
    4. Provide state serialization (export_state / restore_state) for ASM strategy switching.
    5. Maintain convergence history and timing analytics.

    Future Extension Points & ASM Interaction
    -----------------------------------------
    - Step-Level Control: ASM calls step() on active strategy to advance search by 1 iteration.
    - Diversity Feedback: ASM queries get_population() to calculate spatial entropy.
    - Strategy Switching: ASM exports state from current strategy and restores into target.
    """

    def __init__(
        self,
        name: str = "BaseOptimizer",
        dim: int = 35,
        bounds: Tuple[float, float] = (0.0, 1.0),
        budget: int = 10000,
        seed: int = 42,
        verbose: bool = True,
    ):
        self.name = name
        self.dim = dim
        self.bounds = bounds
        self.budget = budget
        self.seed = seed
        self.verbose = verbose

        self.rng = np.random.default_rng(seed)
        self.evaluations_used: int = 0
        self.generation: int = 0
        self.start_time: float = 0.0
        
        self.state: Optional[PopulationState] = None
        self.logger = ExecutionLogger(algorithm_name=name, seed=seed, verbose=verbose)

    # ─────────────────────────────────────────────────────────────────────────
    # Core Evaluation Infrastructure
    # ─────────────────────────────────────────────────────────────────────────
    def evaluate_candidate(
        self,
        candidate: np.ndarray,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
    ) -> Tuple[float, Dict[str, Any]]:
        """
        Evaluate a single candidate parameter vector using the fitness function.

        Enforces boundary clipping, updates evaluation counter, and checks budget limits.
        """
        clipped = np.clip(candidate, self.bounds[0], self.bounds[1])
        fitness, result_dict = fitness_fn(clipped)
        self.evaluations_used += 1
        return float(fitness), result_dict

    def evaluate_population(
        self,
        population: np.ndarray,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
    ) -> np.ndarray:
        """
        Evaluate an entire population matrix of shape (P, D).

        Returns numpy array of fitness scores of shape (P,).
        """
        scores = []
        for ind in population:
            f, _ = self.evaluate_candidate(ind, fitness_fn)
            scores.append(f)
        return np.array(scores, dtype=float)

    def is_budget_exhausted(self) -> bool:
        """Check whether the function evaluation budget limit has been reached."""
        return self.evaluations_used >= self.budget

    # ─────────────────────────────────────────────────────────────────────────
    # Public Abstract Interface Contract
    # ─────────────────────────────────────────────────────────────────────────
    @abstractmethod
    def initialize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        pop_size: int = 30,
    ) -> PopulationState:
        """
        Initialize population state, evaluate initial candidates, and setup structures.

        Must set self.state and reset evaluations_used and generation counters.
        """
        pass

    @abstractmethod
    def step(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
    ) -> PopulationState:
        """
        Execute a single iteration/generation step of the optimization algorithm.

        Advances self.generation by 1 and updates self.state.
        """
        pass

    def optimize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        pop_size: int = 30,
        iterations: int = 50,
    ) -> OptimizationResult:
        """
        Execute full optimization run up to max iterations or budget exhaustion.

        Default infrastructure implementation calling initialize() and step() in loop.
        Algorithm sub-classes may override if specialized workflow is required.
        """
        self.reset()
        self.start_time = time.time()
        self.initialize(fitness_fn, pop_size=pop_size)
        self.logger.start(initial_fitness=self.state.best_fitness)

        for _ in range(iterations):
            if self.is_budget_exhausted():
                break
            self.step(fitness_fn)

        # Final evaluation to retrieve full simulation dict
        best_solution = self.get_best_solution()
        best_fitness, best_result = fitness_fn(best_solution)

        stats = self.get_statistics()
        
        return OptimizationResult(
            algorithm=self.name,
            best_solution=best_solution,
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

    def reset(self) -> None:
        """Reset random number generator, evaluation counter, and state."""
        self.rng = np.random.default_rng(self.seed)
        self.evaluations_used = 0
        self.generation = 0
        self.state = None
        self.start_time = 0.0

    # ─────────────────────────────────────────────────────────────────────────
    # State & Inspection Accessors
    # ─────────────────────────────────────────────────────────────────────────
    def get_best_solution(self) -> np.ndarray:
        """Return parameter vector of current global best candidate."""
        if self.state is None:
            raise RuntimeError("Optimizer not initialized. Call initialize() first.")
        return self.state.best_solution.copy()

    def get_population(self) -> np.ndarray:
        """Return position matrix of current active population."""
        if self.state is None:
            raise RuntimeError("Optimizer not initialized. Call initialize() first.")
        return self.state.population.copy()

    def get_statistics(self) -> OptimizerStatistics:
        """Return runtime statistics object from logger."""
        return self.logger.get_statistics()

    def get_history(self) -> List[float]:
        """Return best-fitness convergence history array."""
        return [m.best_fitness for m in self.logger.metrics_history]

    # ─────────────────────────────────────────────────────────────────────────
    # ASM State Serialization (Export & Restore)
    # ─────────────────────────────────────────────────────────────────────────
    def export_state(self) -> Dict[str, Any]:
        """
        Export complete internal search state dictionary.

        Used by Adaptive Strategy Metaheuristic (ASM) to capture state before switching.
        """
        if self.state is None:
            return {}
        return {
            "name": self.name,
            "generation": self.generation,
            "evaluations_used": self.evaluations_used,
            "population_state": self.state.copy(),
            "history": self.get_history(),
        }

    def restore_state(self, state_dict: Dict[str, Any]) -> None:
        """
        Restore internal search state from dictionary.

        Used by Adaptive Strategy Metaheuristic (ASM) to inject population state into strategy.
        """
        if not state_dict:
            return
        self.generation = state_dict.get("generation", 0)
        self.evaluations_used = state_dict.get("evaluations_used", 0)
        pop_state = state_dict.get("population_state")
        if isinstance(pop_state, PopulationState):
            self.state = pop_state.copy()
