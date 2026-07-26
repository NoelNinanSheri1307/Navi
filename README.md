# 🚦 Navi — Adaptive Traffic Intelligence Framework

### Optimized Intersection Signal Control using Parameterized Fuzzy Logic & Metaheuristic Optimization

Navi is a modular, high-performance research framework designed to optimize vehicular throughput and reduce congestion latency at signalized road intersections. The architecture combines a **Mamdani Fuzzy Inference System (FIS)** with modern metaheuristic algorithms to dynamically generate green-time allocations based on telemetry state vectors.

For the complete technical blueprint and scientific design document, refer to [`docs/architecture_master_blueprint.md`](file:///C:/Users/VICTUS/Navi/docs/architecture_master_blueprint.md).

---

## 🧬 Framework Overview

Navi maps real-time traffic observations (congestion pressure, density, queue length, average wait time, and flow rate) into continuous signal timing directives:

- **Parameterized Antecedents**: A 35-dimensional continuous decision vector ($\mathbf{\theta} \in [0, 1]^{35}$) dynamically scales break-points across 5 linguistic input variables.
- **Rule Base**: A 9-rule Mamdani inference matrix evaluates fuzzy membership states to compute target green-phase durations ($10\text{s} - 90\text{s}$).
- **Optimization Kernels**: Integrates metaheuristic search algorithms (GA, PSO, GWO, DE, ACO, SA) and the new **Adaptive Strategy Metaheuristic (ASM)** framework.

---

## 🏗️ Refactored Project Architecture

```
Navi/
├── backend/                  # Computational engine & research modules
│   ├── adaptive/             # Adaptive Strategy Metaheuristic (ASM) Framework
│   ├── algorithms/           # Standard search algorithms (GA, PSO, GWO, DE, ACO, SA)
│   ├── analytics/            # Statistical testing & profiler submodules
│   ├── api/                  # REST & WebSocket telemetry interfaces
│   ├── configs/              # System & benchmark configuration schemas
│   ├── datasets/             # Data ingestion and VANET CSV loaders
│   ├── evaluation/           # Scalar fitness & multi-objective Pareto kernels
│   ├── experiments/          # Multi-seed benchmark trial runner
│   ├── fuzzy/                # Parameterized Mamdani FIS & explainability
│   ├── simulation/           # Microscopic traffic physics model (Greenshields)
│   ├── tests/                # Verification unit tests
│   ├── main.py               # Main CLI execution pipeline
│   └── requirements.txt      # Dependencies
├── docs/                     # Research Documentation & Master Blueprints
│   └── architecture_master_blueprint.md
├── frontend/                 # Interactive Intelligence Dashboard (React + Vite)
└── vanet.csv                 # Real-world vehicular telemetry dataset (~195k records)
```

---

## 🚀 Quick Start Guide

### Prerequisites
- **Python**: 3.10+
- **Node.js**: v18+

### 1. Frontend Dashboard Setup
```bash
cd frontend
npm install
npm run dev
```
Access the dashboard at `http://localhost:5173`.

### 2. Backend Benchmark Execution
```bash
cd backend
pip install -r requirements.txt
python main.py
```

Run specific optimization modes or quick tests:
```bash
python main.py --algorithms GA PSO
python main.py --fast
```

---

## 📊 Core Performance Metrics

- **Total Flow**: Aggregate vehicular throughput (vehicles/hour).
- **Average Speed**: Mean velocity across lanes ($\text{km/h}$).
- **Wait Latency**: Cumulative wait duration per signal cycle ($\text{seconds}$).
- **Queue Backlog**: Queue accumulation count ($\text{vehicles}$).
- **Congestion Pressure**: Dimensionless ratio derived from lane density and delay metrics.

---

© 2026 Navi Intelligence Framework. All rights reserved.
