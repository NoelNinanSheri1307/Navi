"""
benchmark_config.py
-------------------
Centralized scientific benchmark settings, evaluation budgets, and seed sequences.

Establishes strict evaluation budget equality (N_eval = 10,000) and deterministic
seed lists for fair multi-run statistical evaluation.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any


@dataclass
class BenchmarkConfig:
    """
    Scientific benchmarking protocol settings.

    Attributes
    ----------
    budget : int
        Maximum function evaluation budget per algorithm run (default 10,000).
    num_runs : int
        Number of independent stochastic runs per algorithm (default 30).
    seeds : List[int]
        Sequence of deterministic random seed integers.
    confidence_level : float
        Statistical confidence interval significance level (default 0.95).
    fast_mode_budget : int
        Reduced budget for rapid testing (default 500).
    """
    budget: int = 10000
    num_runs: int = 30
    seeds: List[int] = field(default_factory=lambda: [
        42, 101, 2024, 888, 1337, 7, 123, 999, 555, 321,
        111, 222, 333, 444, 666, 777, 909, 808, 707, 606,
        505, 404, 303, 202, 102, 203, 304, 405, 506, 607
    ])
    confidence_level: float = 0.95
    fast_mode_budget: int = 500


DEFAULT_BENCHMARK_CONFIG = BenchmarkConfig()
