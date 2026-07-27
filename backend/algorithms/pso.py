"""
pso.py — Particle Swarm Optimization (Navi Swarm Optimizer Architecture)
-------------------------------------------------------------------------
Standard Particle Swarm Optimization with linear inertia weight decay and
cognitive/social acceleration (Kennedy & Eberhart, 1995; Shi & Eberhart, 1998).

Refactored to inherit from BaseOptimizer as Navi's first framework-native swarm optimizer.
"""

from typing import Callable, Dict, Any, Tuple, Optional
import numpy as np

from evaluation.fitness import evaluate_fitness
from algorithms.base import (
    BaseOptimizer,
    PopulationState,
    OptimizationResult,
)
from algorithms.operators import (
    PSOVelocityUpdate,
    PSOTopology,
    PSOPositionUpdate,
)

DIM = 35


class ParticleSwarmOptimizer(BaseOptimizer):
    """
    Particle Swarm Optimization Kernel.

    Responsibilities
    ----------------
    1. Continuous global swarm optimization over [0,1]^35 fuzzy parameter space.
    2. Modular operator delegation (Velocity Update, Swarm Topology, Position Update & Pbest Tracking).
    3. Iterative state-machine lifecycle via initialize() and step().
    4. Swarm telemetry calculation (velocity norm, swarm radius, spatial diversity).

    ASM & Framework Integration
    ---------------------------
    - Step-Level Control: ASM can pause after any swarm iteration to re-allocate budget.
    - Auxiliary Swarm State: Velocities, personal bests, and global best stored in PopulationState.
    - State Export: Serializes position matrix, velocity tensor, and pbest arrays for strategy switching.
    """

    def __init__(
        self,
        dim: int = DIM,
        bounds: Tuple[float, float] = (0.0, 1.0),
        budget: int = 10000,
        n_particles: int = 30,
        pop_size: Optional[int] = None,
        w_start: float = 0.9,
        w_end: float = 0.4,
        c1: float = 2.0,
        c2: float = 2.0,
        v_max: Optional[float] = None,
        seed: int = 42,
        verbose: bool = True,
    ):
        super().__init__(
            name="PSO",
            dim=dim,
            bounds=bounds,
            budget=budget,
            seed=seed,
            verbose=verbose,
        )
        self.n_particles = pop_size if pop_size is not None else n_particles
        self.w_start = w_start
        self.w_end = w_end
        self.c1 = c1
        self.c2 = c2
        self.total_iters = 50

        # Swarm Operators
        self.velocity_operator = PSOVelocityUpdate(
            w_start=w_start, w_end=w_end, c1=c1, c2=c2, v_max=v_max
        )
        self.topology = PSOTopology(topology_type="gbest")
        self.position_operator = PSOPositionUpdate(bounds=bounds)

        # Auxiliary Swarm State Tensors
        self.velocities: Optional[np.ndarray] = None
        self.pbest_positions: Optional[np.ndarray] = None
        self.pbest_scores: Optional[np.ndarray] = None

    def initialize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        n_particles: Optional[int] = None,
        pop_size: Optional[int] = None,
    ) -> PopulationState:
        """
        Initialize particle positions, velocity vectors, and evaluate personal/global bests.
        """
        p_count = pop_size if pop_size is not None else n_particles
        if p_count is not None:
            self.n_particles = p_count

        self.reset()

        # Position sampling over [0, 1]^35
        pos = self.rng.uniform(self.bounds[0], self.bounds[1], (self.n_particles, self.dim))
        # Initial velocity sampling over [-0.1, 0.1]^35
        self.velocities = self.rng.uniform(-0.1, 0.1, (self.n_particles, self.dim))

        # Initial fitness evaluation
        scores = self.evaluate_population(pos, fitness_fn)

        self.pbest_positions = pos.copy()
        self.pbest_scores = scores.copy()

        gbest_pos, gbest_score, _ = self.topology.get_global_best(
            self.pbest_positions, self.pbest_scores
        )

        self.state = PopulationState(
            population=pos,
            fitness=scores,
            best_solution=gbest_pos,
            best_fitness=gbest_score,
            evaluation_count=self.evaluations_used,
            generation=0,
            metadata={
                "velocities": self.velocities.copy(),
                "pbest_positions": self.pbest_positions.copy(),
                "pbest_scores": self.pbest_scores.copy(),
                "w_start": self.w_start,
                "w_end": self.w_end,
                "c1": self.c1,
                "c2": self.c2,
            },
        )

        return self.state

    def step(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
    ) -> PopulationState:
        """
        Execute exactly one iteration step of Particle Swarm Optimization.
        """
        if self.state is None or self.velocities is None:
            raise RuntimeError("Optimizer not initialized. Call initialize() first.")

        pos = self.state.population
        gbest_pos = self.state.best_solution

        # 1. Update velocities
        self.velocities = self.velocity_operator.update_velocity(
            positions=pos,
            velocities=self.velocities,
            pbest_positions=self.pbest_positions,
            gbest_position=gbest_pos,
            current_iter=self.generation,
            total_iters=self.total_iters,
            rng=self.rng,
        )

        # 2. Update positions
        pos = self.position_operator.update_positions(pos, self.velocities)

        # 3. Evaluate new positions
        scores = self.evaluate_population(pos, fitness_fn)

        # 4. Update personal bests
        self.pbest_positions, self.pbest_scores = self.position_operator.update_personal_bests(
            positions=pos,
            current_scores=scores,
            pbest_positions=self.pbest_positions,
            pbest_scores=self.pbest_scores,
        )

        # 5. Update global best
        gbest_pos, gbest_score, _ = self.topology.get_global_best(
            self.pbest_positions, self.pbest_scores
        )

        self.generation += 1

        # Calculate Swarm Metrics
        diversity = float(np.mean(np.std(pos, axis=0)))
        vel_norm = self.velocity_operator.calculate_velocity_norm(self.velocities)
        swarm_radius = self.topology.calculate_swarm_radius(pos, gbest_pos)

        # Update state
        self.state = PopulationState(
            population=pos,
            fitness=scores,
            best_solution=gbest_pos,
            best_fitness=gbest_score,
            evaluation_count=self.evaluations_used,
            generation=self.generation,
            metadata={
                "velocities": self.velocities.copy(),
                "pbest_positions": self.pbest_positions.copy(),
                "pbest_scores": self.pbest_scores.copy(),
                "diversity": diversity,
                "velocity_norm": vel_norm,
                "swarm_radius": swarm_radius,
            },
        )

        # Telemetry logging
        self.logger.log_step(
            generation=self.generation,
            evaluation_count=self.evaluations_used,
            best_fitness=gbest_score,
            mean_fitness=float(np.mean(scores)),
            worst_fitness=float(np.min(scores)),
            diversity_index=diversity,
        )

        return self.state

    def optimize(
        self,
        fitness_fn: Callable[[np.ndarray], Tuple[float, Dict[str, Any]]],
        n_particles: Optional[int] = None,
        n_iter: int = 50,
    ) -> OptimizationResult:
        """
        Execute full swarm search up to max iterations or budget exhaustion.
        """
        self.total_iters = n_iter
        p_count = n_particles if n_particles is not None else self.n_particles
        self.initialize(fitness_fn, n_particles=p_count)
        self.logger.start(initial_fitness=self.state.best_fitness)

        for _ in range(n_iter):
            if self.is_budget_exhausted():
                break
            self.step(fitness_fn)

        best_ind = self.get_best_solution()
        best_fitness, best_result = fitness_fn(best_ind)
        stats = self.get_statistics()

        return OptimizationResult(
            algorithm=self.name,
            best_solution=best_ind,
            fitness=best_fitness,
            green_times=best_result.get("green_times", []),
            cycle_time=best_result.get("cycle_time", 120),
            avg_speed=best_result.get("avg_speed", 0.0),
            avg_density=best_result.get("avg_density", 0.0),
            avg_wait_time=best_result.get("avg_wait_time", 0.0),
            total_flow=best_result.get("total_flow", 0.0),
            avg_queue_length=best_result.get("avg_queue_length", 0.0),
            congestion_pressure=best_result.get("congestion_pressure", 0.0),
            speed_density_ratio=best_result.get("speed_density_ratio", 0.0),
            convergence_history=self.get_history(),
            simulation_steps=best_result.get("simulation_steps", []),
            statistics=stats,
        )

    def export_state(self) -> Dict[str, Any]:
        """Export state dictionary including auxiliary swarm state tensors."""
        base_state = super().export_state()
        if self.velocities is not None:
            base_state["velocities"] = self.velocities.copy()
        if self.pbest_positions is not None:
            base_state["pbest_positions"] = self.pbest_positions.copy()
        if self.pbest_scores is not None:
            base_state["pbest_scores"] = self.pbest_scores.copy()
        return base_state

    def restore_state(self, state_dict: Dict[str, Any]) -> None:
        """Restore internal search state including auxiliary swarm state tensors."""
        super().restore_state(state_dict)
        if "velocities" in state_dict:
            self.velocities = state_dict["velocities"].copy()
        if "pbest_positions" in state_dict:
            self.pbest_positions = state_dict["pbest_positions"].copy()
        if "pbest_scores" in state_dict:
            self.pbest_scores = state_dict["pbest_scores"].copy()


# ─────────────────────────────────────────────────────────────────────────────
# Backward-Compatible Wrapper Function
# ─────────────────────────────────────────────────────────────────────────────
def run_pso(
    csv_path: str = "vanet.csv",
    n_particles: int = 30,
    n_iter: int = 50,
    w_start: float = 0.9,
    w_end: float = 0.4,
    c1: float = 2.0,
    c2: float = 2.0,
    seed: int = 42,
) -> dict:
    """
    Backward-compatible wrapper function for Particle Swarm Optimization.

    Preserves function signature expected by main.py, run_algo_graphs.py, and external callers.
    """
    def fitness_fn(cand):
        return evaluate_fitness(cand, csv_path=csv_path, seed=seed)

    pso = ParticleSwarmOptimizer(
        n_particles=n_particles,
        w_start=w_start,
        w_end=w_end,
        c1=c1,
        c2=c2,
        seed=seed,
        verbose=True,
    )

    res = pso.optimize(fitness_fn=fitness_fn, n_particles=n_particles, n_iter=n_iter)
    return res.to_dict()
