"""
Navi Adaptive Strategy Metaheuristic (ASM) Framework Package

Submodules (Architectural Design):
- population_manager: Uniform population representation & diversity tracking
- search_analyzer: Stagnation detection, entropy, velocity, & landscape metrics
- strategy_selector: Multi-Armed Bandit / Markov selection of search kernels
- knowledge_memory: Shared elite solution archive & velocity memory
- adaptive_controller: Orchestrates real-time strategy switching
- termination_manager: Convergence & evaluation budget monitoring
"""

__version__ = "2.0.0"
