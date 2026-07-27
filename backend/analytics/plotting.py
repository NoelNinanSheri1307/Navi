"""
plotting.py
-----------
Publication-quality plotting module for Navi experiment visualizations.

Generates clean, unadorned Matplotlib charts for convergence trajectories,
evaluation progress, mean fitness, and population spatial diversity.
"""

import os
from typing import List, Dict, Any
import matplotlib
matplotlib.use("Agg")  # Non-interactive backend for server/CLI rendering
import matplotlib.pyplot as plt
import numpy as np

from algorithms.base.types import IterationMetrics


def generate_experiment_plots(
    metrics_history: List[IterationMetrics],
    output_dir: str,
    algorithm_name: str = "Optimizer",
) -> List[str]:
    """
    Generate and save experiment visualization plots.

    Parameters
    ----------
    metrics_history : List[IterationMetrics]
        Recorded iteration metrics history.
    output_dir : str
        Target root output directory for the experiment run.
    algorithm_name : str
        Name identifier of the optimizer.

    Returns
    -------
    List[str]
        List of generated filepaths.
    """
    plots_dir = os.path.join(output_dir, "plots")
    os.makedirs(plots_dir, exist_ok=True)

    if not metrics_history:
        return []

    generations = [m.generation for m in metrics_history]
    evaluations = [m.evaluation_count for m in metrics_history]
    best_fitness = [m.best_fitness for m in metrics_history]
    mean_fitness = [m.mean_fitness for m in metrics_history]
    diversity = [m.diversity_index for m in metrics_history]

    generated_files = []

    # Apply minimal publication style parameters
    plt.rcParams.update({
        "font.family": "serif",
        "axes.edgecolor": "#333333",
        "axes.linewidth": 0.8,
        "grid.color": "#e5e5e5",
        "grid.linestyle": "--",
        "grid.alpha": 0.7,
    })

    # 1. Convergence Curve (Best Fitness vs Generations)
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    ax.plot(generations, best_fitness, color="#1e40af", linewidth=1.8, label="Best Fitness")
    ax.set_title(f"Convergence Trajectory — {algorithm_name}", fontsize=11, fontweight="bold", pad=12)
    ax.set_xlabel("Generation", fontsize=10)
    ax.set_ylabel("Fitness Score", fontsize=10)
    ax.grid(True)
    ax.legend(frameon=True, facecolor="#ffffff", edgecolor="#cccccc")
    plt.tight_layout()
    p1 = os.path.join(plots_dir, "convergence_curve.png")
    fig.savefig(p1)
    plt.close(fig)
    generated_files.append(p1)

    # 2. Best Fitness vs Evaluations
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    ax.plot(evaluations, best_fitness, color="#047857", linewidth=1.8, label="Best Fitness")
    ax.set_title(f"Evaluation Progress — {algorithm_name}", fontsize=11, fontweight="bold", pad=12)
    ax.set_xlabel("Function Evaluations", fontsize=10)
    ax.set_ylabel("Fitness Score", fontsize=10)
    ax.grid(True)
    ax.legend(frameon=True, facecolor="#ffffff", edgecolor="#cccccc")
    plt.tight_layout()
    p2 = os.path.join(plots_dir, "best_fitness_vs_evals.png")
    fig.savefig(p2)
    plt.close(fig)
    generated_files.append(p2)

    # 3. Average Fitness vs Evaluations
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    ax.plot(evaluations, mean_fitness, color="#b91c1c", linewidth=1.8, label="Mean Population Fitness")
    ax.plot(evaluations, best_fitness, color="#047857", linewidth=1.2, linestyle="--", label="Best Fitness")
    ax.set_title(f"Mean Fitness Dynamics — {algorithm_name}", fontsize=11, fontweight="bold", pad=12)
    ax.set_xlabel("Function Evaluations", fontsize=10)
    ax.set_ylabel("Fitness Score", fontsize=10)
    ax.grid(True)
    ax.legend(frameon=True, facecolor="#ffffff", edgecolor="#cccccc")
    plt.tight_layout()
    p3 = os.path.join(plots_dir, "mean_fitness_vs_evals.png")
    fig.savefig(p3)
    plt.close(fig)
    generated_files.append(p3)

    # 4. Population Diversity vs Evaluations
    fig, ax = plt.subplots(figsize=(7, 4.5), dpi=300)
    ax.plot(evaluations, diversity, color="#6d28d9", linewidth=1.8, label="Spatial Diversity (Std Dev)")
    ax.set_title(f"Population Diversity Trajectory — {algorithm_name}", fontsize=11, fontweight="bold", pad=12)
    ax.set_xlabel("Function Evaluations", fontsize=10)
    ax.set_ylabel("Population Spatial Diversity", fontsize=10)
    ax.grid(True)
    ax.legend(frameon=True, facecolor="#ffffff", edgecolor="#cccccc")
    plt.tight_layout()
    p4 = os.path.join(plots_dir, "population_diversity.png")
    fig.savefig(p4)
    plt.close(fig)
    generated_files.append(p4)

    return generated_files
