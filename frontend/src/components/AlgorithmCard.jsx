import React, { useState } from "react";
import { motion, AnimatePresence } from "framer-motion";
import { ShieldCheck, Zap, Activity, Brain, Cpu, BarChart3, ChevronRight } from "lucide-react";
import { ALGORITHM_CONFIG } from "../config/constants";

export const ALGO_THEMES = {
  GA:  { color: ALGORITHM_CONFIG.GA.color, icon: ShieldCheck, desc: ALGORITHM_CONFIG.GA.description },
  PSO: { color: ALGORITHM_CONFIG.PSO.color, icon: Activity, desc: ALGORITHM_CONFIG.PSO.description },
  GWO: { color: ALGORITHM_CONFIG.GWO.color, icon: BarChart3, desc: ALGORITHM_CONFIG.GWO.description },
  DE:  { color: ALGORITHM_CONFIG.DE.color, icon: Cpu, desc: ALGORITHM_CONFIG.DE.description },
  ACO: { color: ALGORITHM_CONFIG.ACO.color, icon: Zap, desc: ALGORITHM_CONFIG.ACO.description },
  HYBRID: { color: ALGORITHM_CONFIG.HYBRID.color, icon: Activity, desc: ALGORITHM_CONFIG.HYBRID.description },
  SA:  { color: ALGORITHM_CONFIG.SA.color, icon: Brain, desc: ALGORITHM_CONFIG.SA.description },
};

const AlgorithmCard = ({ algo, active, onClick, metrics }) => {
  const [isHovered, setIsHovered] = useState(false);
  const theme = ALGO_THEMES[algo] || ALGO_THEMES.GA;
  const Icon = theme.icon;

  const fitnessValue = metrics?.fitness !== undefined ? Number(metrics.fitness).toFixed(3) : "0.000";
  const flowValue = metrics?.total_flow ? Math.round(metrics.total_flow) : "0";

  return (
    <motion.button
      onMouseEnter={() => setIsHovered(true)}
      onMouseLeave={() => setIsHovered(false)}
      onClick={() => onClick(algo)}
      whileTap={{ scale: 0.98 }}
      className={`relative w-full h-20 sm:h-24 rounded-xl sm:rounded-2xl border transition-all duration-300 overflow-hidden group text-left ${
        active 
          ? "bg-white/15 border-white/30 shadow-xl" 
          : "bg-white/[0.03] border-white/5 hover:border-white/20 hover:bg-white/[0.06]"
      }`}
    >
      {/* Background Watermark */}
      <div 
        className="absolute top-0 right-3 sm:right-4 text-5xl sm:text-7xl font-bold opacity-[0.03] pointer-events-none select-none transition-all group-hover:opacity-[0.07]"
        style={{ color: theme.color }}
      >
        {algo}
      </div>

      <div className="relative z-10 flex items-center h-full px-3.5 sm:px-5 gap-3 sm:gap-4">
        <div 
          className="w-9 h-9 sm:w-11 sm:h-11 rounded-lg sm:rounded-xl flex items-center justify-center border border-white/10 shrink-0"
          style={{ backgroundColor: `${theme.color}20`, color: theme.color }}
        >
          <Icon size={18} strokeWidth={2.2} />
        </div>
        
        <div className="flex flex-col flex-1 min-w-0">
          <span className="text-[9px] sm:text-[10px] uppercase text-white/40 tracking-wider">Search Engine</span>
          <span className="text-sm sm:text-base md:text-lg uppercase tracking-tight text-white/90 truncate font-bold">
            {algo} Kernel
          </span>
        </div>

        {active && (
          <div className="w-2 h-2 rounded-full bg-emerald-400 shadow-[0_0_10px_#10b981] shrink-0" />
        )}
      </div>

      {/* Hover Info Overlay */}
      <AnimatePresence>
        {isHovered && !active && metrics && (
          <motion.div 
            initial={{ opacity: 0, x: -8 }}
            animate={{ opacity: 1, x: 0 }}
            exit={{ opacity: 0, x: -8 }}
            className="absolute inset-0 bg-black/95 backdrop-blur-md z-20 flex items-center px-4 gap-4"
          >
            <div className="flex flex-col shrink-0">
              <span className="text-[8px] uppercase text-white/40">Fitness</span>
              <span className="text-xs font-mono font-bold" style={{ color: theme.color }}>{fitnessValue}</span>
            </div>
            <div className="flex flex-col shrink-0">
              <span className="text-[8px] uppercase text-white/40">Throughput</span>
              <span className="text-xs font-mono font-bold text-white/90">{flowValue}</span>
            </div>
            <div className="w-px h-6 bg-white/10 shrink-0" />
            <p className="text-[9px] sm:text-[10px] text-white/70 leading-tight flex-1 line-clamp-2">
              {theme.desc}
            </p>
            <ChevronRight size={14} className="text-white/40 shrink-0" />
          </motion.div>
        )}
      </AnimatePresence>
    </motion.button>
  );
};

export default AlgorithmCard;
