"""
stats.py
--------
Statistical utilities for Navi optimization framework.

Provides non-fabricated statistical summaries (mean, median, std, min, max,
and 95% confidence intervals) for multi-trial and single-trial experiment runs.
"""

from typing import Dict, Any, List, Union
import numpy as np


def calculate_array_stats(data: Union[List[float], np.ndarray]) -> Dict[str, float]:
    """
    Calculate summary statistics for a 1D numerical array.

    Parameters
    ----------
    data : Union[List[float], np.ndarray]
        Input numerical array.

    Returns
    -------
    Dict[str, float]
        Dictionary containing mean, median, std, min, max, and 95% confidence interval margin.
    """
    arr = np.asarray(data, dtype=float)
    if len(arr) == 0:
        return {
            "mean": 0.0,
            "median": 0.0,
            "std": 0.0,
            "min": 0.0,
            "max": 0.0,
            "ci_95": 0.0,
        }

    mean_val = float(np.mean(arr))
    median_val = float(np.median(arr))
    std_val = float(np.std(arr, ddof=1 if len(arr) > 1 else 0))
    min_val = float(np.min(arr))
    max_val = float(np.max(arr))

    # Standard error of the mean and 95% confidence interval margin (z = 1.96)
    n = len(arr)
    sem = std_val / np.sqrt(n) if n > 0 else 0.0
    ci_95 = float(1.96 * sem)

    return {
        "mean": mean_val,
        "median": median_val,
        "std": std_val,
        "min": min_val,
        "max": max_val,
        "ci_95": ci_95,
    }
