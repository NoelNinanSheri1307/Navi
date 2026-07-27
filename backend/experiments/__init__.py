"""
Navi Experiments Package

Exposes ExperimentManager, ExperimentConfig, and experiment metadata schemas.
"""

from .config import ExperimentConfig
from .manager import ExperimentManager, register_optimizer
from .metadata import (
    AlgorithmMetadata,
    ExecutionMetadata,
    BenchmarkMetadata,
    ExperimentMetadata,
)

__all__ = [
    "ExperimentConfig",
    "ExperimentManager",
    "register_optimizer",
    "AlgorithmMetadata",
    "ExecutionMetadata",
    "BenchmarkMetadata",
    "ExperimentMetadata",
]
