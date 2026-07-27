# ASM Architecture Documentation
## Adaptive Strategy Metaheuristic -- Stage 4.0A Infrastructure

---

## 1. Overview

ASM is a multi-strategy orchestration optimizer that coordinates existing
BaseOptimizer subclasses (GA, DE, PSO, GWO, ACO, SA) within a single
optimization run. It inherits from BaseOptimizer, exposing the standard
`initialize()` / `step()` / `optimize()` / `reset()` interface. From the
perspective of ExperimentManager, ASM is indistinguishable from any other
optimizer.

**Stage 4.0A delivers the orchestration infrastructure with configurable
switching schedules.** The adaptive decision engine will be implemented in
Stage 4.0B after analysis of the Stage 3.8 baseline benchmark results.

---

## 2. Component Architecture

```
ASM (AdaptiveStrategyMetaheuristic)
 |
 +-- StrategyRegistry        # Maps strategy names to optimizer classes
 |     register() / unregister() / create() / available()
 |
 +-- ASMController           # Manages sub-optimizer lifecycle
 |     load_optimizer()      # Instantiate via registry
 |     initialize_optimizer() # Initialize and sync global best
 |     step_optimizer()      # Delegate step() to active optimizer
 |     switch_strategy()     # Export -> Save -> Create -> Initialize -> Inject
 |     export_controller_state() / reset()
 |
 +-- Switch Schedule         # Configurable evaluation thresholds
       [(strategy, threshold), ...]
       Currently: manual schedule
       Future: adaptive policy (Stage 4.0B)
```

---

## 3. File Inventory

### Created Files

| File | Purpose |
|------|---------|
| `algorithms/asm.py` | Core ASM optimizer class |
| `algorithms/strategy_registry.py` | Strategy name to optimizer class registry |
| `algorithms/operators/asm_controller.py` | Sub-optimizer lifecycle controller |

### Modified Files

| File | Change |
|------|--------|
| `experiments/manager.py` | Added ASM to OPTIMIZER_REGISTRY |
| `main.py` | Added ASM to ALGO_REGISTRY and EXTRA_KWARGS |

---

## 4. Strategy Registry Design

**File:** `algorithms/strategy_registry.py`

The StrategyRegistry provides a factory-style interface for ASM to
instantiate optimizer classes without importing them directly.

### API

- `register(name, cls)` -- Add a new optimizer class.
- `unregister(name)` -- Remove an optimizer class.
- `create(name, dim, bounds, budget, pop_size, seed, verbose, **kwargs)` -- Factory instantiation.
- `available()` -- List all registered strategy names.
- `contains(name)` -- Check if a strategy is registered.
- `get_class(name)` -- Retrieve class without instantiation.

### Default Strategies

GA, DE, PSO, GWO, ACO, SA (lazily populated on first access to avoid
circular imports).

---

## 5. ASM Controller Design

**File:** `algorithms/operators/asm_controller.py`

The ASMController manages the complete lifecycle of sub-strategy optimizers
within an ASM run, using only public BaseOptimizer methods.

### Responsibilities

1. **Load optimizer** -- Instantiate via StrategyRegistry.create().
2. **Initialize optimizer** -- Call initialize() and sync global best.
3. **Monitor execution** -- Delegate step() calls and track evaluations.
4. **Export optimizer state** -- Call export_state() before switches.
5. **Restore optimizer state** -- Archive states for potential reuse.
6. **Switch optimizer** -- Full pipeline: export, save, create, initialize, inject.
7. **Track optimizer history** -- Record StrategyTransition objects.
8. **Maintain global progress** -- Independent global best tracking.

### Interface Contract

The controller never accesses optimizer internals directly. All interaction
flows through:

- `initialize()` / `step()`
- `export_state()` / `restore_state()`
- `get_best_solution()` / `get_population()`
- `is_budget_exhausted()`

---

## 6. Optimizer Lifecycle

```
ASM.initialize()
  |
  +-> Controller.load_optimizer("GA", budget)
  +-> Controller.initialize_optimizer(fitness_fn)
  +-> Sync global best
  +-> Log initial state

ASM.step()  [repeated per iteration]
  |
  +-> Check schedule threshold
  |   |
  |   +-> If threshold crossed:
  |       +-> Controller.switch_strategy(new_strategy)
  |           +-> export_state() on current optimizer
  |           +-> Save state to archive
  |           +-> load_optimizer(new_strategy)
  |           +-> initialize_optimizer(fitness_fn)
  |           +-> Inject global best into new population
  |           +-> Record StrategyTransition
  |
  +-> Controller.step_optimizer(fitness_fn)
  +-> Sync global best
  +-> Log step metrics
```

---

## 7. State Serialization Model

### PopulationState.metadata Contents

```python
{
    "current_strategy": "PSO",
    "strategy_history": [
        {"from": "", "to": "GA", "evals": 0, "reason": "initial_load", ...},
        {"from": "GA", "to": "PSO", "evals": 100, "reason": "schedule", ...},
    ],
    "strategy_switches": 1,
    "strategy_runtime": {"GA": 12.3, "PSO": 8.7},
    "global_best_solution": [0.5, 0.3, ...],
    "global_best_fitness": -2.345678,
    "remaining_budget": 400,
    "elapsed_time": 21.0,
    "schedule_index": 1,
    "switch_schedule": [
        {"strategy": "GA", "threshold": 100},
        {"strategy": "PSO", "threshold": 200},
    ],
}
```

### export_state() Output

```python
{
    "name": "ASM",
    "generation": 25,
    "evaluations_used": 150,
    "schedule_index": 1,
    "total_evaluations": 150,
    "switch_schedule": [...],
    "controller_state": {
        "active_strategy": "PSO",
        "global_best_fitness": -2.345,
        "global_best_solution": [...],
        "switch_count": 1,
        "transition_history": [...],
        "strategy_runtimes": {...},
        "optimizer_states": {"GA": {...}},
    },
    "population_state": PopulationState(...),
    "history": [...]
}
```

---

## 8. Manual Switch Schedule Design

### Structure

```python
switch_schedule = [
    ("GA",  100),   # Run GA until 100 cumulative evaluations
    ("PSO", 200),   # Switch to PSO at 100 evals, run until 200
    ("GWO", 300),   # Switch to GWO at 200, run until 300
    ("SA",  400),   # Switch to SA at 300, run until budget exhaustion
]
```

### Auto-Scaling

When no schedule is provided, ASM auto-generates one by dividing the
budget equally across all six strategies:

```python
budget = 600 -> [(GA, 100), (DE, 200), (PSO, 300), (GWO, 400), (SA, 500), (ACO, 600)]
```

### Isolation for Future Replacement

The switching logic is entirely contained within `_check_and_switch()`.
In Stage 4.0B, this single method will be augmented or replaced by an
adaptive decision engine without modifying the ASM public API.

---

## 9. Interaction with BaseOptimizer

ASM inherits from BaseOptimizer and satisfies its full contract:

| Method | ASM Behavior |
|--------|-------------|
| `initialize()` | Loads first strategy, initializes it, starts logging |
| `step()` | Checks schedule, delegates to active optimizer, logs |
| `optimize()` | Full run loop with schedule-driven transitions |
| `reset()` | Resets ASM + controller + schedule state |
| `export_state()` | Serializes complete ASM state tree |
| `restore_state()` | Restores from serialized state |
| `get_best_solution()` | Returns controller's global best |
| `get_population()` | Returns active optimizer's population |
| `is_budget_exhausted()` | Standard budget check |

---

## 10. Future Adaptive Extension Points

Stage 4.0B will introduce adaptive switching without modifying ASM's
public interface. The following extension points are designed for this:

1. **`_check_and_switch()`** -- Replace schedule logic with adaptive policy.
2. **ASMController** -- Already supports arbitrary switch reasons.
3. **StrategyTransition.reason** -- Records switch rationale for analysis.
4. **PopulationState.metadata** -- Can store additional adaptive telemetry.
5. **StrategyRegistry** -- Can dynamically add/remove strategies at runtime.

---

## 11. Time Complexity

| Operation | Complexity |
|-----------|-----------|
| Strategy switch | O(P*D) -- population re-initialization |
| Step delegation | O(1) overhead -- delegates directly to sub-optimizer |
| Global best sync | O(1) -- single comparison |
| Global best injection | O(P) -- find worst, replace |
| State export | O(P*D) -- copy population arrays |
| Schedule check | O(1) -- index comparison |

Where P = population size, D = dimensionality.

---

## 12. Integration Points

### ExperimentManager

```python
# experiments/manager.py
OPTIMIZER_REGISTRY = {
    ...
    "ASM": AdaptiveStrategyMetaheuristic,
}
```

### main.py

```python
# main.py
ALGO_REGISTRY = {
    ...
    'ASM': ('algorithms.asm', 'run_asm'),
}
```

### CLI Usage

```bash
python run_experiment.py --optimizer ASM
python run_experiment.py --optimizer ASM --fast
python main.py --algorithms ASM --fast
python main.py --algorithms ASM
```
