import React, { useState, useMemo, useCallback, useEffect } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ArrowLeft, LayoutGrid, Layers, Activity, TrendingUp, Clock, Globe, Zap, ShieldCheck, AlertCircle, RefreshCw } from "lucide-react";

import AlgorithmCard, { ALGO_THEMES } from "../components/AlgorithmCard";
import SimulationCanvas from "../components/SimulationCanvas";
import HUDPanel from "../components/HUDPanel";
import rawData from "../data/data.json";
import { APP_CONFIG, FUZZY_SYSTEM_CONFIG } from "../config/constants";

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
  const [liveStats, setLiveStats] = useState({ queue: 0, throughput: 0, activeCars: 0, remainingTime: 0, fps: 60 });
  const [isDataLoaded, setIsDataLoaded] = useState(false);

  useEffect(() => {
    const timer = setTimeout(() => setIsDataLoaded(true), 200);
    return () => clearTimeout(timer);
  }, []);

  const handleStatsUpdate = useCallback((stats) => {
    setLiveStats(stats);
  }, []);

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
      <div className="min-h-screen bg-black flex flex-col items-center justify-center p-6 text-center gap-4">
        <RefreshCw className="animate-spin text-emerald-400" size={32} />
        <p className="text-xs uppercase tracking-widest text-white/60">Initializing Navi Analytics Dashboard...</p>
      </div>
    );
  }

  // Empty State / Fallback
  if (Object.keys(processedData).length === 0) {
    return (
      <div className="min-h-screen bg-black flex flex-col items-center justify-center p-6 text-center gap-4">
        <AlertCircle className="text-rose-400" size={40} />
        <h2 className="text-xl uppercase tracking-tight text-white/90">No Telemetry Data Found</h2>
        <p className="text-xs text-white/50 max-w-md">Please execute the backend benchmark pipeline to generate valid data output.</p>
        <button onClick={onBack} className="mt-4 px-6 py-2 rounded-full bg-white/10 text-white text-xs uppercase tracking-widest hover:bg-white/20 transition-all">
          Return Home
        </button>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-transparent flex flex-col p-3 xs:p-4 sm:p-6 lg:p-10 gap-6 sm:gap-8 lg:gap-10 text-white relative items-center overflow-x-hidden pt-4 sm:pt-6">
      
      {/* Top Navbar */}
      <nav className="w-full max-w-[1600px] flex items-center justify-between border-b border-white/10 pb-4 sm:pb-6 backdrop-blur-md sticky top-0 z-50 bg-black/40 px-2 sm:px-4">
        <div className="flex items-center gap-3 sm:gap-5">
          <motion.button
            onClick={onBack}
            whileHover={{ scale: 1.05, x: -3 }}
            whileTap={{ scale: 0.95 }}
            className="w-9 h-9 sm:w-11 sm:h-11 rounded-xl sm:rounded-2xl bg-white/10 border border-white/20 flex items-center justify-center text-white/60 hover:text-white transition-all shadow-xl"
            aria-label="Back to Home"
          >
            <ArrowLeft size={18} strokeWidth={2.5} />
          </motion.button>
          <div className="flex flex-col">
            <span className="text-[9px] sm:text-[10px] items-center gap-1.5 flex uppercase tracking-[0.2em] text-white/40">
              <LayoutGrid size={10} /> {APP_CONFIG.name} Framework
            </span>
            <h2 className="text-base sm:text-2xl md:text-3xl tracking-tight uppercase leading-none text-white/90 font-normal">
              Intelligence Dashboard
            </h2>
          </div>
        </div>
      </nav>

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
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -15 }}
                className="flex flex-col gap-6 sm:gap-8 lg:gap-10"
              >
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] sm:text-xs uppercase tracking-[0.25em] text-white/40">
                    Scientific Benchmark Suite
                  </span>
                  <h3 className="text-2xl sm:text-4xl md:text-5xl uppercase tracking-tight text-white/95">
                    GLOBAL KERNEL PERFORMANCE
                  </h3>
                </div>

                <div className="bg-white/[0.04] border border-white/10 p-4 sm:p-6 lg:p-8 rounded-2xl sm:rounded-3xl backdrop-blur-2xl">
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
                initial={{ opacity: 0, y: 20 }}
                animate={{ opacity: 1, y: 0 }}
                exit={{ opacity: 0, y: -15 }}
                className="flex flex-col gap-6 sm:gap-8 lg:gap-10"
              >
                <div className="flex flex-col gap-1">
                  <span className="text-[10px] sm:text-xs uppercase tracking-[0.25em] text-white/40">
                    Mamdani FIS Configuration
                  </span>
                  <h3 className="text-2xl sm:text-4xl md:text-5xl uppercase tracking-tight text-blue-400">
                    FUZZY INFERENCE KERNEL
                  </h3>
                </div>
                
                {/* Rules List */}
                <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 sm:gap-4">
                  {FUZZY_SYSTEM_CONFIG.rules.map((rule, idx) => (
                    <FuzzyRuleCard key={idx} index={idx + 1} rule={rule.if} effect={rule.then} priority={rule.priority} />
                  ))}
                </div>

                <div className="bg-white/[0.04] border border-white/10 p-4 sm:p-6 lg:p-8 rounded-2xl sm:rounded-3xl backdrop-blur-2xl">
                  <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6 lg:gap-8">
                    <ComparisonImage src="/results/fuzzy_membership_functions.png" title="Antecedent Membership Profiles" />
                    <ComparisonImage src="/results/fuzzy_lane_allocation.png" title="Lane Priority Allocation Mapping" />
                    <ComparisonImage src="/results/fuzzy_green_time_analysis.png" title="Fuzzy Phase Duration Distribution" />
                    <ComparisonImage src="/results/fuzzy_correlation_heatmap.png" title="Variable Correlation Matrix" />
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-4 sm:gap-6">
                  <div className="bg-white/[0.04] border border-white/10 rounded-2xl sm:rounded-3xl p-4 sm:p-6 lg:p-8 flex flex-col gap-3 backdrop-blur-2xl">
                    <h4 className="text-sm sm:text-base uppercase tracking-wider text-blue-400 font-bold">Inference Methodology</h4>
                    <p className="text-xs sm:text-sm text-white/60 leading-relaxed">
                      The Navi fuzzy inference engine employs Mamdani-style min-max max-min inference to bridge discrete vehicular telemetry vectors with continuous signal durations. Membership functions are parameterized across 35 independent breakpoints.
                    </p>
                  </div>
                  <div className="bg-white/[0.04] border border-white/10 rounded-2xl sm:rounded-3xl p-4 sm:p-6 lg:p-8 flex flex-col gap-3 backdrop-blur-2xl">
                    <h4 className="text-sm sm:text-base uppercase tracking-wider text-blue-400 font-bold">Rule Matrix Architecture</h4>
                    <p className="text-xs sm:text-sm text-white/60 leading-relaxed">
                      A robust 9-rule Mamdani knowledge base evaluates fuzzy antecedent sets (Low, Medium, High / Short, Medium, Long) across Congestion Pressure, Density, Queue Length, Wait Time, and Flow metrics to compute centroid-defuzzified signal phase targets.
                    </p>
                  </div>
                </div>
              </motion.div>
            ) : currentResult ? (
              <motion.div
                key={selectedAlgo}
                initial={{ opacity: 0, scale: 0.99 }}
                animate={{ opacity: 1, scale: 1 }}
                exit={{ opacity: 0, y: -15 }}
                className="flex flex-col gap-6 sm:gap-8 lg:gap-10"
              >
                {/* Header */}
                <div className="flex flex-col sm:flex-row sm:items-end justify-between gap-2 border-b border-white/10 pb-4">
                  <div className="flex flex-col">
                    <span className="text-[10px] sm:text-xs uppercase tracking-[0.25em] text-white/40">
                      Search Kernel Model
                    </span>
                    <h3 className="text-3xl sm:text-5xl md:text-6xl uppercase tracking-tight leading-none" style={{ color: theme.color }}>
                      {selectedAlgo} ARCHITECTURE
                    </h3>
                  </div>
                  <div className="flex items-baseline gap-2 sm:flex-col sm:items-end">
                    <span className="text-[10px] uppercase tracking-widest text-white/40">Optimization Score</span>
                    <span className="text-2xl sm:text-4xl uppercase tracking-tight" style={{ color: theme.color }}>
                      {currentResult.perfScore}%
                    </span>
                  </div>
                </div>

                {/* Simulation Canvas + HUD Stack */}
                <div className="flex flex-col xl:flex-row gap-6 sm:gap-8">
                  <div className="flex-1 bg-black/80 p-3 sm:p-4 rounded-2xl sm:rounded-3xl border border-white/10 backdrop-blur-2xl relative shadow-2xl overflow-hidden">
                    <SimulationCanvas
                      greenTimes={currentResult.green_times}
                      themeColor={theme.color}
                      pressure={currentResult.congestion_pressure}
                      avgSpeed={currentResult.avg_speed / 4.5}
                      onStatsUpdate={handleStatsUpdate}
                    />
                    <div key={selectedAlgo + "_phase_hud"} className="mt-3 flex flex-wrap gap-2 justify-center sm:justify-start">
                      {currentResult.green_times.map((gt, i) => (
                        <div key={i} className="px-2.5 py-1 bg-white/5 backdrop-blur-xl rounded-lg text-[10px] sm:text-xs text-white/70 border border-white/10 uppercase tracking-tight">
                          Lane {i + 1}: <span className="text-white font-bold">{gt}s</span>
                        </div>
                      ))}
                    </div>
                  </div>
                  <HUDPanel stats={liveStats} metrics={currentResult} color={theme.color} />
                </div>

                {/* Specs and Charts Grid */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6 sm:gap-8">
                  <div className="flex flex-col gap-6">
                    <div className="bg-black/80 border border-white/10 p-3 rounded-2xl sm:rounded-3xl flex items-center justify-center min-h-[260px] sm:min-h-[320px] group overflow-hidden relative shadow-2xl">
                      <motion.img
                        key={selectedAlgo}
                        initial={{ opacity: 0, scale: 1.04 }}
                        animate={{ opacity: 1, scale: 1 }}
                        src={`/results/algo_${selectedAlgo.toLowerCase()}.png`}
                        className="w-full h-full object-contain rounded-xl filter contrast-110 brightness-105 transition-transform duration-700"
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
                      <div className="h-48 sm:h-60 w-full flex items-end gap-1 px-3 pt-4 bg-black/50 rounded-xl overflow-hidden border border-white/5">
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
                      <p className="text-[10px] text-white/40 mt-3 text-center uppercase tracking-widest">
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
    className={`flex items-center gap-3 sm:gap-4 p-3.5 sm:p-4 rounded-xl sm:rounded-2xl border transition-all text-left shadow-lg ${
      active
        ? "bg-white/15 border-white/30 text-white"
        : "bg-white/[0.03] border-white/5 text-white/60 hover:text-white hover:bg-white/10"
    }`}
  >
    <div className="w-8 h-8 sm:w-10 sm:h-10 rounded-lg sm:rounded-xl bg-white/10 flex items-center justify-center text-white/80">
      {icon}
    </div>
    <div className="flex flex-col">
      <span className="text-[9px] uppercase tracking-widest text-white/40">{sub}</span>
      <span className="text-xs sm:text-sm uppercase tracking-tight font-bold">{label}</span>
    </div>
  </button>
);

const FuzzyRuleCard = ({ index, rule, effect, priority }) => (
  <div className="p-3.5 sm:p-4 bg-white/[0.03] border border-white/10 rounded-xl sm:rounded-2xl flex flex-col gap-1.5 hover:border-blue-400/40 transition-all">
    <div className="flex items-center justify-between">
      <span className="text-[9px] uppercase text-blue-400 tracking-wider">Rule #{index}</span>
      <span className={`text-[8px] uppercase px-2 py-0.5 rounded-full border ${
        priority === 'Critical' ? 'bg-rose-500/20 text-rose-300 border-rose-500/30' :
        priority === 'High' ? 'bg-amber-500/20 text-amber-300 border-amber-500/30' :
        'bg-emerald-500/20 text-emerald-300 border-emerald-500/30'
      }`}>
        {priority}
      </span>
    </div>
    <p className="text-xs text-white/90 font-medium">IF {rule}</p>
    <p className="text-[10px] text-white/50 uppercase tracking-tight">THEN: {effect}</p>
  </div>
);

const ComparisonImage = ({ src, title }) => (
  <div className="bg-black/90 border border-white/10 p-2 sm:p-3 rounded-xl sm:rounded-2xl flex flex-col items-center justify-center min-h-[220px] sm:min-h-[280px] group overflow-hidden relative shadow-xl">
    <motion.img
      initial={{ opacity: 0 }}
      animate={{ opacity: 1 }}
      src={src}
      className="w-full h-full object-contain rounded-lg filter contrast-105 brightness-105 transition-transform duration-500 group-hover:scale-102"
      alt={title}
      onError={(e) => { e.target.style.display = 'none'; }}
    />
    <div className="mt-2 px-3 py-1 bg-white/5 rounded-full border border-white/10">
      <h5 className="text-[10px] sm:text-xs uppercase tracking-wider text-white/70">{title}</h5>
    </div>
  </div>
);

const ChartBox = ({ title, metric, unit, data, icon: Icon, invert }) => {
  const sorted = Object.keys(data).sort((a, b) => invert ? data[a][metric] - data[b][metric] : data[b][metric] - data[a][metric]);
  const maxVal = Math.max(...Object.values(data).map(d => d[metric])) || 1;
  return (
    <div className="bg-white/[0.04] border border-white/10 p-4 sm:p-6 rounded-2xl sm:rounded-3xl shadow-xl relative overflow-hidden backdrop-blur-xl">
      <div className="flex items-center gap-3 mb-4 sm:mb-6">
        <Icon size={18} className="text-white/50" />
        <h4 className="text-xs uppercase tracking-widest text-white/60">{title}</h4>
      </div>
      <div className="flex flex-col gap-3">
        {sorted.map(key => (
          <div key={key} className="flex flex-col gap-1">
            <div className="flex justify-between items-center text-xs">
              <span className="uppercase tracking-tight" style={{ color: (ALGO_THEMES[key] || ALGO_THEMES.GA).color }}>{key} Engine</span>
              <span className="text-white/60 font-mono">{(data[key][metric]).toLocaleString()} {unit}</span>
            </div>
            <div className="h-2 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
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
    <span className="text-[9px] uppercase text-white/40 tracking-wider mb-0.5">{label}</span>
    <span className="text-base sm:text-xl uppercase tracking-tight" style={{ color }}>{value}</span>
  </div>
);

const DetailBox = ({ title, icon: Icon, color, children }) => (
  <div className="bg-white/[0.04] border border-white/10 rounded-2xl sm:rounded-3xl p-4 sm:p-6 shadow-xl backdrop-blur-xl">
    <div className="flex items-center gap-3 mb-4">
      <Icon size={18} style={{ color }} />
      <h5 className="text-xs uppercase tracking-widest text-white/60">{title}</h5>
    </div>
    {children}
  </div>
);

export default Dashboard;
