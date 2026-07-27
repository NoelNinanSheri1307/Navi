"""
fitness.py
----------
Shared fitness function used by ALL optimization algorithms.

fitness = +0.30 * flow_norm
          +0.25 * speed_norm
          -0.20 * wait_norm
          -0.15 * queue_norm
          -0.10 * pressure_norm

All raw metrics are normalised to [0,1] using soft-clip / reference values so
that the fitness is always comparable across experiments.
"""

import numpy as np

try:
    from simulation.traffic_model import run_simulation
except ImportError:
    from model.traffic_model import run_simulation

# ─────────────────────────────────────────────────────────────────────────────
# Normalisation reference values (domain-expert estimates)
# ─────────────────────────────────────────────────────────────────────────────
REF = {
    'flow':     7200.0,   # veh/hr
    'speed':    70.0,     # km/h
    'wait':     2500.0,   # seconds (scaled for heavy traffic)
    'queue':    120.0,    # vehicles (scaled for heavy traffic)
    'pressure': 2.5,      
}

# Adjusted Weights (Boosted Flow and Speed importance)
W_FLOW     =  0.35
W_SPEED    =  0.30
W_WAIT     = -0.15
W_QUEUE    = -0.10
W_PRESSURE = -0.10


def _norm(value: float, ref: float) -> float:
    """Soft-clip normalisation: tanh(value / ref)."""
    return float(np.tanh(value / max(ref, 1e-9)))


def evaluate_fitness(
    params: np.ndarray,
    csv_path: str = "vanet.csv",
    seed: int | None = None,
) -> tuple[float, dict]:
    """
    Evaluate the fitness of a 35-dim fuzzy parameter vector.

    Parameters
    ----------
    params   : 35-d array in [0, 1]
    csv_path : path to VANET.csv
    seed     : optional random seed for deterministic evaluation

    Returns
    -------
    fitness  : scalar float (higher is better)
    result   : full simulation result dict
    """
    result = run_simulation(params, csv_path=csv_path, seed=seed)

    flow_n     = _norm(result['total_flow'],          REF['flow'])
    speed_n    = _norm(result['avg_speed'],            REF['speed'])
    wait_n     = _norm(result['avg_wait_time'],        REF['wait'])
    queue_n    = _norm(result['avg_queue_length'],     REF['queue'])
    pressure_n = _norm(result['congestion_pressure'],  REF['pressure'])

    fitness = (
        W_FLOW     * flow_n
        + W_SPEED  * speed_n
        + W_WAIT   * wait_n
        + W_QUEUE  * queue_n
        + W_PRESSURE * pressure_n
    )

    return float(fitness), result
