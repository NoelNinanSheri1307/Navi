"""
pso.py — Particle Swarm Optimization
--------------------------------------
Standard PSO with inertia weight decay.
Optimises the 35-dim fuzzy parameter vector.
"""

import numpy as np
from evaluation.fitness import evaluate_fitness

DIM = 35


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
    Run Particle Swarm Optimization.

    Returns dict with best params, fitness, convergence history,
    and full simulation result.
    """
    rng = np.random.default_rng(seed)

    # ── Initialise ──
    pos  = rng.uniform(0.0, 1.0, (n_particles, DIM))
    vel  = rng.uniform(-0.1, 0.1, (n_particles, DIM))
    pbest_pos = pos.copy()

    pbest_scores = np.array([
        evaluate_fitness(p, csv_path=csv_path, seed=seed)[0] for p in pos
    ])

    gbest_idx   = int(np.argmax(pbest_scores))
    gbest_pos   = pbest_pos[gbest_idx].copy()
    gbest_score = pbest_scores[gbest_idx]

    convergence_history = [float(gbest_score)]

    for it in range(n_iter):
        w = w_start - (w_start - w_end) * (it / n_iter)

        r1 = rng.uniform(0, 1, (n_particles, DIM))
        r2 = rng.uniform(0, 1, (n_particles, DIM))

        vel = (
            w * vel
            + c1 * r1 * (pbest_pos - pos)
            + c2 * r2 * (gbest_pos  - pos)
        )
        pos = np.clip(pos + vel, 0.0, 1.0)

        for i, p in enumerate(pos):
            f, _ = evaluate_fitness(p, csv_path=csv_path, seed=seed)
            if f > pbest_scores[i]:
                pbest_scores[i] = f
                pbest_pos[i]    = p.copy()
            if f > gbest_score:
                gbest_score = f
                gbest_pos   = p.copy()

        convergence_history.append(float(gbest_score))
        print(f"  [PSO] Iter {it+1}/{n_iter}  best fitness = {gbest_score:.6f}")

    best_fitness, best_result = evaluate_fitness(gbest_pos, csv_path=csv_path, seed=seed)

    best_result.update({
        'algorithm':           'PSO',
        'fitness':             best_fitness,
        'convergence_history': convergence_history,
    })
    return best_result
