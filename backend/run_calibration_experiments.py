"""
run_calibration_experiments.py
------------------------------
Lightweight experiment runner to evaluate the Adaptive Strategy Metaheuristic (ASM)
under multiple confidence thresholds and compare with the manual scheduling strategy.
"""

import time
import argparse
import numpy as np
from typing import Dict, Any, List

from evaluation.fitness import evaluate_fitness
from algorithms.asm import AdaptiveStrategyMetaheuristic


def run_experiment_for_config(
    threshold: float,
    adaptive_enabled: bool,
    pop_size: int,
    n_gen: int,
    seeds: List[int],
    csv_path: str,
) -> Dict[str, Any]:
    """
    Run ASM for a specific configuration over multiple seeds and collect metrics.
    """
    runs = []
    
    for seed in seeds:
        budget = pop_size * n_gen

        def fitness_fn(cand):
            return evaluate_fitness(cand, csv_path=csv_path, seed=seed)

        # Initialize ASM with the config
        asm = AdaptiveStrategyMetaheuristic(
            pop_size=pop_size,
            budget=budget,
            seed=seed,
            verbose=False,  # Keep output silent during experiment sweeps
            adaptive_switching=adaptive_enabled,
            confidence_threshold=threshold,
            minimum_runtime_steps=3,
            switch_cooldown_steps=2,
        )

        t0 = time.time()
        res = asm.optimize(fitness_fn=fitness_fn, pop_size=pop_size, iterations=n_gen)
        elapsed = time.time() - t0

        # Extract history and metrics
        final_fitness = res.fitness
        history = asm.decision_engine.history()
        transitions = asm._controller.transition_history

        # Count recommendations and switches
        num_recommendations = len(history)
        num_accepted_switches = 0
        num_rejected_switches = 0

        # Calculate average recommendation confidence
        confidences = [r.confidence for r in history]
        avg_confidence = float(np.mean(confidences)) if confidences else 0.0

        # Filter out the initial load (from_strategy == "") for active switches
        active_transitions = [t for t in transitions if t.from_strategy != ""]
        num_accepted_switches = len(active_transitions)
        num_rejected_switches = max(0, num_recommendations - num_accepted_switches)

        # Calculate average improvement per switch
        improvements = []
        for i, trans in enumerate(transitions):
            if trans.from_strategy == "":
                # Initial load, not a switch
                continue
            # Find the fitness at the end of this strategy's execution
            if i + 1 < len(transitions):
                next_fitness = transitions[i + 1].fitness_at_switch
            else:
                next_fitness = final_fitness
            improvements.append(max(0.0, next_fitness - trans.fitness_at_switch))

        avg_improvement = float(np.mean(improvements)) if improvements else 0.0
        switch_frequency = num_accepted_switches / max(1, n_gen)

        runs.append({
            "fitness": final_fitness,
            "runtime": elapsed,
            "recommendations": num_recommendations,
            "accepted_switches": num_accepted_switches,
            "rejected_switches": num_rejected_switches,
            "avg_confidence": avg_confidence,
            "avg_improvement": avg_improvement,
            "switch_frequency": switch_frequency,
            "final_optimizer": asm.current_optimizer,
            "transitions": active_transitions,
            "recommendations_history": history,
        })

    # Aggregate metrics over seeds
    agg = {
        "avg_fitness": float(np.mean([r["fitness"] for r in runs])),
        "avg_runtime": float(np.mean([r["runtime"] for r in runs])),
        "avg_switches": float(np.mean([r["accepted_switches"] for r in runs])),
        "avg_confidence": float(np.mean([r["avg_confidence"] for r in runs])),
        "avg_improvement": float(np.mean([r["avg_improvement"] for r in runs])),
        "avg_switch_frequency": float(np.mean([r["switch_frequency"] for r in runs])),
        "runs": runs,
    }
    return agg


def main():
    parser = argparse.ArgumentParser(description="ASM Calibration Experiment Runner")
    parser.add_argument("--csv", default="../vanet.csv", help="Path to VANET CSV")
    parser.add_argument("--seeds", type=int, nargs="+", default=[42, 100, 2026], help="Random seeds to run")
    parser.add_argument("--pop", type=int, default=15, help="Population size (default 15 for fast sweep)")
    parser.add_argument("--iter", type=int, default=20, help="Iterations count (default 20 for fast sweep)")
    args = parser.parse_args()

    thresholds = [0.01, 0.02, 0.03, 0.05, 0.08, 0.10, 0.15]
    results = {}

    print("=" * 70)
    print("  STARTING ASM CALIBRATION SWEEP")
    print(f"  Seeds: {args.seeds} | Pop: {args.pop} | Iterations: {args.iter}")
    print("=" * 70)

    # 1. Run Sweep over thresholds
    for th in thresholds:
        print(f"  Evaluating Threshold: {th} ...")
        results[f"th_{th}"] = run_experiment_for_config(
            threshold=th,
            adaptive_enabled=True,
            pop_size=args.pop,
            n_gen=args.iter,
            seeds=args.seeds,
            csv_path=args.csv,
        )

    # 2. Run Manual ASM baseline
    print("  Evaluating Manual ASM Baseline ...")
    results["manual"] = run_experiment_for_config(
        threshold=0.0,
        adaptive_enabled=False,
        pop_size=args.pop,
        n_gen=args.iter,
        seeds=args.seeds,
        csv_path=args.csv,
    )

    # 3. Print Comparison Table
    print("\n" + "=" * 80)
    print("  THRESHOLD SWEEP COMPARISON SUMMARY")
    print("=" * 80)
    print(f"{'Config':<12} {'Avg Fitness':>12} {'Avg Time (s)':>12} {'Avg Switches':>12} {'Avg Conf':>10} {'Avg Impr':>10}")
    print("-" * 80)
    
    for th in thresholds:
        key = f"th_{th}"
        res = results[key]
        print(
            f"th_{th:<8} "
            f"{res['avg_fitness']:>12.6f} "
            f"{res['avg_runtime']:>12.2f} "
            f"{res['avg_switches']:>12.1f} "
            f"{res['avg_confidence']:>10.3f} "
            f"{res['avg_improvement']:>10.4f}"
        )

    # Baseline Manual
    res_m = results["manual"]
    print(
        f"{'manual':<12} "
        f"{res_m['avg_fitness']:>12.6f} "
        f"{res_m['avg_runtime']:>12.2f} "
        f"{res_m['avg_switches']:>12.1f} "
        f"{res_m['avg_confidence']:>10.3f} "
        f"{res_m['avg_improvement']:>10.4f}"
    )
    print("=" * 80)

    # 4. Compile Transition and Recommendation Statistics
    # Gather across all threshold configurations
    transition_counts = {}
    total_recommendations = 0
    rec_optimizer_counts = {}
    act_optimizer_counts = {}
    total_accepted_switches = 0
    total_rejected_switches = 0

    for th in thresholds:
        key = f"th_{th}"
        for run in results[key]["runs"]:
            # Transitions
            for trans in run["transitions"]:
                pair = f"{trans.from_strategy} -> {trans.to_strategy}"
                transition_counts[pair] = transition_counts.get(pair, 0) + 1
                total_accepted_switches += 1
                act_optimizer_counts[trans.to_strategy] = act_optimizer_counts.get(trans.to_strategy, 0) + 1

            # Initial strategy load count
            if run["transitions"]:
                init_opt = run["transitions"][0].to_strategy
                act_optimizer_counts[init_opt] = act_optimizer_counts.get(init_opt, 0) + 1

            # Recommendations
            for rec in run["recommendations_history"]:
                total_recommendations += 1
                rec_optimizer_counts[rec.recommended_optimizer] = rec_optimizer_counts.get(rec.recommended_optimizer, 0) + 1

            total_rejected_switches += run["rejected_switches"]

    print("\n" + "=" * 80)
    print("  TRANSITION AND RECOMMENDATION ANALYSIS")
    print("=" * 80)

    # Transition Summary
    print("  Strategy Transition Frequency Summary:")
    for pair, count in sorted(transition_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {pair:<15} : {count}")
    print("-" * 80)

    # Recommendation counts
    print("  Recommendation Frequency by Optimizer:")
    for opt, count in sorted(rec_optimizer_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {opt:<5} : {count}")
    print("-" * 80)

    # Activated counts
    print("  Activation Frequency by Optimizer:")
    for opt, count in sorted(act_optimizer_counts.items(), key=lambda x: x[1], reverse=True):
        print(f"    {opt:<5} : {count}")
    print("-" * 80)

    # Accept / Reject percentages
    if total_recommendations > 0:
        accept_pct = (total_accepted_switches / total_recommendations) * 100
        reject_pct = (total_rejected_switches / total_recommendations) * 100
    else:
        accept_pct = reject_pct = 0.0

    print(f"  Total Recommendations Generated : {total_recommendations}")
    print(f"  Accepted Switches Count          : {total_accepted_switches} ({accept_pct:.1f}%)")
    print(f"  Rejected Recommendations Count   : {total_rejected_switches} ({reject_pct:.1f}%)")
    print("=" * 80)


if __name__ == "__main__":
    main()
