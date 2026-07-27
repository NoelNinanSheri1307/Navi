"""
aco_pheromone.py
----------------
Continuous Ant Colony Optimization (ACOR) archive pheromone operator for Navi.

Calculates rank-based selection probability weights and per-dimension Gaussian
kernel standard deviations (Socha & Dorigo, 2008).
"""

from typing import Tuple
import numpy as np


class ACORArchivePheromone:
    """
    ACOR Archive Pheromone & Kernel Parameter Operator.

    Manages continuous domain pheromone representation via a solution archive,
    rank-based selection probabilities, and Gaussian mixture standard deviations.

    Parameters
    ----------
    q : float
        Search locality parameter (smaller = more localized search, default 0.1).
    xi : float
        Convergence rate / evaporation factor (default 0.85).
    """

    def __init__(self, q: float = 0.1, xi: float = 0.85):
        self.q = q
        self.xi = xi

    def compute_rank_weights(self, archive_size: int) -> np.ndarray:
        """
        Calculate normalized Gaussian rank selection weights for archive members.

        Parameters
        ----------
        archive_size : int
            Number of solutions stored in the archive.

        Returns
        -------
        np.ndarray
            Probability vector of shape (archive_size,) summing to 1.0.
        """
        ranks = np.arange(1, archive_size + 1, dtype=float)
        w = np.exp(-((ranks - 1.0) ** 2) / (2.0 * (self.q ** 2) * (archive_size ** 2)))
        return w / w.sum()

    def compute_dimension_sigmas(
        self,
        archive: np.ndarray,
        template_idx: int,
    ) -> np.ndarray:
        """
        Calculate per-dimension Gaussian standard deviation vector sigma for selected template.

        Parameters
        ----------
        archive : np.ndarray
            Solution archive matrix of shape (K, D).
        template_idx : int
            Index of selected template solution in archive.

        Returns
        -------
        np.ndarray
            Per-dimension standard deviation vector sigma of shape (D,).
        """
        archive_size, dim = archive.shape
        template = archive[template_idx]
        sigma = np.zeros(dim, dtype=float)

        for d in range(dim):
            abs_diff_sum = np.sum(np.abs(archive[:, d] - template[d]))
            sigma[d] = self.xi * abs_diff_sum / (archive_size - 1.0 + 1e-9)
            sigma[d] = max(sigma[d], 1e-4)

        return sigma
