"""
de_mutation.py
--------------
Differential Evolution mutation operators for Navi framework.

Implements DE mutation strategies including DE/rand/1, DE/best/1, and
DE/current-to-best/1 (Storn & Price, 1997).
"""

from typing import Tuple, List, Optional
import numpy as np


class DEMutation:
    """
    Differential Evolution Mutation Operator.

    Generates a donor/mutant vector by combining parameter vectors sampled from
    the current population according to the selected strategy.

    Supported Strategies
    --------------------
    - 'rand/1' : v = a + F * (b - c)  [Default Classic Strategy]
    - 'best/1' : v = best + F * (a - b)
    - 'current-to-best/1' : v = target + F * (best - target) + F * (a - b)

    Parameters
    ----------
    F : float
        Differential mutation scale factor (default 0.8).
    strategy : str
        Mutation strategy identifier (default 'rand/1').
    bounds : Tuple[float, float]
        Parameter boundary limits (default (0.0, 1.0)).
    """

    def __init__(
        self,
        F: float = 0.8,
        strategy: str = "rand/1",
        bounds: Tuple[float, float] = (0.0, 1.0),
    ):
        self.F = F
        self.strategy = strategy.lower()
        self.bounds = bounds

    def mutate(
        self,
        target_idx: int,
        population: np.ndarray,
        best_individual: np.ndarray,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """
        Generate a mutated candidate vector for target individual at target_idx.

        Parameters
        ----------
        target_idx : int
            Index of target individual in population.
        population : np.ndarray
            Current population matrix of shape (P, D).
        best_individual : np.ndarray
            Current global best parameter vector (D,).
        rng : np.random.Generator
            Random number generator instance.

        Returns
        -------
        np.ndarray
            Clipped mutant vector of shape (D,).
        """
        pop_size = len(population)
        candidates = [i for i in range(pop_size) if i != target_idx]

        if self.strategy == "rand/1":
            r = rng.choice(candidates, 3, replace=False)
            a, b, c = population[r[0]], population[r[1]], population[r[2]]
            mutant = a + self.F * (b - c)

        elif self.strategy == "best/1":
            r = rng.choice(candidates, 2, replace=False)
            a, b = population[r[0]], population[r[1]]
            mutant = best_individual + self.F * (a - b)

        elif self.strategy == "current-to-best/1":
            r = rng.choice(candidates, 2, replace=False)
            a, b = population[r[0]], population[r[1]]
            target = population[target_idx]
            mutant = target + self.F * (best_individual - target) + self.F * (a - b)

        else:
            raise ValueError(f"Unsupported DE mutation strategy: '{self.strategy}'")

        low, high = self.bounds
        return np.clip(mutant, low, high)
