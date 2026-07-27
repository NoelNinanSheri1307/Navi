"""
aco_update.py
-------------
Continuous Ant Colony Optimization (ACOR) archive update operator for Navi framework.

Merges newly constructed ant solutions into the solution archive and truncates to top K.
"""

from typing import Tuple
import numpy as np


class ACORArchiveUpdate:
    """
    ACOR Archive Update & Pheromone Deposit Operator.

    Merges evaluated ant candidates into the solution archive, sorts all solutions
    in descending order of fitness, and retains the top K individuals.
    """

    def update_archive(
        self,
        archive: np.ndarray,
        archive_scores: np.ndarray,
        new_ants: np.ndarray,
        new_scores: np.ndarray,
        archive_size: int,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Merge archive and new ant solutions, sort descending by fitness, and keep top K.

        Parameters
        ----------
        archive : np.ndarray
            Current archive matrix of shape (K, D).
        archive_scores : np.ndarray
            Current archive fitness array (K,).
        new_ants : np.ndarray
            Newly evaluated ant positions matrix of shape (N_ants, D).
        new_scores : np.ndarray
            Newly evaluated ant fitness array (N_ants,).
        archive_size : int
            Target archive capacity K.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Updated archive matrix (K, D) and updated fitness array (K,).
        """
        combined_sols = np.vstack([archive, new_ants])
        combined_scores = np.concatenate([archive_scores, new_scores])

        order = np.argsort(combined_scores)[::-1][:archive_size]

        updated_archive = combined_sols[order]
        updated_scores = combined_scores[order]

        return updated_archive, updated_scores
