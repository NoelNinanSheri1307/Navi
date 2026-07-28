"""
feature_extractor.py
--------------------
Feature Extractor for the Adaptive Strategy Metaheuristic (ASM) Decision Engine.

Converts raw telemetry snapshot histories into higher-level search descriptors
(Progress Rate, Diversity Trend, Search Stability, Budget Pressure).
"""

from typing import Any, Dict, List, Optional
import numpy as np

from algorithms.operators.telemetry_engine import TelemetrySnapshot


class FeatureExtractor:
    """
    Derives meaningful search status features from telemetry snapshots.
    """

    @staticmethod
    def extract(window: List[TelemetrySnapshot]) -> Dict[str, Any]:
        """
        Extract search state features from a window of telemetry snapshots.

        Parameters
        ----------
        window : List[TelemetrySnapshot]
            Recent history window of telemetry snapshots.

        Returns
        -------
        Dict[str, Any]
            Extracted features: progress_rate, diversity_trend,
            stability_score, budget_pressure.
        """
        if not window:
            return {
                "progress_rate": "Plateaued",
                "diversity_trend": "Stable",
                "stability_score": 1.0,
                "budget_pressure": 0.0,
            }

        latest = window[-1]

        # 1. Budget Pressure Calculation
        total_evals = latest.evaluations_used + latest.evaluations_remaining
        budget_pressure = float(latest.evaluations_used / max(1, total_evals))

        # Handle edge case where window has only 1 snapshot
        if len(window) < 2:
            return {
                "progress_rate": "Plateaued",
                "diversity_trend": "Stable",
                "stability_score": 1.0,
                "budget_pressure": budget_pressure,
            }

        # 2. Progress Rate Estimation
        fitness_start = window[0].best_fitness
        fitness_end = window[-1].best_fitness
        avg_improvement = (fitness_end - fitness_start) / (len(window) - 1)

        if avg_improvement >= 0.01:
            progress_rate = "Very High"
        elif avg_improvement >= 0.002:
            progress_rate = "High"
        elif avg_improvement >= 0.0005:
            progress_rate = "Moderate"
        elif avg_improvement > 1e-9:
            progress_rate = "Low"
        else:
            progress_rate = "Plateaued"

        # 3. Diversity Trend Estimation
        x = np.arange(len(window))
        y = np.array([s.population_diversity for s in window])
        
        # Compute linear regression slope of diversity
        x_mean = np.mean(x)
        y_mean = np.mean(y)
        x_dev = x - x_mean
        y_dev = y - y_mean
        denom = np.sum(x_dev ** 2)
        
        if denom > 1e-9:
            slope = float(np.sum(x_dev * y_dev) / denom)
        else:
            slope = 0.0

        if slope > 0.002:
            diversity_trend = "Increasing"
        elif slope < -0.005:
            diversity_trend = "Rapidly Collapsing"
        elif slope < -0.001:
            diversity_trend = "Gradually Falling"
        else:
            diversity_trend = "Stable"

        # 4. Search Stability Score
        best_fit_vals = [s.best_fitness for s in window]
        all_same_best = all(abs(f - best_fit_vals[0]) < 1e-9 for f in best_fit_vals)
        
        current_fit_vals = [s.current_fitness for s in window]
        var_current = float(np.var(current_fit_vals))

        if all_same_best:
            stability_score = 0.7 + 0.3 * (1.0 / (1.0 + var_current * 100.0))
        else:
            stability_score = 0.7 * (1.0 / (1.0 + var_current * 100.0))

        return {
            "progress_rate": progress_rate,
            "diversity_trend": diversity_trend,
            "stability_score": round(stability_score, 4),
            "budget_pressure": round(budget_pressure, 4),
        }
