"""
pso_velocity.py
---------------
Particle Swarm Optimization velocity update operator for Navi framework.

Implements inertia weight decay and cognitive/social acceleration velocity updates
(Kennedy & Eberhart, 1995; Shi & Eberhart, 1998).
"""

from typing import Tuple, Optional
import numpy as np


class PSOVelocityUpdate:
    """
    PSO Velocity Update Operator.

    Calculates particle velocity vectors based on inertia decay w, cognitive acceleration c1,
    and social acceleration c2.

    Parameters
    ----------
    w_start : float
        Initial inertia weight (default 0.9).
    w_end : float
        Final inertia weight (default 0.4).
    c1 : float
        Cognitive acceleration coefficient (default 2.0).
    c2 : float
        Social acceleration coefficient (default 2.0).
    v_max : Optional[float]
        Optional maximum velocity magnitude clamp threshold.
    """

    def __init__(
        self,
        w_start: float = 0.9,
        w_end: float = 0.4,
        c1: float = 2.0,
        c2: float = 2.0,
        v_max: Optional[float] = None,
    ):
        self.w_start = w_start
        self.w_end = w_end
        self.c1 = c1
        self.c2 = c2
        self.v_max = v_max

    def compute_inertia_weight(self, current_iter: int, total_iters: int) -> float:
        """Calculate linearly decaying inertia weight w for current iteration."""
        if total_iters <= 1:
            return self.w_end
        progress = min(max(current_iter / total_iters, 0.0), 1.0)
        return self.w_start - (self.w_start - self.w_end) * progress

    def update_velocity(
        self,
        positions: np.ndarray,
        velocities: np.ndarray,
        pbest_positions: np.ndarray,
        gbest_position: np.ndarray,
        current_iter: int,
        total_iters: int,
        rng: np.random.Generator,
    ) -> np.ndarray:
        """
        Update particle velocity matrix of shape (P, D).

        Parameters
        ----------
        positions : np.ndarray
            Current position matrix of shape (P, D).
        velocities : np.ndarray
            Current velocity matrix of shape (P, D).
        pbest_positions : np.ndarray
            Personal best position matrix of shape (P, D).
        gbest_position : np.ndarray
            Global best position vector of shape (D,).
        current_iter : int
            Current iteration index.
        total_iters : int
            Total planned iterations.
        rng : np.random.Generator
            Random number generator instance.

        Returns
        -------
        np.ndarray
            Updated velocity matrix of shape (P, D).
        """
        n_particles, dim = positions.shape
        w = self.compute_inertia_weight(current_iter, total_iters)

        r1 = rng.uniform(0.0, 1.0, (n_particles, dim))
        r2 = rng.uniform(0.0, 1.0, (n_particles, dim))

        cognitive = self.c1 * r1 * (pbest_positions - positions)
        social = self.c2 * r2 * (gbest_position - positions)

        new_velocities = w * velocities + cognitive + social

        if self.v_max is not None:
            new_velocities = np.clip(new_velocities, -self.v_max, self.v_max)

        return new_velocities

    @staticmethod
    def calculate_velocity_norm(velocities: np.ndarray) -> float:
        """Calculate mean Euclidean norm across all particle velocity vectors."""
        norms = np.linalg.norm(velocities, axis=1)
        return float(np.mean(norms))
