import React, { useState } from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { GlassCard } from "../components/ui/GlassCard";
import { InfoPanel } from "../components/ui/InfoPanel";
import { EquationCard } from "../components/ui/EquationCard";
import { Badge } from "../components/ui/Badge";
import { CodeBlock } from "../components/ui/CodeBlock";
import { 
  Signal, 
  TrendingUp, 
  Sliders, 
  Award, 
  GitBranch, 
  Percent, 
  CheckSquare, 
  Target, 
  Play,
  ChevronDown,
  ChevronUp,
  Cpu
} from "lucide-react";

export const AsmIntelligence = () => {
  const [expandedStage, setExpandedStage] = useState("telemetry");

  const stages = [
    {
      id: "telemetry",
      title: "1. Telemetry",
      icon: Signal,
      subtitle: "Observe current optimizer state logs",
      purpose: "Gathers raw population data at the end of each generation, recording individual fitness scores to track convergence trends.",
      file: "backend/algorithms/operators/telemetry_engine.py",
      method: "TelemetryEngine.capture_snapshot(optimizer)",
      sequence: "Invoked at completion of optimizer generation step.",
      equations: {
        title: "Standard Deviation of Population Fitness",
        formula: "D = sqrt( sum( (f_i - mean_f)^2 ) / N )",
        definitions: "D = population diversity standard deviation; f_i = fitness score of individual i; mean_f = mean fitness of active population; N = population size.",
        intuition: "Tracks solutions clustering. A high standard deviation means wide exploration, while a value near zero indicates population stagnation.",
        example: "With population fitnesses [-0.3, -0.2, -0.1]: mean_f = -0.2. Variance = ((-0.1)^2 + 0^2 + 0.1^2)/3 = 0.0066. D = sqrt(0.0066) = 0.081."
      }
    },
    {
      id: "features",
      title: "2. Feature Extraction",
      icon: TrendingUp,
      subtitle: "Extract convergence trends and slopes",
      purpose: "Analyzes a rolling history window of snapshots to extract structural characteristics detailing optimization progress, diversity slope, and stability indices.",
      file: "backend/algorithms/operators/feature_extractor.py",
      method: "FeatureExtractor.extract_features(history_snapshots)",
      sequence: "Pre-processes telemetry history arrays before evaluation sweeps.",
      equations: {
        title: "Linear Diversity Slope (m_D) & Progress Rate (P)",
        formula: "m_D = reg_slope(t, D),  P = (mean(F_recent) - mean(F_older)) / mean(F_older)",
        definitions: "m_D = diversity slope coefficient; reg_slope = linear regression operator; P = progress rate; F_recent = fitness array of recent W/2 steps; F_older = fitness array of older W/2 steps.",
        intuition: "Estimates convergence directions. A negative diversity slope with stagnant progress rates signals search stagnation.",
        example: "If recent fitness average is -0.15 and older is -0.30: P = (-0.15 - -0.30) / -0.30 = -0.50 (50% reduction in delay index)."
      }
    },
    {
      id: "needs",
      title: "3. Need Estimation",
      icon: Sliders,
      subtitle: "Determine search demands",
      purpose: "Converts extracted features into normalized search demands representing Exploration, Exploitation, or local escape actions.",
      file: "backend/algorithms/operators/need_estimator.py",
      method: "NeedEstimator.estimate_needs(features)",
      sequence: "Calculated dynamically on every step to guide strategy evaluations.",
      equations: {
        title: "Exploration, Exploitation, and Escape Needs",
        formula: "E_explr = w1 * (1 - P) + w2 * max(0, -m_D),  E_esc = w3 * Stability * (1 - P)",
        definitions: "E_explr = Exploration need; E_esc = Escape need; P = progress rate; m_D = diversity slope; Stability = standard deviation of progress changes; w = need weights.",
        intuition: "Stagnation (P -> 0) combined with dropping diversity (m_D < 0) flags high exploration needs. High progress rate shifts focus to exploitation.",
        example: "With P = 0.05 (low progress) and m_D = -0.12: E_explr = 0.7 * (0.95) + 0.3 * (0.12) = 0.665 + 0.036 = 0.701."
      }
    },
    {
      id: "capabilities",
      title: "4. Capability Profiles",
      icon: Award,
      subtitle: "Read static optimizer ratings",
      purpose: "Stores static capability ratings for each reference optimizer, defining their exploration, exploitation, and escape performance profile.",
      file: "backend/algorithms/operators/optimizer_capabilities.py",
      method: "OptimizerCapabilities.get_profile(optimizer)",
      sequence: "Static parameter lookup representing design constraints.",
      equations: {
        title: "Capability Profile Vector Specification",
        formula: "C_o = [c_explore, c_exploit, c_escape]",
        definitions: "C_o = capability vector for optimizer o; c_explore = exploration coefficient; c_exploit = exploitation coefficient; c_escape = escape coefficient.",
        intuition: "Direct mathematical design weights based on algorithm mechanics (e.g. PSO has high exploitation, SA has high escape capability).",
        example: "Standard parameters in Navi database: GA = [5, 3, 2]; PSO = [2, 5, 1]; SA = [1, 2, 5]."
      }
    },
    {
      id: "decision",
      title: "5. Decision Engine",
      icon: GitBranch,
      subtitle: "Map needs to algorithm suitabilities",
      purpose: "Projects the active search need vector onto optimizer capability profiles to score and rank suitability.",
      file: "backend/algorithms/operators/decision_engine.py",
      method: "DecisionEngine.evaluate(needs)",
      sequence: "Multi-objective mapping calculation executed on each step.",
      equations: {
        title: "Dot-Product Suitability Projection",
        formula: "S_o = E_explr * c_explore,o + E_explt * c_exploit,o + E_esc * c_escape,o",
        definitions: "S_o = raw suitability score of optimizer o; E = active need weights; c = capability rating coefficients.",
        intuition: "Aligns current search demands with algorithm design strengths. High exploration need highlights GA/ACO; high escape need highlights SA.",
        example: "With needs E = [0.70, 0.20, 0.10] and GA = [5, 3, 2]: S_GA = 0.7*5 + 0.2*3 + 0.1*2 = 3.5 + 0.6 + 0.2 = 4.30."
      }
    },
    {
      id: "confidence",
      title: "6. Confidence Calculation",
      icon: Percent,
      subtitle: "Assess recommendation certainty",
      purpose: "Calculates the selection margin between the top recommendation and the second best choice to evaluate decision confidence.",
      file: "backend/algorithms/operators/decision_engine.py",
      method: "DecisionEngine.calculate_confidence(scores)",
      sequence: "Calculated inside the decision loop immediately after scoring.",
      equations: {
        title: "Confidence Margin Formulation",
        formula: "Margin = S_best - S_second",
        definitions: "Margin = confidence suitability gap; S_best = highest suitability score; S_second = second-highest suitability score.",
        intuition: "Ensures the recommended optimizer is mathematically superior to alternatives, avoiding unnecessary transitions during close ties.",
        example: "If GA score is 4.30 and PSO is 4.10: Margin = 4.30 - 4.10 = 0.20."
      }
    },
    {
      id: "controller",
      title: "7. Adaptive Switch Controller",
      icon: CheckSquare,
      subtitle: "Evaluate safety and threshold rules",
      purpose: "Verifies threshold margins, active run steps, and cooldown counters to avoid premature algorithm switching.",
      file: "backend/algorithms/operators/adaptive_switch_controller.py",
      method: "AdaptiveSwitchController.evaluate_switch(active, target)",
      sequence: "Gatekeeper validation check executed before triggering transitions.",
      equations: {
        title: "Gatekeeper Rule Constraints",
        formula: "Switch = (Margin >= delta) AND (t_active >= t_min) AND (t_since_switch >= t_cooldown)",
        definitions: "Switch = boolean switch authorization; Margin = confidence margin; delta = confidence threshold (0.03); t_active = active steps; t_min = minimum runtime (5); t_cooldown = switch cooldown (5).",
        intuition: "Enforces search stability, preventing rapid oscillating swaps that could waste evaluation budgets.",
        example: "If Margin = 0.20 (>= 0.03) but active steps t_active is 4 (< 5): Switch is BLOCKED due to minimum runtime constraint."
      }
    },
    {
      id: "recommendation",
      title: "8. Algorithm Recommendation",
      icon: Target,
      subtitle: "Designate transition target",
      purpose: "Registers the verified target transition strategy, outputting safety validations and diagnostic parameters.",
      file: "backend/algorithms/operators/adaptive_switch_controller.py",
      method: "AdaptiveSwitchController.get_recommendation()",
      sequence: "Outputs recommendation object to parent control loop.",
      equations: null
    },
    {
      id: "decision_final",
      title: "9. Switch / Stay Decision",
      icon: Play,
      subtitle: "Execute strategy updates",
      purpose: "Triggers state transfer, instantiates the target optimizer, maps coordinates, and updates active records.",
      file: "backend/algorithms/asm.py",
      method: "ASMController.step()",
      sequence: "Execution shift phase updating the active optimizer instance.",
      equations: null
    }
  ];

  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Adaptive Pipeline"
          title="ASM Decision Core"
          description="Interactive visualization of the Adaptive Strategy Metaheuristic (ASM) pipeline. Expand any stage to inspect the actual backend calculation logic, equations, and connections."
        />

        <Callout type="info" title="Adaptive Strategy Metaheuristic (ASM)">
          The ASM controller evaluates the search state in real-time. By observing population diversity trends and progress rates, it shifts execution to a more suitable optimizer to avoid stagnation.
        </Callout>

        {/* Visual Pipeline Map */}
        <div className="flex flex-col gap-4">
          {stages.map((stage) => {
            const isExpanded = expandedStage === stage.id;
            const StageIcon = stage.icon;
            return (
              <GlassCard 
                key={stage.id} 
                className={`transition-all duration-200 border-zinc-900 ${
                  isExpanded ? "border-emerald-500/30 bg-zinc-900/10" : ""
                }`} 
                hover={false}
                padding="none"
              >
                {/* Header Toggle */}
                <button
                  onClick={() => setExpandedStage(isExpanded ? null : stage.id)}
                  className="w-full flex items-center justify-between p-4 sm:p-5 text-left"
                >
                  <div className="flex items-center gap-3">
                    <div className={`w-8 h-8 rounded-lg flex items-center justify-center border text-xs font-semibold ${
                      isExpanded 
                        ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400" 
                        : "bg-zinc-950 border-zinc-900 text-zinc-500"
                    }`}>
                      <StageIcon size={14} />
                    </div>
                    <div className="flex flex-col">
                      <h3 className="text-sm font-semibold tracking-tight text-zinc-100 uppercase">
                        {stage.title}
                      </h3>
                      <span className="text-[10px] text-zinc-500 uppercase tracking-wider leading-none">
                        {stage.subtitle}
                      </span>
                    </div>
                  </div>
                  {isExpanded ? <ChevronUp size={16} className="text-zinc-400" /> : <ChevronDown size={16} className="text-zinc-400" />}
                </button>

                {/* Expandable Content */}
                {isExpanded && (
                  <div className="px-5 pb-5 border-t border-zinc-900 pt-4 flex flex-col gap-5 animate-in fade-in duration-200">
                    {/* Purpose */}
                    <div className="flex flex-col gap-1">
                      <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-bold">Purpose</span>
                      <p className="text-xs text-zinc-300 leading-relaxed font-normal">{stage.purpose}</p>
                    </div>

                    {/* Code connections */}
                    <div className="grid grid-cols-1 sm:grid-cols-2 gap-3 bg-zinc-950/60 p-3 rounded-lg border border-zinc-900 font-mono text-[9px] text-zinc-400">
                      <div>
                        <span className="text-zinc-600 block uppercase tracking-wider mb-0.5">Backend Module File</span>
                        <span className="text-zinc-200 select-all font-semibold font-mono">{stage.file}</span>
                      </div>
                      <div>
                        <span className="text-zinc-600 block uppercase tracking-wider mb-0.5">Execution Method</span>
                        <span className="text-zinc-200 select-all font-semibold font-mono">{stage.method}</span>
                      </div>
                      <div className="sm:col-span-2 border-t border-zinc-900/80 pt-2 mt-1">
                        <span className="text-zinc-600 block uppercase tracking-wider mb-0.5">Execution Sequence</span>
                        <span className="text-zinc-300 font-mono">{stage.sequence}</span>
                      </div>
                    </div>

                    {/* Equations */}
                    {stage.equations && (
                      <div className="flex flex-col gap-3">
                        <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-bold">
                          Mathematical Formulation
                        </span>
                        <EquationCard
                          title={stage.equations.title}
                          equation={stage.equations.formula}
                          description={`${stage.equations.definitions} Intuition: ${stage.equations.intuition}`}
                        />
                        <div className="p-3 bg-zinc-900/30 border border-zinc-900 rounded-lg text-xs text-zinc-400 font-normal leading-relaxed">
                          <span className="font-semibold text-zinc-200 block uppercase tracking-widest text-[9px] mb-1 font-mono">
                            Numerical Example
                          </span>
                          {stage.equations.example}
                        </div>
                      </div>
                    )}
                  </div>
                )}
              </GlassCard>
            );
          })}
        </div>
      </Container>
    </Section>
  );
};
