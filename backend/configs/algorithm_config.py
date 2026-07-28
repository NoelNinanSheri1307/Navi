"""
algorithm_config.py
-------------------
Centralized hyperparameter configurations for Navi optimization algorithms.

Defines standard defaults for all current search kernels (GA, PSO, GWO, DE,
ACO, SA) and future Adaptive Strategy Metaheuristic (ASM) parameters.
"""

from dataclasses import dataclass, field
from typing import Dict, Any


@dataclass
class GAConfig:
    """Genetic Algorithm Hyperparameters."""
    pop_size: int = 30
    n_gen: int = 50
    cx_prob: float = 0.85
    mut_prob: float = 0.15
    eta_c: float = 15.0
    eta_m: float = 20.0
    seed: int = 42


@dataclass
class PSOConfig:
    """Particle Swarm Optimization Hyperparameters."""
    n_particles: int = 30
    n_iter: int = 50
    w_start: float = 0.9
    w_end: float = 0.4
    c1: float = 2.0
    c2: float = 2.0
    seed: int = 42


@dataclass
class GWOConfig:
    """Grey Wolf Optimizer Hyperparameters."""
    n_wolves: int = 30
    n_iter: int = 50
    seed: int = 42


@dataclass
class DEConfig:
    """Differential Evolution Hyperparameters."""
    pop_size: int = 30
    n_gen: int = 50
    F: float = 0.8
    CR: float = 0.9
    seed: int = 42


@dataclass
class ACOConfig:
    """Ant Colony Optimization (ACOR) Hyperparameters."""
    n_ants: int = 20
    archive_size: int = 30
    n_iter: int = 50
    q: float = 0.1
    xi: float = 0.85
    seed: int = 42


@dataclass
class SAConfig:
    """Simulated Annealing Hyperparameters."""
    n_iter: int = 500
    T_start: float = 1.0
    T_end: float = 0.001
    step_size: float = 0.1
    seed: int = 42


@dataclass
class ASMConfig:
    """Adaptive Strategy Metaheuristic (ASM) Hyperparameters."""
    budget: int = 10000
    population_size: int = 50
    diversity_threshold_low: float = 0.10
    diversity_threshold_high: float = 0.25
    stagnation_limit: int = 5
    ucb_exploration_c: float = 1.414
    seed: int = 42

    # Adaptive switching parameters
    adaptive_switching: bool = False
    confidence_threshold: float = 0.15
    minimum_runtime_steps: int = 3
    switch_cooldown_steps: int = 2
    adaptive_debug: bool = False


DEFAULT_ALGO_CONFIGS: Dict[str, Dict[str, Any]] = {
    "GA": {
        "pop_size": 30,
        "n_gen": 50,
        "cx_prob": 0.85,
        "mut_prob": 0.15,
        "eta_c": 15.0,
        "eta_m": 20.0,
    },
    "PSO": {
        "n_particles": 30,
        "n_iter": 50,
        "w_start": 0.9,
        "w_end": 0.4,
        "c1": 2.0,
        "c2": 2.0,
    },
    "GWO": {
        "n_wolves": 30,
        "n_iter": 50,
    },
    "DE": {
        "pop_size": 30,
        "n_gen": 50,
        "F": 0.8,
        "CR": 0.9,
    },
    "ACO": {
        "n_ants": 20,
        "archive_size": 30,
        "n_iter": 50,
        "q": 0.1,
        "xi": 0.85,
    },
    "SA": {
        "n_iter": 500,
        "T_start": 1.0,
        "T_end": 0.001,
        "step_size": 0.1,
    },
    "ASM": {
        "adaptive_switching": False,
        "confidence_threshold": 0.15,
        "minimum_runtime_steps": 3,
        "switch_cooldown_steps": 2,
        "adaptive_debug": False,
    },
}
