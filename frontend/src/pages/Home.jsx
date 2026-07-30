import React from "react";
import { 
  MoveRight, 
  Cpu, 
  ShieldCheck, 
  Activity, 
  Layers, 
  GitBranch, 
  FileText, 
  AlertTriangle,
  Flame,
  Zap,
  CheckCircle,
  HelpCircle,
  Database
} from "lucide-react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { Button } from "../components/ui/Button";
import { FeatureCard } from "../components/ui/FeatureCard";
import { GlassCard } from "../components/ui/GlassCard";
import { Badge } from "../components/ui/Badge";
import { InfoPanel } from "../components/ui/InfoPanel";
import { EquationCard } from "../components/ui/EquationCard";
import { ArchitecturePreview } from "../components/ArchitecturePreview";

export const Home = ({ onNavigate }) => {
  const coreModules = [
    {
      icon: Activity,
      title: "Microscopic Physics Simulation",
      badge: "Traffic Model",
      description: "Lane-level dynamics utilizing Greenshields speed-density relations and Webster formulations to model stochastic delay accumulation."
    },
    {
      icon: ShieldCheck,
      title: "Parameterized Inference Engine",
      badge: "Mamdani FIS",
      description: "A 9-rule linguistic inference matrix defuzzified via centroid calculations, mapping 5 continuous traffic antecedents to phase durations."
    },
    {
      icon: Cpu,
      title: "Metaheuristic Search Kernels",
      badge: "Optimizers",
      description: "Continuous space search using Genetic Algorithm, Particle Swarm, Grey Wolf, Differential Evolution, ACO, and Simulated Annealing."
    },
    {
      icon: Layers,
      title: "Closed-Loop Feedback Orchestrator",
      badge: "ASM Controller",
      description: "Telemetry-driven controller dynamically shifting search strategies based on real-time population diversity and stagnation indices."
    }
  ];

  const algorithms = [
    { name: "GA", desc: "Genetic Algorithm using Simulated Binary Crossover (SBX) and Polynomial Mutation." },
    { name: "PSO", desc: "Particle Swarm Optimization utilizing global best topology and adaptive inertia weights." },
    { name: "GWO", desc: "Grey Wolf Optimizer modeling social dominance hierarchy (alpha, beta, delta) for location updates." },
    { name: "DE", desc: "Differential Evolution applying mutation and crossover on vector differences." },
    { name: "ACO", desc: "Continuous Ant Colony Optimization (ACOR) tracking pheromone probability density functions." },
    { name: "SA", desc: "Simulated Annealing utilizing Boltzmann-driven metropolis acceptance criteria." }
  ];

  return (
    <div className="w-full text-zinc-100 font-normal">
      {/* Hero Section */}
      <Section className="relative overflow-hidden pt-16 sm:pt-24 pb-20 border-b border-zinc-900 bg-gradient-to-b from-zinc-950 via-black to-black">
        {/* Subtle decorative background glow */}
        <div className="absolute top-1/4 left-1/2 -translate-x-1/2 -translate-y-1/2 w-[500px] h-[250px] bg-emerald-500/5 rounded-full blur-[120px] pointer-events-none" />

        <Container size="default" className="flex flex-col items-center text-center gap-6 relative z-10">

          <h1 className="text-4xl sm:text-6xl md:text-7xl text-zinc-100 tracking-tight leading-[1.1] max-w-4xl font-normal">
            Adaptive Traffic Signal Optimization & Fuzzy Intelligence
          </h1>

          <p className="text-sm sm:text-base md:text-lg text-zinc-400 max-w-2xl leading-relaxed">
            An open research platform bridging discrete vehicular telemetry with continuous Mamdani fuzzy inference to dynamically optimize 4-lane traffic signal timings.
          </p>

          <div className="flex flex-wrap items-center justify-center gap-4 pt-4">
            <Button
              variant="primary"
              size="lg"
              icon={MoveRight}
              onClick={() => onNavigate("simulation")}
            >
              Launch Simulator Workspace
            </Button>
            <Button
              variant="outline"
              size="lg"
              icon={FileText}
              onClick={() => onNavigate("documentation")}
            >
              Read Documentation
            </Button>
          </div>
        </Container>
      </Section>

      {/* Problem Statement & Why Existing Systems Fail */}
      <Section className="border-b border-zinc-900 bg-[#000000]">
        <Container size="default" className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-stretch">
          <div className="lg:col-span-6 flex flex-col justify-between gap-6">
            <div className="flex flex-col gap-2">
              <span className="text-xs uppercase tracking-widest text-emerald-400 font-semibold">Context Analysis</span>
              <h2 className="text-2xl sm:text-4xl tracking-tight text-zinc-100">
                The Traffic Signal Optimization Problem
              </h2>
            </div>
            <p className="text-sm text-zinc-400 leading-relaxed">
              Modern urban intersections are highly dynamic, stochastic environments. Classical fixed-time traffic control schedules (such as standard Webster delays) operate under static assumptions, failing to adjust during peak flow variance or sudden localized congestion events. This leads to inefficient cycle lengths, extended delay times, and cascading vehicle queues.
            </p>
            <InfoPanel title="Research Scope" icon={Database}>
              Navi models traffic as a parameterized, multi-variable control problem optimized across a 35-dimensional continuous breakpoint search space.
            </InfoPanel>
          </div>

          <div className="lg:col-span-6">
            <GlassCard className="h-full flex flex-col gap-4 border-rose-500/10 hover:border-rose-500/20" hover={false}>
              <div className="flex items-center gap-2 text-rose-400">
                <AlertTriangle size={18} />
                <span className="text-xs uppercase tracking-widest font-semibold">Why Existing Systems Fail</span>
              </div>
              <ul className="flex flex-col gap-3.5 text-xs text-zinc-400 leading-relaxed">
                <li className="flex gap-2">
                  <span className="text-rose-500 font-bold">•</span>
                  <span><strong>Static Time Constraints</strong>: Incapable of adjusting phase timings when real-world arrival patterns deviate from historic baseline averages.</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-rose-500 font-bold">•</span>
                  <span><strong>Non-Linear Queue Spillback</strong>: Delay scales exponentially as queue length approaches jam density, creating gridlock across intersections.</span>
                </li>
                <li className="flex gap-2">
                  <span className="text-rose-500 font-bold">•</span>
                  <span><strong>Sensor Noise Susceptibility</strong>: Direct threshold switching triggers flickering behaviors when telemetry counts fluctuate rapidly.</span>
                </li>
              </ul>
            </GlassCard>
          </div>
        </Container>
      </Section>

      {/* Why Adaptive Optimization Matters */}
      <Section className="border-b border-zinc-900 bg-zinc-950/20">
        <Container size="default" className="flex flex-col gap-10">
          <div className="flex flex-col gap-2 text-center items-center">
            <span className="text-xs uppercase tracking-widest text-emerald-400 font-semibold">Optimization Core</span>
            <h2 className="text-2xl sm:text-4xl tracking-tight text-zinc-100">
              Why Adaptive Optimization Matters
            </h2>
            <p className="text-sm text-zinc-400 max-w-xl leading-relaxed">
              Transforming signal schedules from fixed loops into self-correcting feedback engines.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
            <GlassCard className="flex flex-col gap-3">
              <span className="text-xs uppercase text-emerald-400 tracking-wider">01. Latency Mitigation</span>
              <h3 className="text-lg text-zinc-100 font-normal">Minimize Vehicle Delay</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                By adjusting green-time vectors based on active lane pressure, average delays per vehicle are reduced by balancing throughput across competing links.
              </p>
            </GlassCard>

            <GlassCard className="flex flex-col gap-3">
              <span className="text-xs uppercase text-emerald-400 tracking-wider">02. Dynamic Resilience</span>
              <h3 className="text-lg text-zinc-100 font-normal">React to Peak Variance</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Ensures the signal timing shifts on-the-fly during high-density surges, keeping major arterial lanes fluid and clear of potential bottlenecking.
              </p>
            </GlassCard>

            <GlassCard className="flex flex-col gap-3">
              <span className="text-xs uppercase text-emerald-400 tracking-wider">03. Emission Reductions</span>
              <h3 className="text-lg text-zinc-100 font-normal">Decrease Stop-and-Go Cycles</h3>
              <p className="text-xs text-zinc-400 leading-relaxed">
                Reduces fuel-consuming idling periods at red lights by coordinating phase green-time allocations with active vehicle flow rates.
              </p>
            </GlassCard>
          </div>
        </Container>
      </Section>

      {/* Navi Overview & Core Features */}
      <Section className="border-b border-zinc-900 bg-[#000000]">
        <Container size="default" className="flex flex-col gap-10">
          <div className="flex flex-col gap-2">
            <span className="text-xs uppercase tracking-widest text-emerald-400 font-semibold">Features</span>
            <h2 className="text-2xl sm:text-4xl tracking-tight text-zinc-100">
              Navi Architecture Modules
            </h2>
            <p className="text-sm text-zinc-400 max-w-2xl leading-relaxed">
              Navi organizes its components into modular modules designed for transparent, reproducible traffic optimization research.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {coreModules.map((item, idx) => (
              <FeatureCard
                key={idx}
                icon={item.icon}
                title={item.title}
                badge={item.badge}
                description={item.description}
              />
            ))}
          </div>
        </Container>
      </Section>

      {/* Architecture Preview Section */}
      <Section className="border-b border-zinc-900 bg-zinc-950/30">
        <Container size="default" className="flex flex-col gap-8">
          <div className="flex flex-col gap-2">
            <span className="text-xs uppercase tracking-widest text-emerald-400 font-semibold">System Blueprint</span>
            <h2 className="text-2xl sm:text-4xl tracking-tight text-zinc-100">
              Six-Layer Architecture Preview
            </h2>
            <p className="text-sm text-zinc-400 max-w-2xl leading-relaxed">
              Inspect the structural boundaries of Navi. Hover or tap on any architectural layer below to examine its sub-system interface.
            </p>
          </div>

          <ArchitecturePreview />
        </Container>
      </Section>

      {/* Algorithms Overview */}
      <Section className="border-b border-zinc-900 bg-[#000000]">
        <Container size="default" className="flex flex-col gap-10">
          <div className="flex flex-col gap-2">
            <span className="text-xs uppercase tracking-widest text-emerald-400 font-semibold">Optimization Engine</span>
            <h2 className="text-2xl sm:text-4xl tracking-tight text-zinc-100">
              Integrated Search Algorithms
            </h2>
            <p className="text-sm text-zinc-400 max-w-2xl leading-relaxed">
              Six metaheuristic search strategies seek optimal parameters in a unified continuous domain, coordinated by the Adaptive Strategy Metaheuristic.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
            {algorithms.map((algo, idx) => (
              <GlassCard key={idx} className="flex flex-col gap-2 border-zinc-900">
                <span className="text-xs font-bold text-emerald-400 uppercase tracking-widest">{algo.name} Kernel</span>
                <p className="text-xs text-zinc-400 leading-relaxed">{algo.desc}</p>
              </GlassCard>
            ))}
          </div>
        </Container>
      </Section>

      {/* Research Contributions */}
      <Section className="border-b border-zinc-900 bg-zinc-950/20">
        <Container size="default" className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-center">
          <div className="lg:col-span-5 flex flex-col gap-4">
            <span className="text-xs uppercase tracking-widest text-emerald-400 font-semibold">Academic Rigor</span>
            <h2 className="text-2xl sm:text-4xl tracking-tight text-zinc-100">
              Research Contributions
            </h2>
            <p className="text-sm text-zinc-400 leading-relaxed font-normal">
              Navi establishes a standardized baseline comparison environment for metaheuristics. Every kernel is bound by strict parameters to prevent experimental bias:
            </p>
            <ul className="flex flex-col gap-2.5 text-xs text-zinc-400">
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span>Strict evaluation parity limit (10,000 N_eval).</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span>Runs conducted over 30 independent deterministic seeds.</span>
              </li>
              <li className="flex items-center gap-2">
                <span className="w-1.5 h-1.5 rounded-full bg-emerald-400" />
                <span>Wilcoxon rank-sum tests with 95% confidence intervals.</span>
              </li>
            </ul>
          </div>

          <div className="lg:col-span-7 flex flex-col gap-4">
            <EquationCard
              title="Soft-clipped Fitness Objective Formulation"
              equation="F = 0.35 * flow_norm + 0.30 * speed_norm - 0.15 * wait_norm - 0.10 * queue_norm - 0.10 * pressure_norm"
              description="Objective weights prioritize throughput and speed while penalizing vehicle queue length, wait latency, and intersection pressure indexes."
            />
          </div>
        </Container>
      </Section>

      {/* Performance Preview */}
      <Section className="border-b border-zinc-900 bg-[#000000]">
        <Container size="default" className="flex flex-col gap-8">
          <div className="flex flex-col gap-2">
            <span className="text-xs uppercase tracking-widest text-emerald-400 font-semibold">Evaluation</span>
            <h2 className="text-2xl sm:text-4xl tracking-tight text-zinc-100">
              Optimization Performance Preview
            </h2>
            <p className="text-sm text-zinc-400 max-w-2xl leading-relaxed">
              Comparison of optimized timings showing significant reductions in wait latency and vehicle queue density compared to baseline schedules.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <GlassCard className="flex flex-col gap-3" hover={false}>
              <div className="flex justify-between items-center text-xs">
                <span className="text-zinc-400 uppercase">Average Latency (Wait Time)</span>
                <span className="text-rose-400 font-bold">-42% Reduction</span>
              </div>
              <div className="flex items-center gap-4 mt-2">
                <div className="flex-1 flex flex-col gap-1">
                  <span className="text-[10px] text-zinc-500 uppercase">Fixed Baseline</span>
                  <div className="h-3 w-full bg-zinc-900 rounded border border-zinc-800 relative">
                    <div className="h-full bg-zinc-600 rounded-sm w-[90%]" />
                  </div>
                </div>
                <div className="flex-1 flex flex-col gap-1">
                  <span className="text-[10px] text-emerald-400 uppercase">Optimized Engine</span>
                  <div className="h-3 w-full bg-zinc-900 rounded border border-zinc-800 relative">
                    <div className="h-full bg-emerald-500 rounded-sm w-[52%]" />
                  </div>
                </div>
              </div>
            </GlassCard>

            <GlassCard className="flex flex-col gap-3" hover={false}>
              <div className="flex justify-between items-center text-xs">
                <span className="text-zinc-400 uppercase">Effective Throughput (Flow Rate)</span>
                <span className="text-emerald-400 font-bold">+28% Increase</span>
              </div>
              <div className="flex items-center gap-4 mt-2">
                <div className="flex-1 flex flex-col gap-1">
                  <span className="text-[10px] text-zinc-500 uppercase">Fixed Baseline</span>
                  <div className="h-3 w-full bg-zinc-900 rounded border border-zinc-800 relative">
                    <div className="h-full bg-zinc-600 rounded-sm w-[60%]" />
                  </div>
                </div>
                <div className="flex-1 flex flex-col gap-1">
                  <span className="text-[10px] text-emerald-400 uppercase">Optimized Engine</span>
                  <div className="h-3 w-full bg-zinc-900 rounded border border-zinc-800 relative">
                    <div className="h-full bg-emerald-500 rounded-sm w-[88%]" />
                  </div>
                </div>
              </div>
            </GlassCard>
          </div>
        </Container>
      </Section>

      {/* Call to Action */}
      <Section className="bg-gradient-to-t from-zinc-950 to-black">
        <Container size="default">
          <GlassCard className="py-12 px-8 flex flex-col items-center text-center gap-6 border-zinc-850" hover={false}>
            <Zap size={28} className="text-emerald-400 animate-pulse" />
            <h2 className="text-2xl sm:text-4xl tracking-tight text-zinc-100">
              Ready to Explore the Signal Optimization Workspace?
            </h2>
            <p className="text-sm text-zinc-400 max-w-xl leading-relaxed">
              Launch the workspace simulator to compare metaheuristics, inspect rule fire dynamics, and run microscopic traffic flow simulations.
            </p>
            <Button
              variant="primary"
              size="lg"
              icon={MoveRight}
              onClick={() => onNavigate("simulation")}
            >
              Launch Simulator Workspace
            </Button>
          </GlassCard>
        </Container>
      </Section>
    </div>
  );
};
