# Navi Backend Engine - Optimization and Simulation Kernel

A modular Python framework for optimizing traffic signal green-time allocations using Parameterized Fuzzy Logic shaped by 6 reference Metaheuristic Optimizers and an Adaptive Strategy Metaheuristic (ASM) orchestrator.

This completes Backend v1.0, establishing a fully calibrated, self-adapting optimization kernel.

---

## Architecture

```
backend/
├── configs/
│   └── algorithm_config.py      # Standardized hyperparameters for all optimizers
├── evaluation/
│   └── fitness.py               # Objective function evaluation kernel
├── fuzzy/
│   └── fuzzy_system.py          # Parameterized 35-dim fuzzy membership function builder
├── model/
│   └── traffic_model.py         # 4-Lane traffic flow simulator (Greenshields model)
├── algorithms/
│   ├── base/
│   │   ├── logger.py            # Unified execution step and progress logger
│   │   ├── optimizer.py         # BaseOptimizer base class for search kernels
│   │   └── types.py             # Shared types, PopulationState, and OptimizationResult
│   ├── operators/
│   │   ├── adaptive_switch_controller.py  # Switch gatekeeper (cooldown, min runtime, confidence)
│   │   ├── asm_controller.py              # Strategy execution registry and transition recorder
│   │   ├── decision_engine.py             # Need-to-capability mapper and selector
│   │   ├── feature_extractor.py           # Trend and pressure analysis on rolling history
│   │   ├── need_estimator.py              # Exploration, Exploitation, and Escape estimator
│   │   ├── optimizer_capabilities.py      # Capability profile ratings for each strategy
│   │   ├── telemetry_engine.py            # Observer tracking rolling optimization performance
│   │   └── ...                            # Specific operators for GA, DE, PSO, GWO, ACO, SA
│   ├── aco.py                   # Continuous Ant Colony Optimization (ACOR)
│   ├── asm.py                   # Adaptive Strategy Metaheuristic orchestrator
│   ├── de.py                    # Differential Evolution (DE/rand/1/bin)
│   ├── ga.py                    # Genetic Algorithm (SBX + Polynomial Mutation)
│   ├── gwo.py                   # Grey Wolf Optimizer
│   ├── pso.py                   # Particle Swarm Optimization
│   ├── sa.py                    # Simulated Annealing
│   └── strategy_registry.py     # Optimizer strategy registration map
├── output/
│   └── results/                 # Standardized JSON benchmark outputs
├── main.py                      # Main pipeline CLI controller
├── run_calibration_experiments.py # Calibration sweep coordinator (Stage 5)
├── requirements.txt             # Requirements manifest
└── README.md                    # Backend documentation
```

---

## Requirements and Installation

```bash
cd backend
pip install -r requirements.txt
```

Dependencies: `numpy>=1.24`, `pandas>=2.0`, `scikit-fuzzy>=0.4.2`, `networkx>=3.0`

---

## Dataset

Place `vanet.csv` in the root directory (`Navi/vanet.csv`). Required fields:

| Field | Description |
|---|---|
| `congestion_pressure` | Dimensionless congestion pressure index |
| `density_veh_per_km` | Vehicle density per kilometer |
| `queue_length_veh` | Queue count in vehicles |
| `avg_wait_time_s` | Average waiting latency (seconds) |
| `flow_veh_per_hr` | Throughput rate (vehicles/hour) |

---

## Execution Pipeline

### Main Benchmarks
Validate individual optimizers and manual ASM execution. Run these from the `backend/` directory:

```bash
# Run all 7 algorithms
python main.py

# Run targeted algorithms
python main.py --algorithms GA PSO ASM

# Fast diagnostic mode (reduced pop=15, iter=20)
python main.py --fast

# Customized pop/iter/seed
python main.py --pop 30 --iter 50 --seed 42
```

### ASM Calibration Sweep (Stage 5)
Sweep different confidence thresholds to calibrate adaptive switching behavior across multiple seeds:

```bash
# Run fast diagnostic sweep (pop=2, iter=2)
python run_calibration_experiments.py --pop 2 --iter 2 --seeds 42 100

# Run complete threshold sweep (pop=15, iter=20)
python run_calibration_experiments.py --pop 15 --iter 20 --seeds 42 100 2026
```

---

## Adaptive Strategy Metaheuristic (ASM)

ASM orchestrates the search by dynamically switching the active optimizer at runtime based on real-time search needs. It operates via the following decoupled pipeline:

1. **TelemetryEngine**: Passively monitors optimization performance (e.g., fitness convergence rate, population diversity, step indexes) in a configured sliding window.
2. **FeatureExtractor**: Analyzes sliding window telemetry to determine high-level search trends, stability, and remaining budget pressure.
3. **NeedEstimator**: Synthesizes trends to compute the search requirements across three dimensions: Exploration, Exploitation, and Escape.
4. **DecisionEngine**: Combines calculated needs with optimizer capability profiles to score suitability and yield strategy recommendations.
5. **AdaptiveSwitchController**: Acts as a safety gatekeeper, validating minimum runtime steps, switch cooldowns, and confidence threshold margins before permitting a transition.

### Direct ASM Execution Test
Test adaptive switching directly with verbose score updates and safety gate logs:
```bash
python -c "from algorithms.asm import run_asm; run_asm(pop_size=5, n_gen=20, adaptive_switching=True, adaptive_debug=True)"
```

---

## Decision Vector Formulation

A **35-dimensional decision vector** $\mathbf{\theta} \in [0, 1]^{35}$ parameters the membership functions of 5 antecedent variables (7 breakpoints each):

| Vector Index | Target Antecedent Variable |
|---|---|
| 0-6 | `congestion_pressure` membership breakpoints |
| 7-13 | `density_veh_per_km` membership breakpoints |
| 14-20 | `queue_length_veh` membership breakpoints |
| 21-27 | `avg_wait_time_s` membership breakpoints |
| 28-34 | `flow_veh_per_hr` membership breakpoints |

---

## Fitness Function

```
fitness = +0.35 * flow_norm
          +0.30 * speed_norm
          -0.15 * wait_norm
          -0.10 * queue_norm
          -0.10 * pressure_norm
```

Metrics are normalized using soft-clipping ($\tanh(\text{value} / \text{reference})$). Higher fitness values correspond to superior signal timing profiles.

---

## Output Data Format

Standardized output JSON files are generated under `output/results/`:

```json
{
  "algorithm": "ASM",
  "green_times": [29.71, 29.71, 14.86, 29.71],
  "cycle_time": 120,
  "avg_speed": 11.448,
  "avg_density": 192.75,
  "avg_wait_time": 3033.91,
  "total_flow": 1543.0,
  "avg_queue_length": 96.37,
  "congestion_pressure": 85.91,
  "speed_density_ratio": 0.059,
  "fitness": -0.1697,
  "convergence_history": [...],
  "simulation_steps": [...]
}
```