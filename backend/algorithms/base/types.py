"""
types.py
--------
Common dataclasses and data models for the Navi optimization framework.

These data models represent framework state, iteration metrics, population
tensors, and execution results without coupling to specific search logic.
"""

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional
import numpy as np


@dataclass
class PopulationState:
    """
    Encapsulates the state of an optimization population at a given generation.

    Attributes
    ----------
    population : np.ndarray
        Position matrix of shape (P, D) where P is population size and D is dimension.
    fitness : np.ndarray
        Fitness array of shape (P,) corresponding to population individuals.
    best_solution : np.ndarray
        Parameter vector of the current global best candidate (D,).
    best_fitness : float
        Fitness value of the current global best candidate.
    evaluation_count : int
        Cumulative number of fitness function evaluations used so far.
    generation : int
        Current generation or iteration number.
    metadata : Dict[str, Any]
        Algorithm-specific state metadata (e.g. velocity, alpha wolf, pheromones).

    Future Extension Points
    -----------------------
    - ASM Interaction: SearchAnalyzer inspects population tensor to compute diversity.
    - Multi-Objective: Extension to store Pareto fronts and dominance ranks.
    """
    population: np.ndarray
    fitness: np.ndarray
    best_solution: np.ndarray
    best_fitness: float
    evaluation_count: int = 0
    generation: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)

    def copy(self) -> "PopulationState":
        """Return a deep copy of the population state."""
        return PopulationState(
            population=self.population.copy(),
            fitness=self.fitness.copy(),
            best_solution=self.best_solution.copy(),
            best_fitness=float(self.best_fitness),
            evaluation_count=self.evaluation_count,
            generation=self.generation,
            metadata=self.metadata.copy(),
        )


@dataclass
class IterationMetrics:
    """
    Records quantitative performance metrics for a single generation step.

    Attributes
    ----------
    generation : int
        Generation or iteration index.
    evaluation_count : int
        Total function evaluations used up to this step.
    best_fitness : float
        Best fitness score achieved in this generation or globally.
    mean_fitness : float
        Average fitness across the active population.
    worst_fitness : float
        Worst fitness score in the current population.
    diversity_index : float
        Spatial variance / mean distance metric of the population.
    elapsed_time : float
        Cumulative execution time in seconds up to this step.
    algorithm_name : str
        Name identifier of the executing algorithm kernel.
    seed : int
        Random seed parameter for the execution.
    """
    generation: int
    evaluation_count: int
    best_fitness: float
    mean_fitness: float
    worst_fitness: float
    diversity_index: float = 0.0
    elapsed_time: float = 0.0
    algorithm_name: str = "UNKNOWN"
    seed: int = 42


@dataclass
class OptimizerStatistics:
    """
    Aggregated statistical summary of an completed optimization run.

    Attributes
    ----------
    total_generations : int
        Total iterations completed.
    total_evaluations : int
        Total fitness evaluations executed.
    best_fitness : float
        Highest fitness score attained.
    initial_fitness : float
        Fitness score of the initial champion.
    fitness_gain : float
        Net fitness improvement (best_fitness - initial_fitness).
    total_elapsed_time : float
        Total execution wall-clock time in seconds.
    mean_eval_time_ms : float
        Average duration per evaluation call in milliseconds.
    """
    total_generations: int = 0
    total_evaluations: int = 0
    best_fitness: float = 0.0
    initial_fitness: float = 0.0
    fitness_gain: float = 0.0
    total_elapsed_time: float = 0.0
    mean_eval_time_ms: float = 0.0


@dataclass
class OptimizationResult:
    """
    Standardized return object for optimization kernel executions.

    Attributes
    ----------
    algorithm : str
        Name identifier of the executed algorithm.
    best_solution : np.ndarray
        Optimal 35-dim parameter vector found.
    fitness : float
        Best scalar fitness value achieved.
    green_times : List[float]
        Optimized green time allocation per lane [g1, g2, g3, g4].
    cycle_time : int
        Signal cycle duration in seconds (default 120s).
    avg_speed : float
        Mean speed metric across intersection cycles (km/h).
    avg_density : float
        Mean density metric across intersection cycles (veh/km).
    avg_wait_time : float
        Mean waiting latency metric across intersection cycles (seconds).
    total_flow : float
        Total vehicular throughput rate (veh/hr).
    avg_queue_length : float
        Mean queue length in vehicles.
    congestion_pressure : float
        Dimensionless congestion pressure ratio.
    speed_density_ratio : float
        Speed-to-density operational ratio.
    convergence_history : List[float]
        Fitness history trajectory over iterations.
    simulation_steps : List[Dict[str, Any]]
        Per-cycle breakdown simulation records.
    statistics : Optional[OptimizerStatistics]
        Detailed runtime performance statistics object.
    """
    algorithm: str
    best_solution: np.ndarray
    fitness: float
    green_times: List[float]
    cycle_time: int = 120
    avg_speed: float = 0.0
    avg_density: float = 0.0
    avg_wait_time: float = 0.0
    total_flow: float = 0.0
    avg_queue_length: float = 0.0
    congestion_pressure: float = 0.0
    speed_density_ratio: float = 0.0
    convergence_history: List[float] = field(default_factory=list)
    simulation_steps: List[Dict[str, Any]] = field(default_factory=list)
    statistics: Optional[OptimizerStatistics] = None

    def to_dict(self) -> Dict[str, Any]:
        """Export standardized dictionary for JSON output compatibility."""
        return {
            "algorithm": self.algorithm,
            "green_times": [round(float(g), 2) for g in self.green_times],
            "cycle_time": self.cycle_time,
            "avg_speed": round(float(self.avg_speed), 4),
            "avg_density": round(float(self.avg_density), 4),
            "avg_wait_time": round(float(self.avg_wait_time), 4),
            "total_flow": round(float(self.total_flow), 4),
            "avg_queue_length": round(float(self.avg_queue_length), 4),
            "congestion_pressure": round(float(self.congestion_pressure), 6),
            "speed_density_ratio": round(float(self.speed_density_ratio), 6),
            "fitness": round(float(self.fitness), 8),
            "convergence_history": [round(float(f), 8) for f in self.convergence_history],
            "simulation_steps": self.simulation_steps,
        }


@dataclass
class ExperimentConfig:
    """
    Centralized configuration dataclass for benchmark experiments.

    Attributes
    ----------
    csv_path : str
        Path to input VANET telemetry dataset.
    budget : int
        Maximum function evaluation budget.
    population_size : int
        Default population size across algorithms.
    iterations : int
        Default iterations/generations limit.
    seed : int
        Random seed for reproducibility.
    out_dir : str
        Output directory path for results.
    """
    csv_path: str = "vanet.csv"
    budget: int = 10000
    population_size: int = 30
    iterations: int = 50
    seed: int = 42
    out_dir: str = "output/results"
