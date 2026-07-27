"""
sa_acceptance.py
----------------
Simulated Annealing Metropolis acceptance criterion operator for Navi framework.

Calculates Metropolis probability P = exp(delta / T) and evaluates probabilistic move acceptance
(Metropolis et al., 1953; Kirkpatrick et al., 1983).
"""

from typing import Tuple
import numpy as np


class SAAcceptanceCriterion:
    """
    SA Metropolis Acceptance Criterion Operator.

    Evaluates whether to accept a candidate neighbor solution based on fitness delta
    and system temperature T.
    """

    @staticmethod
    def calculate_probability(delta_fitness: float, temperature: float) -> float:
        """
        Calculate Metropolis acceptance probability.

        Parameters
        ----------
        delta_fitness : float
            Fitness difference (f_neighbor - f_current).
        temperature : float
            Current system temperature T.

        Returns
        -------
        float
            Metropolis acceptance probability P in [0.0, 1.0].
        """
        if delta_fitness >= 0.0:
            return 1.0
        t_eff = max(temperature, 1e-10)
        return float(np.exp(delta_fitness / t_eff))

    def accept_move(
        self,
        delta_fitness: float,
        temperature: float,
        rng: np.random.Generator,
    ) -> Tuple[bool, float]:
        """
        Evaluate move acceptance decision probabilistically.

        Returns
        -------
        Tuple[bool, float]
            Boolean (accepted_or_not) and float (acceptance_probability).
        """
        prob = self.calculate_probability(delta_fitness, temperature)
        if delta_fitness >= 0.0:
            return True, 1.0
        u = float(rng.uniform(0.0, 1.0))
        return (u < prob), prob
