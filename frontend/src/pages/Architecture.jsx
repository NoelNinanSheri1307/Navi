import React, { useState, useEffect } from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { GlassCard } from "../components/ui/GlassCard";
import { InfoPanel } from "../components/ui/InfoPanel";
import { EquationCard } from "../components/ui/EquationCard";
import { Badge } from "../components/ui/Badge";
import { API_BASE_URL } from "../config/api";
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
  Code
} from "lucide-react";

// Local fallback layers definition
const LOCAL_FALLBACK_NODES = {
  dataset: {
    id: "dataset",
    title: "Traffic Dataset",
    icon: Database,
    step: 1,
    purpose: "Serves as the empirical basis for traffic scenarios, supplying real-world vehicle profiles and demands.",
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
    purpose: "Simulates vehicular flows and lane transitions microscopically.",
    inputs: "Green time phase durations, vehicle arrivals.",
    outputs: "Average velocities, lane congestion densities, waiting times, queue backlogs.",
    files: "backend/simulation/traffic_model.py",
    moduleName: "simulation.traffic_model",
    executionSequence: "2. Evaluated on each candidate parameter step.",
    dependencies: "Traffic Dataset configuration.",
    equations: {
      title: "Greenshields Speed-Density Model",
      formula: "v = v_f * (1 - k / k_j)",
      definitions: "v = mean speed; v_f = free flow speed (60); k = density; k_j = jam density (120).",
      intuition: "As the vehicle density increases, speed decreases linearly to zero.",
      example: "If lane density is 30: v = 45 km/h."
    }
  }
};

const iconMap = {
  dataset: Database,
  model: Activity,
  fitness: Sliders,
  optimizer: Cpu,
  telemetry: Signal,
  extractor: TrendingUp,
  estimator: Sliders,
  decision: GitBranch,
  controller: CheckSquare,
  results: FileText
};

export const Architecture = () => {
  const [selectedNode, setSelectedNode] = useState("dataset");
  const [nodes, setNodes] = useState(LOCAL_FALLBACK_NODES);

  useEffect(() => {
    fetch(`${API_BASE_URL}/architecture`)
      .then(res => {
        if (!res.ok) throw new Error("API server offline");
        return res.json();
      })
      .then(data => {
        const mapped = {};
        data.forEach(item => {
          mapped[item.id] = {
            ...item,
            icon: iconMap[item.id] || Cpu,
            // Reconstruct equations dynamically or fallback
            equations: item.id === "model" ? LOCAL_FALLBACK_NODES.model.equations : null
          };
        });
        setNodes(mapped);
      })
      .catch(() => {
        setNodes(LOCAL_FALLBACK_NODES);
      });
  }, []);

  const selectedData = nodes[selectedNode] || nodes.dataset;
  const SelectedIcon = selectedData.icon || Cpu;

  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8">
        <PageHeader
          eyebrow="System Topography"
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
                const NodeIcon = node.icon || Cpu;
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
                        <div className="w-0.5 bg-gradient-to-b from-zinc-800 to-zinc-900 h-full" />
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
