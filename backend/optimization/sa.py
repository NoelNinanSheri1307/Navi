"""
sa.py — Simulated Annealing
-----------------------------
Standard SA with geometric cooling schedule and Gaussian perturbation.
Optimises the 35-dim fuzzy parameter vector.
"""

import numpy as np
from evaluation.fitness import evaluate_fitness

DIM = 35


def run_sa(
    csv_path: str = "vanet.csv",
    n_iter: int = 500,
    T_start: float = 1.0,
    T_end: float = 0.001,
    step_size: float = 0.1,
    seed: int = 42,
) -> dict:
    """
    Run Simulated Annealing.

    Returns dict with best params, fitness, convergence history,
    and full simulation result.
    """
    rng = np.random.default_rng(seed)

    # Cooling factor for geometric schedule
    alpha = (T_end / T_start) ** (1.0 / n_iter)

    # ── Initialise ──
    current = rng.uniform(0.0, 1.0, DIM)
    current_f, _ = evaluate_fitness(current, csv_path=csv_path, seed=seed)

    best    = current.copy()
    best_f  = current_f
    T       = T_start

    convergence_history = [float(best_f)]

    for it in range(n_iter):
        # Gaussian neighbour
        candidate = np.clip(current + rng.normal(0, step_size, DIM), 0.0, 1.0)
        cand_f, _ = evaluate_fitness(candidate, csv_path=csv_path, seed=seed)
        

        delta = cand_f - current_f
        if delta > 0 or rng.random() < np.exp(delta / T):
            current   = candidate
            current_f = cand_f

        if current_f > best_f:
            best   = current.copy()
            best_f = current_f

        T *= alpha

        if (it + 1) % 10 == 0:
            convergence_history.append(float(best_f))
            print(f"  [SA] Iter {it+1}/{n_iter}  T={T:.6f}  best fitness = {best_f:.6f}")

    best_fitness, best_result = evaluate_fitness(best, csv_path=csv_path, seed=seed)

    best_result.update({
        'algorithm':           'SA',
        'fitness':             best_fitness,
        'convergence_history': convergence_history,
    })
    return best_result
