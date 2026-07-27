"""
pso_topology.py
---------------
Particle Swarm Optimization topology operator for Navi framework.

Implements Global Best (gbest) swarm communication topology and spatial metrics.
"""

from typing import Tuple, Dict, Any
import numpy as np


class PSOTopology:
    """
    PSO Swarm Communication Topology Operator.

    Determines social neighborhood attractors for particles (Global Best default)
    and computes spatial swarm convergence metrics (Swarm Radius).

    Parameters
    ----------
    topology_type : str
        Topology model type (default 'gbest').
    """

    def __init__(self, topology_type: str = "gbest"):
        self.topology_type = topology_type.lower()

    def get_global_best(
        self,
        pbest_positions: np.ndarray,
        pbest_scores: np.ndarray,
    ) -> Tuple[np.ndarray, float, int]:
        """
        Identify global best position and fitness score across particle personal bests.

        Returns
        -------
        Tuple[np.ndarray, float, int]
            gbest_pos (D,), gbest_score (float), and gbest_index (int).
        """
        best_idx = int(np.argmax(pbest_scores))
        gbest_pos = pbest_positions[best_idx].copy()
        gbest_score = float(pbest_scores[best_idx])
        return gbest_pos, gbest_score, best_idx

    @staticmethod
    def calculate_swarm_radius(positions: np.ndarray, gbest_position: np.ndarray) -> float:
        """
        Calculate mean Euclidean distance of all particles relative to global best position.

        Parameters
        ----------
        positions : np.ndarray
            Current position matrix of shape (P, D).
        gbest_position : np.ndarray
            Global best position vector of shape (D,).

        Returns
        -------
        float
            Average spatial radius of the swarm.
        """
        distances = np.linalg.norm(positions - gbest_position, axis=1)
        return float(np.mean(distances))
