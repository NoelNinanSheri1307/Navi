"""
decision_engine.py
------------------
Decision Engine for the Adaptive Strategy Metaheuristic (ASM).

Coordinates feature extraction, search need estimation, and capability matching
to rank and recommend the best optimizer.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

from algorithms.operators.telemetry_engine import TelemetryEngine, TelemetrySnapshot
from algorithms.operators.optimizer_capabilities import OptimizerCapability, OPTIMIZER_CAPABILITIES
from algorithms.operators.feature_extractor import FeatureExtractor
from algorithms.operators.need_estimator import NeedEstimator


# ─────────────────────────────────────────────────────────────────────────────
# Recommendation Dataclass (Immutable)
# ─────────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class Recommendation:
    """
    Immutable search strategy recommendation output by the Decision Engine.
    """
    recommended_optimizer: str
    optimizer_scores: Dict[str, float]
    exploration_need: float
    exploitation_need: float
    escape_need: float
    confidence: float
    explanation: str
    features: Dict[str, Any]


# ─────────────────────────────────────────────────────────────────────────────
# Decision Engine
# ─────────────────────────────────────────────────────────────────────────────
class DecisionEngine:
    """
    Analyzes search state telemetry and produces strategy recommendations.
    """

    def __init__(self, capabilities: Optional[Dict[str, OptimizerCapability]] = None):
        """
        Initialize the Decision Engine.

        Parameters
        ----------
        capabilities : Optional[Dict[str, OptimizerCapability]]
            Custom capability profiles. If None, loads OPTIMIZER_CAPABILITIES.
        """
        self.capabilities = capabilities if capabilities is not None else dict(OPTIMIZER_CAPABILITIES)
        self._history: List[Recommendation] = []

    def reset(self) -> None:
        """Clear recommendation history."""
        self._history.clear()

    def recommend(self, telemetry: TelemetryEngine) -> Recommendation:
        """
        Analyze current telemetry and generate a new strategy recommendation.

        Parameters
        ----------
        telemetry : TelemetryEngine
            The telemetry engine containing history and rolling window data.

        Returns
        -------
        Recommendation
            The immutable recommendation snapshot.
        """
        latest: Optional[TelemetrySnapshot] = telemetry.latest()
        if latest is None:
            # Fallback if no telemetry is collected yet
            scores = {opt: 0.5 for opt in self.capabilities.keys()}
            rec = Recommendation(
                recommended_optimizer=list(self.capabilities.keys())[0],
                optimizer_scores=scores,
                exploration_need=0.33,
                exploitation_need=0.33,
                escape_need=0.34,
                confidence=0.0,
                explanation="No telemetry available yet. Recommending default optimizer.",
                features={
                    "progress_rate": "Plateaued",
                    "diversity_trend": "Stable",
                    "stability_score": 1.0,
                    "budget_pressure": 0.0,
                },
            )
            self._history.append(rec)
            return rec

        # 1. Feature Extraction
        # Use the rolling window from the telemetry engine for trend analysis
        features = FeatureExtractor.extract(telemetry.rolling_window)

        # 2. Need Estimation
        needs = NeedEstimator.estimate(features, latest.iterations_since_improvement)
        exploration_need = needs["exploration"]
        exploitation_need = needs["exploitation"]
        escape_need = needs["escape"]

        # 3. Score Optimizers against Capabilities
        raw_scores: Dict[str, float] = {}
        for opt_name, cap in self.capabilities.items():
            score = (
                exploration_need * cap.exploration +
                exploitation_need * cap.exploitation +
                escape_need * cap.escape
            )
            raw_scores[opt_name] = score

        # Normalize suitability scores to [0.0, 1.0] across registry
        min_s = min(raw_scores.values())
        max_s = max(raw_scores.values())
        range_s = max_s - min_s
        
        normalized_scores: Dict[str, float] = {}
        for opt_name, score in raw_scores.items():
            if range_s > 1e-9:
                normalized_scores[opt_name] = (score - min_s) / range_s
            else:
                normalized_scores[opt_name] = 1.0

        # Sort optimizers by score
        sorted_opts = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        recommended_optimizer = sorted_opts[0][0]
        
        # Calculate raw score difference for confidence
        sorted_raw = sorted(raw_scores.items(), key=lambda x: x[1], reverse=True)
        if len(sorted_raw) > 1:
            confidence = float(sorted_raw[0][1] - sorted_raw[1][1])
        else:
            confidence = 1.0

        # 4. Generate Explanation directly corresponding to evidence
        explanation = self._generate_explanation(
            features,
            exploration_need,
            exploitation_need,
            escape_need
        )

        # Create immutable recommendation
        recommendation = Recommendation(
            recommended_optimizer=recommended_optimizer,
            optimizer_scores={k: round(v, 4) for k, v in normalized_scores.items()},
            exploration_need=exploration_need,
            exploitation_need=exploitation_need,
            escape_need=escape_need,
            confidence=round(confidence, 4),
            explanation=explanation,
            features=features,
        )

        self._history.append(recommendation)
        return recommendation

    def latest(self) -> Optional[Recommendation]:
        """Return the most recent recommendation."""
        if self._history:
            return self._history[-1]
        return None

    def history(self) -> List[Recommendation]:
        """Return the full recommendation history."""
        return self._history

    # ─────────────────────────────────────────────────────────────────────────────
    # Private Explanation Generator
    # ─────────────────────────────────────────────────────────────────────────────
    @staticmethod
    def _generate_explanation(
        features: Dict[str, Any],
        exploration: float,
        exploitation: float,
        escape: float,
    ) -> str:
        """Produce deterministic, evidence-based text explanation of needs."""
        progress_rate = features["progress_rate"]
        diversity_trend = features["diversity_trend"]
        stability_score = features["stability_score"]
        budget_pressure = features["budget_pressure"]

        reasons = []
        
        # Progress Rate explanation
        if progress_rate in ["Very High", "High"]:
            reasons.append("Progress remains strong.")
        elif progress_rate == "Moderate":
            reasons.append("Progress is moderate.")
        else:
            reasons.append("Best fitness has plateaued.")

        # Diversity Trend explanation
        if diversity_trend == "Increasing":
            reasons.append("Diversity is increasing.")
        elif diversity_trend == "Rapidly Collapsing":
            reasons.append("Diversity has collapsed.")
        elif diversity_trend == "Gradually Falling":
            reasons.append("Diversity is gradually decreasing.")
        else:
            reasons.append("Diversity is stable.")

        # Stability explanation
        if stability_score > 0.6:
            reasons.append("Search has remained stable for multiple iterations.")
        else:
            reasons.append("Search dynamics are active.")

        # Budget pressure explanation
        if budget_pressure > 0.8:
            reasons.append("Budget pressure is critical.")
        elif budget_pressure > 0.5:
            reasons.append("Budget pressure is increasing.")
        else:
            reasons.append("Budget pressure is low.")

        # Concluding need statement
        max_need = max(exploration, exploitation, escape)
        if max_need == exploration:
            reasons.append("Exploration behavior is recommended.")
        elif max_need == exploitation:
            reasons.append("Exploitation is currently favored.")
        else:
            reasons.append("Escape behavior is recommended.")

        return " ".join(reasons)

