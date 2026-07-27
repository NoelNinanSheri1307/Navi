"""
sa_temperature.py
------------------
Simulated Annealing temperature schedule operator for Navi framework.

Implements geometric cooling schedule T_{k+1} = alpha * T_k (Kirkpatrick et al., 1983).
"""


class SATemperatureSchedule:
    """
    SA Temperature Cooling Schedule Operator.

    Manages system annealing temperature state using geometric decay.

    Parameters
    ----------
    t_init : float
        Initial system temperature (default 1.0).
    cooling_rate : float
        Geometric cooling decay factor alpha (default 0.95).
    t_min : float
        Minimum temperature threshold floor (default 1e-6).
    """

    def __init__(
        self,
        t_init: float = 1.0,
        cooling_rate: float = 0.95,
        t_min: float = 1e-6,
    ):
        self.t_init = t_init
        self.cooling_rate = cooling_rate
        self.t_min = t_min

    def cool(self, current_temperature: float) -> float:
        """
        Advance system temperature by applying geometric cooling factor.

        Parameters
        ----------
        current_temperature : float
            Current temperature value T_k.

        Returns
        -------
        float
            Updated cooled temperature T_{k+1}.
        """
        cooled = current_temperature * self.cooling_rate
        return max(cooled, self.t_min)
