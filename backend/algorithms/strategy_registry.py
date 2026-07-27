"""
strategy_registry.py
---------------------
ASM Strategy Registry for the Navi optimization framework.

Maintains a mapping from strategy name identifiers (GA, DE, PSO, GWO, ACO, SA)
to their corresponding BaseOptimizer subclasses. ASM instantiates optimizers
exclusively through this registry to ensure full decoupling from specific
algorithm implementations.

Design Rationale
----------------
- Isolation: ASM never imports optimizer classes directly. This allows new
  optimizers to be added without modifying ASM source code.
- Factory Pattern: create() instantiates and returns a fully configured
  optimizer ready for initialize() / step() calls.
- Extensibility: Future optimizers register themselves at import time via
  register(), making them immediately available to ASM.
"""

from typing import Dict, List, Optional, Tuple, Type, Any

from algorithms.base import BaseOptimizer


# ─────────────────────────────────────────────────────────────────────────────
# Module-Level Registry
# ─────────────────────────────────────────────────────────────────────────────
_STRATEGY_REGISTRY: Dict[str, Type[BaseOptimizer]] = {}


def _populate_default_registry() -> None:
    """
    Lazily populate the default strategy registry with all framework-native
    optimizer classes. Called once on first access.

    Uses deferred imports to avoid circular dependency issues and to keep
    registry initialization self-contained.
    """
    if _STRATEGY_REGISTRY:
        return

    from algorithms.ga import GeneticAlgorithm
    from algorithms.de import DifferentialEvolution
    from algorithms.pso import ParticleSwarmOptimizer
    from algorithms.gwo import GreyWolfOptimizer
    from algorithms.aco import AntColonyOptimizer
    from algorithms.sa import SimulatedAnnealingOptimizer

    defaults = {
        "GA": GeneticAlgorithm,
        "DE": DifferentialEvolution,
        "PSO": ParticleSwarmOptimizer,
        "GWO": GreyWolfOptimizer,
        "ACO": AntColonyOptimizer,
        "SA": SimulatedAnnealingOptimizer,
    }
    for name, cls in defaults.items():
        if name not in _STRATEGY_REGISTRY:
            _STRATEGY_REGISTRY[name] = cls


# ─────────────────────────────────────────────────────────────────────────────
# Public API
# ─────────────────────────────────────────────────────────────────────────────
class StrategyRegistry:
    """
    Strategy Registry for Adaptive Strategy Metaheuristic (ASM).

    Provides factory-style access to BaseOptimizer subclasses. ASM must use
    this registry to instantiate all sub-strategy optimizers rather than
    importing them directly.

    Thread Safety
    -------------
    Not thread-safe. Designed for single-threaded optimization execution.
    """

    def __init__(self, registry: Optional[Dict[str, Type[BaseOptimizer]]] = None):
        """
        Initialize strategy registry.

        Parameters
        ----------
        registry : Optional[Dict[str, Type[BaseOptimizer]]]
            Custom registry mapping. If None, loads the default framework
            registry containing GA, DE, PSO, GWO, ACO, SA.
        """
        if registry is not None:
            self._registry: Dict[str, Type[BaseOptimizer]] = dict(registry)
        else:
            _populate_default_registry()
            self._registry = dict(_STRATEGY_REGISTRY)

    def register(self, name: str, cls: Type[BaseOptimizer]) -> None:
        """
        Register a new optimizer class under the given strategy name.

        Parameters
        ----------
        name : str
            Strategy identifier (e.g. 'GA', 'DE', 'CUSTOM_OPT').
        cls : Type[BaseOptimizer]
            BaseOptimizer subclass to associate with the name.

        Raises
        ------
        TypeError
            If cls is not a subclass of BaseOptimizer.
        """
        if not (isinstance(cls, type) and issubclass(cls, BaseOptimizer)):
            raise TypeError(
                f"Cannot register '{name}': {cls} is not a BaseOptimizer subclass."
            )
        self._registry[name.upper()] = cls

    def unregister(self, name: str) -> None:
        """
        Remove a strategy from the registry.

        Parameters
        ----------
        name : str
            Strategy identifier to remove.

        Raises
        ------
        KeyError
            If the strategy name is not registered.
        """
        key = name.upper()
        if key not in self._registry:
            raise KeyError(
                f"Strategy '{key}' not found in registry. "
                f"Available: {list(self._registry.keys())}"
            )
        del self._registry[key]

    def create(
        self,
        name: str,
        dim: int = 35,
        bounds: Tuple[float, float] = (0.0, 1.0),
        budget: int = 10000,
        pop_size: int = 30,
        seed: int = 42,
        verbose: bool = True,
        **kwargs: Any,
    ) -> BaseOptimizer:
        """
        Factory method: instantiate an optimizer by strategy name.

        Parameters
        ----------
        name : str
            Registered strategy identifier.
        dim : int
            Dimensionality of the search space.
        bounds : Tuple[float, float]
            Parameter bounds (lower, upper).
        budget : int
            Maximum evaluation budget to allocate.
        pop_size : int
            Population/swarm/archive size.
        seed : int
            Random seed for deterministic execution.
        verbose : bool
            Console output verbosity flag.
        **kwargs
            Additional algorithm-specific hyperparameters.

        Returns
        -------
        BaseOptimizer
            Instantiated optimizer ready for initialize() / step() calls.

        Raises
        ------
        KeyError
            If the strategy name is not registered.
        """
        key = name.upper()
        if key not in self._registry:
            raise KeyError(
                f"Unknown strategy '{key}'. "
                f"Available: {list(self._registry.keys())}"
            )
        cls = self._registry[key]
        return cls(
            dim=dim,
            bounds=bounds,
            budget=budget,
            pop_size=pop_size,
            seed=seed,
            verbose=verbose,
            **kwargs,
        )

    def available(self) -> List[str]:
        """
        Return sorted list of all registered strategy names.

        Returns
        -------
        List[str]
            Strategy name identifiers in alphabetical order.
        """
        return sorted(self._registry.keys())

    def contains(self, name: str) -> bool:
        """Check whether a strategy name is registered."""
        return name.upper() in self._registry

    def get_class(self, name: str) -> Type[BaseOptimizer]:
        """
        Return the optimizer class for a strategy name without instantiation.

        Parameters
        ----------
        name : str
            Strategy identifier.

        Returns
        -------
        Type[BaseOptimizer]
            The registered optimizer class.

        Raises
        ------
        KeyError
            If the strategy name is not registered.
        """
        key = name.upper()
        if key not in self._registry:
            raise KeyError(
                f"Unknown strategy '{key}'. "
                f"Available: {list(self._registry.keys())}"
            )
        return self._registry[key]
