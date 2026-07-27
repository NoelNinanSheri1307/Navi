"""
gwo_encircling.py
-----------------
Grey Wolf Optimizer encircling and hunting vector operator for Navi framework.

Implements adaptive decay parameter a(t) and leader distance vector calculations
(Mirjalili et al., 2014).
"""

from typing import Tuple
import numpy as np


class GWOEncircling:
    """
    GWO Encircling & Adaptive Control Parameter Operator.

    Calculates the linearly decaying exploration parameter a(t) and coefficient vectors A, C
    to govern wolf pack position updates relative to leaders.
    """

    @staticmethod
    def compute_adaptive_a(current_iter: int, total_iters: int) -> float:
        """
        Compute adaptive parameter a(t) linearly decreasing from 2.0 to 0.0.
        """
        if total_iters <= 1:
            return 0.0
        progress = min(max(current_iter / total_iters, 0.0), 1.0)
        return float(2.0 - 2.0 * progress)

    def calculate_leader_distances(
        self,
        wolf_position: np.ndarray,
        leader_position: np.ndarray,
        a_param: float,
        rng: np.random.Generator,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Calculate coefficient vector A and distance vector D towards target leader.

        Parameters
        ----------
        wolf_position : np.ndarray
            Current position vector of target wolf (D,).
        leader_position : np.ndarray
            Leader position vector (Alpha, Beta, or Delta) (D,).
        a_param : float
            Current adaptive parameter a(t).
        rng : np.random.Generator
            Random number generator instance.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Coefficient vector A and step vector X_leader_contribution.
        """
        dim = len(wolf_position)
        r1 = rng.random(dim)
        r2 = rng.random(dim)

        A = 2.0 * a_param * r1 - a_param
        C = 2.0 * r2

        D_leader = np.abs(C * leader_position - wolf_position)
        X_contribution = leader_position - A * D_leader

        return A, X_contribution
