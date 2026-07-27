"""
telemetry_engine.py
--------------------
Telemetry collection subsystem for the Adaptive Strategy Metaheuristic (ASM).

Continuously observes optimizer execution at each step to collect universal
and optimizer-specific performance metrics, producing telemetry snapshots
without modifying optimizer behavior.
"""

from collections import deque
from dataclasses import dataclass, asdict
import time
from typing import Any, Dict, List, Optional

import numpy as np

from algorithms.base import BaseOptimizer, PopulationState


@dataclass(frozen=True)
class TelemetrySnapshot:
    """
    Quantitative performance metrics collected at a single optimization step.
    """
    iteration: int
    # Universal metrics
    current_fitness: float
    best_fitness: float
    mean_fitness: float
    fitness_variance: float
    fitness_improvement: float
    population_diversity: float
    evaluations_used: int
    evaluations_remaining: int
    iterations_since_improvement: int
    elapsed_runtime: float

    # Optimizer-specific metrics
    # GA
    mutation_success_rate: Optional[float] = None
    crossover_success_rate: Optional[float] = None
    # DE
    successful_trial_rate: Optional[float] = None
    # PSO
    average_velocity: Optional[float] = None
    swarm_dispersion: Optional[float] = None
    personal_best_updates: Optional[int] = None
    # GWO
    alpha_stability: Optional[int] = None
    leader_movement: Optional[float] = None
    # ACOR
    archive_diversity: Optional[float] = None
    archive_sigma: Optional[float] = None
    # SA
    temperature: Optional[float] = None
    acceptance_rate: Optional[float] = None
    improving_move_ratio: Optional[float] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert snapshot to dictionary for serialization."""
        return asdict(self)


class TelemetryEngine:
    """
    Observes optimizer steps and compiles telemetry history.
    """

    def __init__(self, window_size: int = 20):
        self._history: List[TelemetrySnapshot] = []
        self._window: deque = deque(maxlen=window_size)
        self.start_time: float = 0.0
        self.initial_best_fitness: Optional[float] = None

        # Internal tracking variables for stateful metrics
        self._prev_best_fitness: Optional[float] = None
        self._iterations_since_improvement: int = 0
        self._prev_alpha_position: Optional[np.ndarray] = None
        self._alpha_stability_counter: int = 0
        self._sa_improving_moves_count: int = 0
        self._sa_total_moves_count: int = 0

    def reset(self) -> None:
        """Reset telemetry collection state."""
        self._history.clear()
        self._window.clear()
        self.start_time = time.time()
        self.initial_best_fitness = None
        self._prev_best_fitness = None
        self._iterations_since_improvement = 0
        self._prev_alpha_position = None
        self._alpha_stability_counter = 0
        self._sa_improving_moves_count = 0
        self._sa_total_moves_count = 0
        if hasattr(self, "_prev_de_fitness"):
            self._prev_de_fitness = None
        if hasattr(self, "_prev_pbest_scores"):
            self._prev_pbest_scores = None

    def collect(self, optimizer: BaseOptimizer) -> TelemetrySnapshot:
        """
        Observe the current state of the optimizer and append a new snapshot.

        Parameters
        ----------
        optimizer : BaseOptimizer
            The active optimizer instance.

        Returns
        -------
        TelemetrySnapshot
            The collected step telemetry metrics.
        """
        if self.start_time == 0.0:
            self.start_time = time.time()

        state: Optional[PopulationState] = optimizer.state
        if state is None:
            raise RuntimeError("Optimizer state is empty. Call initialize() first.")

        # 1. Universal Metrics Calculation
        current_best = float(state.best_fitness)
        if self.initial_best_fitness is None:
            self.initial_best_fitness = current_best

        # Fitness improvement compared to previous step
        if self._prev_best_fitness is not None:
            improvement = current_best - self._prev_best_fitness
        else:
            improvement = current_best - self.initial_best_fitness

        # Tracking iterations since last improvement
        if self._prev_best_fitness is not None and current_best > self._prev_best_fitness:
            self._iterations_since_improvement = 0
        elif self._prev_best_fitness is not None:
            self._iterations_since_improvement += 1

        self._prev_best_fitness = current_best

        # Population statistics
        pop_fitness = state.fitness
        mean_fit = float(np.mean(pop_fitness))
        var_fit = float(np.var(pop_fitness))
        current_fit = float(np.max(pop_fitness))  # Best of current population

        # Compute population diversity standard deviation across dimensions
        if state.population is not None and len(state.population) > 0:
            div = float(np.mean(np.std(state.population, axis=0)))
        else:
            div = 0.0

        evals_used = optimizer.evaluations_used
        evals_rem = max(0, optimizer.budget - evals_used)
        elapsed = time.time() - self.start_time

        # 2. Optimizer-Specific Metrics Extraction
        specific_metrics: Dict[str, Any] = {}
        opt_name = optimizer.name.upper()

        if opt_name == "GA":
            # GA success rates are unavailable because parent-child tracking
            # is not supported in the GA step interface.
            specific_metrics["mutation_success_rate"] = None
            specific_metrics["crossover_success_rate"] = None

        elif opt_name == "DE":
            # Compute DE successful trial rate by comparing current fitness values
            # against previous step's fitness values for each slot.
            if self._history:
                prev_snapshot = self._history[-1]
                # Compare current population fitness array with previous population fitness array
                # Since DE does greedy parent-child selection in-place, improvement in slot i
                # means a successful trial vector was chosen.
                prev_state = optimizer.state
                # Note: optimizer.state has already been updated. We can access the previous state
                # by storing the population state history or simply computing progress.
                # To remain decoupled, we compare current fitness with the previous step's fitness.
                # However, DE step updates fitness in-place. If we compare the array, we can find the rate.
                # We can store the previous fitness array in telemetry engine.
                # Let's check if we saved it in a previous step.
                # We can dynamically retrieve the previous step's fitness from the last snapshot's state if we stored it,
                # or we can track it statefully in TelemetryEngine.
                pass
            
            # Let's implement robust tracking of the previous fitness array:
            if not hasattr(self, "_prev_de_fitness") or self._prev_de_fitness is None:
                self._prev_de_fitness = pop_fitness.copy()
                specific_metrics["successful_trial_rate"] = 0.0
            else:
                better = np.sum(pop_fitness > self._prev_de_fitness)
                specific_metrics["successful_trial_rate"] = float(better / len(pop_fitness))
                self._prev_de_fitness = pop_fitness.copy()

        elif opt_name == "PSO":
            # Extract velocities
            velocities = state.metadata.get("velocities")
            if velocities is not None:
                specific_metrics["average_velocity"] = float(np.mean(np.linalg.norm(velocities, axis=1)))
            else:
                specific_metrics["average_velocity"] = None

            # Swarm dispersion as mean distance to gravity center
            if state.population is not None and len(state.population) > 0:
                center = np.mean(state.population, axis=0)
                disp = float(np.mean(np.linalg.norm(state.population - center, axis=1)))
                specific_metrics["swarm_dispersion"] = disp
            else:
                specific_metrics["swarm_dispersion"] = None

            # Track personal best updates compared to previous step
            pbest_scores = state.metadata.get("pbest_scores")
            if pbest_scores is not None:
                if not hasattr(self, "_prev_pbest_scores") or self._prev_pbest_scores is None:
                    self._prev_pbest_scores = pbest_scores.copy()
                    specific_metrics["personal_best_updates"] = 0
                else:
                    updated = int(np.sum(pbest_scores > self._prev_pbest_scores))
                    specific_metrics["personal_best_updates"] = updated
                    self._prev_pbest_scores = pbest_scores.copy()
            else:
                specific_metrics["personal_best_updates"] = None

        elif opt_name == "GWO":
            alpha_pos = state.metadata.get("alpha_position")
            if alpha_pos is not None:
                # Alpha stability: consecutive steps with same alpha position
                if self._prev_alpha_position is not None:
                    if np.allclose(alpha_pos, self._prev_alpha_position, atol=1e-8):
                        self._alpha_stability_counter += 1
                    else:
                        self._alpha_stability_counter = 0
                    
                    # Leader movement: distance moved from last step
                    dist = float(np.linalg.norm(alpha_pos - self._prev_alpha_position))
                    specific_metrics["leader_movement"] = dist
                else:
                    self._alpha_stability_counter = 0
                    specific_metrics["leader_movement"] = 0.0

                self._prev_alpha_position = alpha_pos.copy()
                specific_metrics["alpha_stability"] = self._alpha_stability_counter
            else:
                specific_metrics["alpha_stability"] = None
                specific_metrics["leader_movement"] = None

        elif opt_name == "ACO":
            # Archive diversity and sigma
            specific_metrics["archive_diversity"] = state.metadata.get("diversity")
            specific_metrics["archive_sigma"] = state.metadata.get("mean_sigma")

        elif opt_name == "SA":
            specific_metrics["temperature"] = state.metadata.get("temperature")
            specific_metrics["acceptance_rate"] = state.metadata.get("acceptance_rate")

            # Tracking improving move ratio
            is_improving = state.metadata.get("improving_move", False)
            self._sa_total_moves_count += 1
            if is_improving:
                self._sa_improving_moves_count += 1
            
            specific_metrics["improving_move_ratio"] = float(
                self._sa_improving_moves_count / self._sa_total_moves_count
            )

        # 3. Create and store snapshot
        snapshot = TelemetrySnapshot(
            iteration=optimizer.generation,
            current_fitness=current_fit,
            best_fitness=current_best,
            mean_fitness=mean_fit,
            fitness_variance=var_fit,
            fitness_improvement=improvement,
            population_diversity=div,
            evaluations_used=evals_used,
            evaluations_remaining=evals_rem,
            iterations_since_improvement=self._iterations_since_improvement,
            elapsed_runtime=elapsed,
            **specific_metrics
        )

        self._history.append(snapshot)
        self._window.append(snapshot)
        return snapshot

    def latest(self) -> Optional[TelemetrySnapshot]:
        """Return the most recent collected TelemetrySnapshot."""
        if self._history:
            return self._history[-1]
        return None

    def last(self, n: int) -> List[TelemetrySnapshot]:
        """
        Return the last n collected TelemetrySnapshot records.

        Parameters
        ----------
        n : int
            Number of recent snapshots to return.

        Returns
        -------
        List[TelemetrySnapshot]
            The last n snapshots, ordered from oldest to newest.
        """
        if n <= 0:
            return []
        return self._history[-n:]

    def history(self) -> List[TelemetrySnapshot]:
        """Return the complete list of collected TelemetrySnapshot records."""
        return self._history

    @property
    def rolling_window(self) -> List[TelemetrySnapshot]:
        """Return the recent rolling window of snapshots."""
        return list(self._window)
