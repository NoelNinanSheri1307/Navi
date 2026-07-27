"""
aco_transition.py
-----------------
Continuous Ant Colony Optimization (ACOR) ant sampling transition operator for Navi.

Samples new ant solution vectors from Gaussian mixture distributions centered at archive templates.
"""

from typing import Tuple, Any
import numpy as np


class ACORTransition:
    """
    ACOR Ant Transition & Solution Sampling Operator.

    Selects an archive template based on rank weights and samples a new ant solution
    vector using per-dimension Gaussian standard deviations.

    Parameters
    ----------
    bounds : Tuple[float, float]
        Parameter boundary limits (default (0.0, 1.0)).
    """

    def __init__(self, bounds: Tuple[float, float] = (0.0, 1.0)):
        self.bounds = bounds

    def sample_ant(
        self,
        archive: np.ndarray,
        weights: np.ndarray,
        pheromone_op: Any,
        rng: np.random.Generator,
    ) -> Tuple[np.ndarray, int]:
        """
        Sample one ant candidate vector from the solution archive.

        Parameters
        ----------
        archive : np.ndarray
            Solution archive matrix of shape (K, D).
        weights : np.ndarray
            Rank selection weights vector (K,).
        pheromone_op : Any
            ACORArchivePheromone instance to compute dimension sigmas.
        rng : np.random.Generator
            Random number generator instance.

        Returns
        -------
        Tuple[np.ndarray, int]
            Sampled ant position vector (D,) and selected template index.
        """
        archive_size = len(archive)
        chosen_idx = int(rng.choice(archive_size, p=weights))
        template = archive[chosen_idx]

        sigma = pheromone_op.compute_dimension_sigmas(archive, chosen_idx)
        sampled = rng.normal(template, sigma)

        low, high = self.bounds
        return np.clip(sampled, low, high), chosen_idx
