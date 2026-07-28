"""
Navi Optimization Operators Package

Exposes modular selection, crossover, mutation, velocity, topology, hierarchy,
encircling, position update, ant colony, and simulated annealing operators for
GA, DE, PSO, GWO, ACO, and SA search kernels.
"""

from .selection import TournamentSelection
from .crossover import SimulatedBinaryCrossover
from .mutation import PolynomialMutation
from .local_search import LamarckianLocalSearch

from .de_mutation import DEMutation
from .de_crossover import DECrossover
from .de_selection import DESelection

from .pso_velocity import PSOVelocityUpdate
from .pso_topology import PSOTopology
from .pso_update import PSOPositionUpdate

from .gwo_leadership import GWOLeadership
from .gwo_encircling import GWOEncircling
from .gwo_position import GWOPositionUpdate

from .aco_pheromone import ACORArchivePheromone
from .aco_transition import ACORTransition
from .aco_update import ACORArchiveUpdate

from .sa_neighbor import SANeighborGenerator
from .sa_temperature import SATemperatureSchedule
from .sa_acceptance import SAAcceptanceCriterion
from .telemetry_engine import TelemetryEngine, TelemetrySnapshot
from .optimizer_capabilities import OptimizerCapability, OPTIMIZER_CAPABILITIES
from .feature_extractor import FeatureExtractor
from .need_estimator import NeedEstimator
from .decision_engine import DecisionEngine, Recommendation
from .adaptive_switch_controller import AdaptiveSwitchController

__all__ = [
    "TournamentSelection",
    "SimulatedBinaryCrossover",
    "PolynomialMutation",
    "LamarckianLocalSearch",
    "DEMutation",
    "DECrossover",
    "DESelection",
    "PSOVelocityUpdate",
    "PSOTopology",
    "PSOPositionUpdate",
    "GWOLeadership",
    "GWOEncircling",
    "GWOPositionUpdate",
    "ACORArchivePheromone",
    "ACORTransition",
    "ACORArchiveUpdate",
    "SANeighborGenerator",
    "SATemperatureSchedule",
    "SAAcceptanceCriterion",
    "TelemetryEngine",
    "TelemetrySnapshot",
    "OptimizerCapability",
    "OPTIMIZER_CAPABILITIES",
    "FeatureExtractor",
    "NeedEstimator",
    "DecisionEngine",
    "Recommendation",
    "AdaptiveSwitchController",
]
