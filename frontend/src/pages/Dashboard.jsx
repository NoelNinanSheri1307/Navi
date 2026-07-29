import React, { useState, useMemo, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { 
  TrendingUp, 
  Clock, 
  Globe, 
  Zap, 
  ShieldCheck, 
  AlertCircle, 
  RefreshCw,
  Activity,
  RotateCcw,
  CheckCircle,
  Database
} from "lucide-react";

import AlgorithmCard, { ALGO_THEMES } from "../components/AlgorithmCard";
import rawData from "../data/data.json";
import { APP_CONFIG, FUZZY_SYSTEM_CONFIG } from "../config/constants";
import { API_BASE_URL } from "../config/api";
import { GlassCard } from "../components/ui/GlassCard";
import { Badge } from "../components/ui/Badge";

const EXTENDED_THEMES = {
  ...ALGO_THEMES,
  COMPARE: { color: "#ffffff", icon: Globe, desc: "Comparative Analytics Suite. Benchmark all optimization kernels simultaneously." },
  FUZZY: { color: "#3b82f6", icon: ShieldCheck, desc: "Mamdani Fuzzy Inference Engine. Membership functions and 9-rule matrix." }
};

const Dashboard = ({ onBack, onThemeChange }) => {
  const processedData = useMemo(() => {
    if (!Array.isArray(rawData) || rawData.length === 0) return {};
    const map = {};
    rawData.forEach((item) => {
      const algoKey = item.algorithm?.toUpperCase();
      if (!algoKey) return;

      const history = item.convergence_history || [];
      const minFit = Math.min(...history);
      const maxFit = Math.max(...history);
      const diff = maxFit - minFit || 1;
      const normalizedConv = history.map(v => (maxFit - v) / diff);
      const perfScore = Math.min(100, Math.max(0, (1 - Math.abs(item.fitness)) * 100));

      map[algoKey] = {
        ...item,
        avg_wait: item.avg_wait_time || 0,
        normalizedConv: normalizedConv.length > 50 ? normalizedConv.slice(-50) : normalizedConv,
        perfScore: perfScore.toFixed(1)
      };
    });
    return map;
  }, []);

  const [selectedAlgo, setSelectedAlgo] = useState("GA");
  const [isDataLoaded, setIsDataLoaded] = useState(false);

  // Diagnostic states
  const [healthStatus, setHealthStatus] = useState({ status: "offline", platform: "unknown", active_modules: [] });
  const [backendStatus, setBackendStatus] = useState({ running: false, active_algorithm: "None", speed_multiplier: 1.0 });
  const [recentHistory, setRecentHistory] = useState([]);
  const [actionTimeline, setActionTimeline] = useState([]);

  useEffect(() => {
    const timer = setTimeout(() => setIsDataLoaded(true), 200);
    return () => clearTimeout(timer);
  }, []);

  useEffect(() => {
    fetch(`${API_BASE_URL}/health`)
      .then(res => res.json())
      .then(data => setHealthStatus(data))
      .catch(() => {});
      
    fetch(`${API_BASE_URL}/simulation/status`)
      .then(res => res.json())
      .then(data => setBackendStatus(data))
      .catch(() => {});

    fetch(`${API_BASE_URL}/simulation/history`)
      .then(res => res.json())
      .then(data => setRecentHistory(data))
      .catch(() => {});
  }, []);

  const handleAction = async (actionType) => {
    const timestamp = new Date().toLocaleTimeString();
    if (actionType === "clear_cache") {
      try {
        await fetch(`${API_BASE_URL}/simulation/reset`, { method: "POST" });
        setRecentHistory([]);
        setActionTimeline(prev => [`[${timestamp}] Reset server memory state arrays.`, ...prev]);
      } catch (e) {
        setActionTimeline(prev => [`[${timestamp}] Reset failed: ${e.message}`, ...prev]);
      }
    } else if (actionType === "run_benchmark") {
      setActionTimeline(prev => [`[${timestamp}] Launch benchmark trials on backend command line.`, ...prev]);
    }
  };

  const currentResult = processedData[selectedAlgo];
  const theme = EXTENDED_THEMES[selectedAlgo] || EXTENDED_THEMES.GA;

  useEffect(() => {
    if (onThemeChange) {
      onThemeChange({ type: selectedAlgo, color: theme.color });
    }
  }, [selectedAlgo, theme.color, onThemeChange]);

  // Loading State
  if (!isDataLoaded) {
    return (
      <div className="flex-1 min-h-[70vh] bg-black flex flex-col items-center justify-center p-6 text-center gap-4">
        <RefreshCw className="animate-spin text-emerald-400" size={32} />
        <p className="text-xs uppercase tracking-widest text-zinc-500 font-semibold">Initializing Navi Analytics Dashboard...</p>
      </div>
    );
  }

  // Empty State / Fallback
  if (Object.keys(processedData).length === 0) {
    return (
      <div className="flex-1 min-h-[70vh] bg-black flex flex-col items-center justify-center p-6 text-center gap-4">
        <AlertCircle className="text-rose-400" size={40} />
        <h2 className="text-xl uppercase tracking-tight text-zinc-200">No Telemetry Data Found</h2>
        <p className="text-xs text-zinc-500 max-w-md">Please execute the backend benchmark pipeline to generate valid data output.</p>
        <button onClick={onBack} className="mt-4 px-6 py-2 rounded-full bg-zinc-900 border border-zinc-800 text-zinc-200 text-xs uppercase tracking-widest hover:bg-zinc-800 transition-all">
          Return Home
        </button>
      </div>
    );
  }

  return (
    <div className="w-full flex flex-col p-4 sm:p-6 lg:p-8 gap-6 sm:gap-8 text-zinc-100 relative items-center overflow-x-hidden">
      
      {/* Dashboard Sub-Header */}
      <div className="w-full max-w-[1600px] flex flex-col sm:flex-row sm:items-center justify-between gap-4 border-b border-zinc-900 pb-6 mb-2">
        <div className="flex flex-col">
          <span className="text-[10px] uppercase tracking-[0.25em] text-zinc-500 font-semibold">
            Optimization Workspace & Mamdani FIS
          </span>
          <h2 className="text-xl sm:text-3xl tracking-tight uppercase text-zinc-100 font-normal">
            Intelligence Dashboard
          </h2>
        </div>
      </div>

      {/* Main Grid Content */}
      <div className="w-full max-w-[1600px] grid grid-cols-1 lg:grid-cols-12 gap-6 sm:gap-8 lg:gap-10">
        
        {/* Left Sidebar (Algorithm Selection) */}
        <section className="lg:col-span-4 flex flex-col gap-4">
          <div className="flex flex-col gap-2.5 sm:gap-3 max-h-[400px] lg:max-h-[82vh] overflow-y-auto pr-1 custom-scrollbar">
            {Object.keys(processedData).map((key) => (
              <AlgorithmCard
                key={key}
                algo={key}
                active={selectedAlgo === key}
                onClick={setSelectedAlgo}
                metrics={processedData[key]}
              />
            ))}
            <div className="mt-2 sm:mt-4 flex flex-col gap-2.5 sm:gap-3">
              <SidebarButton
                label="Comparative Suite"
                sub="Cross-Kernel Benchmarks"
                active={selectedAlgo === "COMPARE"}
                onClick={() => setSelectedAlgo("COMPARE")}
                icon={<Globe size={18} />}
              />
              <SidebarButton
                label="Mamdani Fuzzy Core"
                sub="9-Rule Inference Engine"
                active={selectedAlgo === "FUZZY"}
                onClick={() => setSelectedAlgo("FUZZY")}
                icon={<ShieldCheck size={18} />}
              />
            </div>
          </div>
        </section>

        {/* Right Main Section */}
        <section className="lg:col-span-8 flex flex-col gap-6 sm:gap-8 lg:gap-10">
          <AnimatePresence mode="wait">
            {selectedAlgo === "COMPARE" ? (
              <motion.div
                key="compare"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex flex-col gap-6 sm:gap-8 lg:gap-10"
              >
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] sm:text-xs uppercase tracking-[0.25em] text-zinc-500">
                    Scientific Benchmark Suite
                  </span>
                  <h3 className="text-2xl sm:text-4xl md:text-5xl uppercase tracking-tight text-zinc-100 font-normal">
                    Global Performance Benchmarks
                  </h3>
                </div>

                <div className="bg-zinc-950/40 border border-zinc-900 p-4 sm:p-6 lg:p-8 rounded-2xl backdrop-blur-md">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
                    <ComparisonImage src="/results/compare_radar.png" title="Kernel Multi-Metric Radar" />
                    <ComparisonImage src="/results/compare_metrics_heatmap.png" title="Parameter Sensitivity Heatmap" />
                    <ComparisonImage src="/results/compare_greentimes_scatter.png" title="Phase Allocation Scatter Study" />
                    <ComparisonImage src="/results/compare_convergence_fitness.png" title="Convergence Trajectory Overlay" />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8">
                  <ChartBox title="Effective Throughput (Flow)" metric="total_flow" unit="VEH/H" data={processedData} icon={Zap} />
                  <ChartBox title="Infrastructure Latency (Wait)" metric="avg_wait" unit="s" data={processedData} icon={Clock} invert />
                </div>
              </motion.div>
            ) : selectedAlgo === "FUZZY" ? (
              <motion.div
                key="fuzzy"
                initial={{ opacity: 0, y: 15 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex flex-col gap-6 sm:gap-8 lg:gap-10"
              >
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] sm:text-xs uppercase tracking-[0.25em] text-zinc-500 font-semibold">
                    Mamdani FIS Configuration
                  </span>
                  <h3 className="text-2xl sm:text-4xl md:text-5xl uppercase tracking-tight text-blue-400 font-normal">
                    Fuzzy Inference Kernel
                  </h3>
                </div>
                
                {/* Rules List */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                  {FUZZY_SYSTEM_CONFIG.rules.map((rule, idx) => (
                    <FuzzyRuleCard key={idx} index={idx + 1} rule={rule.if} effect={rule.then} priority={rule.priority} />
                  ))}
                </div>

                <div className="bg-zinc-950/40 border border-zinc-900 p-4 sm:p-6 lg:p-8 rounded-2xl backdrop-blur-md">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
                    <ComparisonImage src="/results/fuzzy_membership_functions.png" title="Antecedent Membership Profiles" />
                    <ComparisonImage src="/results/fuzzy_lane_allocation.png" title="Lane Priority Allocation Mapping" />
                    <ComparisonImage src="/results/fuzzy_green_time_analysis.png" title="Fuzzy Phase Duration Distribution" />
                    <ComparisonImage src="/results/fuzzy_correlation_heatmap.png" title="Variable Correlation Matrix" />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
                  <div className="bg-zinc-950/40 border border-zinc-900 rounded-2xl p-4 sm:p-6 lg:p-8 flex flex-col gap-3 backdrop-blur-md">
                    <h4 className="text-sm sm:text-base uppercase tracking-wider text-blue-400 font-bold">Inference Methodology</h4>
                    <p className="text-xs sm:text-sm text-zinc-400 leading-relaxed font-normal">
                      The Navi fuzzy inference engine employs Mamdani-style min-max inference to bridge discrete vehicular telemetry vectors with continuous signal durations. Membership functions are parameterized across 35 independent breakpoints.
                    </p>
                  </div>
                  <div className="bg-zinc-950/40 border border-zinc-900 rounded-2xl p-4 sm:p-6 lg:p-8 flex flex-col gap-3 backdrop-blur-md">
                    <h4 className="text-sm sm:text-base uppercase tracking-wider text-blue-400 font-bold">Rule Matrix Architecture</h4>
                    <p className="text-xs sm:text-sm text-zinc-400 leading-relaxed font-normal">
                      A robust 9-rule Mamdani knowledge base evaluates fuzzy antecedent sets (Low, Medium, High / Short, Medium, Long) across Congestion Pressure, Density, Queue Length, Wait Time, and Flow metrics to compute centroid-defuzzified signal phase targets.
                    </p>
                  </div>
                </div>
              </motion.div>
            ) : currentResult ? (
              <motion.div
                key={selectedAlgo}
                initial={{ opacity: 0, scale: 0.995 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, y: -10 }}
                className="flex flex-col gap-6 sm:gap-8 lg:gap-10"
              >
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2 border-b border-zinc-900 pb-4">
                  <div className="flex flex-col">
                    <span className="text-[10px] sm:text-xs uppercase tracking-[0.25em] text-zinc-500">
                      Search Kernel Model
                    </span>
                    <h3 className="text-3xl sm:text-5xl md:text-6xl uppercase tracking-tight leading-none font-normal" style={{ color: theme.color }}>
                      {selectedAlgo} Architecture
                    </h3>
                  </div>
                  <div className="flex items-baseline gap-2 sm:flex-col sm:items-end">
                    <span className="text-[10px] uppercase tracking-widest text-zinc-500 font-medium">Optimization Score</span>
                    <span className="text-2xl sm:text-4xl uppercase tracking-tight font-semibold" style={{ color: theme.color }}>
                      {currentResult.perfScore}%
                    </span>
                  </div>
                </div>

                {/* Dashboard Operations Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-3 gap-6">
                  
                  {/* Latest Run */}
                  <GlassCard className="flex flex-col gap-3 border-zinc-900" hover={false}>
                    <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-bold block border-b border-zinc-900 pb-2 mb-1">
                      Latest Run Metrics
                    </span>
                    {recentHistory.length > 0 ? (
                      <div className="flex flex-col gap-2 text-xs font-mono">
                        <div className="flex justify-between">
                          <span className="text-zinc-500">Algorithm:</span>
                          <span className="text-zinc-200 font-bold">{recentHistory[0].algorithm}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-zinc-500">Best Fitness:</span>
                          <span className="text-emerald-400 font-bold">{recentHistory[0].bestFitness}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-zinc-500">Avg Delay:</span>
                          <span className="text-zinc-300">{recentHistory[0].avgDelay}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-zinc-500">Queue Length:</span>
                          <span className="text-zinc-300">{recentHistory[0].queueLength}</span>
                        </div>
                      </div>
                    ) : (
                      <span className="text-xs text-zinc-500">No simulation runs executed yet.</span>
                    )}
                  </GlassCard>

                  {/* Backend Status */}
                  <GlassCard className="flex flex-col gap-3 border-zinc-900" hover={false}>
                    <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-bold block border-b border-zinc-900 pb-2 mb-1">
                      Backend Status
                    </span>
                    <div className="flex flex-col gap-2 text-xs">
                      <div className="flex justify-between items-center font-mono">
                        <span className="text-zinc-500">Status State:</span>
                        <div className="flex items-center gap-1.5">
                          <span className={`w-1.5 h-1.5 rounded-full ${backendStatus.running ? "bg-emerald-400 animate-pulse" : "bg-zinc-600"}`} />
                          <span className="text-zinc-200">{backendStatus.running ? "Running" : "Idle"}</span>
                        </div>
                      </div>
                      <div className="flex justify-between font-mono">
                        <span className="text-zinc-500">Active Task:</span>
                        <span className="text-zinc-300">{backendStatus.active_algorithm || "None"}</span>
                      </div>
                      <div className="flex justify-between font-mono">
                        <span className="text-zinc-500">Speed:</span>
                        <span className="text-zinc-300">{backendStatus.speed_multiplier}x</span>
                      </div>
                    </div>
                  </GlassCard>

                  {/* System Health */}
                  <GlassCard className="flex flex-col gap-3 border-zinc-900" hover={false}>
                    <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-bold block border-b border-zinc-900 pb-2 mb-1">
                      System Health
                    </span>
                    <div className="flex flex-col gap-2 text-xs font-mono">
                      <div className="flex justify-between">
                        <span className="text-zinc-500">Service:</span>
                        <span className="text-emerald-400 font-bold">{healthStatus.status === "healthy" ? "ONLINE" : "OFFLINE"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-zinc-500">Platform:</span>
                        <span className="text-zinc-300 truncate max-w-[120px]">{healthStatus.platform || "unknown"}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-zinc-500">Server PID:</span>
                        <span className="text-zinc-300">{healthStatus.server_pid || "N/A"}</span>
                      </div>
                    </div>
                  </GlassCard>

                  {/* Recent Benchmark */}
                  <GlassCard className="flex flex-col gap-3 border-zinc-900" hover={false}>
                    <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-bold block border-b border-zinc-900 pb-2 mb-1">
                      Recent Benchmark
                    </span>
                    {processedData.ASM ? (
                      <div className="flex flex-col gap-2 text-xs font-mono">
                        <div className="flex justify-between">
                          <span className="text-zinc-500">Best Strategy:</span>
                          <span className="text-zinc-100 font-bold">ASM</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-zinc-500">Optimal Fitness:</span>
                          <span className="text-emerald-400 font-semibold">{processedData.ASM.fitness.toFixed(5)}</span>
                        </div>
                        <div className="flex justify-between">
                          <span className="text-zinc-500">Mean Wait:</span>
                          <span className="text-zinc-300">{processedData.ASM.avg_wait.toFixed(1)}s</span>
                        </div>
                      </div>
                    ) : (
                      <span className="text-xs text-zinc-500">Awaiting benchmark results dataset...</span>
                    )}
                  </GlassCard>

                  {/* Quick Actions */}
                  <GlassCard className="flex flex-col gap-3 border-zinc-900 md:col-span-2" hover={false}>
                    <span className="text-[9px] uppercase tracking-wider text-zinc-500 font-bold block border-b border-zinc-900 pb-2 mb-1">
                      Quick Operations Actions
                    </span>
                    <div className="flex flex-wrap gap-2 mt-1">
                      <button 
                        onClick={() => handleAction("run_benchmark")} 
                        className="px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 text-xs font-semibold text-zinc-200 transition-all flex items-center gap-1.5"
                      >
                        <Activity size={12} />
                        Run Baseline CLI
                      </button>
                      <button 
                        onClick={() => handleAction("clear_cache")} 
                        className="px-3 py-1.5 rounded-lg border border-zinc-800 bg-zinc-900 hover:bg-zinc-800 text-xs font-semibold text-zinc-200 transition-all flex items-center gap-1.5"
                      >
                        <RotateCcw size={12} />
                        Clear Server Cache
                      </button>
                    </div>
                  </GlassCard>

                </div>

                {/* Specs and Charts Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8">
                  <div className="flex flex-col gap-6">
                    <div className="bg-black border border-zinc-900 p-3 rounded-2xl flex items-center justify-center min-h-[260px] sm:min-h-[320px] group overflow-hidden relative shadow-2xl">
                      <motion.img
                        key={selectedAlgo}
                        initial={{ opacity: 0, scale: 1.02 }}
                        animate={{ opacity: 1, scale: 1 }}
                        src={`/results/algo_${selectedAlgo.toLowerCase()}.png`}
                        className="w-full h-full object-contain rounded-xl filter contrast-105 brightness-105 transition-transform duration-700"
                        alt={`${selectedAlgo} Output Chart`}
                        onError={(e) => { e.target.style.display = 'none'; }}
                      />
                    </div>
                    <DetailBox title="Kernel Specification Report" icon={Layers} color={theme.color}>
                      <div className="grid grid-cols-2 gap-4">
                        <SpecItem label="Total Cycle Duration" value={`${currentResult.cycle_time}s`} color={theme.color} />
                        <SpecItem label="Mean Vehicle Density" value={currentResult.avg_density.toFixed(2)} color={theme.color} />
                        <SpecItem label="Average Velocity" value={`${currentResult.avg_speed.toFixed(2)} km/h`} color={theme.color} />
                        <SpecItem label="Congestion Index" value={currentResult.congestion_pressure.toFixed(2)} color={theme.color} />
                      </div>
                    </DetailBox>
                  </div>

                  <div className="flex flex-col gap-6">
                    <DetailBox title="Convergence Curve Trajectory" icon={TrendingUp} color={theme.color}>
                      <div className="h-48 sm:h-60 w-full flex items-end gap-1 px-3 pt-4 bg-zinc-950/20 rounded-xl overflow-hidden border border-zinc-900">
                        {currentResult.normalizedConv.map((v, i) => (
                          <motion.div
                            key={i}
                            initial={{ height: 0 }}
                            animate={{ height: `${Math.max(5, v * 100)}%` }}
                            className="flex-1 rounded-t-sm"
                            style={{
                              background: theme.color,
                              opacity: 0.25 + (i / currentResult.normalizedConv.length) * 0.75
                            }}
                          />
                        ))}
                      </div>
                      <p className="text-[10px] text-zinc-500 mt-3 text-center uppercase tracking-widest font-semibold font-mono">
                        Fitness Evaluation Trajectory (n={currentResult.normalizedConv.length})
                      </p>
                    </DetailBox>
                  </div>
                </div>
              </motion.div>
            ) : null}
          </AnimatePresence>
        </section>
      </div>
    </div>
  );
};

const SidebarButton = ({ label, sub, active, onClick, icon }) => (
  <button
    onClick={onClick}
    className={`flex items-center gap-3 sm:gap-4 p-3.5 sm:p-4 rounded-xl border transition-all text-left shadow-lg w-full ${
      active
        ? "bg-zinc-900 border-zinc-800 text-zinc-100"
        : "bg-zinc-950/30 border-zinc-900/60 text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/20"
    }`}
  >
    <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg bg-zinc-900 border border-zinc-800 flex items-center justify-center text-zinc-400 group-hover:text-zinc-200">
      {icon}
    </div>
    <div className="flex flex-col">
      <span className="text-[9px] uppercase tracking-widest text-zinc-500 font-semibold">{sub}</span>
      <span className="text-xs sm:text-sm uppercase tracking-tight font-bold">{label}</span>
    </div>
  </button>
);

const FuzzyRuleCard = ({ index, rule, effect, priority }) => (
  <div className="p-3.5 sm:p-4 bg-zinc-950/40 border border-zinc-900 rounded-xl flex flex-col gap-1.5 hover:border-blue-500/40 transition-all">
    <div className="flex items-center justify-between">
      <span className="text-[9px] uppercase text-blue-400 tracking-wider">Rule #{index}</span>
      <span className={`text-[8px] uppercase px-2 py-0.5 rounded border ${
        priority === 'Critical' ? 'bg-rose-500/10 text-rose-400 border-rose-500/20' :
        priority === 'High' ? 'bg-amber-500/10 text-amber-400 border-amber-500/20' :
        'bg-emerald-500/10 text-emerald-400 border-emerald-500/20'
      }`}>
        {priority}
      </span>
    </div>
    <p className="text-xs text-zinc-200 font-normal">IF {rule}</p>
    <p className="text-[10px] text-zinc-500 uppercase tracking-tight">THEN: {effect}</p>
  </div>
);

const ComparisonImage = ({ src, title }) => (
  <div className="bg-black border border-zinc-900 p-2 sm:p-3 rounded-xl flex flex-col items-center justify-center min-h-[220px] sm:min-h-[280px] group overflow-hidden relative shadow-xl">
    <motion.img
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      src={src}
      className="w-full h-full object-contain rounded-lg filter contrast-105 brightness-105 transition-transform duration-500 group-hover:scale-102"
      alt={title}
      onError={(e) => { e.target.style.display = 'none'; }}
    />
    <div className="mt-2 px-3 py-1 bg-zinc-900/60 rounded-full border border-zinc-800">
      <h5 className="text-[10px] sm:text-xs uppercase tracking-wider text-zinc-400">{title}</h5>
    </div>
  </div>
);

const ChartBox = ({ title, metric, unit, data, icon: Icon, invert }) => {
  const sorted = Object.keys(data).sort((a, b) => invert ? data[a][metric] - data[b][metric] : data[b][metric] - data[a][metric]);
  const maxVal = Math.max(...Object.values(data).map(d => d[metric])) || 1;
  return (
    <div className="bg-zinc-950/40 border border-zinc-900 p-4 sm:p-6 rounded-2xl shadow-xl relative overflow-hidden backdrop-blur-md">
      <div className="flex items-center gap-3 mb-4 sm:mb-6">
        <Icon size={18} className="text-zinc-500" />
        <h4 className="text-xs uppercase tracking-widest text-zinc-400">{title}</h4>
      </div>
      <div className="flex flex-col gap-3">
        {sorted.map(key => (
          <div key={key} className="flex flex-col gap-1">
            <div className="flex justify-between items-center text-xs">
              <span className="uppercase tracking-tight font-medium" style={{ color: (ALGO_THEMES[key] || ALGO_THEMES.GA).color }}>{key} Engine</span>
              <span className="text-zinc-400 font-mono font-semibold">{(data[key][metric]).toLocaleString()} {unit}</span>
            </div>
            <div className="h-2 w-full bg-zinc-900 rounded-full overflow-hidden border border-zinc-800">
              <motion.div
                initial={{ width: 0 }}
                animate={{ width: `${(data[key][metric] / maxVal) * 100}%` }}
                className="h-full rounded-full"
                style={{ background: (ALGO_THEMES[key] || ALGO_THEMES.GA).color }}
              />
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

const SpecItem = ({ label, value, color }) => (
  <div className="flex flex-col">
    <span className="text-[9px] uppercase text-zinc-500 tracking-wider mb-0.5">{label}</span>
    <span className="text-base sm:text-xl uppercase tracking-tight font-semibold" style={{ color }}>{value}</span>
  </div>
);

const DetailBox = ({ title, icon: Icon, color, children }) => (
  <div className="bg-zinc-950/40 border border-zinc-900 rounded-2xl p-4 sm:p-6 shadow-xl backdrop-blur-md">
    <div className="flex items-center gap-3 mb-4">
      <Icon size={18} style={{ color }} />
      <h5 className="text-xs uppercase tracking-widest text-zinc-400">{title}</h5>
    </div>
    {children}
  </div>
);

export default Dashboard;
