# 🚦 Navi — Adaptive Traffic Intelligence Framework

### Optimized Intersection Signal Control using Parameterized Fuzzy Logic & Metaheuristic Optimization

Navi is a modular, high-performance research framework designed to optimize vehicular throughput and reduce congestion latency at signalized road intersections. The architecture combines a **Mamdani Fuzzy Inference System (FIS)** with modern metaheuristic algorithms to dynamically generate green-time allocations based on telemetry state vectors.

---

## 🧬 Framework Overview

Navi maps real-time traffic observations (congestion pressure, density, queue length, average wait time, and flow rate) into continuous signal timing directives:

- **Parameterized Antecedents**: A 35-dimensional continuous decision vector ($\mathbf{\theta} \in [0, 1]^{35}$) dynamically scales break-points across 5 linguistic input variables.
- **Rule Base**: A 9-rule Mamdani inference matrix evaluates fuzzy membership states to compute target green-phase durations ($10\text{s} - 90\text{s}$).
- **Optimization Kernels**: Integrates 7 metaheuristic search strategies:
  - **GA**: Genetic Algorithm (Simulated Binary Crossover + Polynomial Mutation)
  - **PSO**: Particle Swarm Optimization (Inertia Weight Decay)
  - **GWO**: Grey Wolf Optimizer (Leadership Hierarchy Dynamics)
  - **DE**: Differential Evolution ($\text{DE/rand/1/bin}$)
  - **ACO**: Ant Colony Optimization for Continuous Domains ($\text{ACOR}$)
  - **SA**: Simulated Annealing (Geometric Cooling Schedule)
  - **HYBRID**: Multi-Stage ACO-SA-GA Hybrid Kernel

---

## 🏗️ Project Architecture

```
Navi/
├── backend/                  # Computational engine & optimization kernels
│   ├── evaluation/           # Shared fitness evaluation module
│   ├── fuzzy/                # Parameterized Mamdani FIS implementation
│   ├── model/                # Traffic flow simulation engine
│   ├── optimization/         # Metaheuristic optimizers (GA, PSO, GWO, DE, ACO, SA, Hybrid)
│   ├── output/results/       # Structured benchmark results
│   ├── main.py               # Backend CLI execution pipeline
│   └── requirements.txt      # Dependencies
├── frontend/                 # Interactive intelligence dashboard (React + Vite)
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
python main.py --algorithms GA PSO HYBRID
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
