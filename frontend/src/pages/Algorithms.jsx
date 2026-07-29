import React, { useState, useEffect } from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { MetricCard } from "../components/ui/MetricCard";
import { GlassCard } from "../components/ui/GlassCard";
import { InfoPanel } from "../components/ui/InfoPanel";
import { EquationCard } from "../components/ui/EquationCard";
import { CodeBlock } from "../components/ui/CodeBlock";
import { Badge } from "../components/ui/Badge";
import { API_BASE_URL } from "../config/api";
import { Cpu, Award, BookOpen, Layers, Check, AlertCircle, FileText, Activity } from "lucide-react";

// Local fallback registry if API server is offline
const LOCAL_FALLBACK_ALGORITHMS = {
  ga: {
    name: "Genetic Algorithm",
    acronym: "GA",
    file: "backend/algorithms/ga.py",
    overview: "Genetic Algorithm is a population-based heuristic search modeled on biological evolution principles, applying selection, crossover, and mutation operators.",
    whyExists: "Provides robust global exploration in discontinuous or multi-modal spaces.",
    intuition: "Survival of the fittest: fit parents reproduce, transferring parameter characteristics while mutations introduce novel solutions.",
    diagram: [
      { state: "Population Initialization", desc: "Random boundary generation" },
      { state: "Fitness Evaluation", desc: "Run microscopic traffic simulation" },
      { state: "Tournament Selection", desc: "Pick best parameter candidates" },
      { state: "Simulated Binary Crossover (SBX)", desc: "Blend parent vectors" },
      { state: "Polynomial Mutation", desc: "Perturb boundaries stochastically" },
      { state: "Generation Replacement", desc: "Iterate until evaluation limit" }
    ],
    pseudoCode: "def optimize_ga(population, bounds, max_evals): ...",
    equations: {
      title: "Simulated Binary Crossover (SBX) Formulation",
      formula: "c1 = 0.5 * ((1 + beta)*p1 + (1 - beta)*p2),  c2 = 0.5 * ((1 - beta)*p1 + (1 + beta)*p2)",
      definitions: "c1, c2 = child solutions; p1, p2 = parents; beta = crossover distribution factor.",
      intuition: "Models continuous blending steps based on distribution probability coefficients.",
      example: "With p1=10s, p2=30s and beta=1.2: c1 = 8s; c2 = 32s."
    },
    advantages: "Strong global exploration, highly parallelizable.",
    limitations: "Slow local convergence rate.",
    whyNaviIncludes: "Serves as the global explorer baseline, mapping continuous boundaries.",
    interaction: "Updates breakpoint arrays and evaluates fitness values.",
    suitability: {
      good: "Rugged landscapes.",
      bad: "Unimodal landscapes.",
      telemetry: "Population diversity std, best fitness slope."
    }
  },
  asm: {
    name: "Adaptive Strategy Metaheuristic",
    acronym: "ASM",
    file: "backend/algorithms/asm.py",
    overview: "The Adaptive Strategy Metaheuristic (ASM) is the orchestrating framework of Navi. It monitors telemetry to swap active optimization strategies on-the-fly.",
    whyExists: "No single algorithm dominates all search phases. ASM dynamically switches strategies to maximize overall convergence speed.",
    intuition: "Resource routing: shifts the focus to global explorers (GA, ACO) during search stagnation, and to local exploiters (PSO, GWO) during refinement.",
    diagram: [
      { state: "Initialize ASM Core", desc: "Select GA baseline kernel" },
      { state: "Record Telemetry", desc: "Build snapshot database logs" },
      { state: "Extract Features", desc: "Calculate gradients & trends" },
      { state: "Estimate Needs", desc: "Identify exploration/exploitation demands" },
      { state: "Evaluate Suitability", desc: "Map needs to algorithm capability ratings" },
      { state: "Execute Strategy Shift", desc: "Verify safety parameters & swap" }
    ],
    pseudoCode: "def optimize_asm(bounds, max_evals): ...",
    equations: {
      title: "Adaptive Need Synthesis",
      formula: "Need_Exploration = w1 * (1 - progress) + w2 * (1 - diversity_slope)",
      definitions: "Need_Exploration = target exploration need index; progress = convergence progress; diversity_slope = diversity change trend.",
      intuition: "Stagnation triggers high Exploration/Escape demands, while high progress rates prioritize Exploitation.",
      example: "With progress = 0.1 (low) and diversity_slope = -0.05 (decreasing): Need_Exploration = 0.94 (very high demand)."
    },
    advantages: "Reduces manual tuning requirements, combines exploration and exploitation benefits.",
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

export const Algorithms = () => {
  const [selectedAlgo, setSelectedAlgo] = useState("ga");
  const [algorithms, setAlgorithms] = useState(LOCAL_FALLBACK_ALGORITHMS);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    fetch(`${API_BASE_URL}/algorithms`)
      .then(res => {
        if (!res.ok) throw new Error("API server offline");
        return res.json();
      })
      .then(data => {
        // Map API keys to lowercase schema
        const mapped = {};
        Object.keys(data).forEach(key => {
          const lowerKey = key.toLowerCase();
          mapped[lowerKey] = {
            ...data[key],
            acronym: key,
            // Reconstruct elements for unified mapping
            diagram: data[key].pseudo_workflow.map((step, idx) => ({
              state: step,
              desc: `Sequence step ${idx + 1}`
            })),
            advantages: data[key].strengths,
            limitations: data[key].weaknesses,
            whyNaviIncludes: `Integrated as a core search runner implementing ${data[key].category} heuristics.`,
            interaction: `Decoupled interface execution mapped under ${data[key].backend_module}.`,
            equations: data[key].name === "Genetic Algorithm" ? LOCAL_FALLBACK_ALGORITHMS.ga.equations : LOCAL_FALLBACK_ALGORITHMS.asm.equations,
            intuition: `Algorithmic mechanics mapped via ${data[key].exploration} exploration and ${data[key].exploitation} exploitation parameters.`,
            suitability: {
              good: data[key].suitable_problems,
              bad: "Unsuited landscapes with mismatched complexity indices.",
              telemetry: data[key].supported_parameters
            }
          };
        });
        setAlgorithms(mapped);
        setLoading(false);
      })
      .catch(() => {
        // Fallback to local default configs on failure
        setAlgorithms(LOCAL_FALLBACK_ALGORITHMS);
        setLoading(false);
      });
  }, []);

  const selectedData = algorithms[selectedAlgo] || algorithms.ga;

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
                    Algorithm Specification File: {selectedData.file || "Dynamic Registry Connection"}
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
              {selectedData.diagram && (
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
              )}

              {/* Math Formulation */}
              {selectedData.equations && (
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
              )}

              {/* Pseudo Code */}
              {selectedData.pseudoCode && selectedData.pseudoCode !== "def optimize_ga(population, bounds, max_evals): ..." && (
                <div className="border-t border-zinc-900 pt-5 flex flex-col gap-3">
                  <span className="text-[10px] uppercase tracking-wider text-zinc-500 font-semibold">
                    Execution Pseudo-Code
                  </span>
                  <CodeBlock
                    filename={`${selectedAlgo}.py (Core Algorithm Loop)`}
                    code={selectedData.pseudoCode}
                  />
                </div>
              )}

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
              {selectedData.suitability && (
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
              )}

            </GlassCard>
          </div>
        </div>
      </Container>
    </Section>
  );
};
