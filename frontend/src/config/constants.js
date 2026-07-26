/**
 * Navi Framework — Centralized Configuration & Constants
 */

export const APP_CONFIG = {
  name: "Navi",
  tagline: "Adaptive Traffic Intelligence Framework",
  subtitle: "Real-Time Signal Control & Metaheuristic Optimization Engine",
  description: "Navi bridges discrete sensor telemetry with continuous Mamdani fuzzy inference to dynamically optimize 4-lane signal timings across 35 decision parameters.",
  version: "2.0.0",
  defaultTargetFps: 60,
  defaultCycleTime: 120,
};

export const ALGORITHM_CONFIG = {
  GA: {
    id: "GA",
    name: "Genetic Algorithm",
    subtitle: "Evolutionary Search Engine",
    color: "#10b981",
    description: "Simulated Binary Crossover (SBX) with polynomial mutation for global search space exploration.",
    parameters: "Pop: 30-100 | Crossover: 0.85 | Mutation: 0.15",
  },
  PSO: {
    id: "PSO",
    name: "Particle Swarm Optimization",
    subtitle: "Swarm Trajectory Velocity Engine",
    color: "#3b82f6",
    description: "Social-cognitive particle updates with linear inertia weight decay for rapid convergence.",
    parameters: "Particles: 30 | c1=2.0 | c2=2.0 | w: 0.9->0.4",
  },
  GWO: {
    id: "GWO",
    name: "Grey Wolf Optimizer",
    subtitle: "Hierarchical Leadership Pack Model",
    color: "#94a3b8",
    description: "Encircling and hunting vector mechanisms modeled after Alpha, Beta, and Delta leadership.",
    parameters: "Wolves: 30 | Decay parameter a: 2.0->0",
  },
  DE: {
    id: "DE",
    name: "Differential Evolution",
    subtitle: "DE/rand/1/bin Vector Mutation Engine",
    color: "#8b5cf6",
    description: "Differential vector mutation and binomial crossover optimized for continuous parameter bounds.",
    parameters: "Pop: 30 | F: 0.8 | CR: 0.9",
  },
  ACO: {
    id: "ACO",
    name: "Ant Colony Optimization",
    subtitle: "Continuous Domain ACOR Pheromone Kernel",
    color: "#f59e0b",
    description: "Archive-driven Gaussian mixture distribution modeling synthetic pheromone trail density.",
    parameters: "Ants: 20 | Archive: 30 | q: 0.1 | xi: 0.85",
  },
  HYBRID: {
    id: "HYBRID",
    name: "Triple-Hybrid Architecture",
    subtitle: "ACO-SA-GA Composite Kernel",
    color: "#22d3ee",
    description: "Multi-stage architecture pairing GA global exploration, ACOR pheromone guidance, and SA local annealing.",
    parameters: "Pop: 50 | Archive: 20 | SA Refinement Steps: 50",
  },
  SA: {
    id: "SA",
    name: "Simulated Annealing",
    subtitle: "Stochastic Thermal Annealing Kernel",
    color: "#f43f5e",
    description: "Metropolis acceptance criterion with exponential geometric cooling to escape local optima.",
    parameters: "Iterations: 500 | T_start: 1.0 | T_end: 0.001",
  },
};

export const FUZZY_SYSTEM_CONFIG = {
  antecedentsCount: 5,
  decisionVectorDimensions: 35,
  rulesCount: 9,
  inferenceMethod: "Mamdani",
  defuzzification: "Centroid",
  outputRange: [10, 90],
  rules: [
    { if: "Congestion Pressure IS High AND Queue IS Long", then: "Green Time IS Long", priority: "Critical" },
    { if: "Congestion Pressure IS High AND Queue IS Medium", then: "Green Time IS Medium", priority: "High" },
    { if: "Congestion Pressure IS Medium AND Queue IS Long", then: "Green Time IS Long", priority: "High" },
    { if: "Wait Time IS High", then: "Green Time IS Long", priority: "Critical" },
    { if: "Wait Time IS Medium AND Flow IS Medium", then: "Green Time IS Medium", priority: "Normal" },
    { if: "Flow IS Low", then: "Green Time IS Short", priority: "Low" },
    { if: "Flow IS High AND Density IS High", then: "Green Time IS Long", priority: "High" },
    { if: "Density IS Low AND Queue IS Short", then: "Green Time IS Short", priority: "Low" },
    { if: "Congestion Pressure IS Low AND Wait Time IS Low", then: "Green Time IS Short", priority: "Low" },
  ],
};

export const UI_BREAKPOINTS = {
  mobileSm: 320,
  mobileMd: 375,
  mobileLg: 425,
  tablet: 768,
  laptop: 1024,
  desktop: 1440,
};
