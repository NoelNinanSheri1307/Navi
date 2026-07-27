"""
pso_update.py
-------------
Particle Swarm Optimization position update operator for Navi framework.

Applies position updates and manages personal best (pbest) particle records.
"""

from typing import Tuple
import numpy as np


class PSOPositionUpdate:
    """
    PSO Position Update Operator.

    Applies velocity steps to particle positions with boundary clipping, and updates
    personal best (pbest) position and fitness records.

    Parameters
    ----------
    bounds : Tuple[float, float]
        Parameter boundary limits (default (0.0, 1.0)).
    """

    def __init__(self, bounds: Tuple[float, float] = (0.0, 1.0)):
        self.bounds = bounds

    def update_positions(
        self,
        positions: np.ndarray,
        velocities: np.ndarray,
    ) -> np.ndarray:
        """
        Advance particle positions by adding velocity vector and clipping to bounds.

        Parameters
        ----------
        positions : np.ndarray
            Current position matrix of shape (P, D).
        velocities : np.ndarray
            Current velocity matrix of shape (P, D).

        Returns
        -------
        np.ndarray
            Clipped updated position matrix of shape (P, D).
        """
        low, high = self.bounds
        return np.clip(positions + velocities, low, high)

    def update_personal_bests(
        self,
        positions: np.ndarray,
        current_scores: np.ndarray,
        pbest_positions: np.ndarray,
        pbest_scores: np.ndarray,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Update personal best position vectors and personal best fitness scores.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Updated (pbest_positions, pbest_scores).
        """
        updated_pbest_pos = pbest_positions.copy()
        updated_pbest_scores = pbest_scores.copy()

        for i, f in enumerate(current_scores):
            if f > updated_pbest_scores[i]:
                updated_pbest_scores[i] = float(f)
                updated_pbest_pos[i] = positions[i].copy()

        return updated_pbest_pos, updated_pbest_scores
