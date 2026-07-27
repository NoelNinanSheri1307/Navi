"""
run_experiment.py
-----------------
Command-Line Interface (CLI) runner for Navi experiment engine.

Executes scientific benchmarks, exports structured result artifacts (JSON/CSV),
and renders convergence charts for any BaseOptimizer algorithm kernel.

Examples
--------
  python run_experiment.py --optimizer GA --fast
  python run_experiment.py --optimizer DE --seed 101
  python run_experiment.py --config configs/ga_experiment.json
"""

import argparse
import os
import sys

# Ensure backend directory is in sys.path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from experiments.config import ExperimentConfig
from experiments.manager import ExperimentManager


def main():
    parser = argparse.ArgumentParser(
        description="Navi Scientific Experiment Runner",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument(
        "--optimizer", "-o",
        type=str,
        default="GA",
        help="Target optimizer kernel ('GA', 'DE')",
    )
    parser.add_argument(
        "--config", "-c",
        type=str,
        default=None,
        help="Path to experiment JSON configuration file",
    )
    parser.add_argument(
        "--dataset", "-d",
        type=str,
        default="vanet.csv",
        help="Input VANET telemetry CSV dataset file path",
    )
    parser.add_argument(
        "--budget", "-b",
        type=int,
        default=10000,
        help="Maximum function evaluation budget",
    )
    parser.add_argument(
        "--pop-size", "-p",
        type=int,
        default=30,
        help="Population size parameter",
    )
    parser.add_argument(
        "--iterations", "-i",
        type=int,
        default=50,
        help="Target iterations/generations limit",
    )
    parser.add_argument(
        "--seed", "-s",
        type=int,
        default=42,
        help="Deterministic random seed parameter",
    )
    parser.add_argument(
        "--out",
        type=str,
        default="output/experiments",
        help="Output root directory for experiment artifacts",
    )
    parser.add_argument(
        "--name",
        type=str,
        default=None,
        help="Custom experiment title name",
    )
    parser.add_argument(
        "--fast",
        action="store_true",
        help="Fast mode for diagnostic verification (pop=15, iter=20, budget=500)",
    )

    args = parser.parse_args()

    # Parse config from file if provided, otherwise build from CLI flags
    if args.config and os.path.isfile(args.config):
        print(f"[INFO] Loading experiment configuration from '{args.config}' ...")
        config = ExperimentConfig.from_json(args.config)
    else:
        pop_size = 15 if args.fast else args.pop_size
        iterations = 20 if args.fast else args.iterations
        budget = 500 if args.fast else args.budget
        exp_name = args.name if args.name else f"{args.optimizer.upper()}_Benchmark"

        config = ExperimentConfig(
            experiment_name=exp_name,
            optimizer=args.optimizer.upper(),
            dataset=args.dataset,
            population_size=pop_size,
            evaluation_budget=budget,
            iterations=iterations,
            random_seed=args.seed,
            output_directory=args.out,
            notes="CLI benchmark run",
        )

    print("=" * 70)
    print("  NAVI EXPERIMENT BENCHMARK ENGINE")
    print(f"  Optimizer  : {config.optimizer}")
    print(f"  Dataset    : {config.dataset}")
    print(f"  Population : {config.population_size}")
    print(f"  Iterations : {config.iterations}")
    print(f"  Budget     : {config.evaluation_budget}")
    print(f"  Seed       : {config.random_seed}")
    print(f"  Output Dir : {config.output_directory}")
    print("=" * 70)

    manager = ExperimentManager()
    result = manager.run_experiment(config)

    print("\n" + "=" * 70)
    print("  EXPERIMENT SUMMARY")
    print("=" * 70)
    print(f"  Experiment ID : {result['experiment_id']}")
    print(f"  Best Fitness  : {result['best_fitness']:.6f}")
    print(f"  Summary File  : {result['summary_path']}")
    print("  Plots Generated:")
    for plot_path in result["plot_files"]:
        print(f"    - {plot_path}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    main()
