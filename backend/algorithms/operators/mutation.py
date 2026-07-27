"""
mutation.py
-----------
Mutation operators for Genetic Algorithms in Navi framework.

Implements Real-Coded Polynomial Mutation (Deb & Goyal, 1996).
"""

from typing import Tuple
import numpy as np


class PolynomialMutation:
    """
    Polynomial Mutation Operator.

    Perturbs individual variables using a polynomial distribution perturbation
    parameterized by distribution index eta_m.

    Parameters
    ----------
    mut_prob : float
        Per-gene mutation probability (default 0.15).
    eta_m : float
        Distribution index controlling perturbation magnitude (default 20.0).
    bounds : Tuple[float, float]
        Parameter boundary limits (default (0.0, 1.0)).
    """

    def __init__(
        self,
        mut_prob: float = 0.15,
        eta_m: float = 20.0,
        bounds: Tuple[float, float] = (0.0, 1.0),
    ):
        self.mut_prob = mut_prob
        self.eta_m = eta_m
        self.bounds = bounds

    def mutate(
        self,
        individual: np.ndarray,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """
        Apply polynomial mutation to candidate vector.

        Parameters
        ----------
        individual : np.ndarray
            Input candidate vector (D,).
        rng : np.random.Generator
            Random number generator instance.

        Returns
        -------
        np.ndarray
            Mutated and clipped candidate vector (D,).
        """
        child = individual.copy()
        dim = len(child)
        low, high = self.bounds

        for i in range(dim):
            if rng.random() < self.mut_prob:
                u = rng.random()
                if u < 0.5:
                    delta = (2.0 * u) ** (1.0 / (self.eta_m + 1.0)) - 1.0
                else:
                    delta = 1.0 - (2.0 * (1.0 - u)) ** (1.0 / (self.eta_m + 1.0))

                child[i] = np.clip(child[i] + delta, low, high)

        return child
