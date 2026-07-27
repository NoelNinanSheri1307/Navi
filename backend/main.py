"""
main.py
-------
Entry point for the Traffic Flow Control Optimization System.

Runs all 6 optimization algorithms sequentially, saves standardised JSON
results to output/results/, and prints a comparison summary table.

Usage:
    cd backend
    python main.py [--algorithms GA PSO GWO DE ACO SA] [--csv ../vanet.csv]
                   [--pop 30] [--iter 50] [--seed 42] [--fast]
"""

import sys
import os
import json
import time
import argparse
import textwrap

# Ensure backend is importable when run from within the package dir
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

try:
    from simulation.traffic_model import get_stats
except ImportError:
    from model.traffic_model import get_stats

# ─────────────────────────────────────────────────────────────────────────────
# Algorithm registry
# ─────────────────────────────────────────────────────────────────────────────
ALGO_REGISTRY = {
    'GA':  ('algorithms.ga',  'run_ga'),
    'PSO': ('algorithms.pso', 'run_pso'),
    'GWO': ('algorithms.gwo', 'run_gwo'),
    'DE':  ('algorithms.de',  'run_de'),
    'ACO': ('algorithms.aco', 'run_aco'),
    'SA':  ('algorithms.sa',  'run_sa'),
}


def _import_runner(module_path: str, func_name: str):
    import importlib
    mod = importlib.import_module(module_path)
    return getattr(mod, func_name)


# ─────────────────────────────────────────────────────────────────────────────
# JSON output helpers
# ─────────────────────────────────────────────────────────────────────────────
def _standardise(result: dict) -> dict:
    """Ensure the result dict matches the required output schema."""
    return {
        "algorithm":            result.get("algorithm", "UNKNOWN"),
        "green_times":          [round(g, 2) for g in result.get("green_times", [])],
        "cycle_time":           result.get("cycle_time", 120),
        "avg_speed":            round(result.get("avg_speed", 0.0), 4),
        "avg_density":          round(result.get("avg_density", 0.0), 4),
        "avg_wait_time":        round(result.get("avg_wait_time", 0.0), 4),
        "total_flow":           round(result.get("total_flow", 0.0), 4),
        "avg_queue_length":     round(result.get("avg_queue_length", 0.0), 4),
        "congestion_pressure":  round(result.get("congestion_pressure", 0.0), 6),
        "speed_density_ratio":  round(result.get("speed_density_ratio", 0.0), 6),
        "fitness":              round(result.get("fitness", 0.0), 8),
        "convergence_history":  [round(f, 8) for f in result.get("convergence_history", [])],
        "simulation_steps":     result.get("simulation_steps", []),
    }


def _save_result(result: dict, out_dir: str) -> str:
    os.makedirs(out_dir, exist_ok=True)
    algo = result["algorithm"].lower()
    path = os.path.join(out_dir, f"{algo}_result.json")
    with open(path, "w", encoding="utf-8") as f:
        json.dump(result, f, indent=2)
    return path


# ─────────────────────────────────────────────────────────────────────────────
# Comparison table
# ─────────────────────────────────────────────────────────────────────────────
def _print_comparison(results: list[dict]) -> None:
    header = f"{'Algorithm':<10} {'Fitness':>10} {'Speed':>8} {'Density':>9} {'Wait':>8} {'Flow':>10} {'Queue':>8} {'Pressure':>10}"
    print("\n" + "=" * 80)
    print("  ALGORITHM COMPARISON SUMMARY")
    print("=" * 80)
    print(header)
    print("-" * 80)
    for r in results:
        print(
            f"{r['algorithm']:<10} "
            f"{r['fitness']:>10.6f} "
            f"{r['avg_speed']:>8.3f} "
            f"{r['avg_density']:>9.3f} "
            f"{r['avg_wait_time']:>8.3f} "
            f"{r['total_flow']:>10.2f} "
            f"{r['avg_queue_length']:>8.3f} "
            f"{r['congestion_pressure']:>10.6f}"
        )
    print("=" * 80)

    # Best
    best = max(results, key=lambda r: r['fitness'])
    print(f"\n  [BEST] Best algorithm: {best['algorithm']}  (fitness = {best['fitness']:.6f})")
    print(f"         Green times:    {best['green_times']}")
    print()


# ─────────────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Traffic Flow Control – Fuzzy + Metaheuristic Optimization",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=textwrap.dedent("""\
            Examples:
              python main.py
              python main.py --algorithms GA PSO DE
              python main.py --pop 20 --iter 30 --fast
        """),
    )
    parser.add_argument(
        "--algorithms", nargs="+",
        choices=list(ALGO_REGISTRY.keys()),
        default=list(ALGO_REGISTRY.keys()),
        help="Which algorithms to run (default: all 6)",
    )
    parser.add_argument("--csv",  default="../vanet.csv", help="Path to VANET.csv")
    parser.add_argument("--pop",  type=int, default=30,  help="Population / archive size")
    parser.add_argument("--iter", type=int, default=50,  help="Iterations / generations")
    parser.add_argument("--seed", type=int, default=42,  help="Random seed")
    parser.add_argument(
        "--fast", action="store_true",
        help="Use reduced pop=15, iter=20 for quick testing",
    )
    parser.add_argument(
        "--out", default="output/results",
        help="Output directory for JSON results",
    )
    args = parser.parse_args()

    if args.fast:
        args.pop  = 15
        args.iter = 20
        print("[INFO] Fast mode: pop=15, iter=20")

    # Validate CSV path
    csv_path = args.csv
    if not os.path.isfile(csv_path):
        # Try relative to this file
        alt = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vanet.csv")
        if os.path.isfile(alt):
            csv_path = alt
        else:
            print(f"[ERROR] VANET.csv not found at '{csv_path}' or '{alt}'")
            print("        Place vanet.csv in the project root and retry.")
            sys.exit(1)

    print(f"\n[INFO] Dataset : {os.path.abspath(csv_path)}")
    print(f"[INFO] Algorithms : {args.algorithms}")
    print(f"[INFO] Pop/Size   : {args.pop}   Iterations: {args.iter}   Seed: {args.seed}")

    # Pre-load dataset stats (validates CSV columns)
    stats = get_stats(csv_path)
    print(f"[INFO] Dataset stats loaded. Columns OK.\n")

    # ── Common kwargs per algo ──
    common = dict(csv_path=csv_path, seed=args.seed)
    pop_kw = dict(pop_size=args.pop,     n_gen=args.iter)
    swarm_kw = dict(n_particles=args.pop, n_iter=args.iter)
    wolf_kw  = dict(n_wolves=args.pop,   n_iter=args.iter)
    de_kw    = dict(pop_size=args.pop,   n_gen=args.iter)
    aco_kw   = dict(n_ants=args.pop,     archive_size=args.pop, n_iter=args.iter)
    sa_kw    = dict(n_iter=args.iter * 10)   # SA needs more iterations

    EXTRA_KWARGS = {
        'GA':  pop_kw,
        'PSO': swarm_kw,
        'GWO': wolf_kw,
        'DE':  de_kw,
        'ACO': aco_kw,
        'SA':  sa_kw,
        'HYBRID': {
            'pop_size': args.pop,
            'n_gen': args.iter,
            'archive_size': max(10, args.pop // 2),
            'sa_interval': 5,
            'sa_steps': 20
        },
    }

    all_results = []
    total_start = time.time()

    for algo_name in args.algorithms:
        module_path, func_name = ALGO_REGISTRY[algo_name]
        runner = _import_runner(module_path, func_name)

        print(f"\n{'-'*60}")
        print(f"  Running {algo_name} ...")
        print(f"{'-'*60}")

        t0 = time.time()
        try:
            raw_result = runner(**common, **EXTRA_KWARGS[algo_name])
        except Exception as e:
            print(f"[ERROR] {algo_name} failed: {e}")
            continue
        elapsed = time.time() - t0

        result = _standardise(raw_result)
        path   = _save_result(result, args.out)

        print(f"\n  [OK] {algo_name} done in {elapsed:.1f}s")
        print(f"       Fitness     : {result['fitness']:.6f}")
        print(f"       Green times : {result['green_times']}")
        print(f"       Saved -> {path}")

        all_results.append(result)

    total_elapsed = time.time() - total_start
    print(f"\n[INFO] Total runtime: {total_elapsed:.1f}s")

    if all_results:
        _print_comparison(all_results)

        # Save combined summary
        summary_path = os.path.join(args.out, "summary.json")
        with open(summary_path, "w", encoding="utf-8") as f:
            json.dump(all_results, f, indent=2)
        print(f"[INFO] Combined summary saved -> {summary_path}\n")
    else:
        print("[WARN] No results to compare.")


if __name__ == "__main__":
    main()
