import React, { useState } from "react";
import { Layers, Database, Cpu, ShieldCheck, Activity, BarChart3 } from "lucide-react";

export const ArchitecturePreview = ({ className = "" }) => {
  const [activeLayer, setActiveLayer] = useState(0);

  const layers = [
    {
      id: "dataset",
      name: "Layer 1: Dataset & Infrastructure",
      icon: Database,
      tag: "Data Ingestion",
      desc: "Ingests raw telemetry records from vehicular datasets, computing traffic density, queue lengths, and flow rates across lane intervals.",
    },
    {
      id: "fuzzy",
      name: "Layer 2: Fuzzy Logic Engine",
      icon: ShieldCheck,
      tag: "Mamdani FIS",
      desc: "Maps continuous state vectors into fuzzy linguistic terms using a 9-rule Mamdani inference engine to derive target green times.",
    },
    {
      id: "evaluation",
      name: "Layer 3: Evaluation Kernel",
      icon: Activity,
      tag: "Objective Evaluation",
      desc: "Evaluates signal allocations using calibrated multi-objective criteria balancing throughput, queue saturation, and latency.",
    },
    {
      id: "optimization",
      name: "Layer 4: Optimization Engine",
      icon: Cpu,
      tag: "Metaheuristics",
      desc: "Executes continuous metaheuristic search algorithms (GA, PSO, GWO, DE, ACO, SA) to discover optimal membership function bounds.",
    },
    {
      id: "adaptive",
      name: "Layer 5: Adaptive Strategy Engine",
      icon: Layers,
      tag: "ASM Controller",
      desc: "Monitors population diversity and entropy in real time, dynamically selecting optimization strategies based on search behavior.",
    },
    {
      id: "analytics",
      name: "Layer 6: Analytics & Delivery",
      icon: BarChart3,
      tag: "Telemetry API & UI",
      desc: "Performs statistical validation and streams real-time signal timing metrics via REST and WebSocket telemetry interfaces.",
    },
  ];

  return (
    <div className={`flex flex-col gap-6 ${className}`}>
      {/* Interactive Scalable SVG Architecture Stack */}
      <div className="grid grid-cols-1 lg:grid-cols-12 gap-6 items-start">
        <div className="lg:col-span-7 flex flex-col gap-2.5">
          {layers.map((layer, idx) => {
            const Icon = layer.icon;
            const isActive = activeLayer === idx;

            return (
              <div
                key={layer.id}
                onMouseEnter={() => setActiveLayer(idx)}
                onClick={() => setActiveLayer(idx)}
                className={`p-4 rounded-xl border transition-all duration-200 cursor-pointer flex items-center justify-between ${
                  isActive
                    ? "bg-zinc-900 border-zinc-700 text-zinc-100 shadow-sm"
                    : "bg-zinc-950/40 border-zinc-800/80 text-zinc-400 hover:border-zinc-700 hover:text-zinc-200"
                }`}
              >
                <div className="flex items-center gap-3">
                  <div
                    className={`p-2 rounded-lg border shrink-0 ${
                      isActive
                        ? "bg-zinc-800 border-zinc-700 text-emerald-400"
                        : "bg-zinc-900 border-zinc-800 text-zinc-500"
                    }`}
                  >
                    <Icon size={16} />
                  </div>
                  <span className="text-sm font-normal tracking-tight">
                    {layer.name}
                  </span>
                </div>
                <span
                  className={`text-xs px-2.5 py-0.5 rounded-full border ${
                    isActive
                      ? "bg-emerald-500/10 border-emerald-500/20 text-emerald-400"
                      : "bg-zinc-900 border-zinc-800 text-zinc-500"
                  }`}
                >
                  {layer.tag}
                </span>
              </div>
            );
          })}
        </div>

        {/* Dynamic Detail Card */}
        <div className="lg:col-span-5 bg-zinc-950 border border-zinc-800 rounded-xl p-6 flex flex-col gap-4 sticky top-24">
          <div className="flex items-center gap-3">
            {React.createElement(layers[activeLayer].icon, {
              className: "w-5 h-5 text-emerald-400 shrink-0",
            })}
            <h4 className="text-base text-zinc-100 font-normal">
              {layers[activeLayer].name}
            </h4>
          </div>
          <div className="h-px bg-zinc-900 w-full" />
          <p className="text-xs text-zinc-400 leading-relaxed">
            {layers[activeLayer].desc}
          </p>
          <div className="mt-2 text-[11px] text-zinc-500 flex items-center gap-2">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
            <span>Hover or tap layers to inspect architectural responsibilities</span>
          </div>
        </div>
      </div>
    </div>
  );
};
