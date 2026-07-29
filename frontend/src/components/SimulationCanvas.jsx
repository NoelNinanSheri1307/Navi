import React, { useRef, useEffect, useState } from "react";
import { Play, Pause } from "lucide-react";
import { TrafficSim } from "../simulation/TrafficSim";

const SimulationCanvas = ({ 
  greenTimes = [30, 30, 30, 30], 
  themeColor = "#10b981", 
  onStatsUpdate, 
  pressure = 80, 
  avgSpeed = 2.5,
  speedMultiplier = 1
}) => {
  const canvasRef = useRef(null);
  const simRef = useRef(null);
  const requestRef = useRef();
  const [isPaused, setIsPaused] = useState(false);
  
  const speedRef = useRef(speedMultiplier);
  useEffect(() => {
    speedRef.current = speedMultiplier;
  }, [speedMultiplier]);

  // 1. Initial Instantiation on Canvas mount
  useEffect(() => {
    const canvas = canvasRef.current;
    if (!canvas) return;

    simRef.current = new TrafficSim(canvas, greenTimes, themeColor, pressure, avgSpeed);

    let lastTime = performance.now();
    let frameCounter = 0;

    const loop = (time) => {
      const dt = time - lastTime;
      lastTime = time;

      if (simRef.current) {
        simRef.current.update(dt * speedRef.current);
        simRef.current.draw();
        
        if (frameCounter % 10 === 0 && onStatsUpdate) {
          const currentPhaseDuration = simRef.current.greenTimes[simRef.current.currentLane] || 30;
          const remaining = Math.max(0, currentPhaseDuration - simRef.current.cycleTimer);
          const fps = dt > 0 ? Math.round(1000 / dt) : 60;
          
          onStatsUpdate({
            queue: simRef.current.metrics.queueLength || 0,
            throughput: simRef.current.metrics.throughput || 0,
            activeCars: simRef.current.metrics.activeCars || 0,
            remainingTime: remaining,
            fps: Math.min(60, fps)
          });
        }
      }
      
      frameCounter++;
      requestRef.current = requestAnimationFrame(loop);
    };

    requestRef.current = requestAnimationFrame(loop);
    return () => cancelAnimationFrame(requestRef.current);
  }, []); // Empty dependencies array prevents deletion and resetting of variables!

  // 2. Dynamically apply parameter updates without wiping state
  useEffect(() => {
    if (simRef.current) {
      simRef.current.greenTimes = greenTimes;
      simRef.current.themeColor = themeColor;
      simRef.current.pressure = pressure;
      simRef.current.maxSpeed = Math.max(1.5, Math.min(5.0, avgSpeed));
    }
  }, [greenTimes, themeColor, pressure, avgSpeed]);

  useEffect(() => {
    if (simRef.current) {
      simRef.current.running = !isPaused;
    }
  }, [isPaused]);

  return (
    <div className="relative w-full aspect-[16/10] bg-black rounded-xl sm:rounded-2xl overflow-hidden border border-white/10 shadow-2xl group">
      <canvas
        ref={canvasRef}
        width={800}
        height={500}
        className="w-full h-full object-contain filter brightness-110"
      />
      
      {/* Play / Pause Control Overlay */}
      <div className="absolute inset-0 bg-black/30 opacity-0 group-hover:opacity-100 transition-opacity flex items-center justify-center pointer-events-none">
        <div className="flex gap-4 pointer-events-auto">
          <button 
            onClick={() => setIsPaused(!isPaused)}
            className="w-12 h-12 sm:w-14 sm:h-14 rounded-full bg-white/15 backdrop-blur-xl border border-white/20 flex items-center justify-center hover:bg-white/30 hover:scale-105 transition-all text-white shadow-2xl"
            aria-label={isPaused ? "Resume Simulation" : "Pause Simulation"}
          >
            {isPaused ? <Play size={20} fill="white" /> : <Pause size={20} fill="white" />}
          </button>
        </div>
      </div>

      {/* Floating Status Indicator */}
      <div className="absolute bottom-3 left-3 sm:bottom-4 sm:left-4 flex items-center gap-2 px-2.5 py-1 rounded-full bg-black/60 backdrop-blur-md border border-white/10">
        <div className={`w-2 h-2 rounded-full ${isPaused ? 'bg-amber-400' : 'bg-emerald-400 animate-ping'}`} />
        <span className="text-[9px] sm:text-[10px] uppercase tracking-widest text-white/70">
          {isPaused ? 'Simulation Paused' : 'Telemetry Live'}
        </span>
      </div>
    </div>
  );
};

export default SimulationCanvas;
