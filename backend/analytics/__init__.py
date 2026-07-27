"""
Navi Analytics Package

Exposes analytics logging, statistical utilities, and plotting visualizations.
"""

from .logger import AnalyticsLogger
from .stats import calculate_array_stats
from .plotting import generate_experiment_plots

__all__ = [
    "AnalyticsLogger",
    "calculate_array_stats",
    "generate_experiment_plots",
]
