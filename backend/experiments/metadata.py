"""
metadata.py
-----------
Experiment metadata dataclasses and exporter abstractions for Navi.

Defines standardized schemas representing algorithm configuration, execution
workstation info, dataset attributes, and scientific benchmark metadata.
Supports export to JSON/CSV structures.
"""

from dataclasses import dataclass, field, asdict
import json
import platform
import time
from typing import Any, Dict, List, Optional


@dataclass
class AlgorithmMetadata:
    """Algorithm configuration metadata for experiment logging."""
    name: str
    version: str = "2.0.0"
    hyperparameters: Dict[str, Any] = field(default_factory=dict)


@dataclass
class ExecutionMetadata:
    """Environment and platform execution metadata."""
    timestamp: str = field(default_factory=lambda: time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()))
    python_version: str = field(default_factory=lambda: platform.python_version())
    platform: str = field(default_factory=lambda: platform.platform())
    cpu_architecture: str = field(default_factory=lambda: platform.machine())


@dataclass
class BenchmarkMetadata:
    """Benchmark trial specification metadata."""
    dataset_name: str = "VANET.csv"
    evaluation_budget: int = 10000
    random_seed: int = 42
    total_trials: int = 1


@dataclass
class ExperimentMetadata:
    """
    Master container for complete experiment run metadata.
    """
    experiment_id: str
    algorithm: AlgorithmMetadata
    benchmark: BenchmarkMetadata
    execution: ExecutionMetadata = field(default_factory=ExecutionMetadata)
    custom_notes: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert metadata hierarchy into standard nested dictionary."""
        return asdict(self)

    def to_json(self, indent: int = 2) -> str:
        """Serialize metadata object to JSON string."""
        return json.dumps(self.to_dict(), indent=indent)
