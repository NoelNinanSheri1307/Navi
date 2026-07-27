"""
de_crossover.py
---------------
Differential Evolution crossover operators for Navi framework.

Implements Binomial Crossover (Storn & Price, 1997).
"""

from typing import Tuple
import numpy as np


class DECrossover:
    """
    Differential Evolution Binomial Crossover Operator.

    Combines target vector components with mutant vector components according to
    crossover probability CR and random dimension forcing.

    Parameters
    ----------
    CR : float
        Crossover rate probability parameter (default 0.9).
    """

    def __init__(self, CR: float = 0.9):
        self.CR = CR

    def cross(
        self,
        target: np.ndarray,
        mutant: np.ndarray,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """
        Perform binomial crossover between target vector and mutant vector.

        Parameters
        ----------
        target : np.ndarray
            Target individual vector of shape (D,).
        mutant : np.ndarray
            Mutant individual vector of shape (D,).
        rng : np.random.Generator
            Random number generator instance.

        Returns
        -------
        np.ndarray
            Trial parameter vector of shape (D,).
        """
        dim = len(target)
        j_rand = rng.integers(0, dim)
        trial = target.copy()

        for j in range(dim):
            if rng.random() < self.CR or j == j_rand:
                trial[j] = mutant[j]

        return trial
