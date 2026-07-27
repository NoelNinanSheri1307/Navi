"""
selection.py
------------
Selection operators for Genetic Algorithms in Navi framework.

Implements Tournament Selection with configurable tournament size k.
"""

from typing import Tuple
import numpy as np


class TournamentSelection:
    """
    Tournament Selection Operator.

    Selects an individual from a population matrix by sampling k random candidate
    indices and selecting the individual with the highest fitness score.

    Parameters
    ----------
    k : int
        Tournament size (number of candidates sampled per tournament, default 5).
    """

    def __init__(self, k: int = 5):
        self.k = k

    def select(
        self,
        population: np.ndarray,
        fitness_scores: np.ndarray,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """
        Select one individual from population via k-tournament selection.

        Parameters
        ----------
        population : np.ndarray
            Array of shape (P, D) containing population vectors.
        fitness_scores : np.ndarray
            Array of shape (P,) containing fitness values.
        rng : np.random.Generator
            Random number generator instance.

        Returns
        -------
        np.ndarray
            Selected candidate parameter vector of shape (D,).
        """
        pop_size = len(population)
        idx = rng.integers(0, pop_size, self.k)
        best_of_k = idx[np.argmax(fitness_scores[idx])]
        return population[best_of_k].copy()
