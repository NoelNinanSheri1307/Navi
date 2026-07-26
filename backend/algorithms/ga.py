"""
ga.py — Genetic Algorithm
--------------------------
Standard real-valued GA with tournament selection, SBX crossover,
and polynomial mutation.  Optimises the 35-dim fuzzy parameter vector.
Includes elitism to ensure the best solution is never lost.
"""

import numpy as np
from evaluation.fitness import evaluate_fitness

DIM = 35


def run_ga(
    csv_path: str = "vanet.csv",
    pop_size: int = 30,
    n_gen: int = 50,
    cx_prob: float = 0.85,
    mut_prob: float = 0.15,
    eta_c: float = 15.0,
    eta_m: float = 20.0,
    seed: int = 42,
) -> dict:
    """
    Run Genetic Algorithm.

    Returns dict with best params, fitness, convergence history,
    and full simulation result.
    """
    rng = np.random.default_rng(seed)

    # ── Initialise population ──
    # Ensure pop is always a numpy array for easy indexing
    pop = rng.uniform(0.0, 1.0, (pop_size, DIM))

    def fitness_all(population):
        scores_list = []
        for ind in population:
            # Pass seed to ensure deterministic evaluation during search
            f, _ = evaluate_fitness(ind, csv_path=csv_path, seed=seed)
            scores_list.append(f)
        return np.array(scores_list)

    def tournament(p, s, k=5):
        idx = rng.integers(0, len(p), k)
        best_of_k = idx[np.argmax(s[idx])]
        return p[best_of_k].copy()

    def sbx_crossover(p1, p2):
        c1, c2 = p1.copy(), p2.copy()
        for i in range(DIM):
            if rng.random() < 0.5:
                u = rng.random()
                if u <= 0.5:
                    beta = (2 * u) ** (1 / (eta_c + 1))
                else:
                    beta = (1 / (2 * (1 - u))) ** (1 / (eta_c + 1))
                c1[i] = 0.5 * ((1 + beta) * p1[i] + (1 - beta) * p2[i])
                c2[i] = 0.5 * ((1 - beta) * p1[i] + (1 + beta) * p2[i])
        return np.clip(c1, 0, 1), np.clip(c2, 0, 1)

    def poly_mutation(ind, mut_rate):
        child = ind.copy()
        for i in range(DIM):
            if rng.random() < mut_rate:
                u = rng.random()
                if u < 0.5:
                    delta = (2 * u) ** (1 / (eta_m + 1)) - 1
                else:
                    delta = 1 - (2 * (1 - u)) ** (1 / (eta_m + 1))
                child[i] = np.clip(child[i] + delta, 0, 1)
        return child

    # Initial evaluation
    scores = fitness_all(pop)
    best_idx = int(np.argmax(scores))
    best_ind = pop[best_idx].copy()
    best_f = float(scores[best_idx])
    convergence_history = [best_f]

    for gen in range(n_gen):
        new_pop_list = []
        while len(new_pop_list) < pop_size:
            parent1 = tournament(pop, scores)
            parent2 = tournament(pop, scores)
            
            if rng.random() < cx_prob:
                child1, child2 = sbx_crossover(parent1, parent2)
            else:
                child1, child2 = parent1.copy(), parent2.copy()
            
            new_pop_list.append(poly_mutation(child1, mut_prob))
            if len(new_pop_list) < pop_size:
                new_pop_list.append(poly_mutation(child2, mut_prob))

        # Convert back to numpy array for the next generation
        current_pop = np.array(new_pop_list[:pop_size])
        current_scores = fitness_all(current_pop)

        # Elitism: Keep track of global best and replace worst if current best is worse
        gen_best_idx = np.argmax(current_scores)
        if current_scores[gen_best_idx] > best_f:
            best_f = float(current_scores[gen_best_idx])
            best_ind = current_pop[gen_best_idx].copy()
        else:
            # Replace worst in current pop with global best
            worst_idx = np.argmin(current_scores)
            current_pop[worst_idx] = best_ind.copy()
            current_scores[worst_idx] = best_f

        pop = current_pop
        scores = current_scores
        
        convergence_history.append(best_f)
        print(f"  [GA] Gen {gen+1}/{n_gen}  best fitness = {best_f:.6f}")

    # 3. ── Lamarckian Hill Climb (Fine-tuning the Global Best) ──
    print(f"  [GA] Evolutionary search complete. Fine-tuning {best_f:.6f} ...")
    refined_ind = best_ind.copy()
    refined_f   = best_f
    
    # Try 100 tiny perturbations around the champion
    for _ in range(100):
        # Very small noise (0.01)
        perturbation = rng.normal(0, 0.01, DIM)
        candidate    = np.clip(refined_ind + perturbation, 0, 1)
        cf, _        = evaluate_fitness(candidate, csv_path=csv_path, seed=seed)
        
        if cf > refined_f:
            refined_f   = cf
            refined_ind = candidate.copy()
            
    # Final evaluation of the REFINED champion
    best_fitness_final, best_result_final = evaluate_fitness(refined_ind, csv_path=csv_path, seed=seed)
    
    # SAFETY LOCK: If fine-tuning somehow failed (precision), use the evolutionary best
    if best_f > best_fitness_final:
        best_fitness_final, best_result_final = evaluate_fitness(best_ind, csv_path=csv_path, seed=seed)

    best_result_final.update({
        'algorithm':          'GA',
        'fitness':            best_fitness_final,
        'convergence_history': convergence_history,
    })
    return best_result_final
