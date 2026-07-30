"""Compatibility wrapper for the traffic model module.

This allows older imports such as ``from model.traffic_model import ...`` to
work while the implementation now lives under ``simulation.traffic_model``.
"""

from simulation.traffic_model import *  # noqa: F401,F403
