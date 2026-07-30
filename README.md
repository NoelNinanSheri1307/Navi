# Navi — Adaptive Traffic Intelligence Framework

### Optimized Intersection Signal Control using Parameterized Fuzzy Logic and Metaheuristic Optimization

Navi is a modular, high-performance research framework designed to optimize vehicular throughput and reduce congestion latency at signalized road intersections. The architecture combines a Parameterized Mamdani Fuzzy Inference System (FIS) with continuous metaheuristic optimization algorithms to dynamically generate green-time allocations based on traffic telemetry state vectors.

For complete system specifications, sequence diagrams, and detailed mathematical concepts, refer to the master documentation in [docs/navi_system_documentation.md](file:///c:/Users/VICTUS/Navi/docs/navi_system_documentation.md).

---

## Project Motivation and Objectives

### Why Navi Exists
Urban traffic congestion represents a major operational and environmental inefficiency. Traditional traffic control models rely on rigid, pre-timed schedules derived from historical flow averages, making them unable to adapt to real-time traffic variance. Static timing systems fail during sudden surges in density, leading to excessive waiting times, long queues, and elevated carbon emissions from idling vehicles.

### What Navi Solves
Navi addresses the problem of signal optimization at a single four-way, four-lane roadway intersection. By assessing live queue lengths and waiting times, the framework dynamically adjusts phase durations to:
- Minimize average wait times across all directions.
- Prevent queue accumulation from reaching critical gridlock levels.
- Maximize vehicle throughput by dynamically adjusting signal phase durations (between 10 seconds and 90 seconds) based on intersection pressure.

### Target Users
- Traffic engineering and municipal planning professionals comparing adaptive control models.
- Academic researchers benchmarking search algorithms under standardized parameters.
- Software developers studying asynchronous, WebSocket-driven IoT telemetry loops.

---

## Technical Architecture Overview

Navi maps real-time traffic observations (congestion pressure, density, queue length, average wait time, and flow rate) into continuous signal timing directives:

- **Client Layer (React SPA)**: Manages visual workspaces, rendering simulations and parsing incoming WebSockets.
- **Service Gateway (FastAPI)**: Coordinates REST requests and WebSocket channels.
- **Orchestration Layer (ASM / Individual Optimizers)**: Controls the optimization runs, selecting and executing search algorithms.
- **Fuzzy Mamdani Kernel**: Evaluates lane queue conditions using membership functions and rules to calculate timing adjustments.
- **Microscopic Physics Simulator**: Simulates intersection vehicle movements, applying Greenshields speed-density relations.
- **Telemetry Data Warehouse**: Stores execution summaries and sweeps metrics in JSON format for analysis.

---

## Integrated Optimization Kernels

The framework supports seven continuous search algorithms to locate optimal fuzzy membership thresholds:

- **Genetic Algorithm (GA)**: Evolves parameters using simulated binary crossover and polynomial mutation.
- **Particle Swarm Optimization (PSO)**: Swarm search modeled after social flocking behaviors.
- **Grey Wolf Optimizer (GWO)**: Updates parameters based on wolf hunting hierarchy (alpha, beta, delta).
- **Differential Evolution (DE)**: Mutates vectors using differential differences.
- **Ant Colony Optimization (ACO)**: Selects parameters using probability density functions based on continuous pheromone paths.
- **Simulated Annealing (SA)**: Physics-inspired thermal search that accepts worse states based on a decreasing temperature probability.
- **Adaptive Strategy Metaheuristic (ASM)**: Navi's core orchestrator. It monitors population diversity and convergence states in real-time, dynamically switching between algorithms to balance exploration and exploitation phases.

---

## Command Reference and Operation Guide

### Prerequisites
- Python 3.10+
- Node.js v18+

### 1. Frontend Client Operations

Navigate to the frontend folder:
```bash
cd frontend
```

#### Install Dependencies
```bash
npm install
```

#### Launch Development Server
Runs the Vite development server with hot-reloading:
```bash
npm run dev
```
By default, the client application is accessible at `http://localhost:5173`.

#### Compile Production Bundle
Builds the optimized production assets inside the `dist` directory:
```bash
npm run build
```

---

### 2. Backend Service Operations

Navigate to the backend folder:
```bash
cd backend
```

#### Install Dependencies
```bash
pip install -r requirements.txt
```

#### Start FastAPI Telemetry Server
Run the Uvicorn web server hosting REST routers and WebSocket channels:
```bash
python -m uvicorn api.main:app --host 127.0.0.1 --port 8000 --reload
```
- `--host 127.0.0.1`: Binds the server to localhost.
- `--port 8000`: Exposes the web API on port 8000.
- `--reload`: Enables hot-reloading on python file modifications (recommended for development).

#### Start Asynchronous CLI Benchmark Run
To run optimization sweeps directly on the command line without the web interface:
```bash
python main.py
```

#### CLI Configuration Arguments
The backend CLI supports the following configuration parameters:
- `--fast`: Runs a quick evaluation sweep with fewer generations (ideal for system checks).
- `--algorithms GA PSO DE`: Limits the evaluation sweep to the specified algorithms.
- `--seeds 42 100 200`: Evaluates performance using specific random seeds.
- `--steps 50`: Set the maximum number of simulation steps per optimization epoch.

Example executing a fast, limited sweep:
```bash
python main.py --fast --algorithms GA GWO --steps 20
```

---

## Core Performance Metrics

- **Total Flow**: Aggregate vehicular throughput (vehicles/hour).
- **Average Speed**: Mean velocity across lanes (km/h) derived from Greenshields relation.
- **Wait Latency**: Cumulative wait duration per signal cycle (seconds).
- **Queue Backlog**: Queue accumulation count (vehicles).
- **Congestion Pressure**: Dimensionless ratio comparing lane density with delay metrics.

---

Navi Intelligence Framework. All rights reserved.
