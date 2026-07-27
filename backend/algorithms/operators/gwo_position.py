"""
gwo_position.py
---------------
Grey Wolf Optimizer position update operator for Navi framework.

Averages leadership vector contributions X1, X2, X3 and enforces parameter bounds.
"""

from typing import Tuple
import numpy as np


class GWOPositionUpdate:
    """
    GWO Position Update Operator.

    Averages the three hunting vectors X1 (alpha), X2 (beta), and X3 (delta)
    to update wolf positions in the search space.

    Parameters
    ----------
    bounds : Tuple[float, float]
        Parameter boundary limits (default (0.0, 1.0)).
    """

    def __init__(self, bounds: Tuple[float, float] = (0.0, 1.0)):
        self.bounds = bounds

    def update_position(
        self,
        X1: np.ndarray,
        X2: np.ndarray,
        X3: np.ndarray,
    ) -> np.ndarray:
        """
        Calculate new position by averaging leader vector contributions.

        Parameters
        ----------
        X1 : np.ndarray
            Position contribution from Alpha wolf (D,).
        X2 : np.ndarray
            Position contribution from Beta wolf (D,).
        X3 : np.ndarray
            Position contribution from Delta wolf (D,).

        Returns
        -------
        np.ndarray
            Clipped new position vector of shape (D,).
        """
        new_pos = (X1 + X2 + X3) / 3.0
        low, high = self.bounds
        return np.clip(new_pos, low, high)
