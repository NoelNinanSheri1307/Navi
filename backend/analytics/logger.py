"""
logger.py
---------
Analytics logging utility for tracking trial metrics and execution telemetry.

Provides persistent logging capabilities for benchmark runs, exporting iteration
trajectories and summary metrics to structured JSON / CSV records.
"""

from dataclasses import asdict
import json
import os
from typing import List, Dict, Any, Optional
from algorithms.base.types import IterationMetrics, OptimizationResult


class AnalyticsLogger:
    """
    Analytics logging recorder for tracking and exporting optimization runs.

    Attributes
    ----------
    out_dir : str
        Target output directory for saving result files.
    """

    def __init__(self, out_dir: str = "output/results"):
        self.out_dir = out_dir
        os.makedirs(self.out_dir, exist_ok=True)

    def save_result(self, result: OptimizationResult, filename: Optional[str] = None) -> str:
        """
        Serialize and save an OptimizationResult object to JSON file.

        Parameters
        ----------
        result : OptimizationResult
            Result object to serialize.
        filename : Optional[str]
            Custom output filename. Defaults to '<algorithm_name>_result.json'.

        Returns
        -------
        str : Path to written JSON file.
        """
        if filename is None:
            filename = f"{result.algorithm.lower()}_result.json"

        filepath = os.path.join(self.out_dir, filename)
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2)

        return filepath

    def save_metrics_history(
        self, metrics: List[IterationMetrics], filename: str = "metrics_history.json"
    ) -> str:
        """
        Save per-iteration metrics history list to JSON.
        """
        filepath = os.path.join(self.out_dir, filename)
        data = [asdict(m) for m in metrics]
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

        return filepath
