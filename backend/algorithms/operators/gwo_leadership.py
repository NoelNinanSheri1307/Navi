"""
gwo_leadership.py
-----------------
Grey Wolf Optimizer leadership hierarchy operator for Navi framework.

Manages alpha, beta, and delta wolf pack hierarchy ranking and position updates
(Mirjalili et al., 2014).
"""

from typing import Tuple, Dict, Any
import numpy as np


class GWOLeadership:
    """
    GWO Leadership Hierarchy Operator.

    Identifies and updates top 3 leaders (Alpha, Beta, Delta) based on candidate
    fitness scores.
    """

    @staticmethod
    def identify_leaders(
        population: np.ndarray,
        scores: np.ndarray,
    ) -> Tuple[np.ndarray, float, np.ndarray, float, np.ndarray, float]:
        """
        Extract alpha, beta, and delta leader vectors and fitness scores from population.

        Returns
        -------
        Tuple containing (alpha_pos, alpha_score, beta_pos, beta_score, delta_pos, delta_score).
        """
        sorted_idx = np.argsort(scores)[::-1]  # Descending order

        alpha_pos = population[sorted_idx[0]].copy()
        alpha_score = float(scores[sorted_idx[0]])

        beta_pos = population[sorted_idx[1]].copy() if len(population) > 1 else alpha_pos.copy()
        beta_score = float(scores[sorted_idx[1]]) if len(population) > 1 else alpha_score

        delta_pos = population[sorted_idx[2]].copy() if len(population) > 2 else beta_pos.copy()
        delta_score = float(scores[sorted_idx[2]]) if len(population) > 2 else beta_score

        return alpha_pos, alpha_score, beta_pos, beta_score, delta_pos, delta_score

    @staticmethod
    def update_leaders(
        population: np.ndarray,
        scores: np.ndarray,
        alpha_pos: np.ndarray,
        alpha_score: float,
        beta_pos: np.ndarray,
        beta_score: float,
        delta_pos: np.ndarray,
        delta_score: float,
    ) -> Tuple[np.ndarray, float, np.ndarray, float, np.ndarray, float]:
        """
        Update historical leaders if current population contains superior candidates.
        """
        sorted_idx = np.argsort(scores)[::-1]

        c0_pos, c0_score = population[sorted_idx[0]], float(scores[sorted_idx[0]])
        c1_pos, c1_score = population[sorted_idx[1]], float(scores[sorted_idx[1]])
        c2_pos, c2_score = population[sorted_idx[2]], float(scores[sorted_idx[2]])

        if c0_score > alpha_score:
            alpha_pos, alpha_score = c0_pos.copy(), c0_score

        if c1_score > beta_score:
            beta_pos, beta_score = c1_pos.copy(), c1_score

        if c2_score > delta_score:
            delta_pos, delta_score = c2_pos.copy(), c2_score

        return alpha_pos, alpha_score, beta_pos, beta_score, delta_pos, delta_score
