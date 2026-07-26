"""
hybrid_aco_sa_ga.py
-------------------
A high-performance hybrid optimization model combining:
1. Genetic Algorithm (GA): For population diversity and global search via crossover.
2. Ant Colony Optimization (ACO): Using an archive-based pheromone model (ACOR) 
    to guide the mutation and sampling process.
3. Simulated Annealing (SA): For elite local refinement to escape local optima.

This "Triple-Hybrid" is designed to achieve the best possible fitness value 
for the 35-dimensional fuzzy traffic parameter vector.
"""

import numpy as np
from evaluation.fitness import evaluate_fitness

DIM = 35

def run_hybrid(
    csv_path: str = "vanet.csv",
    pop_size: int = 30,
    n_gen: int = 50,
    archive_size: int = 20,
    cx_prob: float = 0.8,
    mut_prob: float = 0.2,
    sa_steps: int = 20,
    sa_interval: int = 5,
    q: float = 0.1,    # ACO locality
    xi: float = 0.85,  # ACO evaporation
    seed: int = 42,
) -> dict:
    """
    Run the Hybrid ACO-SA-GA Optimization.
    """
    rng = np.random.default_rng(seed)
    
    # ── 1. Initialize Population & Archive ──
    # Archive stores the globally best solutions for ACO pheromone guidance
    pop = rng.uniform(0.0, 1.0, (pop_size, DIM))
    
    def get_scores(population):
        scores = []
        for ind in population:
            f, _ = evaluate_fitness(ind, csv_path=csv_path, seed=seed)
            scores.append(f)
        return np.array(scores)

    pop_scores = get_scores(pop)
    
    # Sort and initialize archive
    idx_sorted = np.argsort(pop_scores)[::-1]
    archive = pop[idx_sorted[:archive_size]].copy()
    archive_scores = pop_scores[idx_sorted[:archive_size]].copy()
    
    best_f = float(archive_scores[0])
    best_ind = archive[0].copy()
    convergence_history = [best_f]

    # Pre-compute ACO weights
    def get_aco_weights(k):
        ranks = np.arange(1, k + 1, dtype=float)
        w = np.exp(-((ranks - 1) ** 2) / (2 * q ** 2 * k ** 2))
        return w / w.sum()

    aco_weights = get_aco_weights(archive_size)

    # ── 2. Hybrid Evolution Loop ──
    for gen in range(n_gen):
        new_pop = []
        
        # --- GA CROSSOVER PHASE ---
        while len(new_pop) < pop_size:
            # Tournament Selection
            def tournament(p, s, k=3):
                idx = rng.integers(0, len(p), k)
                return p[idx[np.argmax(s[idx])]].copy()
            
            p1 = tournament(pop, pop_scores)
            p2 = tournament(pop, pop_scores)
            
            if rng.random() < cx_prob:
                # SBX Crossover
                c1, c2 = p1.copy(), p2.copy()
                eta_c = 15.0
                for i in range(DIM):
                    if rng.random() < 0.5:
                        u = rng.random()
                        beta = (2*u)**(1/(eta_c+1)) if u <= 0.5 else (1/(2*(1-u)))**(1/(eta_c+1))
                        c1[i] = 0.5 * ((1 + beta) * p1[i] + (1 - beta) * p2[i])
                        c2[i] = 0.5 * ((1 - beta) * p1[i] + (1 + beta) * p2[i])
                new_pop.append(np.clip(c1, 0, 1))
                if len(new_pop) < pop_size:
                    new_pop.append(np.clip(c2, 0, 1))
            else:
                new_pop.append(p1)
                if len(new_pop) < pop_size:
                    new_pop.append(p2)

        # --- ACO-GUIDED MUTATION PHASE ---
        for i in range(len(new_pop)):
            if rng.random() < mut_prob:
                # Instead of random mutation, sample from ACO archive
                chosen = rng.choice(archive_size, p=aco_weights)
                template = archive[chosen]
                
                # Diversity-based sigma
                sigma = np.zeros(DIM)
                for d in range(DIM):
                    sigma[d] = xi * np.sum(np.abs(archive[:, d] - template[d])) / (archive_size - 1 + 1e-9)
                    sigma[d] = max(sigma[d], 1e-4)
                
                # Perturb toward the "pheromone trail"
                new_pop[i] = np.clip(rng.normal(new_pop[i], sigma * 0.5), 0, 1)

        pop = np.array(new_pop)
        pop_scores = get_scores(pop)

        # Update global best and archive
        combined_sols = np.vstack([archive, pop])
        combined_scores = np.concatenate([archive_scores, pop_scores])
        
        idx_top = np.argsort(combined_scores)[::-1][:archive_size]
        archive = combined_sols[idx_top].copy()
        archive_scores = combined_scores[idx_top].copy()
        
        if archive_scores[0] > best_f:
            best_f = float(archive_scores[0])
            best_ind = archive[0].copy()

        # ── 3. SA REFINEMENT (The "Polish") ──
        # Frequent, deep SA polish to hit target fitness
        if (gen + 1) % 4 == 0:
            print(f"  [Hybrid] Gen {gen+1} - CRITICAL SA Refinement...")
            curr_sa = best_ind.copy()
            curr_sa_f = best_f
            
            t_start = 0.08
            t_end = 0.0005
            sa_steps_deep = 50
            alpha = (t_end / t_start) ** (1.0 / sa_steps_deep)
            temp = t_start
            
            for _ in range(sa_steps_deep):
                # Precise neighborhood search
                candidate = np.clip(curr_sa + rng.normal(0, 0.015, DIM), 0, 1)
                cf, _ = evaluate_fitness(candidate, csv_path=csv_path, seed=seed)
                
                delta = cf - curr_sa_f
                if delta > 0 or rng.random() < np.exp(delta / temp):
                    curr_sa = candidate
                    curr_sa_f = cf
                temp *= alpha
                
            if curr_sa_f > best_f:
                print(f"    -> SA improved fitness: {best_f:.6f} -> {curr_sa_f:.6f}")
                best_f = curr_sa_f
                best_ind = curr_sa.copy()
                # Inject back into archive
                archive[0] = best_ind.copy()
                archive_scores[0] = best_f

        convergence_history.append(best_f)
        print(f"  [Hybrid] Gen {gen+1}/{n_gen}  best fitness = {best_f:.6f}")

    # Final evaluation
    final_f, final_res = evaluate_fitness(best_ind, csv_path=csv_path, seed=seed)
    
    final_res.update({
        'algorithm': 'Hybrid_ACO_SA_GA',
        'fitness': final_f,
        'convergence_history': convergence_history,
    })
    
    return final_res
