"""
aco.py — Ant Colony Optimization (continuous domain)
-----------------------------------------------------
Implements the ACO for Continuous Domains (ACOR) variant where each
ant samples from a Gaussian mixture built from the solution archive.
This optimises a 35-dim real-valued fuzzy parameter vector — NOT paths.

Reference: Socha & Dorigo, 2008 – "Ant colony optimization for continuous domains"
"""

import numpy as np
from evaluation.fitness import evaluate_fitness

DIM = 35


def run_aco(
    csv_path: str = "vanet.csv",
    n_ants: int = 20,
    archive_size: int = 30,
    n_iter: int = 50,
    q: float = 0.1,        # locality of search (smaller = more focused)
    xi: float = 0.85,      # evaporation / speed of convergence
    seed: int = 42,
) -> dict:
    """
    Run ACO for Continuous Domains (ACOR).

    Returns dict with best params, fitness, convergence history,
    and full simulation result.
    """
    rng = np.random.default_rng(seed)

    # ── Build initial solution archive ──
    archive = rng.uniform(0.0, 1.0, (archive_size, DIM))
    scores  = np.array([evaluate_fitness(s, csv_path=csv_path, seed=seed)[0] for s in archive])

    # Sort by fitness descending
    order   = np.argsort(scores)[::-1]
    archive = archive[order]
    scores  = scores[order]

    convergence_history = [float(scores[0])]

    # Pre-compute selection weights for each archive member (Gaussian)
    def _weights(k):
        ranks = np.arange(1, k + 1, dtype=float)
        w = np.exp(-((ranks - 1) ** 2) / (2 * q ** 2 * k ** 2))
        return w / w.sum()

    for it in range(n_iter):
        weights = _weights(archive_size)
        new_solutions = []

        for _ in range(n_ants):
            # Select a solution from archive using weights
            chosen = rng.choice(archive_size, p=weights)
            template = archive[chosen]

            # Compute per-dimension Gaussian σ
            sigma = np.zeros(DIM)
            for d in range(DIM):
                sigma[d] = xi * np.sum(np.abs(archive[:, d] - template[d])) / (archive_size - 1 + 1e-9)
                sigma[d] = max(sigma[d], 1e-4)

            # Sample new ant position
            new_sol = np.clip(rng.normal(template, sigma), 0.0, 1.0)
            new_solutions.append(new_sol)

        # Evaluate new ants
        new_scores = np.array([evaluate_fitness(s, csv_path=csv_path, seed=seed)[0] for s in new_solutions])

        # Merge archive + new solutions, keep top archive_size
        combined_sols   = np.vstack([archive, np.array(new_solutions)])
        combined_scores = np.concatenate([scores, new_scores])

        order   = np.argsort(combined_scores)[::-1][:archive_size]
        archive = combined_sols[order]
        scores  = combined_scores[order]

        convergence_history.append(float(scores[0]))
        print(f"  [ACO] Iter {it+1}/{n_iter}  best fitness = {scores[0]:.6f}")

    best_params  = archive[0]
    best_fitness, best_result = evaluate_fitness(best_params, csv_path=csv_path, seed=seed)

    best_result.update({
        'algorithm':           'ACO',
        'fitness':             best_fitness,
        'convergence_history': convergence_history,
    })
    return best_result
