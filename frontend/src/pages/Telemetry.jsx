import React, { useState, useEffect, useRef } from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { MetricCard } from "../components/ui/MetricCard";
import { InfoPanel } from "../components/ui/InfoPanel";
import { GlassCard } from "../components/ui/GlassCard";
import { WS_BASE_URL } from "../config/api";
import { Signal, Terminal, Activity, TrendingUp, Sliders } from "lucide-react";

export const Telemetry = () => {
  const [socketStatus, setSocketStatus] = useState("DISCONNECTED");
  const [lastPacket, setLastPacket] = useState(null);
  const [historyCount, setHistoryCount] = useState(0);
  const [packetsLog, setPacketsLog] = useState([]);
  
  const [metrics, setMetrics] = useState({
    fitness: 0.0,
    bestFitness: 0.0,
    currentAlgo: "None",
    avgWait: 0.0,
    avgQueue: 0.0,
    pressure: 0.0
  });

  const [fitnessTrend, setFitnessTrend] = useState([]);
  const wsRef = useRef(null);

  useEffect(() => {
    // Connect to WebSocket stream
    const socket = new WebSocket(`${WS_BASE_URL}/simulation/ws`);
    wsRef.current = socket;
    setSocketStatus("CONNECTING");

    socket.onopen = () => {
      setSocketStatus("CONNECTED");
    };

    socket.onmessage = (event) => {
      const msg = JSON.parse(event.data);
      setLastPacket(msg);
      
      const timestamp = new Date().toLocaleTimeString();
      setPacketsLog(prev => [`[${timestamp}] ${JSON.stringify(msg)}`, ...prev].slice(0, 20));
      setHistoryCount(prev => prev + 1);

      if (msg.type === "telemetry") {
        const d = msg.data;
        setMetrics({
          fitness: d.fitness,
          bestFitness: d.best_fitness,
          currentAlgo: d.current_optimizer,
          avgWait: d.avg_wait_time,
          avgQueue: d.avg_queue_length,
          pressure: d.congestion_pressure
        });
        setFitnessTrend(prev => [...prev, d.fitness].slice(-40));
      }
    };

    socket.onerror = () => {
      setSocketStatus("ERROR");
    };

    socket.onclose = () => {
      setSocketStatus("DISCONNECTED");
    };

    return () => {
      if (wsRef.current) wsRef.current.close();
    };
  }, []);

  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8 bg-black">
        <PageHeader
          eyebrow="Real-time Stream"
          title="Telemetry Data Stream"
          description="Live visualization of vehicle arrival queues, departure statistics, and phase timing updates."
        />

        <Callout type={socketStatus === "CONNECTED" ? "success" : "info"} title="WebSocket Telemetry Channel">
          {socketStatus === "CONNECTED" 
            ? "Successfully connected to active uvicorn telemetry server. Streaming live parameters."
            : "Awaiting active simulation run. Start a run inside the simulator page to trigger telemetry streams."
          }
        </Callout>

        {metrics.currentAlgo === "None" && (
          <Callout type="warning" title="No Active Simulation Detected">
            The telemetry stream is currently idle. Please navigate to the Simulation page, select an algorithm, and click "Start" to begin streaming real-time optimization packets.
          </Callout>
        )}

        {/* Status Metrics Row */}
        <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
          <MetricCard 
            label="Socket Connection" 
            value={socketStatus} 
            description={socketStatus === "CONNECTED" ? "Full-duplex channel active" : "Offline / inactive"} 
          />
          <MetricCard 
            label="Stream Packets" 
            value={`${historyCount} Packets`} 
            description="Total updates received" 
          />
          <MetricCard 
            label="Active Optimizer" 
            value={metrics.currentAlgo} 
            description="Current running strategy" 
          />
          <MetricCard 
            label="Centroid Pressure" 
            value={metrics.pressure.toFixed(2)} 
            description="Mean lane queues pressure" 
          />
        </div>

        {/* Live Stream Charts & Metrics console */}
        <div className="grid grid-cols-1 lg:grid-cols-12 gap-8">
          
          {/* Telemetry charts */}
          <div className="lg:col-span-8 flex flex-col gap-6">
            <GlassCard className="flex flex-col gap-4 border-zinc-900" hover={false}>
              <div className="flex items-center gap-2 pb-2 border-b border-zinc-900">
                <TrendingUp size={15} className="text-emerald-400" />
                <span className="text-xs uppercase tracking-widest text-zinc-300 font-bold">
                  Dynamic Convergence Stream
                </span>
              </div>
              
              <div className="h-60 w-full bg-zinc-950 border border-zinc-900 rounded-lg flex items-end justify-center px-4 pt-6 relative overflow-hidden">
                {fitnessTrend.length > 1 ? (
                  <svg className="w-full h-full" viewBox="0 0 100 100" preserveAspectRatio="none">
                    <polyline
                      fill="none"
                      stroke="#10b981"
                      strokeWidth="2.5"
                      points={fitnessTrend.map((v, idx) => {
                        const min = Math.min(...fitnessTrend);
                        const max = Math.max(...fitnessTrend);
                        const x = (idx / (fitnessTrend.length - 1)) * 100;
                        const y = 90 - ((v - min) / (max - min || 1)) * 80;
                        return `${x},${y}`;
                      }).join(" ")}
                    />
                  </svg>
                ) : (
                  <span className="text-xs text-zinc-600 font-normal absolute inset-0 flex items-center justify-center">
                    Awaiting active simulation data updates...
                  </span>
                )}
                <div className="absolute top-2 right-2 text-[10px] font-mono text-zinc-400">
                  Current Fitness: {metrics.fitness.toFixed(5)}
                </div>
              </div>
            </GlassCard>

            <div className="grid grid-cols-1 sm:grid-cols-2 gap-4 text-xs font-normal">
              <GlassCard className="flex flex-col gap-2 border-zinc-900" hover={false}>
                <span className="text-zinc-500 uppercase tracking-wider text-[9px] font-bold block">Mean Wait Delay</span>
                <span className="text-2xl font-bold font-mono text-zinc-200">{metrics.avgWait.toFixed(1)}s</span>
              </GlassCard>
              <GlassCard className="flex flex-col gap-2 border-zinc-900" hover={false}>
                <span className="text-zinc-500 uppercase tracking-wider text-[9px] font-bold block">Average Queue Length</span>
                <span className="text-2xl font-bold font-mono text-zinc-200">{metrics.avgQueue.toFixed(1)}</span>
              </GlassCard>
            </div>
          </div>

          {/* Console logger */}
          <div className="lg:col-span-4 flex flex-col gap-6">
            <GlassCard className="flex-1 flex flex-col gap-3 border-zinc-900 min-h-[360px]" hover={false} padding="sm">
              <div className="flex items-center justify-between border-b border-zinc-900 pb-2 mb-1">
                <div className="flex items-center gap-1.5">
                  <Terminal size={14} className="text-emerald-400" />
                  <span className="text-[9px] uppercase tracking-wider text-zinc-300 font-bold">
                    Socket Packet Logs
                  </span>
                </div>
              </div>
              <div className="flex-1 overflow-y-auto max-h-[350px] pr-1 flex flex-col gap-2.5 custom-scrollbar text-[9px] text-zinc-500 font-mono">
                {packetsLog.map((log, idx) => (
                  <div key={idx} className="flex gap-2">
                    <span className="text-emerald-500 shrink-0">&raquo;</span>
                    <span className="leading-relaxed select-all">{log}</span>
                  </div>
                ))}
                {packetsLog.length === 0 && (
                  <span className="text-zinc-600 block text-center mt-6">
                    Awaiting server telemetry packets...
                  </span>
                )}
              </div>
            </GlassCard>
          </div>

        </div>

        <InfoPanel title="Continuous Observation Model" icon={Signal}>
          Every simulation step records current_fitness, best_fitness, mean_fitness, variance, and active vehicles. This observability profile feeds directly into the telemetry operators.
        </InfoPanel>
      </Container>
    </Section>
  );
};
