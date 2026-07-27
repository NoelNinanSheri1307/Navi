"""
run_baseline_benchmark.py
--------------------------
Navi Stage 3.8 -- Framework Validation & Baseline Benchmark Suite.

Executes all six reference optimizers (GA, DE, PSO, GWO, ACO, SA) under
identical evaluation budgets across multiple random seeds, producing:

  1. Per-optimizer, per-seed experiment artifacts via ExperimentManager.
  2. Aggregated multi-seed statistical summaries (mean, median, std, best, worst, CI95).
  3. Cross-optimizer ranking table (sorted by median fitness).
  4. Determinism verification (re-run seed 42 twice and compare).
  5. Combined convergence CSV for cross-algorithm plotting.

All outputs are saved under:
    output/baseline_benchmark/<timestamp>/

Usage:
    python run_baseline_benchmark.py                          # Default: 5 seeds, fast mode
    python run_baseline_benchmark.py --seeds 10               # 10 seeds
    python run_baseline_benchmark.py --seeds 30 --full        # 30 seeds, full budget
    python run_baseline_benchmark.py --seeds 5 --fast         # 5 seeds, fast mode
    python run_baseline_benchmark.py --algorithms GA DE PSO   # Subset of optimizers
"""

import argparse
import csv
import json
import os
import sys
import time
from typing import Dict, List, Any

import numpy as np

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from experiments.manager import ExperimentManager
from experiments.config import ExperimentConfig
from analytics.stats import calculate_array_stats


# ─────────────────────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────────────────────
ALL_OPTIMIZERS = ["GA", "DE", "PSO", "GWO", "ACO", "SA"]

FAST_DEFAULTS = {
    "population_size": 15,
    "iterations": 20,
    "evaluation_budget": 500,
}

FULL_DEFAULTS = {
    "population_size": 30,
    "iterations": 50,
    "evaluation_budget": 10000,
}


def generate_seed_list(n_seeds: int, base_seed: int = 42) -> List[int]:
    """Generate reproducible seed sequence from base seed."""
    rng = np.random.default_rng(base_seed)
    return [int(s) for s in rng.choice(10000, size=n_seeds, replace=False)]


def run_single_experiment(
    manager: ExperimentManager,
    optimizer_name: str,
    seed: int,
    params: Dict[str, Any],
    output_dir: str,
) -> Dict[str, Any]:
    """Run a single optimizer experiment and return summary dict."""
    config = ExperimentConfig(
        experiment_name=f"Baseline_{optimizer_name}_seed{seed}",
        optimizer=optimizer_name,
        dataset="vanet.csv",
        population_size=params["population_size"],
        evaluation_budget=params["evaluation_budget"],
        iterations=params["iterations"],
        random_seed=seed,
        output_directory=output_dir,
        notes=f"Baseline benchmark run, seed={seed}",
    )
    result = manager.run_experiment(config)
    return result


def aggregate_optimizer_results(
    results: List[Dict[str, Any]],
    optimizer_name: str,
) -> Dict[str, Any]:
    """Compute multi-seed aggregated statistics for one optimizer."""
    fitness_values = [float(r["best_fitness"]) for r in results]
    stats = calculate_array_stats(fitness_values)
    return {
        "optimizer": optimizer_name,
        "n_seeds": len(results),
        "best": stats["min"],     # Most negative = best for minimization
        "worst": stats["max"],
        "mean": stats["mean"],
        "median": stats["median"],
        "std": stats["std"],
        "ci_95": stats["ci_95"],
        "all_fitness": fitness_values,
    }


def verify_determinism(
    manager: ExperimentManager,
    params: Dict[str, Any],
    output_dir: str,
) -> Dict[str, Any]:
    """Run GA seed=42 twice and check if results match."""
    results = []
    for trial in range(2):
        config = ExperimentConfig(
            experiment_name=f"Determinism_Check_trial{trial}",
            optimizer="GA",
            dataset="vanet.csv",
            population_size=params["population_size"],
            evaluation_budget=params["evaluation_budget"],
            iterations=params["iterations"],
            random_seed=42,
            output_directory=output_dir,
            notes=f"Determinism verification trial {trial}",
        )
        result = manager.run_experiment(config)
        results.append(result)

    f1 = float(results[0]["best_fitness"])
    f2 = float(results[1]["best_fitness"])
    passed = abs(f1 - f2) < 1e-10

    return {
        "trial_1_fitness": f1,
        "trial_2_fitness": f2,
        "absolute_diff": abs(f1 - f2),
        "determinism_passed": passed,
    }


def build_ranking_table(
    aggregated: List[Dict[str, Any]],
) -> List[Dict[str, Any]]:
    """Sort optimizers by median fitness (ascending = better for minimization)."""
    sorted_agg = sorted(aggregated, key=lambda x: x["median"])
    ranked = []
    for rank, entry in enumerate(sorted_agg, 1):
        ranked.append({
            "rank": rank,
            "optimizer": entry["optimizer"],
            "median": round(entry["median"], 8),
            "mean": round(entry["mean"], 8),
            "std": round(entry["std"], 8),
            "best": round(entry["best"], 8),
            "worst": round(entry["worst"], 8),
            "ci_95": round(entry["ci_95"], 8),
            "n_seeds": entry["n_seeds"],
        })
    return ranked


def export_ranking_table_csv(
    ranking: List[Dict[str, Any]],
    output_path: str,
) -> None:
    """Write ranking table to CSV."""
    with open(output_path, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=[
            "rank", "optimizer", "median", "mean", "std", "best", "worst", "ci_95", "n_seeds"
        ])
        writer.writeheader()
        writer.writerows(ranking)


def export_combined_convergence(
    all_results: Dict[str, List[Dict[str, Any]]],
    benchmark_dir: str,
) -> str:
    """Merge per-run convergence CSVs into a single combined file."""
    combined_path = os.path.join(benchmark_dir, "combined_convergence.csv")
    with open(combined_path, "w", newline="", encoding="utf-8") as out_f:
        writer = csv.writer(out_f)
        writer.writerow([
            "optimizer", "seed", "generation", "evaluation_count", "best_fitness"
        ])

        for opt_name, results in all_results.items():
            for result in results:
                exp_dir = result["experiment_dir"]
                conv_path = os.path.join(exp_dir, "convergence.csv")
                if not os.path.isfile(conv_path):
                    continue
                # Extract seed from experiment_id
                exp_id = result["experiment_id"]
                seed_str = exp_id.split("seed")[-1] if "seed" in exp_id else "0"
                with open(conv_path, "r", encoding="utf-8") as in_f:
                    reader = csv.DictReader(in_f)
                    for row in reader:
                        writer.writerow([
                            opt_name, seed_str,
                            row["generation"], row["evaluation_count"],
                            row["best_fitness"],
                        ])

    return combined_path


def print_ranking_table(ranking: List[Dict[str, Any]]) -> None:
    """Print formatted ranking table to console."""
    print()
    print("=" * 100)
    print("  BASELINE BENCHMARK RANKING TABLE")
    print("=" * 100)
    header = f"{'Rank':<6}{'Optimizer':<12}{'Median':<14}{'Mean':<14}{'Std':<12}{'Best':<14}{'Worst':<14}{'CI95':<12}{'Seeds':<6}"
    print(header)
    print("-" * 100)
    for r in ranking:
        line = f"{r['rank']:<6}{r['optimizer']:<12}{r['median']:<14.8f}{r['mean']:<14.8f}{r['std']:<12.8f}{r['best']:<14.8f}{r['worst']:<14.8f}{r['ci_95']:<12.8f}{r['n_seeds']:<6}"
        print(line)
    print("=" * 100)


def main():
    parser = argparse.ArgumentParser(description="Navi Baseline Benchmark Suite")
    parser.add_argument("--seeds", type=int, default=5,
                        help="Number of random seeds (default: 5)")
    parser.add_argument("--fast", action="store_true", default=False,
                        help="Use fast mode (reduced pop/iter/budget)")
    parser.add_argument("--full", action="store_true", default=False,
                        help="Use full budget mode (pop=30, iter=50, budget=10000)")
    parser.add_argument("--algorithms", nargs="+", default=None,
                        help="Subset of optimizers to benchmark (default: all)")
    parser.add_argument("--pop-size", type=int, default=None,
                        help="Override population size")
    parser.add_argument("--iterations", type=int, default=None,
                        help="Override iterations")
    parser.add_argument("--budget", type=int, default=None,
                        help="Override evaluation budget")
    parser.add_argument("--out", type=str, default="output/baseline_benchmark",
                        help="Output root directory")
    parser.add_argument("--skip-determinism", action="store_true", default=False,
                        help="Skip determinism verification step")

    args = parser.parse_args()

    # Resolve mode defaults
    if args.full:
        params = dict(FULL_DEFAULTS)
    else:
        params = dict(FAST_DEFAULTS)

    # Apply CLI overrides
    if args.pop_size is not None:
        params["population_size"] = args.pop_size
    if args.iterations is not None:
        params["iterations"] = args.iterations
    if args.budget is not None:
        params["evaluation_budget"] = args.budget

    optimizers = [o.upper() for o in args.algorithms] if args.algorithms else ALL_OPTIMIZERS
    n_seeds = args.seeds
    seed_list = generate_seed_list(n_seeds)

    # Timestamped benchmark directory
    timestamp = time.strftime("%Y%m%d_%H%M%S", time.localtime())
    benchmark_dir = os.path.join(args.out, timestamp)
    experiments_dir = os.path.join(benchmark_dir, "experiments")
    os.makedirs(experiments_dir, exist_ok=True)

    total_runs = len(optimizers) * n_seeds
    mode_label = "FULL" if args.full else "FAST"

    print()
    print("=" * 80)
    print("  NAVI BASELINE BENCHMARK SUITE")
    print("=" * 80)
    print(f"  Mode         : {mode_label}")
    print(f"  Optimizers   : {', '.join(optimizers)}")
    print(f"  Seeds        : {n_seeds}  {seed_list}")
    print(f"  Population   : {params['population_size']}")
    print(f"  Iterations   : {params['iterations']}")
    print(f"  Budget       : {params['evaluation_budget']}")
    print(f"  Total Runs   : {total_runs}")
    print(f"  Output       : {benchmark_dir}")
    print("=" * 80)
    print()

    manager = ExperimentManager()
    all_results: Dict[str, List[Dict[str, Any]]] = {}
    aggregated_stats: List[Dict[str, Any]] = []

    benchmark_start = time.time()
    run_counter = 0

    for opt_name in optimizers:
        print(f"\n  --- Benchmarking {opt_name} ({n_seeds} seeds) ---")
        opt_results = []

        for seed in seed_list:
            run_counter += 1
            print(f"    [{run_counter}/{total_runs}] {opt_name} seed={seed} ...", end=" ", flush=True)

            t0 = time.time()
            result = run_single_experiment(
                manager=manager,
                optimizer_name=opt_name,
                seed=seed,
                params=params,
                output_dir=experiments_dir,
            )
            elapsed = time.time() - t0
            print(f"fitness={result['best_fitness']:.8f}  ({elapsed:.1f}s)")

            opt_results.append(result)

        all_results[opt_name] = opt_results
        agg = aggregate_optimizer_results(opt_results, opt_name)
        aggregated_stats.append(agg)

        print(f"  {opt_name} aggregate: median={agg['median']:.8f}  mean={agg['mean']:.8f}  std={agg['std']:.8f}")

    # ─── Ranking Table ───
    ranking = build_ranking_table(aggregated_stats)
    print_ranking_table(ranking)

    # ─── Determinism Verification ───
    determinism_result = None
    if not args.skip_determinism:
        print("\n  --- Determinism Verification (GA seed=42 x2) ---")
        determinism_result = verify_determinism(manager, params, experiments_dir)
        status = "PASSED" if determinism_result["determinism_passed"] else "FAILED"
        print(f"    Trial 1 fitness : {determinism_result['trial_1_fitness']:.10f}")
        print(f"    Trial 2 fitness : {determinism_result['trial_2_fitness']:.10f}")
        print(f"    Absolute diff   : {determinism_result['absolute_diff']:.2e}")
        print(f"    Status          : {status}")

    # ─── Export Artifacts ───

    # (1) Ranking table CSV
    ranking_csv_path = os.path.join(benchmark_dir, "ranking_table.csv")
    export_ranking_table_csv(ranking, ranking_csv_path)

    # (2) Combined convergence CSV
    combined_conv_path = export_combined_convergence(all_results, benchmark_dir)

    # (3) Aggregated summary JSON
    summary = {
        "benchmark_timestamp": timestamp,
        "mode": mode_label,
        "n_seeds": n_seeds,
        "seed_list": seed_list,
        "parameters": params,
        "optimizers": optimizers,
        "total_runs": total_runs,
        "total_elapsed_seconds": round(time.time() - benchmark_start, 2),
        "ranking": ranking,
        "aggregated_statistics": [
            {
                "optimizer": a["optimizer"],
                "n_seeds": a["n_seeds"],
                "best": round(a["best"], 8),
                "worst": round(a["worst"], 8),
                "mean": round(a["mean"], 8),
                "median": round(a["median"], 8),
                "std": round(a["std"], 8),
                "ci_95": round(a["ci_95"], 8),
            }
            for a in aggregated_stats
        ],
        "determinism_verification": determinism_result,
    }

    summary_path = os.path.join(benchmark_dir, "benchmark_summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, indent=2)

    # ─── Final Report ───
    total_elapsed = time.time() - benchmark_start
    print()
    print("=" * 80)
    print("  BENCHMARK COMPLETE")
    print("=" * 80)
    print(f"  Total time       : {total_elapsed:.1f}s")
    print(f"  Total runs       : {total_runs}")
    print(f"  Summary          : {summary_path}")
    print(f"  Ranking Table    : {ranking_csv_path}")
    print(f"  Convergence Data : {combined_conv_path}")
    print(f"  Experiment Runs  : {experiments_dir}")
    print("=" * 80)
    print()


if __name__ == "__main__":
    main()
