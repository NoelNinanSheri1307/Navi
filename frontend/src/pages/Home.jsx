import React from "react";
import { motion } from "framer-motion";
import { MoveRight, CircuitBoard, Layers, Database, Activity, ShieldCheck, Cpu, GitBranch, Terminal } from "lucide-react";
import { APP_CONFIG, ALGORITHM_CONFIG, FUZZY_SYSTEM_CONFIG } from "../config/constants";

const Home = ({ onNavigate, dataVolume = 0, bestPerf = 0 }) => {
  return (
    <div className="relative min-h-screen bg-transparent flex flex-col items-center justify-center p-4 sm:p-6 md:p-8 lg:p-12 overflow-x-hidden">
      {/* Background Glow Elements */}
      <div className="absolute inset-0 z-0 pointer-events-none overflow-hidden">
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 w-[300px] sm:w-[500px] md:w-[700px] h-[300px] sm:h-[500px] md:h-[700px] bg-emerald-500/10 blur-[120px] sm:blur-[160px] rounded-full animate-pulse" />
        <div className="absolute bottom-1/4 right-1/4 w-[250px] sm:w-[450px] md:w-[600px] h-[250px] sm:h-[450px] md:h-[600px] bg-cyan-500/10 blur-[120px] sm:blur-[160px] rounded-full animate-pulse" style={{ animationDelay: "2s" }} />

        {/* Animated Grid Pattern */}
        <div className="absolute inset-0 opacity-[0.03] bg-[linear-gradient(to_right,#808080_1px,transparent_1px),linear-gradient(to_bottom,#808080_1px,transparent_1px)] bg-[size:24px_24px] sm:bg-[size:40px_40px] [mask-image:radial-gradient(ellipse_60%_50%_at_50%_50%,#000_70%,transparent_100%)]" />
      </div>

      <div className="relative z-10 max-w-6xl w-full flex flex-col items-center gap-8 sm:gap-10 md:gap-12 text-center py-6 sm:py-10">
        
        {/* Framework Status Badge */}
        <motion.div
          initial={{ opacity: 0, y: 15 }}
          animate={{ opacity: 1, y: 0 }}
          className="px-3 sm:px-5 py-1.5 sm:py-2 rounded-full bg-white/5 border border-white/10 flex items-center gap-2 sm:gap-3 backdrop-blur-xl group hover:border-white/20 transition-all cursor-default"
        >
          <div className="w-2 h-2 rounded-full bg-emerald-400 group-hover:animate-ping" />
          <span className="text-[10px] sm:text-xs uppercase tracking-[0.15em] sm:tracking-[0.2em] text-white/70">
            {APP_CONFIG.name} v{APP_CONFIG.version} &bull; {APP_CONFIG.tagline}
          </span>
        </motion.div>

        {/* Hero Title & Subtitle */}
        <div className="flex flex-col gap-4 sm:gap-6 px-2 sm:px-4">
          <motion.h1
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ delay: 0.15 }}
            className="text-3xl xs:text-4xl sm:text-6xl md:text-7xl lg:text-8xl tracking-tight leading-[1.15] text-white/95 uppercase font-normal"
          >
            ADAPTIVE TRAFFIC <br />
            <span className="text-emerald-400/90 block mt-1 sm:mt-2">
              INTELLIGENCE FRAMEWORK
            </span>
          </motion.h1>

          <motion.p
            initial={{ opacity: 0, scale: 0.96 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ delay: 0.3 }}
            className="text-xs sm:text-base md:text-lg text-white/60 max-w-3xl mx-auto leading-relaxed px-2 sm:px-4"
          >
            {APP_CONFIG.description}
          </motion.p>
        </div>

        {/* Primary Action */}
        <motion.div
          initial={{ opacity: 0, y: 20 }}
          animate={{ opacity: 1, y: 0 }}
          transition={{ delay: 0.45 }}
          className="flex flex-col sm:flex-row items-center gap-4 sm:gap-6 w-full justify-center px-4"
        >
          <button
            onClick={onNavigate}
            className="group relative px-6 sm:px-8 md:px-10 py-3.5 sm:py-4 md:py-5 rounded-full bg-emerald-500 text-black uppercase text-xs sm:text-sm tracking-widest shadow-[0_0_30px_rgba(16,185,129,0.25)] hover:shadow-[0_0_50px_rgba(16,185,129,0.4)] transition-all flex items-center justify-center gap-3 sm:gap-4 w-full sm:w-auto font-bold"
          >
            <span>Launch Research Suite</span>
            <MoveRight size={18} className="group-hover:translate-x-1.5 transition-transform" strokeWidth={2.5} />
          </button>
        </motion.div>

        {/* Architectural Highlights */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.6 }}
          className="w-full max-w-5xl px-2 sm:px-4 mt-2 sm:mt-4"
        >
          <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            <FeatureCard
              icon={<ShieldCheck className="text-emerald-400" size={22} />}
              title="Mamdani Fuzzy Core"
              subtitle={`${FUZZY_SYSTEM_CONFIG.rulesCount}-Rule Linguistic Inference Engine`}
              desc="Maps discrete pressure, wait, density, flow, and queue vectors into optimized green-time allocations."
            />
            <FeatureCard
              icon={<Cpu className="text-cyan-400" size={22} />}
              title="7 Metaheuristic Kernels"
              subtitle="Global & Local Parameter Search"
              desc="Benchmarks GA, PSO, GWO, DE, ACO, SA, and Composite Hybrid optimization algorithms."
            />
            <FeatureCard
              icon={<GitBranch className="text-purple-400" size={22} />}
              title="35-Dim Decision Space"
              subtitle="Continuous MF Breakpoint Control"
              desc="Shapes antecedent membership functions across 35 bounded dimensions for fine-grained response curves."
            />
          </div>
        </motion.div>

        {/* Quantitative Performance Cards */}
        <motion.div
          initial={{ opacity: 0 }}
          animate={{ opacity: 1 }}
          transition={{ delay: 0.75 }}
          className="w-full grid grid-cols-2 md:grid-cols-4 gap-4 sm:gap-6 md:gap-8 pt-8 sm:pt-12 border-t border-white/10 mt-4 sm:mt-8"
        >
          <HomeMetric label="Telemetry Records" value={`${dataVolume >= 1000 ? (dataVolume / 1000).toFixed(1) + 'k' : dataVolume}+`} icon={<Database size={14} />} />
          <HomeMetric label="Search Kernels" value="07 Architectures" icon={<CircuitBoard size={14} />} />
          <HomeMetric label="Optimal FIS Score" value={`${bestPerf}%`} icon={<Layers size={14} />} />
          <HomeMetric label="Physics Engine" value="60 FPS Sync" icon={<Activity size={14} />} />
        </motion.div>
      </div>
    </div>
  );
};

const FeatureCard = ({ icon, title, subtitle, desc }) => (
  <div className="bg-white/[0.04] border border-white/10 rounded-2xl sm:rounded-3xl p-4 sm:p-6 text-left flex flex-col gap-2 sm:gap-3 backdrop-blur-xl hover:border-white/20 transition-all hover:bg-white/[0.06]">
    <div className="flex items-center gap-3">
      <div className="p-2 rounded-xl bg-white/5 border border-white/10">{icon}</div>
      <div className="flex flex-col">
        <h3 className="text-sm sm:text-base text-white/90 uppercase tracking-tight font-bold">{title}</h3>
        <span className="text-[10px] sm:text-xs text-white/40 uppercase tracking-wide">{subtitle}</span>
      </div>
    </div>
    <p className="text-xs sm:text-sm text-white/60 leading-relaxed mt-1">{desc}</p>
  </div>
);

const HomeMetric = ({ label, value, icon }) => (
  <div className="flex flex-col gap-1.5 sm:gap-2 items-center md:items-start p-3 sm:p-4 rounded-2xl bg-white/[0.02] border border-white/5 hover:border-white/10 transition-all">
    <div className="flex items-center gap-2 text-white/40">
      {icon}
      <span className="text-[9px] sm:text-[10px] uppercase tracking-widest">{label}</span>
    </div>
    <div className="text-xl sm:text-2xl md:text-3xl text-white/90 tracking-tight">{value}</div>
  </div>
);

export default Home;
