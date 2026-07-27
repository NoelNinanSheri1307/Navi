"""
local_search.py
---------------
Local search and fine-tuning operators for Navi framework optimizers.

Implements Lamarckian Local Search hill-climbing perturbation strategy.
Can be invoked optionally by GA, future optimizers, or the ASM framework.
"""

from typing import Callable, Tuple, Dict, Any
import numpy as np


class LamarckianLocalSearch:
    """
    Lamarckian Local Search Hill-Climbing Operator.

    Performs stochastic local perturbations around a champion candidate vector
    to fine-tune solutions in narrow optima basins.

    Parameters
    ----------
    n_steps : int
        Number of local perturbation trials (default 100).
    step_std : float
        Standard deviation of Gaussian noise perturbation (default 0.01).
    bounds : Tuple[float, float]
        Parameter boundary limits (default (0.0, 1.0)).
    """

    def __init__(
        self,
        n_steps: int = 100,
        step_std: float = 0.01,
        bounds: Tuple[float, float] = (0.0, 1.0),
    ):
        self.n_steps = n_steps
        self.step_std = step_std
        self.bounds = bounds

    def search(
        self,
        champion: np.ndarray,
        champion_fitness: float,
        eval_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        rng: np.random.Generator,
    ) -> Tuple[np.ndarray, float, int]:
        """
        Execute hill-climbing fine-tuning search around champion vector.

        Parameters
        ----------
        champion : np.ndarray
            Current champion parameter vector (D,).
        champion_fitness : float
            Fitness score of current champion.
        eval_fn : Callable
            Fitness evaluation function wrapper returning (fitness, result_dict).
        rng : np.random.Generator
            Random number generator instance.

        Returns
        -------
        Tuple[np.ndarray, float, int]
            Refined champion vector, refined fitness score, and evaluations executed.
        """
        refined_ind = champion.copy()
        refined_f = champion_fitness
        dim = len(champion)
        low, high = self.bounds
        evals_executed = 0

        for _ in range(self.n_steps):
            perturbation = rng.normal(0.0, self.step_std, dim)
            candidate = np.clip(refined_ind + perturbation, low, high)
            cf, _ = eval_fn(candidate)
            evals_executed += 1

            if cf > refined_f:
                refined_f = cf
                refined_ind = candidate.copy()

        return refined_ind, float(refined_f), evals_executed
