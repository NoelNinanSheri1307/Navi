"""
traffic_model.py
----------------
Semi-realistic 4-lane intersection traffic simulation.

The model evolves over `n_cycles` signal cycles, each of length
`cycle_time` seconds. At every cycle it:
  1. Samples 4 rows from VANET.csv as initial lane conditions.
  2. Uses the fuzzy system to compute a green-time allocation per lane.
  3. Simulates arrivals, departures, queue, wait, speed, flow, density,
     and congestion pressure with small Gaussian noise.
  4. Records per-cycle metrics and returns a summary dict.
"""

import numpy as np
import pandas as pd

from fuzzy.fuzzy_system import build_fuzzy_system, compute_green_time
from datasets.loader import DatasetLoader
from configs.simulation_config import DEFAULT_SIMULATION_CONFIG

# ─────────────────────────────────────────────────────────────────────────────
# Constants (Imported from centralized simulation config for framework consistency)
# ─────────────────────────────────────────────────────────────────────────────
N_LANES     = DEFAULT_SIMULATION_CONFIG.n_lanes
CYCLE_TIME  = int(DEFAULT_SIMULATION_CONFIG.cycle_time)
N_CYCLES    = DEFAULT_SIMULATION_CONFIG.n_cycles
FREE_SPEED  = DEFAULT_SIMULATION_CONFIG.free_speed
LANE_LENGTH = DEFAULT_SIMULATION_CONFIG.lane_length
NOISE_STD   = DEFAULT_SIMULATION_CONFIG.noise_std


def _load_dataset(csv_path: str) -> pd.DataFrame:
    """Delegates dataset loading to thread-safe DatasetLoader while preserving signature."""
    return DatasetLoader.load_dataset(csv_path)


def get_stats(csv_path: str = "vanet.csv") -> dict:
    """Delegates dataset stats extraction to thread-safe DatasetLoader while preserving signature."""
    return DatasetLoader.get_stats(csv_path)


# ─────────────────────────────────────────────────────────────────────────────
# Noise helper
# ─────────────────────────────────────────────────────────────────────────────
def _noisy(value: float, std: float = NOISE_STD) -> float:
    return max(0.0, value * (1.0 + np.random.normal(0, std)))


# ─────────────────────────────────────────────────────────────────────────────
# Single-cycle lane update
# ─────────────────────────────────────────────────────────────────────────────
def _simulate_lane_cycle(
    lane_row: dict,
    green_t: float,
    prev_queue: float,
) -> dict:
    """
    Simulate one cycle for one lane.

    Returns dict with updated metrics.
    """
    # --- Arrival rate (veh/s) from flow ---
    flow_hr   = _noisy(lane_row['flow_veh_per_hr'])
    arr_rate  = flow_hr / 3600.0                    # veh/s
    arrivals  = arr_rate * CYCLE_TIME               # vehicles this cycle

    # --- Saturation flow (capacity) ---
    sat_flow  = 1800.0 / 3600.0                     # veh/s (typical 1800 veh/hr)
    departures = min(sat_flow * green_t, arrivals + prev_queue)
    departures = _noisy(max(departures, 0.0))

    # --- Queue ---
    queue = max(prev_queue + arrivals - departures, 0.0)

    # --- Wait time (Webster's approximation, simplified) ---
    x = min(departures / max(sat_flow * green_t, 1e-6), 0.99)   # saturation degree
    wait = (CYCLE_TIME * (1 - green_t / CYCLE_TIME) ** 2) / (2 * (1 - x)) + \
           queue / max(sat_flow, 1e-6)
    wait = _noisy(max(wait, 0.5))

    # --- Density (veh/km) ---
    density = queue / LANE_LENGTH if queue > 0 else _noisy(lane_row['density_veh_per_km'])

    # --- Speed (Greenshields model) ---
    k_jam = 120.0   # jam density veh/km
    speed = max(FREE_SPEED * (1.0 - density / k_jam), 5.0)
    speed = _noisy(speed)

    # --- Actual throughput flow (veh/hr) ---
    actual_flow = _noisy(departures / CYCLE_TIME * 3600.0)

    # --- Congestion pressure ---
    pressure = (density / k_jam) * (wait / 60.0)
    pressure = _noisy(pressure)

    return {
        'arrivals':    arrivals,
        'departures':  departures,
        'queue':       queue,
        'wait':        wait,
        'flow':        actual_flow,
        'density':     density,
        'speed':       speed,
        'pressure':    pressure,
        'green_time':  green_t,
    }


# ─────────────────────────────────────────────────────────────────────────────
# Full simulation
# ─────────────────────────────────────────────────────────────────────────────
def run_simulation(
    params: np.ndarray,
    csv_path: str = "vanet.csv",
    n_cycles: int = N_CYCLES,
    seed: int | None = None,
) -> dict:
    """
    Run `n_cycles` signal cycles for a 4-lane intersection.

    Parameters
    ----------
    params   : 35-dim fuzzy parameter vector
    csv_path : path to VANET.csv
    n_cycles : number of signal cycles
    seed     : random seed for reproducibility

    Returns
    -------
    dict containing aggregated metrics and simulation_steps list
    """
    rng = np.random.default_rng(seed)
    df  = _load_dataset(csv_path)

    # Build fuzzy simulation once per call
    try:
        fuzzy_sim = build_fuzzy_system(params)
    except Exception:
        # If fuzzy build fails, return worst-case metrics
        return _worst_case_result(params)

    # Per-lane running queue
    queues = [0.0] * N_LANES

    # Accumulators
    all_speeds:    list[float] = []
    all_densities: list[float] = []
    all_waits:     list[float] = []
    all_flows:     list[float] = []
    all_queues:    list[float] = []
    all_pressures: list[float] = []
    simulation_steps: list[dict] = []

    for cycle in range(n_cycles):
        # Sample 4 rows (with replacement) as initial conditions
        idx    = rng.integers(0, len(df), size=N_LANES)
        rows   = [df.iloc[i].to_dict() for i in idx]

        # Compute green times via fuzzy system
        green_times = []
        for row in rows:
            gt = compute_green_time(fuzzy_sim, row)
            green_times.append(gt)

        # Proportionally scale so sum ≤ cycle_time - overhead
        overhead  = N_LANES * 4       # 4s amber per lane
        budget    = CYCLE_TIME - overhead
        total_gt  = sum(green_times)
        if total_gt > 0:
            scale = min(budget / total_gt, 1.0)
        else:
            scale = 1.0
        green_times = [max(10.0, min(gt * scale, 90.0)) for gt in green_times]

        # Simulate each lane
        lane_metrics = []
        for i, (row, gt) in enumerate(zip(rows, green_times)):
            m = _simulate_lane_cycle(row, gt, queues[i])
            queues[i] = m['queue']
            lane_metrics.append(m)

        # Aggregate across lanes for this cycle
        c_speed    = np.mean([m['speed']    for m in lane_metrics])
        c_density  = np.mean([m['density']  for m in lane_metrics])
        c_wait     = np.mean([m['wait']     for m in lane_metrics])
        c_flow     = np.sum( [m['flow']     for m in lane_metrics])
        c_queue    = np.mean([m['queue']    for m in lane_metrics])
        c_pressure = np.mean([m['pressure'] for m in lane_metrics])

        all_speeds.append(c_speed)
        all_densities.append(c_density)
        all_waits.append(c_wait)
        all_flows.append(c_flow)
        all_queues.append(c_queue)
        all_pressures.append(c_pressure)

        simulation_steps.append({
            'cycle':       cycle + 1,
            'green_times': [round(g, 2) for g in green_times],
            'avg_speed':   round(c_speed, 3),
            'avg_density': round(c_density, 3),
            'avg_wait':    round(c_wait, 3),
            'total_flow':  round(c_flow, 3),
            'avg_queue':   round(c_queue, 3),
            'pressure':    round(c_pressure, 4),
        })

    # Final green times = last cycle's allocation
    final_green_times = simulation_steps[-1]['green_times']

    return {
        'green_times':         final_green_times,
        'cycle_time':          CYCLE_TIME,
        'avg_speed':           float(np.mean(all_speeds)),
        'avg_density':         float(np.mean(all_densities)),
        'avg_wait_time':       float(np.mean(all_waits)),
        'total_flow':          float(np.mean(all_flows)),
        'avg_queue_length':    float(np.mean(all_queues)),
        'congestion_pressure': float(np.mean(all_pressures)),
        'speed_density_ratio': float(np.mean(all_speeds) / max(np.mean(all_densities), 1e-6)),
        'simulation_steps':    simulation_steps,
    }


def _worst_case_result(params: np.ndarray) -> dict:
    """Return a worst-case result dict when the fuzzy system fails."""
    return {
        'green_times':         [30.0, 30.0, 30.0, 30.0],
        'cycle_time':          CYCLE_TIME,
        'avg_speed':           5.0,
        'avg_density':         100.0,
        'avg_wait_time':       120.0,
        'total_flow':          100.0,
        'avg_queue_length':    50.0,
        'congestion_pressure': 5.0,
        'speed_density_ratio': 0.05,
        'simulation_steps':    [],
    }
