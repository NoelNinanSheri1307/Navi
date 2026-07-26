"""
gwo.py — Grey Wolf Optimizer
------------------------------
Standard GWO (Mirjalili et al., 2014).
Optimises the 35-dim fuzzy parameter vector.
"""

import numpy as np
from evaluation.fitness import evaluate_fitness

DIM = 35


def run_gwo(
    csv_path: str = "vanet.csv",
    n_wolves: int = 30,
    n_iter: int = 50,
    seed: int = 42,
) -> dict:
    """
    Run Grey Wolf Optimizer.

    Returns dict with best params, fitness, convergence history,
    and full simulation result.
    """
    rng = np.random.default_rng(seed)

    # ── Initialise pack ──
    wolves = rng.uniform(0.0, 1.0, (n_wolves, DIM))
    scores = np.array([evaluate_fitness(w, csv_path=csv_path, seed=seed)[0] for w in wolves])

    sorted_idx = np.argsort(scores)[::-1]   # descending
    alpha = wolves[sorted_idx[0]].copy();  alpha_s = scores[sorted_idx[0]]
    beta  = wolves[sorted_idx[1]].copy();  beta_s  = scores[sorted_idx[1]]
    delta = wolves[sorted_idx[2]].copy();  delta_s = scores[sorted_idx[2]]

    convergence_history = [float(alpha_s)]

    for it in range(n_iter):
        a = 2.0 - 2.0 * it / n_iter   # linearly decreases from 2 to 0

        for i in range(n_wolves):
            r1, r2 = rng.random(DIM), rng.random(DIM)
            A1 = 2 * a * r1 - a;  C1 = 2 * rng.random(DIM)
            D_alpha = np.abs(C1 * alpha - wolves[i])
            X1 = alpha - A1 * D_alpha

            r1, r2 = rng.random(DIM), rng.random(DIM)
            A2 = 2 * a * r1 - a;  C2 = 2 * rng.random(DIM)
            D_beta = np.abs(C2 * beta - wolves[i])
            X2 = beta - A2 * D_beta

            r1, r2 = rng.random(DIM), rng.random(DIM)
            A3 = 2 * a * r1 - a;  C3 = 2 * rng.random(DIM)
            D_delta = np.abs(C3 * delta - wolves[i])
            X3 = delta - A3 * D_delta

            wolves[i] = np.clip((X1 + X2 + X3) / 3.0, 0.0, 1.0)

        scores = np.array([evaluate_fitness(w, csv_path=csv_path, seed=seed)[0] for w in wolves])

        sorted_idx = np.argsort(scores)[::-1]
        if scores[sorted_idx[0]] > alpha_s:
            alpha = wolves[sorted_idx[0]].copy(); alpha_s = scores[sorted_idx[0]]
        if scores[sorted_idx[1]] > beta_s:
            beta  = wolves[sorted_idx[1]].copy(); beta_s  = scores[sorted_idx[1]]
        if scores[sorted_idx[2]] > delta_s:
            delta = wolves[sorted_idx[2]].copy(); delta_s = scores[sorted_idx[2]]

        convergence_history.append(float(alpha_s))
        print(f"  [GWO] Iter {it+1}/{n_iter}  alpha fitness = {alpha_s:.6f}")

    best_fitness, best_result = evaluate_fitness(alpha, csv_path=csv_path, seed=seed)

    best_result.update({
        'algorithm':           'GWO',
        'fitness':             best_fitness,
        'convergence_history': convergence_history,
    })
    return best_result
