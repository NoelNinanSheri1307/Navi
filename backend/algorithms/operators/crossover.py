"""
crossover.py
------------
Crossover operators for Genetic Algorithms in Navi framework.

Implements Real-Coded Simulated Binary Crossover (SBX) (Deb & Agrawal, 1995).
"""

from typing import Tuple
import numpy as np


class SimulatedBinaryCrossover:
    """
    Simulated Binary Crossover (SBX) Operator.

    Models the probability distribution of single-point crossover in binary-coded
    GA for real-valued decision variables using a distribution index eta_c.

    Parameters
    ----------
    cx_prob : float
        Probability of applying crossover between parents (default 0.85).
    eta_c : float
        Distribution index controlling offspring spread (default 15.0).
    bounds : Tuple[float, float]
        Parameter boundary limits (default (0.0, 1.0)).
    """

    def __init__(
        self,
        cx_prob: float = 0.85,
        eta_c: float = 15.0,
        bounds: Tuple[float, float] = (0.0, 1.0),
    ):
        self.cx_prob = cx_prob
        self.eta_c = eta_c
        self.bounds = bounds

    def cross(
        self,
        parent1: np.ndarray,
        parent2: np.ndarray,
        rng: np.random.Generator,
    ) -> Tuple[np.ndarray, np.ndarray]:
        """
        Apply SBX crossover to generate two offspring from two parents.

        Parameters
        ----------
        parent1 : np.ndarray
            First parent parameter vector (D,).
        parent2 : np.ndarray
            Second parent parameter vector (D,).
        rng : np.random.Generator
            Random number generator instance.

        Returns
        -------
        Tuple[np.ndarray, np.ndarray]
            Two clipped offspring vectors (c1, c2).
        """
        if rng.random() >= self.cx_prob:
            return parent1.copy(), parent2.copy()

        dim = len(parent1)
        c1, c2 = parent1.copy(), parent2.copy()

        for i in range(dim):
            if rng.random() < 0.5:
                u = rng.random()
                if u <= 0.5:
                    beta = (2.0 * u) ** (1.0 / (self.eta_c + 1.0))
                else:
                    beta = (1.0 / (2.0 * (1.0 - u))) ** (1.0 / (self.eta_c + 1.0))

                c1[i] = 0.5 * ((1.0 + beta) * parent1[i] + (1.0 - beta) * parent2[i])
                c2[i] = 0.5 * ((1.0 - beta) * parent1[i] + (1.0 + beta) * parent2[i])

        low, high = self.bounds
        return np.clip(c1, low, high), np.clip(c2, low, high)
