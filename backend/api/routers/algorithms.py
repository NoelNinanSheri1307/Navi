from fastapi import APIRouter

router = APIRouter(prefix="/algorithms", tags=["Algorithms"])

ALGO_METADATA = {
    "GA": {
        "name": "Genetic Algorithm",
        "description": "Biological evolutionary search mechanism executing crossover and mutations.",
        "category": "Evolutionary Heuristic",
        "strengths": "Robust global exploration, escapes local traps in discontinuous landscapes.",
        "weaknesses": "Slow local convergence rate, high computation cost.",
        "exploration": "High (Simulated Binary Crossover spreads coordinates)",
        "exploitation": "Medium (Tournament selection isolates top candidates)",
        "suitable_problems": "Highly rugged, non-linear multi-modal spaces.",
        "backend_module": "algorithms.ga",
        "pseudo_workflow": [
            "Initialize candidate population stochastically",
            "Evaluate fitness scores via Webster delay equations",
            "Perform tournament selections on population",
            "Apply simulated binary crossover (SBX)",
            "Apply polynomial mutation",
            "Replace generations stochastically"
        ],
        "supported_parameters": "pop_size, n_gen, crossover_rate, mutation_rate"
    },
    "PSO": {
        "name": "Particle Swarm Optimization",
        "description": "Stochastic swarm mechanics tracking position and velocity coordinates.",
        "category": "Swarm Intelligence",
        "strengths": "Fast local convergence, simple parameters tuning.",
        "weaknesses": "Susceptible to premature stagnation inside local optima.",
        "exploration": "Medium (Decaying inertia weight restricts steps over generations)",
        "exploitation": "High (Social attractor forces particles to global best)",
        "suitable_problems": "Continuous unimodal parameters tuning.",
        "backend_module": "algorithms.pso",
        "pseudo_workflow": [
            "Initialize particle coordinates and velocities",
            "Evaluate fitness and update pbest/gbest parameters",
            "Compute inertia weight linear decay",
            "Calculate cognitive and social acceleration components",
            "Update velocity vectors and advance coordinates"
        ],
        "supported_parameters": "n_particles, n_iter, c1, c2, w_bounds"
    },
    "GWO": {
        "name": "Grey Wolf Optimizer",
        "description": "Leadership hierarchy and encircling hunting behavior optimizer.",
        "category": "Swarm Intelligence",
        "strengths": "Well-balanced exploration and exploitation, high stability.",
        "weaknesses": "Slow search speed in flat multi-modal spaces.",
        "exploration": "Medium (Alpha, Beta, Delta vectors partition bounds)",
        "exploitation": "High (Wolf coordinates average to leader locations)",
        "suitable_problems": "Constrained engineering parameter bounds.",
        "backend_module": "algorithms.gwo",
        "pseudo_workflow": [
            "Initialize pack locations stochastically",
            "Sort solutions to assign Alpha, Beta, Delta leaders",
            "Calculate encircling vectors to top three guides",
            "Averaging location coordinates to adjust pack positions",
            "Scale convergence coefficient linearly"
        ],
        "supported_parameters": "n_wolves, n_iter, decay_param_a"
    },
    "DE": {
        "name": "Differential Evolution",
        "description": "Vector-based differential mutations and binomial crossover checks.",
        "category": "Evolutionary Heuristic",
        "strengths": "Self-scaling step behavior, high reliability.",
        "weaknesses": "Slow execution speeds due to one-by-one replacement checks.",
        "exploration": "High (Binomial crossover blends coordinates)",
        "exploitation": "Medium (Vector difference mutation paths)",
        "suitable_problems": "Continuous non-separable optimization functions.",
        "backend_module": "algorithms.de",
        "pseudo_workflow": [
            "Initialize parameter vector population",
            "Select three random distinct candidate vectors",
            "Calculate mutant vectors using scaled vector difference",
            "Perform binomial crossover check on coordinates",
            "Retain vector if trial configuration yields higher fitness"
        ],
        "supported_parameters": "pop_size, n_gen, F, CR"
    },
    "ACO": {
        "name": "Ant Colony Optimization",
        "description": "Gaussian probability density matrices modeling pheromone density paths.",
        "category": "Swarm Intelligence",
        "strengths": "Excellent multi-modal path coordination, high search stability.",
        "weaknesses": "High computational overhead, memory intensive archive tracking.",
        "exploration": "High (Gaussian mixture distributions check alternative routes)",
        "exploitation": "Medium (Roulette wheel rank-based archive selection)",
        "suitable_problems": "Complex routing and coordinate scheduling.",
        "backend_module": "algorithms.aco",
        "pseudo_workflow": [
            "Initialize solution archive with coordinates",
            "Rank solution rows based on fitness criteria",
            "Calculate rank weights for archive lines",
            "Sample coordinates stochastically from Gaussian profiles",
            "Insert new results and truncate archive"
        ],
        "supported_parameters": "n_ants, archive_size, n_iter, decay_q, std_xi"
    },
    "SA": {
        "name": "Simulated Annealing",
        "description": "Boltzmann accepting logic cooling state coordinates.",
        "category": "Trajectory Heuristic",
        "strengths": "Lightweight execution, escapes local traps in multi-modal landscapes.",
        "weaknesses": "Extremely slow sequential execution.",
        "exploration": "Low (High starting temperature allows wide stochastics)",
        "exploitation": "High (Cooling freezes states inside local traps)",
        "suitable_problems": "Localized coordinate escapes and single-state refinements.",
        "backend_module": "algorithms.sa",
        "pseudo_workflow": [
            "Initialize position state and starting temperature",
            "Perturb coordinates to generate neighbor candidates",
            "Calculate transition energy delta",
            "Apply Metropolis checks to decide acceptance",
            "Scale temperature exponentially"
        ],
        "supported_parameters": "n_iter, T_start, cooling_rate"
    },
    "ASM": {
        "name": "Adaptive Strategy Metaheuristic",
        "description": "Closed-loop feedback engine orchestrating transitions between reference optimizers.",
        "category": "Meta-Orchestrator",
        "strengths": "Reduces parameter tuning overhead, combines exploration and exploitation.",
        "weaknesses": "Adds computation step overhead, requires control thresholds.",
        "exploration": "Dynamic (Shifts to GA/ACO when stagnation is detected)",
        "exploitation": "Dynamic (Shifts to PSO/GWO during active convergence)",
        "suitable_problems": "Complex, non-linear parameter landscapes with varying optimization demands.",
        "backend_module": "algorithms.asm",
        "pseudo_workflow": [
            "Initialize baseline search strategy",
            "Capture telemetry snapshots at iteration intervals",
            "Extract convergence slopes and stability features",
            "Synthesize Exploration, Exploitation, and Escape need states",
            "Map demands to capability vectors to select recommendations",
            "Verify confidence margins and runtime limits to execute swaps"
        ],
        "supported_parameters": "pop_size, n_gen, confidence_threshold, minimum_runtime_steps"
    }
}

@router.get("")
async def get_algorithms():
    """Returns dynamic encyclopedia profiles for all reference optimizers and ASM."""
    return ALGO_METADATA
