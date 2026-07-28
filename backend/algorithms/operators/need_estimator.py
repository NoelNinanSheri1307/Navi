"""
need_estimator.py
-----------------
Need Estimator for the Adaptive Strategy Metaheuristic (ASM) Decision Engine.

Processes high-level search features to estimate Exploration, Exploitation, and
Escape Needs independently using evidence accumulation.
"""

from typing import Any, Dict


class NeedEstimator:
    """
    Estimates search needs based on extracted search features.
    """

    @staticmethod
    def estimate(
        features: Dict[str, Any],
        iterations_since_improvement: int,
    ) -> Dict[str, float]:
        """
        Estimate search needs independently and normalize them.

        Parameters
        ----------
        features : Dict[str, Any]
            Extracted features from FeatureExtractor.
        iterations_since_improvement : int
            Telemetry metric tracking iterations since last fitness improvement.

        Returns
        -------
        Dict[str, float]
            Estimated search needs: exploration, exploitation, escape.
        """
        progress_rate = features["progress_rate"]
        diversity_trend = features["diversity_trend"]
        stability_score = features["stability_score"]
        budget_pressure = features["budget_pressure"]

        # 1. Exploration Need Evidence Accumulation
        # - High collapse trend indicates a critical need to explore elsewhere
        if diversity_trend == "Rapidly Collapsing":
            expl_div_evidence = 0.4
        elif diversity_trend == "Gradually Falling":
            expl_div_evidence = 0.2
        elif diversity_trend == "Stable":
            expl_div_evidence = 0.1
        else:
            expl_div_evidence = 0.0

        # - High search stability suggests stagnation, favoring exploration
        expl_stability_evidence = 0.3 * stability_score

        # - High budget pressure suppresses exploration
        expl_budget_evidence = 0.3 * (1.0 - budget_pressure)

        raw_exploration = expl_div_evidence + expl_stability_evidence + expl_budget_evidence

        # 2. Exploitation Need Evidence Accumulation
        # - Active progress rate suggests exploiting the current path works
        if progress_rate == "Very High":
            explt_progress_evidence = 0.5
        elif progress_rate == "High":
            explt_progress_evidence = 0.4
        elif progress_rate == "Moderate":
            explt_progress_evidence = 0.3
        elif progress_rate == "Low":
            explt_progress_evidence = 0.1
        else:
            explt_progress_evidence = 0.0

        # - Higher budget pressure forces exploitation
        explt_budget_evidence = 0.3 * budget_pressure

        # - Lower stability indicates active search movements, favoring exploitation
        explt_stability_evidence = 0.2 * (1.0 - stability_score)

        raw_exploitation = explt_progress_evidence + explt_budget_evidence + explt_stability_evidence

        # 3. Escape Need Evidence Accumulation
        # - High iterations since improvement is a strong stagnation indicator
        stagnation_factor = min(iterations_since_improvement / 10.0, 1.0)
        esc_stagnation_evidence = 0.5 * stagnation_factor

        # - Collapsing diversity combined with lack of progress highlights entrapment
        if diversity_trend == "Rapidly Collapsing":
            esc_div_evidence = 0.3
        elif diversity_trend == "Gradually Falling":
            esc_div_evidence = 0.1
        else:
            esc_div_evidence = 0.0

        # - Stabilized search state when stuck reinforces the escape need
        esc_stability_evidence = 0.2 * stability_score

        raw_escape = esc_stagnation_evidence + esc_div_evidence + esc_stability_evidence

        # 4. Normalization to sum to 1.0
        total = raw_exploration + raw_exploitation + raw_escape
        if total > 1e-9:
            exploration_need = raw_exploration / total
            exploitation_need = raw_exploitation / total
            escape_need = raw_escape / total
        else:
            exploration_need = 0.33
            exploitation_need = 0.33
            escape_need = 0.34

        return {
            "exploration": round(exploration_need, 4),
            "exploitation": round(exploitation_need, 4),
            "escape": round(escape_need, 4),
        }
