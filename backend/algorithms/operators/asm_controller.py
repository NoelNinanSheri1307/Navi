"""
asm_controller.py
------------------
ASM Controller for the Navi optimization framework.

Manages the lifecycle of sub-strategy optimizers within an ASM run:
loading, initializing, stepping, exporting state, restoring state,
switching between strategies, and tracking execution history.

Design Principles
-----------------
- Never accesses optimizer internals directly.
- Interacts only through the public BaseOptimizer interface:
  initialize(), step(), export_state(), restore_state(),
  get_best_solution(), get_population(), is_budget_exhausted().
- Maintains a complete history of strategy transitions.
- Preserves global best solution independently of individual optimizers.

Future Extension Points
-----------------------
- The switch_strategy() method is called by ASM whenever a transition is
  needed. Currently ASM triggers this from a configurable schedule.
  In Stage 4.0B, ASM will trigger it from an adaptive decision engine.
  The controller interface remains unchanged.
"""

import time
from typing import Any, Callable, Dict, List, Optional, Tuple

import numpy as np

from algorithms.base import BaseOptimizer, PopulationState
from algorithms.strategy_registry import StrategyRegistry


# ─────────────────────────────────────────────────────────────────────────────
# Strategy Transition Record
# ─────────────────────────────────────────────────────────────────────────────
class StrategyTransition:
    """
    Immutable record of a single strategy switch event.

    Attributes
    ----------
    from_strategy : str
        Name of the outgoing strategy (empty string for the initial load).
    to_strategy : str
        Name of the incoming strategy.
    evaluation_count : int
        Total evaluations at the moment of the switch.
    timestamp : float
        Wall-clock time of the switch event.
    reason : str
        Explanation for the switch (e.g. 'schedule', 'stagnation').
    fitness_at_switch : float
        Global best fitness at the moment of the switch.
    """

    __slots__ = (
        "from_strategy", "to_strategy", "evaluation_count",
        "timestamp", "reason", "fitness_at_switch",
    )

    def __init__(
        self,
        from_strategy: str,
        to_strategy: str,
        evaluation_count: int,
        timestamp: float,
        reason: str,
        fitness_at_switch: float,
    ):
        self.from_strategy = from_strategy
        self.to_strategy = to_strategy
        self.evaluation_count = evaluation_count
        self.timestamp = timestamp
        self.reason = reason
        self.fitness_at_switch = fitness_at_switch

    def to_dict(self) -> Dict[str, Any]:
        """Serialize transition record to dictionary."""
        return {
            "from_strategy": self.from_strategy,
            "to_strategy": self.to_strategy,
            "evaluation_count": self.evaluation_count,
            "timestamp": self.timestamp,
            "reason": self.reason,
            "fitness_at_switch": self.fitness_at_switch,
        }


# ─────────────────────────────────────────────────────────────────────────────
# ASM Controller
# ─────────────────────────────────────────────────────────────────────────────
class ASMController:
    """
    Manages sub-strategy optimizer lifecycle within an ASM optimization run.

    Responsibilities
    ----------------
    1. Load optimizer via StrategyRegistry.create().
    2. Initialize optimizer and delegate step() calls.
    3. Export and restore optimizer state on strategy switches.
    4. Maintain global best solution independently of active optimizer.
    5. Track complete strategy transition history.
    6. Report execution telemetry (strategy runtimes, switch counts).

    Interface Contract
    ------------------
    The controller never accesses optimizer internals. All interaction flows
    through the public BaseOptimizer API.
    """

    def __init__(
        self,
        registry: StrategyRegistry,
        dim: int = 35,
        bounds: Tuple[float, float] = (0.0, 1.0),
        budget: int = 10000,
        pop_size: int = 30,
        seed: int = 42,
        verbose: bool = True,
    ):
        self.registry = registry
        self.dim = dim
        self.bounds = bounds
        self.budget = budget
        self.pop_size = pop_size
        self.seed = seed
        self.verbose = verbose

        # Active optimizer state
        self.active_optimizer: Optional[BaseOptimizer] = None
        self.active_strategy_name: str = ""
        self.strategy_start_time: float = 0.0

        # Global best tracking (independent of individual optimizers)
        self.global_best_solution: Optional[np.ndarray] = None
        self.global_best_fitness: float = -np.inf

        # History and telemetry
        self.transition_history: List[StrategyTransition] = []
        self.strategy_runtimes: Dict[str, float] = {}
        self.optimizer_states: Dict[str, Dict[str, Any]] = {}
        self.switch_count: int = 0

    def load_optimizer(
        self,
        strategy_name: str,
        remaining_budget: int,
        **kwargs: Any,
    ) -> BaseOptimizer:
        """
        Instantiate a new optimizer from the strategy registry.

        Parameters
        ----------
        strategy_name : str
            Registered strategy identifier (e.g. 'GA', 'DE').
        remaining_budget : int
            Evaluation budget to allocate to the new optimizer.
        **kwargs
            Additional algorithm-specific hyperparameters.

        Returns
        -------
        BaseOptimizer
            Instantiated optimizer ready for initialize() / step().
        """
        optimizer = self.registry.create(
            name=strategy_name,
            dim=self.dim,
            bounds=self.bounds,
            budget=remaining_budget,
            pop_size=self.pop_size,
            seed=self.seed,
            verbose=self.verbose,
            **kwargs,
        )
        self.active_optimizer = optimizer
        self.active_strategy_name = strategy_name.upper()
        self.strategy_start_time = time.time()

        if self.verbose:
            print(
                f"  [ASMController] Loaded strategy: {self.active_strategy_name} "
                f"(budget={remaining_budget})"
            )

        return optimizer

    def initialize_optimizer(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        pop_size: int = 30,
    ) -> PopulationState:
        """
        Initialize the active optimizer and sync global best.

        Parameters
        ----------
        fitness_fn : Callable
            Fitness evaluation function.
        pop_size : int
            Population size for initialization.

        Returns
        -------
        PopulationState
            Initial population state from the optimizer.
        """
        if self.active_optimizer is None:
            raise RuntimeError("No active optimizer loaded. Call load_optimizer() first.")

        state = self.active_optimizer.initialize(fitness_fn, pop_size=pop_size)
        self._sync_global_best(state)

        # Record initial load transition
        transition = StrategyTransition(
            from_strategy="",
            to_strategy=self.active_strategy_name,
            evaluation_count=self.active_optimizer.evaluations_used,
            timestamp=time.time(),
            reason="initial_load",
            fitness_at_switch=self.global_best_fitness,
        )
        self.transition_history.append(transition)

        return state

    def step_optimizer(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
    ) -> PopulationState:
        """
        Execute one iteration step on the active optimizer.

        Parameters
        ----------
        fitness_fn : Callable
            Fitness evaluation function.

        Returns
        -------
        PopulationState
            Updated population state after the step.
        """
        if self.active_optimizer is None:
            raise RuntimeError("No active optimizer loaded. Call load_optimizer() first.")

        state = self.active_optimizer.step(fitness_fn)
        self._sync_global_best(state)
        return state

    def switch_strategy(
        self,
        new_strategy_name: str,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        remaining_budget: int,
        reason: str = "schedule",
        **kwargs: Any,
    ) -> PopulationState:
        """
        Execute a complete strategy switch.

        Pipeline:
        1. Export current optimizer state.
        2. Save state to optimizer_states archive.
        3. Record strategy runtime.
        4. Instantiate new optimizer via registry.
        5. Initialize new optimizer.
        6. Inject global best solution into new optimizer's population.
        7. Record transition.

        Parameters
        ----------
        new_strategy_name : str
            Target strategy to switch to.
        fitness_fn : Callable
            Fitness evaluation function.
        remaining_budget : int
            Evaluation budget for the new optimizer.
        reason : str
            Switch reason string for logging.
        **kwargs
            Additional algorithm-specific hyperparameters.

        Returns
        -------
        PopulationState
            Initial population state of the new optimizer.
        """
        old_strategy = self.active_strategy_name
        old_evals = 0

        # 1. Export and save current optimizer state
        if self.active_optimizer is not None:
            exported_state = self.active_optimizer.export_state()
            self.optimizer_states[old_strategy] = exported_state
            old_evals = self.active_optimizer.evaluations_used

            # Record runtime for the outgoing strategy
            elapsed = time.time() - self.strategy_start_time
            self.strategy_runtimes[old_strategy] = (
                self.strategy_runtimes.get(old_strategy, 0.0) + elapsed
            )

        if self.verbose:
            print(
                f"  [ASMController] Switching: {old_strategy} -> {new_strategy_name.upper()} "
                f"(reason={reason}, global_best={self.global_best_fitness:.6f})"
            )

        # 2. Load and initialize new optimizer
        self.load_optimizer(new_strategy_name, remaining_budget, **kwargs)
        state = self.active_optimizer.initialize(fitness_fn, pop_size=self.pop_size)

        # 3. Inject global best into new optimizer's population
        if self.global_best_solution is not None:
            self._inject_global_best(fitness_fn)

        self._sync_global_best(self.active_optimizer.state)

        # 4. Record transition
        self.switch_count += 1
        transition = StrategyTransition(
            from_strategy=old_strategy,
            to_strategy=self.active_strategy_name,
            evaluation_count=old_evals,
            timestamp=time.time(),
            reason=reason,
            fitness_at_switch=self.global_best_fitness,
        )
        self.transition_history.append(transition)

        return state

    def get_active_strategy(self) -> str:
        """Return the name of the currently active strategy."""
        return self.active_strategy_name

    def get_active_optimizer(self) -> Optional[BaseOptimizer]:
        """Return the currently active optimizer instance."""
        return self.active_optimizer

    def get_evaluations_used(self) -> int:
        """Return total evaluations consumed by the active optimizer."""
        if self.active_optimizer is None:
            return 0
        return self.active_optimizer.evaluations_used

    def get_transition_history(self) -> List[Dict[str, Any]]:
        """Return serialized list of all strategy transitions."""
        return [t.to_dict() for t in self.transition_history]

    def get_strategy_runtimes(self) -> Dict[str, float]:
        """Return cumulative runtime per strategy in seconds."""
        runtimes = dict(self.strategy_runtimes)
        # Include currently active strategy's ongoing runtime
        if self.active_strategy_name and self.strategy_start_time > 0:
            current_elapsed = time.time() - self.strategy_start_time
            runtimes[self.active_strategy_name] = (
                runtimes.get(self.active_strategy_name, 0.0) + current_elapsed
            )
        return runtimes

    def export_controller_state(self) -> Dict[str, Any]:
        """
        Export complete controller state for ASM metadata serialization.

        Returns
        -------
        Dict[str, Any]
            Controller state dictionary containing global best, histories,
            optimizer states, and telemetry.
        """
        # Export active optimizer state if present
        if self.active_optimizer is not None:
            self.optimizer_states[self.active_strategy_name] = (
                self.active_optimizer.export_state()
            )

        return {
            "active_strategy": self.active_strategy_name,
            "global_best_fitness": float(self.global_best_fitness),
            "global_best_solution": (
                self.global_best_solution.tolist()
                if self.global_best_solution is not None
                else None
            ),
            "switch_count": self.switch_count,
            "transition_history": self.get_transition_history(),
            "strategy_runtimes": self.get_strategy_runtimes(),
            "optimizer_states": {
                name: {
                    k: v.tolist() if isinstance(v, np.ndarray) else v
                    for k, v in state.items()
                    if k != "population_state"
                }
                for name, state in self.optimizer_states.items()
            },
        }

    def reset(self) -> None:
        """Reset all controller state for a fresh ASM run."""
        self.active_optimizer = None
        self.active_strategy_name = ""
        self.strategy_start_time = 0.0
        self.global_best_solution = None
        self.global_best_fitness = -np.inf
        self.transition_history.clear()
        self.strategy_runtimes.clear()
        self.optimizer_states.clear()
        self.switch_count = 0

    # ─────────────────────────────────────────────────────────────────────────
    # Private Helpers
    # ─────────────────────────────────────────────────────────────────────────
    def _sync_global_best(self, state: Optional[PopulationState]) -> None:
        """
        Update global best solution if the optimizer found a better candidate.

        Parameters
        ----------
        state : Optional[PopulationState]
            Current population state from the active optimizer.
        """
        if state is None:
            return
        if state.best_fitness > self.global_best_fitness:
            self.global_best_fitness = float(state.best_fitness)
            self.global_best_solution = state.best_solution.copy()

    def _inject_global_best(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
    ) -> None:
        """
        Replace the worst individual in the new optimizer's population with
        the global best solution. This ensures continuity of search progress
        across strategy switches.

        Uses only the public interface: modifies state.population and
        state.fitness arrays, then updates state.best_solution/best_fitness
        if the global best is superior.
        """
        if self.active_optimizer is None or self.active_optimizer.state is None:
            return
        if self.global_best_solution is None:
            return

        state = self.active_optimizer.state
        pop = state.population
        fit = state.fitness

        if len(pop) == 0:
            return

        # Find worst individual and replace with global best
        worst_idx = int(np.argmin(fit))
        pop[worst_idx] = self.global_best_solution.copy()
        fit[worst_idx] = self.global_best_fitness

        # Update optimizer's best tracking if global best is superior
        if self.global_best_fitness > state.best_fitness:
            state.best_solution = self.global_best_solution.copy()
            state.best_fitness = float(self.global_best_fitness)
