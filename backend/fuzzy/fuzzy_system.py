"""
fuzzy_system.py
---------------
Parameterized fuzzy logic system for traffic signal green-time computation.
The 35-dimensional parameter vector (5 variables × 7 internal breakpoints)
shapes the membership functions of all antecedent variables.
"""

import threading
from typing import Dict, Any, List
import numpy as np
import skfuzzy as fuzz
from skfuzzy import control as ctrl


class FuzzyContext:
    """
    Thread-safe state container for dataset statistics bounds.
    Replaces global module-level mutable dict while preserving API compatibility.
    """

    def __init__(self):
        self._stats: Dict[str, float] = {}
        self._lock = threading.Lock()

    def set_stats(self, stats: Dict[str, float]) -> None:
        """Set or update dataset bounds thread-safely."""
        with self._lock:
            self._stats.update(stats)

    def get_stats(self) -> Dict[str, float]:
        """Return dataset statistics bounds or raise RuntimeError if uninitialized."""
        with self._lock:
            if not self._stats:
                raise RuntimeError(
                    "Dataset statistics not set. Call set_dataset_stats() first."
                )
            return self._stats.copy()

    def is_initialized(self) -> bool:
        """Check if dataset stats have been set."""
        with self._lock:
            return bool(self._stats)


# Global context instance
_CONTEXT = FuzzyContext()


def set_dataset_stats(stats: dict) -> None:
    """
    Provide per-column (min, max) stats derived from VANET.csv.
    Expected keys:
        cp_min, cp_max, den_min, den_max, que_min, que_max,
        wt_min,  wt_max,  fl_min,  fl_max
    """
    _CONTEXT.set_stats(stats)


def _require_stats() -> dict:
    return _CONTEXT.get_stats()


# ─────────────────────────────────────────────────────────────────────────────
# Helper: Break-point generator
# ─────────────────────────────────────────────────────────────────────────────
def _generate_vals(lo: float, hi: float, params: np.ndarray) -> list:
    """
    Map 7 unit-interval params to sorted breakpoints within [lo, hi].
    Returns a 9-element list: [lo, p0, p1, p2, p3, p4, p5, p6, hi].
    """
    span = hi - lo
    p = np.sort(lo + np.clip(params, 0.0, 1.0) * span)
    return [lo, p[0], p[1], p[2], p[3], p[4], p[5], p[6], hi]


# ─────────────────────────────────────────────────────────────────────────────
# Core builder
# ─────────────────────────────────────────────────────────────────────────────
def build_fuzzy_system(params: np.ndarray) -> ctrl.ControlSystemSimulation:
    """
    Build and return a ControlSystemSimulation from a 35-dim parameter vector.

    params layout (each block = 7 values, mapped to [0,1]):
        [0:7]   → congestion_pressure breakpoints
        [7:14]  → density_veh_per_km  breakpoints
        [14:21] → queue_length_veh    breakpoints
        [21:28] → avg_wait_time_s     breakpoints
        [28:35] → flow_veh_per_hr     breakpoints
    """
    s = _require_stats()
    params = np.asarray(params, dtype=float)

    # ---------- Extract breakpoints per variable ----------
    def block(start):
        return params[start: start + 7]

    cp_v = _generate_vals(s['cp_min'],  s['cp_max'],  block(0))
    d_v  = _generate_vals(s['den_min'], s['den_max'], block(7))
    q_v  = _generate_vals(s['que_min'], s['que_max'], block(14))
    w_v  = _generate_vals(s['wt_min'],  s['wt_max'],  block(21))
    f_v  = _generate_vals(s['fl_min'],  s['fl_max'],  block(28))

    # ---------- Universes ----------
    n = 200
    cong_pressure = ctrl.Antecedent(np.linspace(s['cp_min'],  s['cp_max'],  n), 'congestion_pressure')
    density       = ctrl.Antecedent(np.linspace(s['den_min'], s['den_max'], n), 'density_veh_per_km')
    queue         = ctrl.Antecedent(np.linspace(s['que_min'], s['que_max'], n), 'queue_length_veh')
    wait_time     = ctrl.Antecedent(np.linspace(s['wt_min'],  s['wt_max'],  n), 'avg_wait_time_s')
    flow          = ctrl.Antecedent(np.linspace(s['fl_min'],  s['fl_max'],  n), 'flow_veh_per_hr')
    green_time    = ctrl.Consequent(np.arange(10, 91, 1), 'green_time')

    # ---------- Membership functions: Antecedents ----------
    cong_pressure['low']    = fuzz.trapmf(cong_pressure.universe, [cp_v[0], cp_v[0], cp_v[1], cp_v[2]])
    cong_pressure['medium'] = fuzz.trimf(cong_pressure.universe,  [cp_v[3], cp_v[4], cp_v[5]])
    cong_pressure['high']   = fuzz.trapmf(cong_pressure.universe, [cp_v[6], cp_v[7], cp_v[8], cp_v[8]])

    density['low']    = fuzz.trapmf(density.universe, [d_v[0], d_v[0], d_v[1], d_v[2]])
    density['medium'] = fuzz.trimf(density.universe,  [d_v[3], d_v[4], d_v[5]])
    density['high']   = fuzz.trapmf(density.universe, [d_v[6], d_v[7], d_v[8], d_v[8]])

    queue['short']  = fuzz.trapmf(queue.universe, [q_v[0], q_v[0], q_v[1], q_v[2]])
    queue['medium'] = fuzz.trimf(queue.universe,  [q_v[3], q_v[4], q_v[5]])
    queue['long']   = fuzz.trapmf(queue.universe, [q_v[6], q_v[7], q_v[8], q_v[8]])

    wait_time['low']    = fuzz.trapmf(wait_time.universe, [w_v[0], w_v[0], w_v[1], w_v[2]])
    wait_time['medium'] = fuzz.trimf(wait_time.universe,  [w_v[3], w_v[4], w_v[5]])
    wait_time['high']   = fuzz.trapmf(wait_time.universe, [w_v[6], w_v[7], w_v[8], w_v[8]])

    flow['low']    = fuzz.trapmf(flow.universe, [f_v[0], f_v[0], f_v[1], f_v[2]])
    flow['medium'] = fuzz.trimf(flow.universe,  [f_v[3], f_v[4], f_v[5]])
    flow['high']   = fuzz.trapmf(flow.universe, [f_v[6], f_v[7], f_v[8], f_v[8]])

    # ---------- Membership functions: Consequent ----------
    green_time['short']  = fuzz.trimf(green_time.universe, [10, 25, 40])
    green_time['medium'] = fuzz.trimf(green_time.universe, [35, 50, 65])
    green_time['long']   = fuzz.trimf(green_time.universe, [60, 75, 90])

    # ---------- Rules ----------
    rules = [
        ctrl.Rule(cong_pressure['high'] & queue['long'],  green_time['long']),
        ctrl.Rule(cong_pressure['high'] & queue['medium'],green_time['medium']),
        ctrl.Rule(cong_pressure['medium'] & queue['long'],green_time['long']),
        ctrl.Rule(wait_time['high'],                      green_time['long']),
        ctrl.Rule(wait_time['medium'] & flow['medium'],   green_time['medium']),
        ctrl.Rule(flow['low'],                            green_time['short']),
        ctrl.Rule(flow['high'] & density['high'],         green_time['long']),
        ctrl.Rule(density['low'] & queue['short'],        green_time['short']),
        ctrl.Rule(cong_pressure['low'] & wait_time['low'],green_time['short']),
    ]

    system = ctrl.ControlSystem(rules)
    return ctrl.ControlSystemSimulation(system)


# ─────────────────────────────────────────────────────────────────────────────
# Compute green time for a single lane row
# ─────────────────────────────────────────────────────────────────────────────
def compute_green_time(sim: ctrl.ControlSystemSimulation, row: dict) -> float:
    """
    Feed one lane's sensor readings into the fuzzy system and return green time.

    Parameters
    ----------
    sim : ControlSystemSimulation built by build_fuzzy_system()
    row : dict with keys matching the 5 VANET.csv column names

    Returns
    -------
    float – green time in seconds [10, 90]
    """
    try:
        sim.input['congestion_pressure'] = float(row['congestion_pressure'])
        sim.input['density_veh_per_km']  = float(row['density_veh_per_km'])
        sim.input['queue_length_veh']    = float(row['queue_length_veh'])
        sim.input['avg_wait_time_s']     = float(row['avg_wait_time_s'])
        sim.input['flow_veh_per_hr']     = float(row['flow_veh_per_hr'])
        sim.compute()
        return float(sim.output.get('green_time', 50.0))
    except Exception:
        return 50.0
