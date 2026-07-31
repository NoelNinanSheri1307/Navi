import os
import sys
import time
import json
import threading
import numpy as np

# Ensure parent directory is in the path for local imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from evaluation.fitness import evaluate_fitness
from algorithms.asm import AdaptiveStrategyMetaheuristic
from algorithms.strategy_registry import StrategyRegistry

def generate_replay_for_algo(algorithm: str, csv_path: str, pop_size: int, n_gen: int):
    print(f"Generating replay for {algorithm}...")
    seed = 42
    
    def fitness_fn(cand):
        return evaluate_fitness(cand, csv_path=csv_path, seed=seed)
        
    if algorithm == "ASM":
        optimizer = AdaptiveStrategyMetaheuristic(
            dim=35,
            bounds=(0.0, 1.0),
            budget=pop_size * n_gen,
            pop_size=pop_size,
            seed=seed,
            verbose=True,
            adaptive_switching=True,
            confidence_threshold=0.03,
            minimum_runtime_steps=5,
            switch_cooldown_steps=5,
            adaptive_debug=True
        )
    else:
        registry = StrategyRegistry()
        optimizer = registry.create(
            name=algorithm,
            dim=35,
            bounds=(0.0, 1.0),
            budget=pop_size * n_gen,
            pop_size=pop_size,
            seed=seed,
            verbose=True
        )

    optimizer.initialize(fitness_fn, pop_size=pop_size)
    
    steps = []
    
    for step_idx in range(n_gen):
        t0 = time.time()
        state = optimizer.step(fitness_fn)
        step_elapsed = time.time() - t0
        
        best_sol = optimizer.get_best_solution()
        fit, fit_res = fitness_fn(best_sol)
        
        telemetry = {
            "iteration": step_idx,
            "fitness": float(fit),
            "best_fitness": float(optimizer.state.best_fitness),
            "current_optimizer": getattr(optimizer, "current_optimizer", algorithm),
            "runtime": float(step_elapsed),
            "green_times": [float(g) for g in fit_res.get("green_times", [])],
            "cycle_time": float(fit_res.get("cycle_time", 120)),
            "avg_speed": float(fit_res.get("avg_speed", 0.0)),
            "avg_density": float(fit_res.get("avg_density", 0.0)),
            "avg_wait_time": float(fit_res.get("avg_wait_time", 0.0)),
            "total_flow": float(fit_res.get("total_flow", 0.0)),
            "avg_queue_length": float(fit_res.get("avg_queue_length", 0.0)),
            "congestion_pressure": float(fit_res.get("congestion_pressure", 0.0)),
        }
        
        if algorithm == "ASM":
            telemetry.update({
                "confidence": float(getattr(optimizer, "last_confidence", 0.0) or 0.0),
                "recommendation": str(getattr(optimizer, "last_recommendation", "") or ""),
                "switch_decision": "SWITCH" if getattr(optimizer, "steps_since_last_switch", 0) == 0 else "STAY",
                "cooldown": int(getattr(optimizer, "steps_since_last_switch", 0)),
                "runtime_gates": int(getattr(optimizer, "current_optimizer_runtime", 0)),
            })
            try:
                latest_rec = getattr(optimizer, "latest_recommendation", None)
                if latest_rec is not None:
                    telemetry["needs"] = {
                        "exploration": float(latest_rec.needs.get("Exploration", 0.0)),
                        "exploitation": float(latest_rec.needs.get("Exploitation", 0.0)),
                        "escape": float(latest_rec.needs.get("Escape", 0.0))
                    }
            except Exception:
                pass
                
        step_events = []
        
        # 1. Telemetry event
        step_events.append({
            "type": "telemetry",
            "data": telemetry
        })
        
        # 2. Iteration Completed event
        step_events.append({
            "type": "event",
            "event": "Iteration Completed",
            "payload": {"iteration": step_idx, "fitness": float(fit)}
        })
        
        # 3. ASM switch accepted event
        if algorithm == "ASM" and getattr(optimizer, "steps_since_last_switch", 0) == 0:
            step_events.append({
                "type": "event",
                "event": "Switch Accepted",
                "payload": {"target": optimizer.current_optimizer}
            })
            
        steps.append({
            "step": step_idx,
            "events": step_events
        })
        
    # Compile final result to standard format
    best_solution = optimizer.get_best_solution()
    best_fitness, best_result = fitness_fn(best_solution)
    
    final_result = {
        "algorithm": algorithm,
        "green_times": [round(float(g), 2) for g in best_result.get("green_times", [])],
        "cycle_time": int(best_result.get("cycle_time", 120)),
        "avg_speed": round(float(best_result.get("avg_speed", 0.0)), 4),
        "avg_density": round(float(best_result.get("avg_density", 0.0)), 4),
        "avg_wait_time": round(float(best_result.get("avg_wait_time", 0.0)), 4),
        "total_flow": round(float(best_result.get("total_flow", 0.0)), 4),
        "avg_queue_length": round(float(best_result.get("avg_queue_length", 0.0)), 4),
        "congestion_pressure": round(float(best_result.get("congestion_pressure", 0.0)), 6),
        "fitness": round(float(best_fitness), 8),
        "convergence_history": [round(float(f), 8) for f in optimizer.get_history()],
        "simulation_steps": best_result.get("simulation_steps", [])
    }
    
    # Save files
    replays_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets", "replays")
    os.makedirs(replays_dir, exist_ok=True)
    
    replay_path = os.path.join(replays_dir, f"{algorithm.lower()}_replay.json")
    with open(replay_path, "w", encoding="utf-8") as f:
        json.dump({"algorithm": algorithm, "steps": steps, "final_result": final_result}, f, indent=2)
        
    print(f"Saved replay asset to {replay_path}")

if __name__ == "__main__":
    csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "datasets", "vanet.csv")
    if not os.path.exists(csv_path):
        # fallback
        csv_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "vanet.csv")
        
    algos = ["GA", "PSO", "GWO", "DE", "ACO", "SA", "ASM"]
    for algo in algos:
        generate_replay_for_algo(algo, csv_path, pop_size=15, n_gen=20)
    print("All replays successfully generated!")
