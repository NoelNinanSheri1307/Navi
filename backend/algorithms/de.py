"""
de.py — Differential Evolution
--------------------------------
Classic DE/rand/1/bin strategy.
Optimises the 35-dim fuzzy parameter vector.
"""

import numpy as np
from evaluation.fitness import evaluate_fitness

DIM = 35


def run_de(
    csv_path: str = "vanet.csv",
    pop_size: int = 30,
    n_gen: int = 50,
    F: float = 0.8,
    CR: float = 0.9,
    seed: int = 42,
) -> dict:
    """
    Run Differential Evolution (DE/rand/1/bin).

    Returns dict with best params, fitness, convergence history,
    and full simulation result.
    """
    rng = np.random.default_rng(seed)

    # ── Initialise ──
    pop    = rng.uniform(0.0, 1.0, (pop_size, DIM))
    scores = np.array([evaluate_fitness(ind, csv_path=csv_path, seed=seed)[0] for ind in pop])

    best_idx   = int(np.argmax(scores))
    convergence_history = [float(scores[best_idx])]

    for gen in range(n_gen):
        for i in range(pop_size):
            # Select 3 distinct random indices ≠ i
            idxs = list(range(pop_size))
            idxs.remove(i)
            r = rng.choice(idxs, 3, replace=False)
            a, b, c = pop[r[0]], pop[r[1]], pop[r[2]]

            # Mutation
            mutant = np.clip(a + F * (b - c), 0.0, 1.0)

            # Crossover (binomial)
            j_rand = rng.integers(0, DIM)
            trial  = pop[i].copy()
            for j in range(DIM):
                if rng.random() < CR or j == j_rand:
                    trial[j] = mutant[j]

            # Selection
            f_trial, _ = evaluate_fitness(trial, csv_path=csv_path, seed=seed)
            if f_trial > scores[i]:
                pop[i]    = trial
                scores[i] = f_trial

        best_idx = int(np.argmax(scores))
        convergence_history.append(float(scores[best_idx]))
        print(f"  [DE] Gen {gen+1}/{n_gen}  best fitness = {scores[best_idx]:.6f}")

    best_params  = pop[best_idx]
    best_fitness, best_result = evaluate_fitness(best_params, csv_path=csv_path, seed=seed)

    best_result.update({
        'algorithm':           'DE',
        'fitness':             best_fitness,
        'convergence_history': convergence_history,
    })
    return best_result
