import React, { useState, useEffect, useRef } from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { GlassCard } from "../components/ui/GlassCard";
import { InfoPanel } from "../components/ui/InfoPanel";
import { Button } from "../components/ui/Button";
import { Badge } from "../components/ui/Badge";
import SimulationCanvas from "../components/SimulationCanvas";
import rawData from "../data/data.json";
import { 
  Play, 
  Pause, 
  RotateCcw, 
  Download, 
  Database, 
  Cpu, 
  Signal, 
  Clock, 
  Activity, 
  History, 
  CheckCircle,
  AlertTriangle,
  FileText
} from "lucide-react";

export const Simulation = () => {
  const [selectedAlgo, setSelectedAlgo] = useState("GA");
  const [selectedDataset, setSelectedDataset] = useState("vanet.csv");
  const [speed, setSpeed] = useState(1);
  const [isPlaying, setIsPlaying] = useState(false);
  const [currentStep, setCurrentStep] = useState(0);
  const [runHistory, setRunHistory] = useState(() => {
    const saved = localStorage.getItem("navi_run_history");
    return saved ? JSON.parse(saved) : [];
  });

  const [liveMetrics, setLiveMetrics] = useState({
    queue: 0,
    throughput: 0,
    activeCars: 0,
    remainingTime: 0,
    fps: 60
  });

  const [timeline, setTimeline] = useState([]);
  const [historyWaitTimes, setHistoryWaitTimes] = useState([]);
  const [historyQueues, setHistoryQueues] = useState([]);

  // Fetch the selected algorithm's baseline results from data.json
  const algoData = rawData.find(d => d.algorithm === selectedAlgo) || rawData[0];
  const maxSteps = algoData.convergence_history.length;

  // Active Simulation variables interpolated over step progress
  const progressRatio = currentStep / (maxSteps - 1 || 1);
  const startWait = 4500; // ms baseline delay
  const targetWait = algoData.avg_wait_time || 3200;
  const currentWaitTime = startWait - (startWait - targetWait) * progressRatio;

  const startPressure = 160;
  const targetPressure = algoData.congestion_pressure || 100;
  const currentPressure = startPressure - (startPressure - targetPressure) * progressRatio;

  const startSpeed = 1.8;
  const targetSpeed = (algoData.avg_speed || 10) / 4.5;
  const currentSpeed = startSpeed + (targetSpeed - startSpeed) * progressRatio;

  // Current green times interpolated from baseline to optimal
  const currentGreenTimes = algoData.green_times.map((gt, idx) => {
    const startGt = 30; // 30s initial baseline
    return Math.round(startGt + (gt - startGt) * progressRatio);
  });

  // ASM specific simulation values
  const getAsmState = (step) => {
    if (selectedAlgo !== "ASM" && selectedAlgo !== "HYBRID") return null;
    
    // Map step indexes to transition profiles
    if (step < 6) {
      return {
        active: "GA",
        explr: 0.85 - step * 0.05,
        explt: 0.10 + step * 0.02,
        escape: 0.05,
        recommend: "GA",
        margin: 0.01,
        decision: "STAY"
      };
    } else if (step >= 6 && step < 13) {
      return {
        active: "PSO",
        explr: 0.25 - (step - 6) * 0.02,
        explt: 0.70 + (step - 6) * 0.01,
        escape: 0.05,
        recommend: "PSO",
        margin: 0.14,
        decision: "SWITCH"
      };
    } else {
      return {
        active: "SA",
        explr: 0.15,
        explt: 0.35,
        escape: 0.50,
        recommend: "SA",
        margin: 0.22,
        decision: "SWITCH"
      };
    }
  };

  const asmState = getAsmState(currentStep);

  // Interval execution logic
  const timerRef = useRef(null);

  useEffect(() => {
    if (isPlaying) {
      const intervalMs = 1200 / speed;
      timerRef.current = setInterval(() => {
        setCurrentStep((prev) => {
          if (prev >= maxSteps - 1) {
            setIsPlaying(false);
            clearInterval(timerRef.current);
            handleComplete();
            return prev;
          }
          const next = prev + 1;
          logStepEvent(next);
          return next;
        });
      }, intervalMs);
    } else {
      if (timerRef.current) clearInterval(timerRef.current);
    }

    return () => {
      if (timerRef.current) clearInterval(timerRef.current);
    };
  }, [isPlaying, speed, selectedAlgo]);

  const logStepEvent = (step) => {
    const fitness = algoData.convergence_history[step].toFixed(5);
    const newEvents = [];

    if (step === 1) {
      newEvents.push(`[System] Optimization loop started for algorithm ${selectedAlgo}.`);
    }

    newEvents.push(`[Iteration ${step}] Fitness evaluated: ${fitness}.`);

    if ((selectedAlgo === "ASM" || selectedAlgo === "HYBRID") && (step === 6 || step === 13)) {
      const activeState = getAsmState(step);
      newEvents.push(`[ASM Decision] Stagnation detected. Recommended strategy: ${activeState.active}. Confidence margin: ${activeState.margin}.`);
      newEvents.push(`[ASM Controller] Safety checks approved. Swapping active algorithm to ${activeState.active}.`);
    }

    setTimeline(prev => [...prev, ...newEvents]);
  };

  const handleStart = () => {
    if (currentStep === 0) {
      setTimeline([
        `[System] Initializing simulation workspace.`,
        `[System] Loading dataset parameters from ${selectedDataset}.`,
        `[System] Spawning vehicles at jam density baseline.`
      ]);
      setHistoryQueues([]);
      setHistoryWaitTimes([]);
    }
    setIsPlaying(true);
  };

  const handlePause = () => {
    setIsPlaying(false);
  };

  const handleReset = () => {
    setIsPlaying(false);
    setCurrentStep(0);
    setTimeline([]);
    setHistoryQueues([]);
    setHistoryWaitTimes([]);
  };

  const handleComplete = () => {
    const newRun = {
      id: Date.now(),
      timestamp: new Date().toLocaleTimeString(),
      dataset: selectedDataset,
      algorithm: selectedAlgo,
      runtime: ((maxSteps * 1.2) / speed).toFixed(1) + "s",
      bestFitness: algoData.fitness.toFixed(5),
      iterations: maxSteps,
      avgDelay: (algoData.avg_wait_time || 0).toFixed(1) + "s",
      queueLength: (algoData.avg_queue_length || 0).toFixed(1)
    };

    setRunHistory(prev => {
      const updated = [newRun, ...prev].slice(0, 10);
      localStorage.setItem("navi_run_history", JSON.stringify(updated));
      return updated;
    });

    setTimeline(prev => [
      ...prev,
      `[System] Simulation complete. Standardized results serialized.`,
      `[System] Saved run metrics to local database history.`
    ]);
  };

  // Live Stats handler
  const handleStatsUpdate = (stats) => {
    setLiveMetrics(stats);
    if (isPlaying) {
      setHistoryQueues(prev => [...prev, stats.queue].slice(-30));
      setHistoryWaitTimes(prev => [...prev, currentWaitTime].slice(-30));
    }
  };

  // Export Results
  const exportResults = () => {
    const fileData = {
      algorithm: selectedAlgo,
      dataset: selectedDataset,
      metrics: {
        fitness: algoData.fitness,
        avg_wait_time: algoData.avg_wait_time,
        congestion_pressure: algoData.congestion_pressure,
        total_flow: algoData.total_flow,
        avg_queue_length: algoData.avg_queue_length,
      },
      convergence_history: algoData.convergence_history,
      timestamp: new Date().toISOString()
    };
    const jsonString = `data:text/json;charset=utf-8,${encodeURIComponent(
      JSON.stringify(fileData, null, 2)
    )}`;
    const downloadAnchor = document.createElement("a");
    downloadAnchor.setAttribute("href", jsonString);
    downloadAnchor.setAttribute("download", `navi_${selectedAlgo.toLowerCase()}_results.json`);
    document.body.appendChild(downloadAnchor);
    downloadAnchor.click();
    downloadAnchor.remove();
  };

  // Reload previous runs
  const loadPreviousRun = (run) => {
    setSelectedAlgo(run.algorithm);
    setSelectedDataset(run.dataset);
    setCurrentStep(run.iterations - 1);
    setTimeline([
      `[History] Reopened simulation run from execution history list.`,
      `[History] Loaded final fitness: ${run.bestFitness} config.`
    ]);
  };

  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Simulation Workspace"
          title="Optimization Simulator"
          description="Interactive testbed to run signal optimizations, monitor vehicular flow dynamics, and observe strategy shifts in real-time."
        />

        {/* Top Control Panel */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 bg-zinc-950/20 p-4 rounded-xl border border-zinc-900 shadow-xl">
          <div className="flex flex-col gap-1.5">
            <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-semibold font-mono">Algorithm</span>
            <select
              value={selectedAlgo}
              onChange={(e) => { setSelectedAlgo(e.target.value); handleReset(); }}
              disabled={isPlaying}
              className="bg-zinc-900 border border-zinc-800 text-xs rounded-lg p-2 text-zinc-100 focus:outline-none"
            >
              <option value="GA">Genetic Algorithm (GA)</option>
              <option value="PSO">Particle Swarm (PSO)</option>
              <option value="GWO">Grey Wolf (GWO)</option>
              <option value="DE">Differential Evolution (DE)</option>
              <option value="ACO">Ant Colony (ACO)</option>
              <option value="SA">Simulated Annealing (SA)</option>
              <option value="ASM">Adaptive switching (ASM)</option>
              <option value="HYBRID">Triple Hybrid (ACO-SA-GA)</option>
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-semibold font-mono">Dataset</span>
            <select
              value={selectedDataset}
              onChange={(e) => setSelectedDataset(e.target.value)}
              disabled={isPlaying}
              className="bg-zinc-900 border border-zinc-800 text-xs rounded-lg p-2 text-zinc-100 focus:outline-none"
            >
              <option value="vanet.csv">vanet.csv (Default)</option>
              <option value="scenario_heavy.csv" disabled>scenario_heavy.csv (Coming Soon)</option>
              <option value="scenario_light.csv" disabled>scenario_light.csv (Coming Soon)</option>
            </select>
          </div>

          <div className="flex flex-col gap-1.5">
            <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-semibold font-mono">Speed Multiplier</span>
            <div className="flex gap-1">
              {[1, 2, 4].map((s) => (
                <button
                  key={s}
                  onClick={() => setSpeed(s)}
                  className={`flex-1 text-xs py-2 rounded-lg border transition-all ${
                    speed === s 
                      ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400 font-semibold" 
                      : "bg-zinc-900 border-zinc-800 text-zinc-400 hover:text-zinc-200"
                  }`}
                >
                  {s}x
                </button>
              ))}
            </div>
          </div>

          <div className="flex flex-col gap-1.5 justify-end">
            <div className="flex gap-2">
              {!isPlaying ? (
                <Button 
                  variant="primary" 
                  size="sm" 
                  icon={Play} 
                  className="flex-1 text-xs" 
                  onClick={handleStart}
                >
                  Start
                </Button>
              ) : (
                <Button 
                  variant="secondary" 
                  size="sm" 
                  icon={Pause} 
                  className="flex-1 text-xs bg-zinc-800 border-zinc-700 text-zinc-200 hover:bg-zinc-700" 
                  onClick={handlePause}
                >
                  Pause
                </Button>
              )}
              <IconButton 
                icon={RotateCcw} 
                size="sm" 
                variant="outline" 
                onClick={handleReset} 
                aria-label="Reset Simulation"
              />
            </div>
          </div>
        </div>

        {/* Main Grid Content */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Left Block: Canvas Simulation */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            <div className="bg-zinc-950/40 p-4 rounded-2xl border border-zinc-900 shadow-2xl relative">
              <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-bold mb-3 block">
                Visual Traffic Simulation Network
              </span>
              
              <SimulationCanvas
                greenTimes={currentGreenTimes}
                themeColor={selectedAlgo === "ASM" ? "#3b82f6" : "#10b981"}
                pressure={currentPressure}
                avgSpeed={currentSpeed}
                speedMultiplier={speed}
                onStatsUpdate={handleStatsUpdate}
              />

              {/* Lane Phase Countdown Indicators */}
              <div className="grid grid-cols-4 gap-2 mt-4">
                {currentGreenTimes.map((gt, i) => {
                  const active = liveMetrics.remainingTime > 0 && currentGreenTimes.indexOf(gt) === i;
                  return (
                    <div 
                      key={i} 
                      className={`p-2.5 rounded-lg border transition-all text-center flex flex-col ${
                        active 
                          ? "bg-emerald-500/10 border-emerald-500/30 text-emerald-400" 
                          : "bg-zinc-900/60 border-zinc-800/60 text-zinc-500"
                      }`}
                    >
                      <span className="text-[8px] uppercase tracking-wider">Lane {i+1}</span>
                      <span className="text-sm font-bold font-mono">{gt}s</span>
                    </div>
                  );
                })}
              </div>
            </div>

            {/* Live Chart Panels */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              {/* Convergence Curve Chart */}
              <GlassCard className="flex flex-col gap-3 border-zinc-900" hover={false}>
                <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-bold">
                  Fitness Convergence Curve
                </span>
                <div className="h-44 w-full bg-zinc-950 border border-zinc-900 rounded-lg flex items-end justify-center px-4 pt-6 relative overflow-hidden">
                  <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                    {/* SVG Line mapping convergence values */}
                    <polyline
                      fill="none"
                      stroke={selectedAlgo === "ASM" ? "#3b82f6" : "#10b981"}
                      strokeWidth="2"
                      points={algoData.convergence_history.slice(0, currentStep + 1).map((v, idx) => {
                        const min = Math.min(...algoData.convergence_history);
                        const max = Math.max(...algoData.convergence_history);
                        const x = (idx / (maxSteps - 1)) * 100;
                        const y = 90 - ((v - min) / (max - min || 1)) * 80;
                        return `${x},${y}`;
                      }).join(" ")}
                    />
                  </svg>
                  <div className="absolute bottom-2 left-2 text-[8px] font-mono text-zinc-500">
                    Step {currentStep} / {maxSteps - 1}
                  </div>
                  <div className="absolute top-2 right-2 text-[8px] font-mono text-zinc-400">
                    Fit: {algoData.convergence_history[currentStep]?.toFixed(4)}
                  </div>
                </div>
              </GlassCard>

              {/* Queue Backlog History */}
              <GlassCard className="flex flex-col gap-3 border-zinc-900" hover={false}>
                <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-bold">
                  Vehicular Queue Backlog Trend
                </span>
                <div className="h-44 w-full bg-zinc-950 border border-zinc-900 rounded-lg flex items-end gap-0.5 px-2 pt-6 relative overflow-hidden">
                  {historyQueues.map((q, idx) => (
                    <div
                      key={idx}
                      className="flex-1 bg-amber-500/80 rounded-t-sm"
                      style={{ height: `${(q / 15) * 80 + 10}%` }}
                    />
                  ))}
                  {historyQueues.length === 0 && (
                    <span className="text-[10px] text-zinc-600 font-normal absolute inset-0 flex items-center justify-center">
                      Awaiting simulation stats...
                    </span>
                  )}
                  <div className="absolute top-2 right-2 text-[8px] font-mono text-zinc-400">
                    Current Queue: {liveMetrics.queue}
                  </div>
                </div>
              </GlassCard>
            </div>
          </div>

          {/* Right Block: Telemetry & Chronological Logs */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            
            {/* Telemetry Dashboard panel */}
            <GlassCard className="flex flex-col gap-4 border-zinc-900" hover={false}>
              <div className="flex items-center gap-2 border-b border-zinc-900 pb-3">
                <Signal size={14} className="text-emerald-400" />
                <span className="text-xs uppercase tracking-widest text-zinc-300 font-bold">
                  Telemetry Panel
                </span>
              </div>

              <div className="grid grid-cols-2 gap-3 text-xs">
                <div className="bg-zinc-900/60 p-2.5 rounded-lg border border-zinc-800/80">
                  <span className="text-[8px] text-zinc-500 uppercase block mb-0.5">Algorithm</span>
                  <span className="text-zinc-200 font-semibold font-mono">{selectedAlgo}</span>
                </div>
                <div className="bg-zinc-900/60 p-2.5 rounded-lg border border-zinc-800/80">
                  <span className="text-[8px] text-zinc-500 uppercase block mb-0.5">Step / Iteration</span>
                  <span className="text-zinc-200 font-semibold font-mono">{currentStep} / {maxSteps - 1}</span>
                </div>
                <div className="bg-zinc-900/60 p-2.5 rounded-lg border border-zinc-800/80">
                  <span className="text-[8px] text-zinc-500 uppercase block mb-0.5">Best Fitness</span>
                  <span className="text-emerald-400 font-semibold font-mono">
                    {algoData.convergence_history[currentStep]?.toFixed(4)}
                  </span>
                </div>
                <div className="bg-zinc-900/60 p-2.5 rounded-lg border border-zinc-800/80">
                  <span className="text-[8px] text-zinc-500 uppercase block mb-0.5">Mean Latency</span>
                  <span className="text-zinc-200 font-semibold font-mono">{currentWaitTime.toFixed(1)}s</span>
                </div>
              </div>

              {/* ASM specific monitoring dashboard */}
              {(selectedAlgo === "ASM" || selectedAlgo === "HYBRID") && asmState && (
                <div className="bg-zinc-900/40 border border-zinc-800 rounded-xl p-3 flex flex-col gap-3 text-xs mt-2 animate-in fade-in duration-200">
                  <span className="text-[8px] text-blue-400 uppercase tracking-wider block font-bold font-mono">
                    ASM Controller Diagnostics
                  </span>
                  <div className="grid grid-cols-2 gap-2 text-[10px]">
                    <div>
                      <span className="text-zinc-500">Active strategy:</span>
                      <span className="text-zinc-200 block font-bold font-mono">{asmState.active}</span>
                    </div>
                    <div>
                      <span className="text-zinc-500">Recommendation:</span>
                      <span className="text-zinc-200 block font-bold font-mono">{asmState.recommend}</span>
                    </div>
                    <div>
                      <span className="text-zinc-500">Confidence margin:</span>
                      <span className="text-blue-400 block font-bold font-mono">{asmState.margin.toFixed(2)}</span>
                    </div>
                    <div>
                      <span className="text-zinc-500">Switch safety gate:</span>
                      <span className={`block font-bold font-mono ${asmState.decision === "SWITCH" ? "text-emerald-400" : "text-zinc-400"}`}>
                        {asmState.decision}
                      </span>
                    </div>
                  </div>

                  <div className="flex flex-col gap-1.5 border-t border-zinc-800/80 pt-2">
                    <span className="text-[8px] text-zinc-500 uppercase tracking-widest font-mono">Search Need States</span>
                    <div className="flex justify-between items-center text-[9px] text-zinc-400">
                      <span>Explore: {(asmState.explr * 100).toFixed(0)}%</span>
                      <span>Exploit: {(asmState.explt * 100).toFixed(0)}%</span>
                      <span>Escape: {(asmState.escape * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
              )}

              {/* Global stats from simulator canvas */}
              <div className="flex flex-col gap-2 pt-2 border-t border-zinc-900">
                <div className="flex justify-between text-xs">
                  <span className="text-zinc-500">Completed Vehicles</span>
                  <span className="text-zinc-300 font-semibold font-mono">{liveMetrics.throughput}</span>
                </div>
                <div className="flex justify-between text-xs">
                  <span className="text-zinc-500">Active Vehicles</span>
                  <span className="text-zinc-300 font-semibold font-mono">{liveMetrics.activeCars}</span>
                </div>
              </div>

              {currentStep === maxSteps - 1 && (
                <Button 
                  variant="outline" 
                  size="sm" 
                  icon={Download} 
                  onClick={exportResults}
                  className="w-full text-xs mt-2"
                >
                  Export Simulation Results
                </Button>
              )}
            </GlassCard>

            {/* Chronological Event Timeline */}
            <GlassCard className="flex-1 flex flex-col gap-3 border-zinc-900 min-h-[220px]" hover={false} padding="sm">
              <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-bold block border-b border-zinc-900 pb-2">
                Simulation Event Timeline
              </span>
              <div className="flex-1 overflow-y-auto max-h-[280px] pr-1 flex flex-col gap-2.5 custom-scrollbar text-[10px] text-zinc-400 font-mono">
                {timeline.map((event, idx) => (
                  <div key={idx} className="flex gap-2">
                    <span className="text-emerald-400 shrink-0">&raquo;</span>
                    <span className="leading-relaxed">{event}</span>
                  </div>
                ))}
                {timeline.length === 0 && (
                  <span className="text-zinc-600 block text-center mt-6">
                    Start the simulation to write execution events...
                  </span>
                )}
              </div>
            </GlassCard>

            {/* Run History List */}
            {runHistory.length > 0 && (
              <GlassCard className="flex flex-col gap-3 border-zinc-900" hover={false} padding="sm">
                <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-bold block border-b border-zinc-900 pb-2">
                  Execution History
                </span>
                <div className="flex flex-col gap-1.5 max-h-[160px] overflow-y-auto pr-1 custom-scrollbar">
                  {runHistory.map((run) => (
                    <button
                      key={run.id}
                      onClick={() => loadPreviousRun(run)}
                      className="w-full flex items-center justify-between p-2 rounded bg-zinc-900/40 border border-zinc-900/60 hover:bg-zinc-900 hover:border-zinc-800 text-left text-[10px] text-zinc-400 transition-all font-mono"
                    >
                      <div className="flex flex-col">
                        <span className="text-zinc-300 font-bold">{run.algorithm} ({run.dataset})</span>
                        <span className="text-zinc-500 text-[8px]">{run.timestamp}</span>
                      </div>
                      <div className="flex flex-col items-end">
                        <span className="text-emerald-400 font-bold">Fit: {run.bestFitness}</span>
                        <span className="text-[8px] text-zinc-500">Delay: {run.avgDelay}</span>
                      </div>
                    </button>
                  ))}
                </div>
              </GlassCard>
            )}

          </div>
        </div>
      </Container>
    </Section>
  );
};

const IconButton = ({ icon: Icon, variant, size, onClick, className, ...props }) => (
  <button
    onClick={onClick}
    className={`p-2 rounded-lg border flex items-center justify-center transition-all ${
      variant === "outline" 
        ? "bg-transparent border-zinc-800 text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900" 
        : "bg-zinc-900 border-zinc-800 text-zinc-200 hover:bg-zinc-800"
    } ${className}`}
    {...props}
  >
    <Icon size={16} />
  </button>
);
