import React from "react";
import { Activity, Car, Clock } from "lucide-react";

const HUDPanel = ({ stats = {}, metrics = {}, color = "#10b981" }) => {
  const perfScore = metrics.perfScore ?? "0.0";
  const avgWait = metrics.avg_wait !== undefined ? Number(metrics.avg_wait).toFixed(1) : "0.0";
  const remainingTime = stats.remainingTime !== undefined ? Math.max(0, stats.remainingTime).toFixed(1) : "0.0";

  return (
    <div className="bg-black/60 backdrop-blur-2xl p-4 sm:p-5 lg:p-6 rounded-2xl sm:rounded-3xl border border-white/10 shadow-2xl flex flex-col gap-4 sm:gap-6 w-full xl:w-72 2xl:w-80 shrink-0">
      <div className="flex items-center justify-between border-b border-white/10 pb-3">
        <div className="flex items-center gap-2.5">
          <Activity size={18} style={{ color }} />
          <span className="text-xs uppercase tracking-widest text-white/60 font-bold">Real-Time HUD</span>
        </div>
        <div className="flex items-center gap-1.5 px-2 py-0.5 bg-emerald-500/10 rounded-lg border border-emerald-500/20">
          <div className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
          <span className="text-[10px] font-mono font-bold text-emerald-400">{stats.fps || 60} Hz</span>
        </div>
      </div>

      <div className="grid grid-cols-2 gap-3">
        <MetricItem label="FIS Efficiency" value={perfScore} color={color} icon={<Car size={13} />} sub="%" />
        <MetricItem label="Mean Latency" value={avgWait} color="#f43f5e" icon={<Clock size={13} />} sub="s" />
      </div>

      <div className="flex flex-col gap-3.5 pt-1">
        <LiveStatBar label="Queue Backlog" value={stats.queue || 0} max={15} color="#f59e0b" />
        <LiveStatBar label="Throughput Flux" value={stats.throughput || 0} max={100} color="#10b981" />
        <LiveStatBar label="Active Vehicles" value={stats.activeCars || 0} max={30} color={color} />
      </div>

      <div className="mt-1 text-center border-t border-white/10 pt-3">
        <div className="text-[9px] sm:text-[10px] text-white/40 uppercase tracking-widest mb-0.5">Active Signal Phase</div>
        <div className="text-3xl sm:text-4xl lg:text-5xl font-mono leading-none font-bold" style={{ color }}>
          {remainingTime}
          <span className="text-xs ml-1 text-white/30">s</span>
        </div>
      </div>
    </div>
  );
};

const MetricItem = ({ label, value, color, icon, sub }) => (
  <div className="bg-white/[0.04] p-3 rounded-xl flex flex-col gap-1 border border-white/5 hover:bg-white/[0.07] transition-all">
    <div className="flex items-center gap-1.5 text-white/40">
      {icon}
      <span className="text-[9px] uppercase tracking-widest leading-none">{label}</span>
    </div>
    <div className="flex items-baseline gap-1">
      <span className="text-lg sm:text-xl font-mono font-bold tracking-tight" style={{ color }}>{value}</span>
      <span className="text-[9px] text-white/30">{sub}</span>
    </div>
  </div>
);

const LiveStatBar = ({ label, value, max, color }) => {
  const p = Math.min(100, Math.max(0, (value / max) * 100));
  return (
    <div className="flex flex-col gap-1.5">
      <div className="flex justify-between text-xs items-center">
        <span className="text-white/40 uppercase tracking-wider text-[9px] sm:text-[10px]">{label}</span>
        <span className="text-white/80 font-mono font-bold text-xs" style={{ color }}>{value}</span>
      </div>
      <div className="h-1.5 w-full bg-white/5 rounded-full overflow-hidden border border-white/5">
        <div
          className="h-full transition-all duration-300 rounded-full"
          style={{ background: color, width: `${p}%` }}
        />
      </div>
    </div>
  );
};

export default HUDPanel;
