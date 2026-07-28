"""
adaptive_switch_controller.py
-----------------------------
Adaptive Switch Controller for the Adaptive Strategy Metaheuristic (ASM).

Evaluates strategy recommendations against safety rules (runtime step limits,
confidence thresholds, switch cooldowns) to decide whether to switch the
active optimizer.
"""

from typing import Any


class AdaptiveSwitchController:
    """
    Observes recommendations and safety states to control strategy switches.
    """

    @staticmethod
    def decide(
        current_optimizer: str,
        recommendation: Any,
        current_runtime: int,
        steps_since_last_switch: int,
        confidence_threshold: float,
        minimum_runtime_steps: int,
        switch_cooldown_steps: int,
        verbose: bool = True,
    ) -> str:
        """
        Evaluate recommendation and determine target optimizer.

        Parameters
        ----------
        current_optimizer : str
            Name of the active optimizer (e.g. 'GA').
        recommendation : Recommendation
            Recommendation dataclass from the Decision Engine.
        current_runtime : int
            Steps executed by current_optimizer since it was loaded.
        steps_since_last_switch : int
            Steps executed since the last strategy switch occurred.
        confidence_threshold : float
            Required confidence margin to trigger switch.
        minimum_runtime_steps : int
            Minimum steps an optimizer must execute before being switched out.
        switch_cooldown_steps : int
            Minimum steps between consecutive strategy switches.
        verbose : bool
            Console logging verbosity.

        Returns
        -------
        str
            The target optimizer name (either current_optimizer or the recommended one).
        """
        rec_opt = recommendation.recommended_optimizer

        # Rule 2: Recommended optimizer equals active optimizer -> immediately continue
        if rec_opt.upper() == current_optimizer.upper():
            return current_optimizer

        # Evaluate safety rules
        rejections = []

        # Rule 3: Confidence threshold
        if recommendation.confidence < confidence_threshold:
            rejections.append(f"confidence below threshold ({recommendation.confidence:.2f} < {confidence_threshold:.2f})")

        # Rule 4: Minimum runtime steps
        if current_runtime < minimum_runtime_steps:
            rejections.append(f"minimum runtime not satisfied ({current_runtime} < {minimum_runtime_steps} steps)")

        # Rule 5: Switch cooldown
        if steps_since_last_switch < switch_cooldown_steps:
            rejections.append(f"cooldown not expired ({steps_since_last_switch} < {switch_cooldown_steps} steps)")

        if rejections:
            # Reject switch recommendation
            reason = rejections[0]
            if verbose:
                print(
                    f"  [Adaptive Controller] Current : {current_optimizer} | "
                    f"Recommendation : {rec_opt} | "
                    f"Confidence : {recommendation.confidence:.2f} | "
                    f"Decision : Continue {current_optimizer} | "
                    f"Reason : {reason}"
                )
            return current_optimizer
        else:
            # Accept switch recommendation
            if verbose:
                print(
                    f"  [Adaptive Controller] Current : {current_optimizer} | "
                    f"Recommendation : {rec_opt} | "
                    f"Confidence : {recommendation.confidence:.2f} | "
                    f"Decision : Switch | "
                    f"Reason : confidence threshold satisfied, minimum runtime satisfied, cooldown expired"
                )
            return rec_opt
