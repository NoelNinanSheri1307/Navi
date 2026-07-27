"""
config.py
---------
Standardized Experiment Configuration schema and loader for Navi framework.

Supports JSON file parsing, dictionary serialization, and default hyperparameter
injection for algorithm benchmarks.
"""

from dataclasses import dataclass, field, asdict
import json
import os
from typing import Dict, Any, Optional


@dataclass
class ExperimentConfig:
    """
    Standard experiment configuration container.

    Attributes
    ----------
    experiment_name : str
        Human-readable title identifier for the experiment run.
    optimizer : str
        Algorithm kernel name ('GA', 'DE', etc.).
    dataset : str
        Filename or relative path to VANET telemetry dataset.
    population_size : int
        Default population size across algorithms.
    evaluation_budget : int
        Maximum function evaluation budget allocation.
    iterations : int
        Target generation/iteration limit.
    random_seed : int
        Deterministic random seed parameter.
    output_directory : str
        Target root output directory for experiment runs.
    notes : Optional[str]
        Descriptive user notes or experimental context.
    hyperparameters : Dict[str, Any]
        Algorithm-specific hyperparameters dictionary.
    """
    experiment_name: str = "Standard_Experiment"
    optimizer: str = "GA"
    dataset: str = "vanet.csv"
    population_size: int = 30
    evaluation_budget: int = 10000
    iterations: int = 50
    random_seed: int = 42
    output_directory: str = "output/experiments"
    notes: Optional[str] = None
    hyperparameters: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """Convert configuration instance to dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize configuration instance to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "ExperimentConfig":
        """Construct ExperimentConfig from dictionary."""
        valid_fields = {
            "experiment_name", "optimizer", "dataset", "population_size",
            "evaluation_budget", "iterations", "random_seed",
            "output_directory", "notes", "hyperparameters"
        }
        filtered = {k: v for k, v in data.items() if k in valid_fields}
        return cls(**filtered)

    @classmethod
    def from_json(cls, json_path: str) -> "ExperimentConfig":
        """Parse ExperimentConfig from JSON file."""
        if not os.path.isfile(json_path):
            raise FileNotFoundError(f"Experiment config file not found: '{json_path}'")
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
        return cls.from_dict(data)
