"""
optimizer_capabilities.py
-------------------------
Optimizer Capability Configuration Profiles for Navi framework.

Defines exploration, exploitation, and escape capabilities for each reference
optimizer kernel (GA, DE, PSO, GWO, ACO, SA).
"""

from dataclasses import dataclass
from typing import Dict


@dataclass(frozen=True)
class OptimizerCapability:
    """
    Search capability profile of an optimizer kernel.
    """
    exploration: float
    exploitation: float
    escape: float


# Centralized, configurable capability profiles
OPTIMIZER_CAPABILITIES: Dict[str, OptimizerCapability] = {
    "GA":  OptimizerCapability(exploration=0.4, exploitation=0.4, escape=0.2),
    "DE":  OptimizerCapability(exploration=0.5, exploitation=0.3, escape=0.2),
    "PSO": OptimizerCapability(exploration=0.3, exploitation=0.5, escape=0.2),
    "GWO": OptimizerCapability(exploration=0.3, exploitation=0.4, escape=0.3),
    "ACO": OptimizerCapability(exploration=0.4, exploitation=0.3, escape=0.3),
    "SA":  OptimizerCapability(exploration=0.2, exploitation=0.3, escape=0.5),
}
