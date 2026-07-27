"""
logger.py
---------
Structured execution and iteration logger for Navi optimizers.

Provides standardized logging hooks for recording generation step metrics,
tracking evaluation progress, and printing formatted console outputs without
hardcoding print statements inside search algorithms.
"""

import time
from typing import List, Optional
from .types import IterationMetrics, OptimizerStatistics


class ExecutionLogger:
    """
    Tracks and records iteration metrics during optimizer execution.

    Attributes
    ----------
    algorithm_name : str
        Name identifier of the optimizer being tracked.
    seed : int
        Random seed parameter for the current run.
    verbose : bool
        If True, prints progress updates to console during search.
    metrics_history : List[IterationMetrics]
        Historical record of per-generation metrics objects.
    """

    def __init__(self, algorithm_name: str, seed: int = 42, verbose: bool = True):
        self.algorithm_name = algorithm_name
        self.seed = seed
        self.verbose = verbose
        self.metrics_history: List[IterationMetrics] = []
        self.start_time: float = 0.0
        self.initial_fitness: float = 0.0

    def start(self, initial_fitness: float = 0.0) -> None:
        """Mark start of optimization execution and initialize clock."""
        self.start_time = time.time()
        self.initial_fitness = initial_fitness
        self.metrics_history.clear()

    def log_step(
        self,
        generation: int,
        evaluation_count: int,
        best_fitness: float,
        mean_fitness: float,
        worst_fitness: float,
        diversity_index: float = 0.0,
        print_interval: int = 1,
    ) -> IterationMetrics:
        """
        Record performance metrics for a single generation step.

        Parameters
        ----------
        generation : int
            Current generation or iteration index.
        evaluation_count : int
            Total function evaluations performed up to this step.
        best_fitness : float
            Highest fitness score achieved in current state.
        mean_fitness : float
            Average fitness score of active population.
        worst_fitness : float
            Worst fitness score in active population.
        diversity_index : float
            Spatial diversity index of the population.
        print_interval : int
            Console print frequency interval (e.g. log every N generations).
        """
        elapsed = time.time() - self.start_time if self.start_time > 0 else 0.0
        
        metrics = IterationMetrics(
            generation=generation,
            evaluation_count=evaluation_count,
            best_fitness=best_fitness,
            mean_fitness=mean_fitness,
            worst_fitness=worst_fitness,
            diversity_index=diversity_index,
            elapsed_time=elapsed,
            algorithm_name=self.algorithm_name,
            seed=self.seed,
        )
        self.metrics_history.append(metrics)

        if self.verbose and (generation % print_interval == 0 or generation == 1):
            print(
                f"  [{self.algorithm_name}] Step {generation:<4} | "
                f"Evals: {evaluation_count:<6} | "
                f"Best Fit: {best_fitness:>10.6f} | "
                f"Mean Fit: {mean_fitness:>10.6f} | "
                f"Time: {elapsed:.2f}s"
            )

        return metrics

    def get_statistics(self) -> OptimizerStatistics:
        """Calculate and return runtime summary statistics object."""
        if not self.metrics_history:
            return OptimizerStatistics()

        total_elapsed = time.time() - self.start_time if self.start_time > 0 else 0.0
        last = self.metrics_history[-1]
        best_f = last.best_fitness
        total_evals = last.evaluation_count
        
        mean_eval_ms = (total_elapsed * 1000.0 / total_evals) if total_evals > 0 else 0.0

        return OptimizerStatistics(
            total_generations=last.generation,
            total_evaluations=total_evals,
            best_fitness=best_f,
            initial_fitness=self.initial_fitness,
            fitness_gain=best_f - self.initial_fitness,
            total_elapsed_time=total_elapsed,
            mean_eval_time_ms=mean_eval_ms,
        )
