"""
manager.py
----------
Unified Experiment Manager for the Navi optimization framework.

Executes, logs, benchmarks, exports, and visualizes experiments for any
optimizer derived from BaseOptimizer (GA, DE, and future PSO, GWO, ACO, SA, ASM).
"""

import csv
from dataclasses import asdict
import json
import os
import platform
import time
from typing import Dict, Any, List, Type, Optional
import numpy as np

from evaluation.fitness import evaluate_fitness
from algorithms.base import BaseOptimizer, PopulationState, IterationMetrics
from algorithms.ga import GeneticAlgorithm
from algorithms.de import DifferentialEvolution
from algorithms.pso import ParticleSwarmOptimizer
from algorithms.gwo import GreyWolfOptimizer
from algorithms.aco import AntColonyOptimizer
from algorithms.sa import SimulatedAnnealingOptimizer
from analytics.stats import calculate_array_stats
from analytics.plotting import generate_experiment_plots
from experiments.config import ExperimentConfig
from experiments.metadata import (
    AlgorithmMetadata,
    ExecutionMetadata,
    BenchmarkMetadata,
    ExperimentMetadata,
)

# Registry mapping algorithm names to BaseOptimizer subclasses
OPTIMIZER_REGISTRY: Dict[str, Type[BaseOptimizer]] = {
    "GA": GeneticAlgorithm,
    "DE": DifferentialEvolution,
    "PSO": ParticleSwarmOptimizer,
    "GWO": GreyWolfOptimizer,
    "ACO": AntColonyOptimizer,
    "SA": SimulatedAnnealingOptimizer,
}


def register_optimizer(name: str, cls: Type[BaseOptimizer]) -> None:
    """Register a new optimizer kernel class with the ExperimentManager."""
    OPTIMIZER_REGISTRY[name.upper()] = cls


class ExperimentManager:
    """
    Unified Experiment Manager for executing and exporting benchmark runs.

    Responsibilities
    ----------------
    1. Parse and validate ExperimentConfig objects.
    2. Instantiate target optimizer kernels inheriting from BaseOptimizer.
    3. Execute standardized step-by-step optimization loop (initialize -> step -> step).
    4. Record per-iteration metrics, compute non-fabricated statistical summaries.
    5. Export standardized result artifacts: config.json, summary.json, metrics.csv, convergence.csv, metadata.json.
    6. Render publication-ready plots into plots/ subdirectory.
    """

    def __init__(self, registry: Optional[Dict[str, Type[BaseOptimizer]]] = None):
        self.registry = registry if registry is not None else OPTIMIZER_REGISTRY

    def run_experiment(self, config: ExperimentConfig) -> Dict[str, Any]:
        """
        Execute an experiment from configuration and export results.

        Parameters
        ----------
        config : ExperimentConfig
            Experiment configuration specifications.

        Returns
        -------
        Dict[str, Any]
            Execution summary dictionary containing fitness, paths, and stats.
        """
        opt_name = config.optimizer.upper()
        if opt_name not in self.registry:
            raise ValueError(
                f"Unknown optimizer '{opt_name}'. Registered optimizers: {list(self.registry.keys())}"
            )

        optimizer_cls = self.registry[opt_name]

        # Timestamped execution output directory
        timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
        run_dir_name = f"{timestamp}_{opt_name}_seed{config.random_seed}"
        exp_dir = os.path.join(config.output_directory, run_dir_name)
        os.makedirs(exp_dir, exist_ok=True)

        # Fitness evaluation closure
        def fitness_fn(cand):
            return evaluate_fitness(cand, csv_path=config.dataset, seed=config.random_seed)

        # 1. Instantiate Optimizer
        optimizer = optimizer_cls(
            dim=35,
            bounds=(0.0, 1.0),
            budget=config.evaluation_budget,
            pop_size=config.population_size,
            seed=config.random_seed,
            verbose=True,
            **config.hyperparameters,
        )

        # 2. Standard Iterative Execution Loop (initialize -> step -> step)
        start_time = time.time()
        state = optimizer.initialize(fitness_fn, pop_size=config.population_size)

        for _ in range(config.iterations):
            if optimizer.is_budget_exhausted():
                break
            state = optimizer.step(fitness_fn)

        total_elapsed = time.time() - start_time

        # 3. Final Champion Simulation Evaluation
        best_solution = optimizer.get_best_solution()
        best_fitness, best_result = fitness_fn(best_solution)

        # 4. Metrics Collection
        metrics_history: List[IterationMetrics] = optimizer.logger.metrics_history
        history_fitness = [m.best_fitness for m in metrics_history]

        # Statistical Calculations
        stats_summary = calculate_array_stats(history_fitness)

        # 5. Result Artifact Exports
        # (a) config.json
        config_path = os.path.join(exp_dir, "config.json")
        with open(config_path, "w", encoding="utf-8") as f:
            f.write(config.to_json())

        # (b) metadata.json
        meta = ExperimentMetadata(
            experiment_id=run_dir_name,
            algorithm=AlgorithmMetadata(
                name=opt_name,
                hyperparameters=config.hyperparameters,
            ),
            benchmark=BenchmarkMetadata(
                dataset_name=config.dataset,
                evaluation_budget=config.evaluation_budget,
                random_seed=config.random_seed,
                total_trials=1,
            ),
            execution=ExecutionMetadata(
                timestamp=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
                python_version=platform.python_version(),
                platform=platform.platform(),
                cpu_architecture=platform.machine(),
            ),
            custom_notes=config.notes,
        )
        metadata_path = os.path.join(exp_dir, "metadata.json")
        with open(metadata_path, "w", encoding="utf-8") as f:
            f.write(meta.to_json())

        # (c) summary.json
        summary_dict = {
            "experiment_id": run_dir_name,
            "algorithm": opt_name,
            "seed": config.random_seed,
            "best_fitness": round(float(best_fitness), 8),
            "green_times": [round(float(g), 2) for g in best_result.get("green_times", [])],
            "cycle_time": best_result.get("cycle_time", 120),
            "avg_speed": round(float(best_result.get("avg_speed", 0)), 4),
            "avg_density": round(float(best_result.get("avg_density", 0)), 4),
            "avg_wait_time": round(float(best_result.get("avg_wait_time", 0)), 4),
            "total_flow": round(float(best_result.get("total_flow", 0)), 4),
            "avg_queue_length": round(float(best_result.get("avg_queue_length", 0)), 4),
            "congestion_pressure": round(float(best_result.get("congestion_pressure", 0)), 6),
            "total_evaluations": optimizer.evaluations_used,
            "total_generations": optimizer.generation,
            "elapsed_time": round(total_elapsed, 2),
            "statistics": stats_summary,
            "simulation_steps": best_result.get("simulation_steps", []),
        }
        summary_path = os.path.join(exp_dir, "summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(summary_dict, f, indent=2)

        # (d) metrics.csv
        metrics_csv_path = os.path.join(exp_dir, "metrics.csv")
        with open(metrics_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow([
                "generation", "evaluation_count", "best_fitness",
                "mean_fitness", "worst_fitness", "diversity_index",
                "elapsed_time", "algorithm_name", "seed"
            ])
            for m in metrics_history:
                writer.writerow([
                    m.generation, m.evaluation_count, m.best_fitness,
                    m.mean_fitness, m.worst_fitness, m.diversity_index,
                    m.elapsed_time, m.algorithm_name, m.seed
                ])

        # (e) convergence.csv
        convergence_csv_path = os.path.join(exp_dir, "convergence.csv")
        with open(convergence_csv_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["generation", "evaluation_count", "best_fitness"])
            for m in metrics_history:
                writer.writerow([m.generation, m.evaluation_count, m.best_fitness])

        # 6. Plot Generation
        plot_files = generate_experiment_plots(
            metrics_history=metrics_history,
            output_dir=exp_dir,
            algorithm_name=opt_name,
        )

        print(f"  [ExperimentManager] Run complete. Results exported -> {exp_dir}")

        return {
            "experiment_id": run_dir_name,
            "experiment_dir": exp_dir,
            "algorithm": opt_name,
            "best_fitness": best_fitness,
            "summary_path": summary_path,
            "plot_files": plot_files,
        }
