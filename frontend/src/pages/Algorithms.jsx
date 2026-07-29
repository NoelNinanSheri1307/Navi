import React, { useState } from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { GlassCard } from "../components/ui/GlassCard";
import { InfoPanel } from "../components/ui/InfoPanel";
import { EquationCard } from "../components/ui/EquationCard";
import { CodeBlock } from "../components/ui/CodeBlock";
import { Badge } from "../components/ui/Badge";
import { Cpu, Award, BookOpen, Layers, Check, AlertCircle, FileText, Activity } from "lucide-react";

export const Algorithms = () => {
  const [selectedAlgo, setSelectedAlgo] = useState("ga");

  const algorithms = {
    ga: {
      name: "Genetic Algorithm",
      acronym: "GA",
      file: "backend/algorithms/ga.py",
      overview: "Genetic Algorithm is a population-based heuristic search modeled on biological evolution principles, applying selection, crossover, and mutation operators to search spaces.",
      whyExists: "Provides robust global exploration in discontinuous or multi-modal spaces. In traffic control, it helps identify diverse configuration clusters across the 35-dimensional fuzzy breakpoint boundary space.",
      intuition: "Survival of the fittest: fit parents reproduce, transferring parameter characteristics while stochastic mutations introduce novel timing solutions.",
      workflow: [
        "Initialize candidate population randomly within membership constraints.",
        "Evaluate fitness scores using the microscopic simulation model.",
        "Perform tournament selection to select high-performance configurations.",
        "Apply Simulated Binary Crossover (SBX) to generate child parameter arrays.",
        "Apply Polynomial Mutation to prevent premature search stagnation.",
        "Replace old population with children and repeat until budget limits are met."
      ],
      diagram: [
        { state: "Population Initialization", desc: "Random boundary generation" },
        { state: "Fitness Evaluation", desc: "Run microscopic traffic simulation" },
        { state: "Tournament Selection", desc: "Pick best parameter candidates" },
        { state: "Simulated Binary Crossover (SBX)", desc: "Blend parent vectors" },
        { state: "Polynomial Mutation", desc: "Perturb boundaries stochastically" },
        { state: "Generation Replacement", desc: "Iterate until evaluation limit" }
      ],
      pseudoCode: `def optimize_ga(population, bounds, max_evals):
    pop = initialize_population(population, bounds)
    evals = 0
    while evals < max_evals:
        fitness = [evaluate_simulation(ind) for ind in pop]
        evals += len(pop)
        parents = tournament_selection(pop, fitness)
        children = simulated_binary_crossover(parents, crossover_rate=0.85)
        children = polynomial_mutation(children, mutation_rate=0.15)
        pop = children
    return get_best(pop)`,
      equations: {
        title: "Simulated Binary Crossover (SBX) Formulation",
        formula: "c1 = 0.5 * ((1 + beta)*p1 + (1 - beta)*p2),  c2 = 0.5 * ((1 - beta)*p1 + (1 + beta)*p2)",
        definitions: "c1, c2 = child solutions; p1, p2 = parent vectors; beta = probability distribution parameter generated from random distribution factor eta_c.",
        intuition: "Models continuous blending: high eta_c parameters create children close to parents, low eta_c values force wider exploratory steps.",
        example: "With p1=10s, p2=30s and beta=1.2: c1 = 0.5*((2.2)*10 + (-0.2)*30) = 8s; c2 = 0.5*((-0.2)*10 + (2.2)*30) = 32s."
      },
      advantages: "Strong global exploration, highly parallelizable, does not require derivative/gradient information.",
      limitations: "Slow local convergence, computationally expensive evaluation loops, sensitive to parameter tuning.",
      whyNaviIncludes: "Serves as the global explorer baseline, mapping continuous breakpoint boundaries across all variables.",
      interaction: "Accepts membership breakpoint arrays from the algorithm interface, updates coordinates, and calls the fitness function.",
      suitability: {
        good: "Complex, high-dimensional multi-modal landscapes with no clear gradients.",
        bad: "Unimodal landscapes where simple gradient-based heuristics converge faster.",
        telemetry: "Population diversity std, best fitness slope, convergence rate."
      }
    },
    pso: {
      name: "Particle Swarm Optimization",
      acronym: "PSO",
      file: "backend/algorithms/pso.py",
      overview: "Particle Swarm Optimization is a stochastic search strategy inspired by the social mechanics of bird flocking, tracing position and velocity coordinates.",
      whyExists: "Provides rapid exploitation of local search space minima. Useful for fine-tuning signal configurations within known high-quality boundary regions.",
      intuition: "Social influence: particles adjust trajectories based on personal historical best positions and the swarm's global best position.",
      workflow: [
        "Initialize particle positions and velocity arrays stochastically.",
        "Simulate traffic and evaluate fitness metrics for all particles.",
        "Update personal best (pbest) for each particle and global best (gbest) for the swarm.",
        "Calculate cognitive and social velocity vectors.",
        "Apply inertia weight decay to scale step coordinates.",
        "Update particle positions and repeat."
      ],
      diagram: [
        { state: "Initialize Particles", desc: "Assign random positions & velocity vectors" },
        { state: "Simulation Evaluation", desc: "Compute fitness values" },
        { state: "Update pbest & gbest", desc: "Compare history records" },
        { state: "Velocity Calculation", desc: "Apply cognitive & social coefficients" },
        { state: "Decay Inertia Weight", desc: "Decrease step size over generations" },
        { state: "Update Positions", desc: "Iterate search" }
      ],
      pseudoCode: `def optimize_pso(swarm, bounds, max_evals):
    particles = init_particles(swarm, bounds)
    gbest = get_best(particles)
    while evals < max_evals:
        for p in particles:
            fit = evaluate_simulation(p.pos)
            if fit > p.pbest_fit:
                p.pbest = p.pos
            if fit > gbest_fit:
                gbest = p.pos
        for p in particles:
            p.vel = w*p.vel + c1*r1*(p.pbest - p.pos) + c2*r2*(gbest - p.pos)
            p.pos = p.pos + p.vel
    return gbest`,
      equations: {
        title: "Swarm Velocity Update Equation",
        formula: "v(t+1) = w * v(t) + c1 * r1 * (pbest - x(t)) + c2 * r2 * (gbest - x(t))",
        definitions: "v(t) = velocity vector; w = inertia decay weight (0.9 -> 0.4); c1, c2 = cognitive/social accelerations (2.0); r1, r2 = random coefficients in [0,1]; x(t) = position vector.",
        intuition: "Combines momentum with attraction forces to search coordinates, scaling down step sizes over runtime.",
        example: "With w=0.8, velocity=2, c1=2, c2=2, r1=0.5, r2=0.5, pbest-x=3, gbest-x=4: v(t+1) = 0.8*2 + 2*0.5*3 + 2*0.5*4 = 1.6 + 3 + 4 = 8.6."
      },
      advantages: "Rapid convergence rates, simple implementation, few parameter requirements.",
      limitations: "Susceptible to premature stagnation inside local optima, poor performance in non-separable functions.",
      whyNaviIncludes: "Serves as Navi's exploitational driver, optimizing timing vectors when candidates group near optima.",
      interaction: "Directly updates candidate position variables, passing them to the simulation executor.",
      suitability: {
        good: "Continuous unimodal landscapes where rapid convergence to local minima is prioritized.",
        bad: "Highly rugged landscapes where particles cluster prematurely in suboptimal basins.",
        telemetry: "Mean particle velocity, swarm diversity slope, evaluation steps."
      }
    },
    gwo: {
      name: "Grey Wolf Optimizer",
      acronym: "GWO",
      file: "backend/algorithms/gwo.py",
      overview: "Grey Wolf Optimizer mimics the social leadership hierarchy and group hunting strategies of grey wolves.",
      whyExists: "Maintains balanced search exploration and exploitation behavior through hierarchical consensus updates, mitigating premature local convergence.",
      intuition: "Encircling the prey: search steps are guided by a consensus calculated from the three best wolves (alpha, beta, delta).",
      workflow: [
        "Initialize wolf pack locations randomly within boundary dimensions.",
        "Run simulation to evaluate fitness quality for all pack members.",
        "Sort wolves to designate alpha, beta, delta leader positions.",
        "Calculate encircling distances relative to alpha, beta, delta locations.",
        "Averaging location coordinates to calculate updated pack positions.",
        "Decrease decay parameter a linearly and iterate."
      ],
      diagram: [
        { state: "Pack Initialization", desc: "Set random pack locations" },
        { state: "Fitness Sweep", desc: "Evaluate configurations via simulator" },
        { state: "Identify Leaders", desc: "Assign Alpha, Beta, Delta vectors" },
        { state: "Distance Calculation", desc: "Compute encircling steps to leaders" },
        { state: "Coordinate Averaging", desc: "Combine locations into pack updates" },
        { state: "Decay step size", desc: "Scale down convergence parameter a" }
      ],
      pseudoCode: `def optimize_gwo(pack, bounds, max_evals):
    wolves = init_pack(pack, bounds)
    while evals < max_evals:
        fitness = [evaluate_simulation(w) for w in wolves]
        alpha, beta, delta = get_top_three(wolves, fitness)
        for w in wolves:
            X1 = alpha.pos - A1 * abs(C1 * alpha.pos - w.pos)
            X2 = beta.pos - A2 * abs(C2 * beta.pos - w.pos)
            X3 = delta.pos - A3 * abs(C3 * delta.pos - w.pos)
            w.pos = (X1 + X2 + X3) / 3
    return alpha`,
      equations: {
        title: "Wolf Location Consensus Formulation",
        formula: "X(t+1) = (X1 + X2 + X3) / 3",
        definitions: "X1, X2, X3 = encircling vectors relative to alpha, beta, and delta positions; X(t+1) = updated pack coordinate.",
        intuition: "Averages leadership influence stochastically. Dictates whether search steps drift towards global or local coordinates.",
        example: "If leader updates suggest coordinate targets X1=12s, X2=16s, X3=17s: X(t+1) = (12+16+17)/3 = 15s."
      },
      advantages: "Strong balance between exploration and exploitation, high stability, few parameters.",
      limitations: "Can fail to escape complex local basins if alpha, beta, and delta positions converge in the same trap.",
      whyNaviIncludes: "Implements hierarchical search profiles, refining signal cycles based on multi-leader criteria.",
      interaction: "Adjusts wolf configuration arrays, tracking the top three best candidates for convergence updates.",
      suitability: {
        good: "Constrained parameter search environments with complex correlations.",
        bad: "High dimensional multi-modal functions with flat regions.",
        telemetry: "Distance between leaders, pack spread, objective convergence."
      }
    },
    de: {
      name: "Differential Evolution",
      acronym: "DE",
      file: "backend/algorithms/de.py",
      overview: "Differential Evolution is a vector-based mathematical search strategy using mutation and crossover on vector differences.",
      whyExists: "Provides excellent search performance in continuous spaces by scaling step offsets based on population distributions, avoiding manual scale configuration.",
      intuition: "Self-scaling: mutant steps are scaled by vector differences. As the population converges, step sizes shrink automatically.",
      workflow: [
        "Initialize candidate vector population stochastically.",
        "Run simulation to obtain base fitness scores.",
        "For each vector, select three random distinct candidates.",
        "Calculate mutant vector by adding scaled differences of candidates.",
        "Apply crossover based on crossover parameter CR to build trial vector.",
        "Substitute original vector if trial vector yields higher fitness."
      ],
      diagram: [
        { state: "Initialize Vectors", desc: "Generate coordinate sets" },
        { state: "Evaluation Sweep", desc: "Obtain fitness indicators" },
        { state: "Random Triplet Selection", desc: "Select base, target, offset vectors" },
        { state: "Difference Mutation", desc: "Scale and add vector differences" },
        { state: "Binomial Crossover", desc: "Mix mutant coordinates with original" },
        { state: "Selection Check", desc: "Retain best candidate for next step" }
      ],
      pseudoCode: `def optimize_de(pop, bounds, max_evals):
    vectors = init_pop(pop, bounds)
    while evals < max_evals:
        for i, target in enumerate(vectors):
            r1, r2, r3 = select_three_distinct_random(vectors, exclude=i)
            mutant = r1 + F * (r2 - r3)
            trial = crossover(target, mutant, CR=0.9)
            if evaluate_simulation(trial) > fitness[i]:
                vectors[i] = trial
    return get_best(vectors)`,
      equations: {
        title: "DE/rand/1/bin Mutation Formulation",
        formula: "v = x_r1 + F * (x_r2 - x_r3)",
        definitions: "v = mutant vector; x_r1 = base random vector; x_r2, x_r3 = random target vectors; F = mutation scaling factor (0.8).",
        intuition: "Adds scaled direction vectors to base positions, driving the search along high-performing gradient coordinates.",
        example: "With base coordinate x_r1=10, step bounds x_r2=25, x_r3=15, scaling factor F=0.8: v = 10 + 0.8*(25 - 15) = 18."
      },
      advantages: "Self-scaling step behavior, high convergence reliability, robust in non-linear parameter landscapes.",
      limitations: "High population dependency, slow execution speed due to one-by-one replacement checks.",
      whyNaviIncludes: "Serves as the core continuous optimizer, adjusting the 35 breakpoints precisely.",
      interaction: "Executes continuous coordinate mutation checks and returns the candidate configuration values.",
      suitability: {
        good: "Non-separable continuous optimization domains with high inter-variable coupling.",
        bad: "Highly discrete or combinatorial parameter domains.",
        telemetry: "Difference vector norm averages, crossover success rates."
      }
    },
    aco: {
      name: "Ant Colony Optimization",
      acronym: "ACO",
      file: "backend/algorithms/aco.py",
      overview: "Continuous Ant Colony Optimization (ACOR) extends discrete ant decisions to continuous parameter spaces by tracking pheromone probability distributions.",
      whyExists: "Models continuous density distributions across timing variables, tracking multiple coordination pathways.",
      intuition: "Pheromone trail tracking: ants sample new solutions using a Gaussian probability density function built from the solution archive.",
      workflow: [
        "Initialize solution archive with random candidate parameters.",
        "Sort archive based on fitness performance values.",
        "Calculate selection probability weightings for archived solutions.",
        "Sample new candidates stochastically using Gaussian kernels.",
        "Evaluate and insert new candidate solutions into the archive.",
        "Truncate archive to maintain size limits, updates, and repeat."
      ],
      diagram: [
        { state: "Initialize Archive", desc: "Build base parameter history table" },
        { state: "Sort Solutions", desc: "Rank archive rows by fitness" },
        { state: "Compute Probabilities", desc: "Assign weights based on ranking" },
        { state: "Gaussian Sampling", desc: "Sample coordinates stochastically" },
        { state: "Fitness Assessment", desc: "Run simulator evaluations" },
        { state: "Archive Update", desc: "Insert and remove worst row" }
      ],
      pseudoCode: `def optimize_aco(ants, archive_size, bounds):
    archive = initialize_archive(archive_size, bounds)
    while evals < max_evals:
        sort_by_fitness(archive)
        weights = calculate_weights(archive, q=0.1)
        for ant in range(ants):
            selected = roulette_wheel(weights)
            solution = sample_gaussian_mixture(archive[selected], deviation)
            fit = evaluate_simulation(solution)
            insert_into_archive(solution, fit)
    return archive[0]`,
      equations: {
        title: "Gaussian Mixture Probability Sampling",
        formula: "g(x) = sum( w_l * g_l(x) )",
        definitions: "g(x) = continuous probability density function; w_l = probability weight of archive row l; g_l(x) = Gaussian function matching row coordinate parameters.",
        intuition: "Blends multiple coordinate profiles, guiding step selection towards proven timing paths.",
        example: "High-rank rows (e.g. w_1=0.45) heavily influence sample probability over low-rank rows (e.g. w_10=0.02)."
      },
      advantages: "Strong multi-modal routing, robust coordination tracking, avoids collapsing to single coordinates.",
      limitations: "High computation costs, memory usage scaling with archive depth.",
      whyNaviIncludes: "Investigates traffic coordination combinations, balancing phase timings simultaneously.",
      interaction: "Samples new variables from the Gaussian profiles, evaluates them, and updates the search archive.",
      suitability: {
        good: "Search spaces with distinct alternative basins of convergence.",
        bad: "Narrow, smooth unimodal optimization problems.",
        telemetry: "Archive standard deviations, weight profiles, transition counters."
      }
    },
    sa: {
      name: "Simulated Annealing",
      acronym: "SA",
      file: "backend/algorithms/sa.py",
      overview: "Simulated Annealing is a single-state trajectory search modeled after the thermodynamic cooling process of metal crystallization.",
      whyExists: "Provides a lightweight local escape capability. Useful during stagnated search periods to perturb candidate parameters out of local basins.",
      intuition: "Thermal escapes: high temperatures allow exploration steps. Cooling down limits movement, trapping the state in optimal basins.",
      workflow: [
        "Initialize parent coordinate state and temperature variable.",
        "Run simulation to evaluate starting fitness.",
        "Generate adjacent candidate state via stochastic perturbation.",
        "Evaluate candidate state fitness.",
        "Compute Metropolis probability indicator.",
        "Accept state transition stochastically, cool temperature, and repeat."
      ],
      diagram: [
        { state: "State Initialization", desc: "Set initial location and starting Temp" },
        { state: "Base Evaluation", desc: "Obtain fitness parameters" },
        { state: "Candidate Perturbation", desc: "Add local random coordinate shift" },
        { state: "Metropolis Check", desc: "Accept automatically if better, stochastically if worse" },
        { state: "Cooling Step", desc: "Reduce temperature parameter T" },
        { state: "State Transition", desc: "Iterate step updates" }
      ],
      pseudoCode: `def optimize_sa(start_pos, bounds, T_start, cooling_rate):
    state = start_pos
    T = T_start
    while T > T_min:
        candidate = perturb(state, bounds)
        delta_E = evaluate_simulation(candidate) - evaluate_simulation(state)
        if delta_E > 0 or random() < exp(delta_E / T):
            state = candidate
        T *= cooling_rate
    return state`,
      equations: {
        title: "Metropolis Acceptance Probability",
        formula: "P(accept) = exp(delta_E / T)",
        definitions: "P(accept) = probability of accepting a worse candidate; delta_E = change in fitness (negative values); T = current temperature.",
        intuition: "Determines state transition behavior. Permits worse timing choices at high T, freezing them as T approaches zero.",
        example: "With delta_E = -0.05 and T = 0.1: P(accept) = exp(-0.05 / 0.1) = exp(-0.5) = 0.60 (60% acceptance chance)."
      },
      advantages: "Guaranteed asymptotic convergence to global optima, minimal memory usage, escapes local traps.",
      limitations: "Requires fine tuning of cooling schedules, slow execution speed due to sequential single-state design.",
      whyNaviIncludes: "Serves as Navi's primary escape valve when global population diversity collapses.",
      interaction: "Maintains a single timing candidate, executing localized perturbations to search coordinates.",
      suitability: {
        good: "Escaping local traps, continuous local refinement phases.",
        bad: "Parallel searching environments or multi-modal explorations.",
        telemetry: "Acceptance ratio percentage, current temperature, perturbation distances."
      }
    },
    asm: {
      name: "Adaptive Strategy Metaheuristic",
      acronym: "ASM",
      file: "backend/algorithms/asm.py",
      overview: "The Adaptive Strategy Metaheuristic (ASM) is the orchestrating framework of Navi. It monitors telemetry to swap active optimization strategies on-the-fly.",
      whyExists: "No single algorithm dominates all search phases. ASM dynamically switches strategies to maximize overall convergence speed.",
      intuition: "Resource routing: shifts the focus to global explorers (GA, ACO) during search stagnation, and to local exploiters (PSO, GWO) during refinement.",
      workflow: [
        "Initialize default optimizer kernel (GA).",
        "Record telemetry snapshot logs on each generation step.",
        "Extract slope features and search characteristics.",
        "Calculate Exploration, Exploitation, and Escape need states.",
        "Map needs against optimizer capability vectors to yield suitability ratings.",
        "Execute strategy transition if threshold margins and safety locks permit."
      ],
      diagram: [
        { state: "Initialize ASM Core", desc: "Select GA baseline kernel" },
        { state: "Record Telemetry", desc: "Build snapshot database logs" },
        { state: "Extract Features", desc: "Calculate gradients & trends" },
        { state: "Estimate Needs", desc: "Identify exploration/exploitation demands" },
        { state: "Evaluate Suitability", desc: "Map needs to algorithm capability ratings" },
        { state: "Execute Strategy Shift", desc: "Verify safety parameters & swap" }
      ],
      pseudoCode: `def optimize_asm(bounds, max_evals):
    active_optimizer = GA
    telemetry = TelemetryEngine()
    while evals < max_evals:
        run_generation(active_optimizer)
        snap = telemetry.capture_snapshot(active_optimizer)
        features = extract_features(telemetry)
        needs = estimate_needs(features)
        recommendation = decision_engine.evaluate(needs)
        if switch_controller.validate_switch(active_optimizer, recommendation):
            active_optimizer = recommendation.target
    return get_best_solution()`,
      equations: {
        title: "Adaptive Need Synthesis",
        formula: "Need_Exploration = w1 * (1 - progress) + w2 * (1 - diversity_slope)",
        definitions: "Need_Exploration = target exploration need index; progress = convergence progress; diversity_slope = normalized diversity change trend; w = weighting coefficients.",
        intuition: "Calculates active search demands. Stagnation triggers high Exploration/Escape demands, while high progress rates prioritize Exploitation.",
        example: "With progress = 0.1 (low) and diversity_slope = -0.05 (decreasing): Need_Exploration = 0.7*(0.9) + 0.3*(1.05) = 0.94 (very high demand)."
      },
      advantages: "Reduces manual tuning requirements, combines exploration and exploitation benefits, robust across landscapes.",
      limitations: "Adds control loop overhead, requires calibration of transition thresholds.",
      whyNaviIncludes: "Serves as the core logic framework, integrating and switching all optimization search strategies.",
      interaction: "Wraps and runs sub-optimizers, adjusting bounds and sharing population state histories.",
      suitability: {
        good: "Complex, non-linear parameter landscapes with shifting search dynamics.",
        bad: "Simple, flat optimization problems where metaheuristics are overkill.",
        telemetry: "Active optimizer name, steps since last switch, need values."
      }
    }
  };

  const selectedData = algorithms[selectedAlgo];

  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Encyclopedia"
          title="Search Algorithms"
          description="Detailed breakdown of reference optimization algorithms and the Adaptive Strategy Metaheuristic (ASM) controller."
        />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Selection List */}
          <div className="lg:col-span-4 flex flex-col gap-2 bg-zinc-950/20 p-4 rounded-2xl border border-zinc-900 shadow-2xl">
            <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-bold px-3 mb-2 block">
              Reference Registry
            </span>
            {Object.keys(algorithms).map((key) => {
              const active = selectedAlgo === key;
              const isAsm = key === "asm";
              return (
                <button
                  key={key}
                  onClick={() => setSelectedAlgo(key)}
                  className={`w-full flex items-center justify-between px-3 py-3 rounded-lg text-xs transition-all text-left ${
                    active
                      ? "bg-zinc-900 border border-zinc-800 text-zinc-100 font-semibold shadow-sm"
                      : "text-zinc-400 border border-transparent hover:text-zinc-200 hover:bg-zinc-900/30"
                  }`}
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center text-xs font-semibold ${
                      active
                        ? isAsm ? "bg-blue-500/10 border border-blue-500/20 text-blue-400" : "bg-emerald-500/10 border border-emerald-500/20 text-emerald-400"
                        : "bg-zinc-950 border border-zinc-900 text-zinc-500"
                    }`}>
                      {algorithms[key].acronym}
                    </div>
                    <span>{algorithms[key].name}</span>
                  </div>
                  {isAsm && <Badge variant="blue" className="text-[8px]">Core</Badge>}
                </button>
              );
            })}
          </div>

          {/* Right Content Panel */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            <GlassCard className="flex flex-col gap-6 border-zinc-850" hover={false}>
              
              {/* Header */}
              <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-900 pb-5">
                <div className="flex flex-col gap-1">
                  <span className="text-[9px] uppercase tracking-widest text-zinc-500 font-mono font-bold">
                    Algorithm Specification File: {selectedData.file}
                  </span>
                  <h2 className="text-2xl sm:text-3xl uppercase tracking-tight text-zinc-100 font-normal">
                    {selectedData.name}
                  </h2>
                </div>
                <Badge variant={selectedAlgo === "asm" ? "blue" : "emerald"} className="text-[10px] self-start sm:self-center">
                  {selectedAlgo === "asm" ? "Meta-Orchestrator" : "Search Kernel"}
                </Badge>
              </div>

              {/* Overview & Intuition */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                <div className="flex flex-col gap-2">
                  <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">Overview</span>
                  <p className="text-xs text-zinc-300 leading-relaxed font-normal">{selectedData.overview}</p>
                </div>
                <div className="flex flex-col gap-2">
                  <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">Core Intuition</span>
                  <p className="text-xs text-zinc-300 leading-relaxed font-normal">{selectedData.intuition}</p>
                </div>
              </div>

              {/* Integration & Motivation */}
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 border-t border-zinc-900 pt-5">
                <div className="flex flex-col gap-2">
                  <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">Why Navi Includes It</span>
                  <p className="text-xs text-zinc-400 leading-relaxed font-normal">{selectedData.whyNaviIncludes}</p>
                </div>
                <div className="flex flex-col gap-2">
                  <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">Interaction with Simulator</span>
                  <p className="text-xs text-zinc-400 leading-relaxed font-normal">{selectedData.interaction}</p>
                </div>
              </div>

              {/* Step-by-Step Flow diagram */}
              <div className="border-t border-zinc-900 pt-5 flex flex-col gap-3">
                <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">
                  Execution Workflow
                </span>
                <div className="flex flex-col gap-2 bg-zinc-950/40 p-4 rounded-xl border border-zinc-900">
                  {selectedData.diagram.map((step, idx) => (
                    <div key={idx} className="flex items-center gap-3 text-xs">
                      <div className="w-5 h-5 rounded-full bg-zinc-900 border border-zinc-800 text-[10px] text-zinc-400 flex items-center justify-center font-bold font-mono">
                        {idx + 1}
                      </div>
                      <div className="flex-1 flex flex-col sm:flex-row sm:justify-between font-normal text-zinc-300">
                        <span className="font-semibold">{step.state}</span>
                        <span className="text-[10px] text-zinc-500">{step.desc}</span>
                      </div>
                    </div>
                  ))}
                </div>
              </div>

              {/* Math Formulation */}
              <div className="border-t border-zinc-900 pt-5 flex flex-col gap-3">
                <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">
                  Mathematical Formulation
                </span>
                <EquationCard
                  title={selectedData.equations.title}
                  equation={selectedData.equations.formula}
                  description={selectedData.equations.definitions}
                />
                <div className="p-3 bg-zinc-900/30 border border-zinc-900 rounded-lg text-xs text-zinc-400 leading-relaxed font-normal">
                  <span className="font-semibold text-zinc-200 block uppercase tracking-widest text-[9px] mb-1 font-mono">
                    Calculation Mechanics & Intuition
                  </span>
                  {selectedData.equations.intuition}
                  <span className="block mt-2 font-mono text-[10px] text-zinc-500">
                    <strong>Numerical Example:</strong> {selectedData.equations.example}
                  </span>
                </div>
              </div>

              {/* Pseudo Code */}
              <div className="border-t border-zinc-900 pt-5 flex flex-col gap-3">
                <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">
                  Execution Pseudo-Code
                </span>
                <CodeBlock
                  filename={`${selectedAlgo}.py (Core Algorithm Loop)`}
                  code={selectedData.pseudoCode}
                />
              </div>

              {/* Advantages, Limitations & Suitability */}
              <div className="border-t border-zinc-900 pt-5 grid grid-cols-1 md:grid-cols-2 gap-6 text-xs font-normal">
                <div className="flex flex-col gap-3">
                  <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold text-emerald-400 flex items-center gap-1">
                    <Check size={12} /> Key Advantages
                  </span>
                  <p className="text-zinc-400 leading-relaxed font-normal">{selectedData.advantages}</p>
                </div>
                <div className="flex flex-col gap-3">
                  <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold text-rose-400 flex items-center gap-1">
                    <AlertCircle size={12} /> Algorithm Limitations
                  </span>
                  <p className="text-zinc-400 leading-relaxed font-normal">{selectedData.limitations}</p>
                </div>
              </div>

              {/* Suitability Mapping */}
              <div className="border-t border-zinc-900 pt-5 flex flex-col gap-3 bg-zinc-950/20 p-4 rounded-xl border border-zinc-900 text-xs">
                <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">
                  Decision Engine Suitability Criteria
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div>
                    <span className="text-[9px] uppercase tracking-wider text-emerald-400 block mb-0.5 font-bold font-mono">
                      Prefer Selection When
                    </span>
                    <p className="text-zinc-400 leading-relaxed font-normal">{selectedData.suitability.good}</p>
                  </div>
                  <div>
                    <span className="text-[9px] uppercase tracking-wider text-rose-400 block mb-0.5 font-bold font-mono">
                      Avoid Selection When
                    </span>
                    <p className="text-zinc-400 leading-relaxed font-normal">{selectedData.suitability.bad}</p>
                  </div>
                  <div className="sm:col-span-2 border-t border-zinc-900 pt-2 mt-1">
                    <span className="text-[9px] uppercase tracking-wider text-zinc-500 block mb-0.5 font-bold font-mono flex items-center gap-1">
                      <Activity size={10} /> Associated Telemetry Signals
                    </span>
                    <p className="text-zinc-400 font-mono font-semibold">{selectedData.suitability.telemetry}</p>
                  </div>
                </div>
              </div>

            </GlassCard>
          </div>
        </div>
      </Container>
    </Section>
  );
};
