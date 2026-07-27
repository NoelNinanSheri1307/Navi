"""
decision_engine.py
------------------
Decision Engine for the Adaptive Strategy Metaheuristic (ASM).

Analyzes telemetry snapshots to estimate current search needs (exploration,
exploitation, escape) and recommends the most suitable optimizer kernel
based on their configured capability profiles.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional, Tuple

from algorithms.operators.telemetry_engine import TelemetryEngine, TelemetrySnapshot


# ─────────────────────────────────────────────────────────────────────────────
# Optimizer Capability Configuration
# ─────────────────────────────────────────────────────────────────────────────
@dataclass(frozen=True)
class OptimizerCapability:
    """
    Search capability profile of an optimizer kernel.
    """
    exploration: float
    exploitation: float
    escape: float


# Default capability profiles for the six reference optimizers
DEFAULT_CAPABILITIES: Dict[str, OptimizerCapability] = {
    "GA":  OptimizerCapability(exploration=0.4, exploitation=0.4, escape=0.2),
    "DE":  OptimizerCapability(exploration=0.5, exploitation=0.3, escape=0.2),
    "PSO": OptimizerCapability(exploration=0.3, exploitation=0.5, escape=0.2),
    "GWO": OptimizerCapability(exploration=0.3, exploitation=0.4, escape=0.3),
    "ACO": OptimizerCapability(exploration=0.4, exploitation=0.3, escape=0.3),
    "SA":  OptimizerCapability(exploration=0.2, exploitation=0.3, escape=0.5),
}


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
            Custom capability profiles. If None, uses DEFAULT_CAPABILITIES.
        """
        self.capabilities = capabilities if capabilities is not None else dict(DEFAULT_CAPABILITIES)
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
            )
            self._history.append(rec)
            return rec

        # 1. Compute Search Needs (Exploration, Exploitation, Escape)
        escape_score = min(latest.iterations_since_improvement / 10.0, 1.0)
        
        # Exploitation is proportional to recent fitness improvement and low stagnation
        raw_improvement = max(0.0, latest.fitness_improvement)
        exploitation_score = min(raw_improvement * 100.0, 1.0) * (1.0 - escape_score)
        
        # Exploration is the default need when not stagnating and not actively exploiting
        exploration_score = (1.0 - escape_score) * (1.0 - exploitation_score)

        # Enforce sum-to-one constraint via normalization
        total_need = escape_score + exploitation_score + exploration_score
        if total_need > 0.0:
            escape_need = escape_score / total_need
            exploitation_need = exploitation_score / total_need
            exploration_need = exploration_score / total_need
        else:
            escape_need = 0.33
            exploitation_need = 0.33
            exploration_need = 0.34

        # 2. Score Optimizers against Needs
        raw_scores: Dict[str, float] = {}
        for opt_name, cap in self.capabilities.items():
            score = (
                exploration_need * cap.exploration +
                exploitation_need * cap.exploitation +
                escape_need * cap.escape
            )
            raw_scores[opt_name] = score

        # Normalize scores to [0.0, 1.0]
        min_s = min(raw_scores.values())
        max_s = max(raw_scores.values())
        range_s = max_s - min_s
        
        normalized_scores: Dict[str, float] = {}
        for opt_name, score in raw_scores.items():
            if range_s > 1e-9:
                normalized_scores[opt_name] = (score - min_s) / range_s
            else:
                normalized_scores[opt_name] = 1.0

        # Determine best optimizer and confidence
        sorted_opts = sorted(normalized_scores.items(), key=lambda x: x[1], reverse=True)
        recommended_optimizer = sorted_opts[0][0]
        
        # Confidence is the margin between the first and second best choices
        if len(sorted_opts) > 1:
            confidence = float(sorted_opts[0][1] - sorted_opts[1][1])
        else:
            confidence = 1.0

        # 3. Generate Programmatic Explanation
        explanation = self._generate_explanation(
            latest.iterations_since_improvement,
            latest.fitness_improvement,
            latest.population_diversity,
            exploration_need,
            exploitation_need,
            escape_need
        )

        # Create immutable recommendation
        recommendation = Recommendation(
            recommended_optimizer=recommended_optimizer,
            optimizer_scores={k: round(v, 4) for k, v in normalized_scores.items()},
            exploration_need=round(exploration_need, 4),
            exploitation_need=round(exploitation_need, 4),
            escape_need=round(escape_need, 4),
            confidence=round(confidence, 4),
            explanation=explanation,
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
        stagnation: int,
        improvement: float,
        diversity: float,
        exploration: float,
        exploitation: float,
        escape: float,
    ) -> str:
        """Produce deterministic, rule-based text explanation of needs."""
        if escape > 0.4:
            return (
                f"Search has stagnated for {stagnation} iterations with low diversity "
                f"({diversity:.4f}), increasing the need for escape."
            )
        elif exploitation > 0.4:
            return (
                f"Improvement of {improvement:.6f} has been detected in recent steps, "
                f"increasing the need for exploitation."
            )
        elif exploration > 0.4:
            return (
                f"Diversity is stabilizing ({diversity:.4f}) without significant recent "
                f"improvement, increasing the need for exploration."
            )
        else:
            return (
                f"Balanced search dynamics: exploration ({exploration:.2f}), "
                f"exploitation ({exploitation:.2f}), escape ({escape:.2f})."
            )
