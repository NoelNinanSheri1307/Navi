"""
simulation_config.py
--------------------
Centralized physical constants and simulation parameters for the traffic engine.

Centralizes physical intersection dynamics without altering existing physics.
"""

from dataclasses import dataclass


@dataclass
class SimulationConfig:
    """
    Physical parameters for 4-lane intersection simulation.

    Attributes
    ----------
    n_lanes : int
        Number of physical traffic lanes (default 4).
    cycle_time : float
        Total duration of one signal cycle in seconds (default 120.0s).
    n_cycles : int
        Number of simulation cycles to execute per fitness evaluation (default 5).
    free_speed : float
        Free-flow speed limit in km/h (default 60.0 km/h).
    lane_length : float
        Length of each lane section in km (default 0.5 km).
    amber_overhead_s : float
        Amber clearance duration per lane phase in seconds (default 4.0s).
    saturation_flow_veh_hr : float
        Theoretical saturation departure capacity in vehicles/hour (default 1800.0).
    jam_density_veh_km : float
        Jam density threshold in vehicles/km (default 120.0).
    noise_std : float
        Stochastic simulation jitter noise standard deviation (default 0.03).
    """
    n_lanes: int = 4
    cycle_time: float = 120.0
    n_cycles: int = 5
    free_speed: float = 60.0
    lane_length: float = 0.5
    amber_overhead_s: float = 4.0
    saturation_flow_veh_hr: float = 1800.0
    jam_density_veh_km: float = 120.0
    noise_std: float = 0.03

    @property
    def total_overhead_s(self) -> float:
        """Total signal phase overhead in seconds across all lanes."""
        return self.n_lanes * self.amber_overhead_s

    @property
    def green_time_budget_s(self) -> float:
        """Net available green time budget in seconds per cycle."""
        return self.cycle_time - self.total_overhead_s

    @property
    def saturation_flow_veh_s(self) -> float:
        """Saturation flow rate in vehicles per second."""
        return self.saturation_flow_veh_hr / 3600.0


DEFAULT_SIMULATION_CONFIG = SimulationConfig()
