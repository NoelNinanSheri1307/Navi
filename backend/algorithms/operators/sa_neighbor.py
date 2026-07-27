"""
sa_neighbor.py
--------------
Simulated Annealing neighbor generation operator for Navi framework.

Generates candidate neighbor solution vectors via Gaussian perturbation with boundary clipping
(Kirkpatrick et al., 1983).
"""

from typing import Tuple
import numpy as np


class SANeighborGenerator:
    """
    SA Neighbor Generator Operator.

    Applies Gaussian perturbation noise to current solution vector and clips to bounds.

    Parameters
    ----------
    bounds : Tuple[float, float]
        Parameter boundary limits (default (0.0, 1.0)).
    step_size : float
        Standard deviation for Gaussian perturbation noise (default 0.05).
    """

    def __init__(
        self,
        bounds: Tuple[float, float] = (0.0, 1.0),
        step_size: float = 0.05,
    ):
        self.bounds = bounds
        self.step_size = step_size

    def generate_neighbor(
        self,
        current_solution: np.ndarray,
        rng: np.random.Generator,
        scale: float = 1.0,
    ) -> np.ndarray:
        """
        Generate candidate neighbor vector by adding Gaussian noise.

        Parameters
        ----------
        current_solution : np.ndarray
            Current trajectory solution vector of shape (D,).
        rng : np.random.Generator
            Random number generator instance.
        scale : float
            Optional temperature scaling factor for adaptive step sizes.

        Returns
        -------
        np.ndarray
            Clipped neighbor solution vector of shape (D,).
        """
        dim = len(current_solution)
        noise = rng.normal(0.0, self.step_size * scale, size=dim)
        neighbor = current_solution + noise
        low, high = self.bounds
        return np.clip(neighbor, low, high)
