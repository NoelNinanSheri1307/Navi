import React, { useState } from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { GlassCard } from "../components/ui/GlassCard";
import { InfoPanel } from "../components/ui/InfoPanel";
import { EquationCard } from "../components/ui/EquationCard";
import { Badge } from "../components/ui/Badge";
import { 
  Database, 
  Activity, 
  Plus, 
  Cpu, 
  Signal, 
  Sliders, 
  TrendingUp, 
  GitBranch, 
  CheckSquare, 
  FileText,
  ArrowRight,
  HelpCircle,
  Code
} from "lucide-react";

export const Architecture = () => {
  const [selectedNode, setSelectedNode] = useState("dataset");

  const nodes = {
    dataset: {
      id: "dataset",
      title: "Traffic Dataset",
      icon: Database,
      step: 1,
      purpose: "Serves as the empirical basis for traffic scenarios, supplying real-world vehicle profiles and demands into the simulation.",
      inputs: "None (initial database read).",
      outputs: "Historical traffic flows, lane speeds, queue counts, congestion pressures.",
      files: "vanet.csv",
      moduleName: "vanet.csv Loader",
      executionSequence: "1. Executed at startup inside simulation initialization.",
      dependencies: "None.",
      equations: null
    },
    model: {
      id: "model",
      title: "Traffic Model",
      icon: Activity,
      step: 2,
      purpose: "Simulates vehicular flows and lane transitions microscopically based on speed-density and capacity relationships.",
      inputs: "Green time phase durations, vehicle arrivals.",
      outputs: "Average velocities, lane congestion densities, waiting times, queue backlogs.",
      files: "backend/simulation/traffic_model.py",
      moduleName: "simulation.traffic_model",
      executionSequence: "2. Evaluated on each candidate parameter step to build queue configurations.",
      dependencies: "Traffic Dataset configuration.",
      equations: {
        title: "Greenshields Speed-Density Model",
        formula: "v = v_f * (1 - k / k_j)",
        definitions: "v = mean speed (km/h); v_f = free flow speed (60 km/h); k = vehicle density (veh/km); k_j = jam density (120 veh/km).",
        intuition: "As the vehicle density increases towards jam capacity, speed decreases linearly to zero.",
        example: "If lane density is 30 veh/km: v = 60 * (1 - 30/120) = 45 km/h."
      }
    },
    fitness: {
      id: "fitness",
      title: "Fitness Evaluation",
      icon: Sliders,
      step: 3,
      purpose: "Translates vehicular metrics into a standardized quality score, determining the efficiency of candidate timing parameters.",
      inputs: "Average speed, total flow rate, waiting latency, queue lengths, congestion index.",
      outputs: "Continuous score value (fitness) within [-1.0, 1.0].",
      files: "backend/evaluation/fitness.py",
      moduleName: "evaluation.fitness",
      executionSequence: "3. Calculated inside the objective evaluator function for every candidate vector.",
      dependencies: "Traffic Model output arrays.",
      equations: {
        title: "Multi-Objective Fitness Formulation",
        formula: "F = 0.35 * flow_norm + 0.30 * speed_norm - 0.15 * wait_norm - 0.10 * queue_norm - 0.10 * pressure_norm",
        definitions: "flow_norm = tanh-scaled throughput; speed_norm = normalized average speed; wait_norm = scaled total latency; queue_norm = scaled average backlog; pressure_norm = scaled congestion pressure.",
        intuition: "Maximizes throughput and speed values while penalizing queue lengths, latency delays, and boundary pressures.",
        example: "With normalized inputs [1.0, 0.8, 0.4, 0.3, 0.2]: F = 0.35*(1.0) + 0.30*(0.8) - 0.15*(0.4) - 0.10*(0.3) - 0.10*(0.2) = 0.48."
      }
    },
    optimizer: {
      id: "optimizer",
      title: "Optimizer Layer",
      icon: Cpu,
      step: 4,
      purpose: "Runs continuous space parameter adjustments to find the best-performing membership breakpoint boundaries.",
      inputs: "Fitness evaluation function, boundary dimensions, seed variables.",
      outputs: "Updated population positions, global best parameter arrays.",
      files: "backend/algorithms/ (ga.py, pso.py, gwo.py, de.py, aco.py, sa.py)",
      moduleName: "algorithms.base.optimizer",
      executionSequence: "4. Iteratively adjusts decision positions over generations during execution.",
      dependencies: "Fitness Evaluation function.",
      equations: null
    },
    telemetry: {
      id: "telemetry",
      title: "Telemetry Collector",
      icon: Signal,
      step: 5,
      purpose: "Records step-by-step search characteristics and fitness progress at the end of every optimization generation.",
      inputs: "Population fitness lists, evaluations index, generation counter.",
      outputs: "Immutably frozen TelemetrySnapshot entries stored in a rolling window deque.",
      files: "backend/algorithms/operators/telemetry_engine.py",
      moduleName: "algorithms.operators.telemetry_engine",
      executionSequence: "5. Invoked inside the step handler immediately after optimizer evaluation.",
      dependencies: "Optimizer Layer state outputs.",
      equations: {
        title: "Population Diversity Calculation",
        formula: "D = std(F_pop)",
        definitions: "D = population diversity metric; std = standard deviation; F_pop = array of fitness values for the active population.",
        intuition: "Measures the convergence spread of active solutions. A value near zero indicates the population has converged.",
        example: "For a population with fitnesses [-0.15, -0.15, -0.15]: D = 0.0."
      }
    },
    extractor: {
      id: "extractor",
      title: "Feature Extraction",
      icon: TrendingUp,
      step: 6,
      purpose: "Analyzes historical snapshot arrays to evaluate convergence gradients and stability rates.",
      inputs: "Rolling window array of TelemetrySnapshot entries.",
      outputs: "Progress Rate, Diversity Trend, Search Stability, Budget Pressure features.",
      files: "backend/algorithms/operators/feature_extractor.py",
      moduleName: "algorithms.operators.feature_extractor",
      executionSequence: "6. Executed inside decision engine pre-processing pipeline.",
      dependencies: "Telemetry Collector database.",
      equations: {
        title: "Linear Diversity Regression Slope",
        formula: "m = sum((x - mean(x)) * (y - mean(y))) / sum((x - mean(x))^2)",
        definitions: "m = slope coefficient; x = step sequence arrays; y = population diversity metrics; mean = average operator.",
        intuition: "Extracts the overall direction of search convergence. Negative slope shows decreasing diversity.",
        example: "With step indexes [1, 2, 3] and diversities [0.8, 0.6, 0.4]: m = -0.2 (decreasing diversity)."
      }
    },
    estimator: {
      id: "estimator",
      title: "Need Estimation",
      icon: Sliders,
      step: 7,
      purpose: "Evaluates trend indicators to score demands for searching behavior across three distinct objectives.",
      inputs: "Extracted feature trends (Progress Rate, Diversity Trend, Search Stability, Budget Pressure).",
      outputs: "Ratings for Exploration, Exploitation, and Escape needs.",
      files: "backend/algorithms/operators/need_estimator.py",
      moduleName: "algorithms.operators.need_estimator",
      executionSequence: "7. Executed to create the current demand profile before evaluation mapping.",
      dependencies: "Feature Extraction outputs.",
      equations: {
        title: "Need Evidence Normalization",
        formula: "N_norm = N / (Exploration + Exploitation + Escape)",
        definitions: "N = raw need index; Exploration = raw exploration; Exploitation = raw exploitation; Escape = raw escape.",
        intuition: "Normalizes calculated needs so they sum to exactly 1.0, representing proportional demands.",
        example: "If raw needs are Exploration=4, Exploitation=2, Escape=2: N_norm for Exploration = 4 / 8 = 0.50."
      }
    },
    decision: {
      id: "decision",
      title: "Decision Engine",
      icon: GitBranch,
      step: 8,
      purpose: "Maps current needs to static optimizer capability profiles to score suitability.",
      inputs: "Normalized search needs, static optimizer capability configurations.",
      outputs: "Sorted capability scoring lists, target strategy recommendation.",
      files: "backend/algorithms/operators/decision_engine.py, optimizer_capabilities.py",
      moduleName: "algorithms.operators.decision_engine",
      executionSequence: "8. Evaluates profiles on every step to yield a strategy choice.",
      dependencies: "Need Estimation outputs, Capability configurations.",
      equations: {
        title: "Strategy Suitability Score",
        formula: "S_o = w_explr * C_explr + w_explt * C_explt + w_esc * C_esc",
        definitions: "S_o = suitability score for optimizer o; w = normalized need weights; C = static capability rating coefficients of optimizer o.",
        intuition: "Projects the need vector onto the algorithm's capability ratings to calculate alignment.",
        example: "With needs [0.6, 0.3, 0.1] and DE capabilities [5, 4, 3]: S_DE = 0.6*5 + 0.3*4 + 0.1*3 = 4.5."
      }
    },
    controller: {
      id: "controller",
      title: "Adaptive Switch Controller",
      icon: CheckSquare,
      step: 9,
      purpose: "Validates switch safety thresholds and cooldown locks before triggering strategy transitions.",
      inputs: "Best recommended optimizer, current active optimizer name, active optimizer runtime steps, steps since last switch.",
      outputs: "Boolean transition decision, target strategy updates.",
      files: "backend/algorithms/operators/adaptive_switch_controller.py, asm_controller.py",
      moduleName: "algorithms.operators.adaptive_switch_controller",
      executionSequence: "9. Executed at the beginning of the step loop before invoking sub-optimizers.",
      dependencies: "Decision Engine recommendations.",
      equations: {
        title: "Confidence Margin Calculation",
        formula: "C = S_best - S_second",
        definitions: "C = confidence margin; S_best = highest suitability score; S_second = second-highest suitability score.",
        intuition: "Estimates selection certainty. If margin is below the threshold, no switch is allowed.",
        example: "If DE suitability is 0.67 and GA is 0.64: C = 0.67 - 0.64 = 0.03."
      }
    },
    results: {
      id: "results",
      title: "Results Output",
      icon: FileText,
      step: 10,
      purpose: "Exports optimization records, convergence values, and timing configurations to local database files.",
      inputs: "Optimized parameter lists, convergence arrays, simulation metrics.",
      outputs: "JSON result records saved to output directories.",
      files: "backend/output/results/",
      moduleName: "main.py Results Exporter",
      executionSequence: "10. Executed at the completion of optimization runs.",
      dependencies: "Adaptive Switch Controller evaluations.",
      equations: null
    }
  };

  const selectedData = nodes[selectedNode];
  const SelectedIcon = selectedData.icon;

  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8">
        <PageHeader
          eyebrow="System Blueprint"
          title="Architecture Explorer"
          description="Interactive specification mapping Navi's multi-stage optimization pipeline. Select any module to view inputs, outputs, files, and formulas."
        />

        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          {/* Left Panel: Flow Chart */}
          <div className="lg:col-span-5 flex flex-col gap-4 bg-zinc-950/20 p-6 rounded-2xl border border-zinc-900 shadow-2xl">
            <h3 className="text-xs uppercase tracking-widest text-zinc-500 font-bold mb-2">
              Optimization Pipeline Flow
            </h3>
            
            <div className="flex flex-col gap-2 relative">
              {Object.values(nodes).map((node, index) => {
                const active = selectedNode === node.id;
                const NodeIcon = node.icon;
                return (
                  <React.Fragment key={node.id}>
                    <button
                      onClick={() => setSelectedNode(node.id)}
                      className={`flex items-center gap-4 p-3.5 rounded-xl border transition-all text-left relative z-10 ${
                        active
                          ? "bg-zinc-900 border-zinc-800 text-zinc-100 shadow-lg"
                          : "bg-zinc-950/40 border-zinc-900/60 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/20"
                      }`}
                    >
                      <div className={`w-8 h-8 rounded-lg flex items-center justify-center border text-xs font-semibold ${
                        active 
                          ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400" 
                          : "bg-zinc-900 border-zinc-800 text-zinc-400"
                      }`}>
                        {node.step}
                      </div>
                      
                      <div className="flex-1 flex flex-col">
                        <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-mono">
                          Step 0{node.step}
                        </span>
                        <span className="text-sm font-semibold tracking-tight uppercase">
                          {node.title}
                        </span>
                      </div>
                      
                      <NodeIcon size={14} className={active ? "text-emerald-400 animate-pulse" : "text-zinc-500"} />
                    </button>
                    
                    {index < Object.values(nodes).length - 1 && (
                      <div className="flex justify-center my-0.5 relative z-0 h-4">
                        <div className="w-0.5 bg-gradient-to-b from-zinc-800 to-zinc-900 h-full animate-pulse" />
                      </div>
                    )}
                  </React.Fragment>
                );
              })}
            </div>
          </div>

          {/* Right Panel: Detail Panel */}
          <div className="lg:col-span-7 flex flex-col gap-6">
            <GlassCard className="flex flex-col gap-6 border-zinc-800/80" hover={false}>
              <div className="flex items-center gap-3 border-b border-zinc-900 pb-4">
                <div className="p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-emerald-400">
                  <SelectedIcon size={18} />
                </div>
                <div className="flex flex-col">
                  <span className="text-[9px] uppercase tracking-widest text-zinc-500 font-mono font-bold">
                    Module Specifications (Step {selectedData.step})
                  </span>
                  <h3 className="text-xl sm:text-2xl uppercase tracking-tight text-zinc-100 font-normal">
                    {selectedData.title}
                  </h3>
                </div>
              </div>

              {/* Purpose */}
              <div className="flex flex-col gap-2">
                <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">Purpose</span>
                <p className="text-xs text-zinc-300 leading-relaxed font-normal">
                  {selectedData.purpose}
                </p>
              </div>

              {/* Inputs/Outputs */}
              <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 border-t border-zinc-900 pt-4">
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">Inputs</span>
                  <p className="text-xs text-zinc-400 leading-relaxed font-normal">{selectedData.inputs}</p>
                </div>
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">Outputs</span>
                  <p className="text-xs text-zinc-400 leading-relaxed font-normal">{selectedData.outputs}</p>
                </div>
              </div>

              {/* Code Connections */}
              <div className="border-t border-zinc-900 pt-4 flex flex-col gap-3">
                <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold flex items-center gap-1.5">
                  <Code size={12} /> Code Connection
                </span>
                <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-zinc-950/60 p-3 rounded-lg border border-zinc-900 font-mono text-[10px] text-zinc-400">
                  <div>
                    <span className="text-zinc-600 block uppercase tracking-wider mb-0.5">Relevant Files</span>
                    <span className="text-zinc-200 select-all font-semibold font-mono">{selectedData.files}</span>
                  </div>
                  <div>
                    <span className="text-zinc-600 block uppercase tracking-wider mb-0.5">Module Path</span>
                    <span className="text-zinc-200 select-all font-semibold font-mono">{selectedData.moduleName}</span>
                  </div>
                  <div className="sm:col-span-2 border-t border-zinc-900/80 pt-2 mt-1">
                    <span className="text-zinc-600 block uppercase tracking-wider mb-0.5">Execution Sequence</span>
                    <span className="text-zinc-300 font-mono">{selectedData.executionSequence}</span>
                  </div>
                  <div className="sm:col-span-2">
                    <span className="text-zinc-600 block uppercase tracking-wider mb-0.5">System Dependencies</span>
                    <span className="text-zinc-300 font-mono">{selectedData.dependencies}</span>
                  </div>
                </div>
              </div>

              {/* Related Equations */}
              {selectedData.equations && (
                <div className="border-t border-zinc-900 pt-4 flex flex-col gap-3">
                  <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">
                    Mathematical Formulation
                  </span>
                  <EquationCard
                    title={selectedData.equations.title}
                    equation={selectedData.equations.formula}
                    description={`${selectedData.equations.definitions} Intuition: ${selectedData.equations.intuition}`}
                  />
                  <div className="p-3 bg-zinc-900/30 border border-zinc-900 rounded-lg text-xs text-zinc-400">
                    <span className="font-semibold text-zinc-200 block uppercase tracking-widest text-[9px] mb-1">Numerical Example</span>
                    {selectedData.equations.example}
                  </div>
                </div>
              )}
            </GlassCard>
          </div>
        </div>
      </Container>
    </Section>
  );
};
