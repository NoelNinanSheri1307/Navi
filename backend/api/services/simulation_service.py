import os
import time
import asyncio
import threading
from typing import Dict, List, Any, Optional, Tuple
import numpy as np

try:
    from simulation.traffic_model import get_stats
except ImportError:
    from model.traffic_model import get_stats

from evaluation.fitness import evaluate_fitness
from algorithms.strategy_registry import StrategyRegistry
from algorithms.asm import AdaptiveStrategyMetaheuristic
from algorithms.base import PopulationState

class SimulationService:
    """
    Thread-safe Singleton service managing the execution state of the traffic simulator
    and optimization runners, bridging synchronous calculations with asynchronous FastAPI streams.
    """
    _instance: Optional['SimulationService'] = None
    _lock = threading.Lock()

    def __new__(cls, *args, **kwargs):
        with cls._lock:
            if cls._instance is None:
                cls._instance = super(SimulationService, cls).__new__(cls)
                cls._instance._init_service()
            return cls._instance

    def _init_service(self):
        self.lock = threading.Lock()
        self.running = False
        self.paused = False
        self.current_step = 0
        self.total_steps = 50
        self.speed_multiplier = 1.0
        
        self.active_algorithm: Optional[str] = None
        self.active_dataset: Optional[str] = None
        self.optimizer: Optional[Any] = None
        
        self.subscribers: List[Any] = [] # WebSocket connection pools
        self.history_records: List[Dict[str, Any]] = []
        self.loop: Optional[asyncio.AbstractEventLoop] = None
        self.run_thread: Optional[threading.Thread] = None

    def register_loop(self, loop: asyncio.AbstractEventLoop):
        self.loop = loop

    def add_subscriber(self, websocket: Any):
        with self.lock:
            self.subscribers.append(websocket)

    def remove_subscriber(self, websocket: Any):
        with self.lock:
            if websocket in self.subscribers:
                self.subscribers.remove(websocket)

    def set_speed(self, multiplier: float):
        with self.lock:
            self.speed_multiplier = max(0.1, min(10.0, multiplier))

    def pause(self):
        with self.lock:
            if self.running:
                self.paused = True

    def resume(self):
        with self.lock:
            if self.running:
                self.paused = False

    def cancel(self):
        with self.lock:
            self.running = False
            self.paused = False

    def reset(self):
        self.cancel()
        with self.lock:
            self.current_step = 0
            self.optimizer = None
            self.active_algorithm = None
            self.active_dataset = None

    def broadcast_sync(self, message: Dict[str, Any]):
        if self.loop and self.subscribers:
            asyncio.run_coroutine_threadsafe(
                self._broadcast_async(message), 
                self.loop
            )

    async def _broadcast_async(self, message: Dict[str, Any]):
        disconnected = []
        for ws in list(self.subscribers):
            try:
                await ws.send_json(message)
            except Exception:
                disconnected.append(ws)
        
        with self.lock:
            for ws in disconnected:
                if ws in self.subscribers:
                    self.subscribers.remove(ws)

    def start_simulation(self, algorithm: str, dataset: str, pop_size: int, n_gen: int):
        with self.lock:
            if self.running:
                raise RuntimeError("Simulation is already running.")
            
            self.running = True
            self.paused = False
            self.current_step = 0
            self.total_steps = n_gen
            self.active_algorithm = algorithm.upper()
            self.active_dataset = dataset
            
            # Resolve dataset path absolutely relative to module structure
            backend_datasets_dir = os.path.abspath(
                os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..", "datasets")
            )
            project_root_dir = os.path.dirname(os.path.dirname(backend_datasets_dir))  # Navi/

            possible_paths = [
                os.path.abspath(dataset),
                os.path.join(backend_datasets_dir, dataset),
                os.path.join(project_root_dir, dataset),
            ]

            csv_path = None
            for p in possible_paths:
                if os.path.isfile(p):
                    csv_path = p
                    break

            if not csv_path:
                checked = ", ".join(f"'{p}'" for p in possible_paths)
                raise FileNotFoundError(
                    f"Dataset path '{dataset}' could not be resolved. Checked: {checked}"
                )

            # Spawn runner thread
            self.run_thread = threading.Thread(
                target=self._run_optimization_loop,
                args=(self.active_algorithm, csv_path, pop_size, n_gen),
                daemon=True
            )
            self.run_thread.start()

    def _run_optimization_loop(self, algorithm: str, csv_path: str, pop_size: int, n_gen: int):
        # 1. Emit Simulation Started Event
        self.broadcast_sync({
            "type": "event",
            "event": "Simulation Started",
            "timestamp": time.time(),
            "payload": {"algorithm": algorithm, "dataset": csv_path}
        })

        seed = 42
        def fitness_fn(cand):
            return evaluate_fitness(cand, csv_path=csv_path, seed=seed)

        try:
            # 2. Instantiate Optimizer
            if algorithm == "ASM":
                self.optimizer = AdaptiveStrategyMetaheuristic(
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
                self.optimizer = registry.create(
                    name=algorithm,
                    dim=35,
                    bounds=(0.0, 1.0),
                    budget=pop_size * n_gen,
                    pop_size=pop_size,
                    seed=seed,
                    verbose=True
                )

            self.optimizer.initialize(fitness_fn, pop_size=pop_size)
            
            # 3. Stepping loop
            for step_idx in range(n_gen):
                # Check execution flags
                while True:
                    with self.lock:
                        if not self.running:
                            self.broadcast_sync({
                                "type": "event",
                                "event": "Simulation Cancelled",
                                "timestamp": time.time(),
                                "payload": {}
                            })
                            return
                        if not self.paused:
                            break
                    time.sleep(0.1)

                with self.lock:
                    self.current_step = step_idx

                t0 = time.time()
                # Run one step
                state = self.optimizer.step(fitness_fn)
                step_elapsed = time.time() - t0

                # Interpolate intermediate simulation stats (e.g. mock intermediate steps based on best candidate)
                best_sol = self.optimizer.get_best_solution()
                fit, fit_res = fitness_fn(best_sol)

                # Assemble Telemetry Snapshot
                telemetry = {
                    "iteration": step_idx,
                    "fitness": float(fit),
                    "best_fitness": float(self.optimizer.state.best_fitness),
                    "current_optimizer": getattr(self.optimizer, "current_optimizer", algorithm),
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

                # Attach ASM metrics if active
                if algorithm == "ASM":
                    telemetry.update({
                        "confidence": float(getattr(self.optimizer, "last_confidence", 0.0) or 0.0),
                        "recommendation": str(getattr(self.optimizer, "last_recommendation", "") or ""),
                        "switch_decision": "SWITCH" if getattr(self.optimizer, "steps_since_last_switch", 0) == 0 else "STAY",
                        "cooldown": int(getattr(self.optimizer, "steps_since_last_switch", 0)),
                        "runtime_gates": int(getattr(self.optimizer, "current_optimizer_runtime", 0)),
                    })
                    # Attempt to extract needs
                    try:
                        latest_rec = getattr(self.optimizer, "latest_recommendation", None)
                        if latest_rec is not None:
                            telemetry["needs"] = {
                                "exploration": float(latest_rec.needs.get("Exploration", 0.0)),
                                "exploitation": float(latest_rec.needs.get("Exploitation", 0.0)),
                                "escape": float(latest_rec.needs.get("Escape", 0.0))
                            }
                    except Exception:
                        pass

                # Emit Iteration Completed Event & Telemetry Snapshot
                self.broadcast_sync({
                    "type": "telemetry",
                    "data": telemetry
                })
                self.broadcast_sync({
                    "type": "event",
                    "event": "Iteration Completed",
                    "timestamp": time.time(),
                    "payload": {"iteration": step_idx, "fitness": float(fit)}
                })

                # Check if switch accepted or recommended
                if algorithm == "ASM":
                    if getattr(self.optimizer, "steps_since_last_switch", 0) == 0:
                        self.broadcast_sync({
                            "type": "event",
                            "event": "Switch Accepted",
                            "timestamp": time.time(),
                            "payload": {"target": self.optimizer.current_optimizer}
                        })

                # Delay based on speed multiplier
                delay_sec = 1.0 / self.speed_multiplier
                time.sleep(delay_sec)

            # Finalize optimization result
            best_solution = self.optimizer.get_best_solution()
            best_fitness, best_result = fitness_fn(best_solution)
            
            # Serialize result JSON to disk
            out_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "output", "results")
            os.makedirs(out_dir, exist_ok=True)
            
            result_path = os.path.join(out_dir, f"{algorithm.lower()}_result.json")
            standardized = {
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
                "convergence_history": [round(float(f), 8) for f in self.optimizer.get_history()],
                "simulation_steps": best_result.get("simulation_steps", [])
            }
            
            with open(result_path, "w", encoding="utf-8") as f:
                import json
                json.dump(standardized, f, indent=2)

            # Save to local cache history
            with self.lock:
                self.history_records.append({
                    "timestamp": time.strftime("%H:%M:%S"),
                    "dataset": os.path.basename(csv_path),
                    "algorithm": algorithm,
                    "runtime": f"{step_idx * delay_sec:.1f}s",
                    "bestFitness": f"{best_fitness:.5f}",
                    "iterations": n_gen,
                    "avgDelay": f"{best_result.get('avg_wait_time', 0.0):.1f}s",
                    "queueLength": f"{best_result.get('avg_queue_length', 0.0):.1f}"
                })

            # 4. Emit Optimization Finished Event
            self.broadcast_sync({
                "type": "event",
                "event": "Optimization Finished",
                "timestamp": time.time(),
                "payload": {"best_fitness": float(best_fitness)}
            })

        except Exception as e:
            self.broadcast_sync({
                "type": "event",
                "event": "Error Occurred",
                "timestamp": time.time(),
                "payload": {"error": str(e)}
            })
        finally:
            with self.lock:
                self.running = False
                self.paused = False
