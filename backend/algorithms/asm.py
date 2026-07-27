"""
asm.py — Adaptive Strategy Metaheuristic (Navi Framework)
----------------------------------------------------------
Multi-strategy orchestration optimizer that coordinates existing BaseOptimizer
subclasses (GA, DE, PSO, GWO, ACO, SA) within a single optimization run.

Stage 4.0A delivers the orchestration infrastructure with configurable
switching schedules. Stage 4.0B will replace the manual schedule with an
adaptive decision engine. The ASM public API will not change.

Architecture
------------
- ASM inherits from BaseOptimizer, exposing the standard initialize/step/
  optimize/reset interface.
- ExperimentManager treats ASM identically to any other optimizer.
- Strategy instantiation is delegated to StrategyRegistry (no hardcoded
  optimizer imports).
- Strategy lifecycle is managed by ASMController (no direct access to
  optimizer internals).
- Global best solution is maintained independently by ASMController and
  injected into incoming optimizers on strategy switches.
- All ASM metadata is stored in PopulationState.metadata.

Configurable Switch Schedule
-----------------------------
The switch_schedule parameter defines evaluation-count thresholds at which
ASM transitions to a new strategy:

    switch_schedule = [
        ("GA",  40),
        ("PSO", 80),
        ("GWO", 120),
        ("SA",  160),
    ]

Interpretation: Run GA until 40 evaluations, then switch to PSO until 80
evaluations, then GWO until 120, then SA until budget exhaustion.

The schedule implementation is isolated so it can be replaced by an adaptive
controller without modifying the ASM public API.
"""

import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from algorithms.base import (
    BaseOptimizer,
    PopulationState,
    OptimizationResult,
)
from algorithms.strategy_registry import StrategyRegistry
from algorithms.operators.asm_controller import ASMController
from algorithms.operators.telemetry_engine import TelemetryEngine
from algorithms.operators.decision_engine import DecisionEngine


# ─────────────────────────────────────────────────────────────────────────────
# Default Switch Schedule
# ─────────────────────────────────────────────────────────────────────────────
DEFAULT_SWITCH_SCHEDULE: List[Tuple[str, int]] = [
    ("GA",  100),
    ("DE",  200),
    ("PSO", 300),
    ("GWO", 400),
    ("SA",  450),
    ("ACO", 500),
]
"""
Default schedule for fast-mode runs (budget=500). Each tuple is
(strategy_name, cumulative_evaluation_threshold). The final strategy
runs until budget exhaustion.
"""


# ─────────────────────────────────────────────────────────────────────────────
# ASM Optimizer
# ─────────────────────────────────────────────────────────────────────────────
class AdaptiveStrategyMetaheuristic(BaseOptimizer):
    """
    Adaptive Strategy Metaheuristic (ASM) optimizer.

    Orchestrates multiple BaseOptimizer strategies within a single optimization
    run, coordinating transitions via a configurable switch schedule.

    Stage 4.0A: Manual schedule-based switching.
    Stage 4.0B: Adaptive policy-based switching (future).

    Parameters
    ----------
    dim : int
        Search space dimensionality.
    bounds : Tuple[float, float]
        Parameter bounds (lower, upper).
    budget : int
        Maximum evaluation budget.
    pop_size : int
        Population size passed to sub-strategies.
    seed : int
        Random seed for deterministic execution.
    verbose : bool
        Console output verbosity.
    switch_schedule : Optional[List[Tuple[str, int]]]
        Strategy transition schedule as list of (name, eval_threshold) tuples.
        If None, uses DEFAULT_SWITCH_SCHEDULE.
    registry : Optional[StrategyRegistry]
        Custom strategy registry. If None, uses default registry.

    Lifecycle
    ---------
    1. initialize() — loads first strategy, initializes it, records state.
    2. step() — delegates to active optimizer; triggers switch if threshold reached.
    3. optimize() — full run loop with schedule-driven transitions.
    4. reset() — resets all internal state for a fresh run.
    5. export_state() — serializes complete ASM state including sub-optimizer states.
    6. restore_state() — restores ASM state from serialized dictionary.
    """

    def __init__(
        self,
        dim: int = 35,
        bounds: Tuple[float, float] = (0.0, 1.0),
        budget: int = 10000,
        pop_size: int = 30,
        seed: int = 42,
        verbose: bool = True,
        switch_schedule: Optional[List[Tuple[str, int]]] = None,
        registry: Optional[StrategyRegistry] = None,
        telemetry_window: int = 20,
        **kwargs: Any,
    ):
        super().__init__(
            name="ASM",
            dim=dim,
            bounds=bounds,
            budget=budget,
            seed=seed,
            verbose=verbose,
        )
        self.pop_size = pop_size

        # Schedule configuration
        if switch_schedule is not None:
            self._switch_schedule = list(switch_schedule)
        else:
            self._switch_schedule = self._auto_scale_schedule(budget)

        # Strategy registry and controller
        self._registry = registry if registry is not None else StrategyRegistry()
        self._controller = ASMController(
            registry=self._registry,
            dim=dim,
            bounds=bounds,
            budget=budget,
            pop_size=pop_size,
            seed=seed,
            verbose=verbose,
        )

        # Schedule tracking
        self._schedule_index: int = 0
        self._total_evaluations: int = 0

        # Telemetry Engine (Configurable Window Size)
        self.telemetry = TelemetryEngine(window_size=telemetry_window)

        # Decision Engine
        self.decision_engine = DecisionEngine()
        self.latest_recommendation = None

    # ─────────────────────────────────────────────────────────────────────────
    # Schedule Scaling
    # ─────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _auto_scale_schedule(budget: int) -> List[Tuple[str, int]]:
        """
        Generate a proportionally scaled switch schedule for the given budget.

        Divides budget equally across all six strategies, each receiving
        approximately 1/6 of total evaluations.

        Parameters
        ----------
        budget : int
            Total evaluation budget.

        Returns
        -------
        List[Tuple[str, int]]
            Scaled switch schedule.
        """
        strategies = ["GA", "DE", "PSO", "GWO", "SA", "ACO"]
        n = len(strategies)
        segment = budget // n
        schedule = []
        for i, name in enumerate(strategies):
            threshold = segment * (i + 1)
            schedule.append((name, threshold))
        return schedule

    # ─────────────────────────────────────────────────────────────────────────
    # BaseOptimizer Interface Implementation
    # ─────────────────────────────────────────────────────────────────────────
    def initialize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        pop_size: int = 30,
    ) -> PopulationState:
        """
        Initialize ASM by loading and initializing the first scheduled strategy.

        Parameters
        ----------
        fitness_fn : Callable
            Fitness evaluation function.
        pop_size : int
            Population size parameter.

        Returns
        -------
        PopulationState
            Initial population state from the first strategy.
        """
        self.pop_size = pop_size
        self._controller.pop_size = pop_size
        self._schedule_index = 0
        self._total_evaluations = 0
        self.start_time = time.time()

        # Load first strategy from schedule
        first_strategy, _ = self._switch_schedule[0]
        self._controller.load_optimizer(
            strategy_name=first_strategy,
            remaining_budget=self.budget,
        )
        state = self._controller.initialize_optimizer(fitness_fn, pop_size=pop_size)

        # Sync ASM-level counters
        self._sync_from_controller()
        self.state = state

        # Log initial state
        self.logger.start(initial_fitness=state.best_fitness)
        self._log_step()

        if self.verbose:
            print(
                f"  [ASM] Initialized with {first_strategy} | "
                f"Schedule: {[(s, t) for s, t in self._switch_schedule]}"
            )

        return state

    def step(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
    ) -> PopulationState:
        """
        Execute one iteration step of ASM.

        Delegates to the active sub-strategy optimizer. If the evaluation
        count crosses a scheduled threshold, triggers a strategy switch.

        Parameters
        ----------
        fitness_fn : Callable
            Fitness evaluation function.

        Returns
        -------
        PopulationState
            Updated population state.
        """
        if self._controller.active_optimizer is None:
            raise RuntimeError("ASM not initialized. Call initialize() first.")

        # Check if a strategy switch is needed BEFORE stepping
        self._check_and_switch(fitness_fn)

        # Delegate step to active optimizer
        state = self._controller.step_optimizer(fitness_fn)

        # Collect telemetry snapshot
        self.telemetry.collect(self._controller.active_optimizer)

        # Execute Decision Engine recommendation
        self.latest_recommendation = self.decision_engine.recommend(self.telemetry)

        # Sync ASM-level counters
        self._sync_from_controller()
        self.state = state
        self._log_step()

        return state

    def optimize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        pop_size: int = 30,
        iterations: int = 50,
    ) -> OptimizationResult:
        """
        Execute full ASM optimization run with schedule-driven transitions.

        Parameters
        ----------
        fitness_fn : Callable
            Fitness evaluation function.
        pop_size : int
            Population size.
        iterations : int
            Maximum iteration limit.

        Returns
        -------
        OptimizationResult
            Standardized optimization result.
        """
        self.reset()
        self.start_time = time.time()
        self.initialize(fitness_fn, pop_size=pop_size)

        for _ in range(iterations):
            if self.is_budget_exhausted():
                break
            self.step(fitness_fn)

        # Final evaluation for complete result dict
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
        """Reset all ASM state for a fresh optimization run."""
        super().reset()
        self._controller.reset()
        self._schedule_index = 0
        self._total_evaluations = 0
        self.telemetry.reset()
        self.decision_engine.reset()
        self.latest_recommendation = None

    # ─────────────────────────────────────────────────────────────────────────
    # State Accessors (Override for global best from controller)
    # ─────────────────────────────────────────────────────────────────────────
    def get_best_solution(self) -> np.ndarray:
        """Return the global best solution tracked by the ASM controller."""
        if self._controller.global_best_solution is not None:
            return self._controller.global_best_solution.copy()
        return super().get_best_solution()

    def get_population(self) -> np.ndarray:
        """Return the active sub-optimizer's current population."""
        if self._controller.active_optimizer is not None:
            return self._controller.active_optimizer.get_population()
        return super().get_population()

    # ─────────────────────────────────────────────────────────────────────────
    # ASM State Serialization
    # ─────────────────────────────────────────────────────────────────────────
    def export_state(self) -> Dict[str, Any]:
        """
        Export complete ASM state including controller state, schedule
        progress, and all sub-optimizer states.

        Returns
        -------
        Dict[str, Any]
            Serialized ASM state dictionary.
        """
        controller_state = self._controller.export_controller_state()

        return {
            "name": self.name,
            "generation": self.generation,
            "evaluations_used": self.evaluations_used,
            "schedule_index": self._schedule_index,
            "total_evaluations": self._total_evaluations,
            "switch_schedule": [
                {"strategy": s, "threshold": t} for s, t in self._switch_schedule
            ],
            "controller_state": controller_state,
            "population_state": self.state.copy() if self.state else None,
            "history": self.get_history(),
            "telemetry_history": [s.to_dict() for s in self.telemetry.history()],
            "recommendation_history": [
                {
                    "recommended_optimizer": r.recommended_optimizer,
                    "optimizer_scores": r.optimizer_scores,
                    "exploration_need": r.exploration_need,
                    "exploitation_need": r.exploitation_need,
                    "escape_need": r.escape_need,
                    "confidence": r.confidence,
                    "explanation": r.explanation,
                }
                for r in self.decision_engine.history()
            ],
        }

    def restore_state(self, state_dict: Dict[str, Any]) -> None:
        """
        Restore ASM state from a serialized dictionary.

        Parameters
        ----------
        state_dict : Dict[str, Any]
            Previously exported ASM state dictionary.
        """
        if not state_dict:
            return

        self.generation = state_dict.get("generation", 0)
        self.evaluations_used = state_dict.get("evaluations_used", 0)
        self._schedule_index = state_dict.get("schedule_index", 0)
        self._total_evaluations = state_dict.get("total_evaluations", 0)

        pop_state = state_dict.get("population_state")
        if isinstance(pop_state, PopulationState):
            self.state = pop_state.copy()

        if "telemetry_history" in state_dict:
            from algorithms.operators.telemetry_engine import TelemetrySnapshot
            self.telemetry._history = [TelemetrySnapshot(**s) for s in state_dict["telemetry_history"]]

        if "recommendation_history" in state_dict:
            from algorithms.operators.decision_engine import Recommendation
            self.decision_engine._history = [
                Recommendation(**r) for r in state_dict["recommendation_history"]
            ]
            if self.decision_engine._history:
                self.latest_recommendation = self.decision_engine._history[-1]

        # Restore controller global best
        ctrl = state_dict.get("controller_state", {})
        if ctrl.get("global_best_solution") is not None:
            self._controller.global_best_solution = np.array(
                ctrl["global_best_solution"], dtype=float
            )
            self._controller.global_best_fitness = float(
                ctrl.get("global_best_fitness", -np.inf)
            )

    # ─────────────────────────────────────────────────────────────────────────
    # ASM Metadata for PopulationState
    # ─────────────────────────────────────────────────────────────────────────
    def _build_asm_metadata(self) -> Dict[str, Any]:
        """
        Build ASM-specific metadata for PopulationState.metadata.

        Stores all ASM orchestration state: current strategy, switch history,
        global best, runtimes, and sub-optimizer states.
        """
        return {
            "current_strategy": self._controller.active_strategy_name,
            "strategy_history": [
                t.to_dict() for t in self._controller.transition_history
            ],
            "strategy_switches": self._controller.switch_count,
            "strategy_runtime": self._controller.get_strategy_runtimes(),
            "global_best_solution": (
                self._controller.global_best_solution.tolist()
                if self._controller.global_best_solution is not None
                else None
            ),
            "global_best_fitness": float(self._controller.global_best_fitness),
            "remaining_budget": max(0, self.budget - self._total_evaluations),
            "elapsed_time": time.time() - self.start_time if self.start_time > 0 else 0.0,
            "schedule_index": self._schedule_index,
            "switch_schedule": [
                {"strategy": s, "threshold": t} for s, t in self._switch_schedule
            ],
        }

    # ─────────────────────────────────────────────────────────────────────────
    # Private: Schedule-Driven Switching
    # ─────────────────────────────────────────────────────────────────────────
    def _check_and_switch(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
    ) -> None:
        """
        Check if the current evaluation count has crossed the next scheduled
        threshold and trigger a strategy switch if needed.

        This method is the sole switching trigger in Stage 4.0A. In Stage 4.0B,
        this will be augmented or replaced by an adaptive decision policy
        without changing the ASM public API.
        """
        # Already past the last schedule entry -- continue with final strategy
        if self._schedule_index >= len(self._switch_schedule) - 1:
            return

        _, current_threshold = self._switch_schedule[self._schedule_index]

        if self._total_evaluations >= current_threshold:
            # Advance to next scheduled strategy
            self._schedule_index += 1
            next_strategy, _ = self._switch_schedule[self._schedule_index]
            remaining = max(0, self.budget - self._total_evaluations)

            if remaining <= 0:
                return

            self._controller.switch_strategy(
                new_strategy_name=next_strategy,
                fitness_fn=fitness_fn,
                remaining_budget=remaining,
                reason="schedule",
            )

    def _sync_from_controller(self) -> None:
        """
        Synchronize ASM-level evaluation counters and state from the active
        sub-optimizer via the controller.
        """
        opt = self._controller.active_optimizer
        if opt is None:
            return

        self._total_evaluations = self._compute_total_evaluations()
        self.evaluations_used = self._total_evaluations
        self.generation += 1

        # Update PopulationState metadata with ASM info
        if self.state is not None:
            self.state.metadata.update(self._build_asm_metadata())

    def _compute_total_evaluations(self) -> int:
        """
        Compute total evaluations across all strategy phases.

        Sums evaluations from archived optimizer states plus the active
        optimizer's current evaluation count.
        """
        total = 0
        # Sum evaluations from all archived states
        for name, state_dict in self._controller.optimizer_states.items():
            if name != self._controller.active_strategy_name:
                total += state_dict.get("evaluations_used", 0)

        # Add active optimizer's current evaluations
        if self._controller.active_optimizer is not None:
            total += self._controller.active_optimizer.evaluations_used

        return total

    def _log_step(self) -> None:
        """Log current step metrics via ExecutionLogger."""
        if self.state is None:
            return

        pop_fitness = self.state.fitness
        diversity = float(np.std(pop_fitness)) if len(pop_fitness) > 1 else 0.0

        self.logger.log_step(
            generation=self.generation,
            evaluation_count=self._total_evaluations,
            best_fitness=float(self._controller.global_best_fitness),
            mean_fitness=float(np.mean(pop_fitness)),
            worst_fitness=float(np.min(pop_fitness)),
            diversity_index=diversity,
            print_interval=1,
        )

        # Print Decision Engine recommendations if verbose
        if self.verbose and hasattr(self, "latest_recommendation") and self.latest_recommendation is not None:
            rec = self.latest_recommendation
            print(
                f"  [Decision Engine] Rec: {rec.recommended_optimizer} | "
                f"Needs (Explr={rec.exploration_need:.2f}, Explt={rec.exploitation_need:.2f}, Esc={rec.escape_need:.2f}) | "
                f"Confidence: {rec.confidence:.2f} | "
                f"Explanation: {rec.explanation}"
            )


# ─────────────────────────────────────────────────────────────────────────────
# Backward-Compatible Wrapper Function
# ─────────────────────────────────────────────────────────────────────────────
def run_asm(
    csv_path: str = "vanet.csv",
    pop_size: int = 30,
    n_gen: int = 50,
    seed: int = 42,
    switch_schedule: Optional[List[Tuple[str, int]]] = None,
) -> dict:
    """
    Backward-compatible wrapper function for ASM.

    Preserves function signature pattern expected by main.py.

    Parameters
    ----------
    csv_path : str
        Path to VANET telemetry dataset.
    pop_size : int
        Population size.
    n_gen : int
        Maximum generations/iterations.
    seed : int
        Random seed.
    switch_schedule : Optional[List[Tuple[str, int]]]
        Custom switch schedule. If None, auto-scales to budget.

    Returns
    -------
    dict
        Standardized result dictionary.
    """
    from evaluation.fitness import evaluate_fitness

    budget = pop_size * n_gen

    def fitness_fn(cand):
        return evaluate_fitness(cand, csv_path=csv_path, seed=seed)

    asm = AdaptiveStrategyMetaheuristic(
        pop_size=pop_size,
        budget=budget,
        seed=seed,
        verbose=True,
        switch_schedule=switch_schedule,
    )

    res = asm.optimize(fitness_fn=fitness_fn, pop_size=pop_size, iterations=n_gen)
    
    # Telemetry Snapshot count validation check
    num_snapshots = len(asm.telemetry.history())
    num_steps = asm.generation
    print(f"\n  [Telemetry Validation] Snapshots: {num_snapshots} | Steps: {num_steps} | Match: {num_snapshots == num_steps}\n")

    return res.to_dict()
