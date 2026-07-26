# ⚙️ Navi Backend Engine — Optimization & Simulation Kernel

A modular Python framework for optimizing traffic signal green-time allocations using **Parameterized Fuzzy Logic** shaped by **7 Metaheuristic Algorithms**.

---

## Architecture

```
backend/
├── fuzzy/
│   └── fuzzy_system.py          # Parameterized 35-dim fuzzy membership function builder
├── optimization/
│   ├── ga.py                    # Genetic Algorithm (SBX + Polynomial Mutation)
│   ├── pso.py                   # Particle Swarm Optimization
│   ├── gwo.py                   # Grey Wolf Optimizer
│   ├── de.py                    # Differential Evolution (DE/rand/1/bin)
│   ├── aco.py                   # Continuous Ant Colony Optimization (ACOR)
│   ├── sa.py                    # Simulated Annealing
│   └── hybrid_aco_sa_ga.py      # Triple-Hybrid Optimizer
├── model/
│   └── traffic_model.py         # 4-Lane traffic flow simulator (Greenshields model)
├── evaluation/
│   └── fitness.py               # Objective function evaluation kernel
├── output/
│   └── results/                 # Standardized JSON benchmark outputs
├── main.py                      # Main pipeline CLI controller
└── requirements.txt             # Requirements manifest
```

---

## Requirements & Installation

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

```bash
cd backend

# Run all 7 algorithms
python main.py

# Run targeted algorithms
python main.py --algorithms GA PSO HYBRID

# Fast diagnostic mode (reduced pop/iter)
python main.py --fast

# Customized pop/iter/seed
python main.py --pop 40 --iter 100 --seed 42
```

---

## Decision Vector Formulation

A **35-dimensional decision vector** $\mathbf{\theta} \in [0, 1]^{35}$ parameters the membership functions of 5 antecedent variables (7 breakpoints each):

| Vector Index | Target Antecedent Variable |
|---|---|
| 0–6 | `congestion_pressure` membership breakpoints |
| 7–13 | `density_veh_per_km` membership breakpoints |
| 14–20 | `queue_length_veh` membership breakpoints |
| 21–27 | `avg_wait_time_s` membership breakpoints |
| 28–34 | `flow_veh_per_hr` membership breakpoints |

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
  "algorithm": "GA",
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

Combined summary files are exported to `output/results/summary.json`.