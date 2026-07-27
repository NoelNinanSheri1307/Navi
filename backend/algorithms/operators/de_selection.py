"""
de_selection.py
---------------
Differential Evolution selection operators for Navi framework.

Implements Greedy One-to-One Selection (Storn & Price, 1997).
"""

from typing import Tuple
import numpy as np


class DESelection:
    """
    Differential Evolution Greedy Selection Operator.

    Compares trial offspring fitness against target parent fitness. Replaces parent
    if trial fitness is strictly superior or equal.
    """

    def select(
        self,
        target_individual: np.ndarray,
        target_fitness: float,
        trial_individual: np.ndarray,
        trial_fitness: float,
    ) -> Tuple[np.ndarray, float, bool]:
        """
        Perform greedy parent-vs-trial selection.

        Parameters
        ----------
        target_individual : np.ndarray
            Target parent parameter vector (D,).
        target_fitness : float
            Fitness value of target parent.
        trial_individual : np.ndarray
            Trial offspring parameter vector (D,).
        trial_fitness : float
            Fitness value of trial offspring.

        Returns
        -------
        Tuple[np.ndarray, float, bool]
            Selected vector (D,), selected fitness, and boolean indicating if trial replaced parent.
        """
        if trial_fitness > target_fitness:
            return trial_individual.copy(), float(trial_fitness), True
        return target_individual.copy(), float(target_fitness), False
