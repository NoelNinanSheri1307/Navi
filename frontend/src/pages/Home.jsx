import React from "react";
import { MoveRight, Cpu, ShieldCheck, Activity, Layers, GitBranch, Database, Terminal, FileText, CheckCircle2 } from "lucide-react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { Button } from "../components/ui/Button";
import { FeatureCard } from "../components/ui/FeatureCard";
import { Timeline } from "../components/ui/Timeline";
import { CodeBlock } from "../components/ui/CodeBlock";
import { Callout } from "../components/ui/Callout";
import { ArchitecturePreview } from "../components/ArchitecturePreview";

export const Home = ({ onNavigate }) => {
  const frameworkOverview = [
    {
      icon: Activity,
      title: "Traffic Simulation",
      badge: "Physics Engine",
      description: "Microscopic intersection dynamics applying Greenshields speed-density relations and Webster delay formulations across lane telemetry.",
    },
    {
      icon: ShieldCheck,
      title: "Fuzzy Reasoning",
      badge: "Mamdani FIS",
      description: "9-rule Mamdani inference matrix translating discrete pressure, wait time, queue length, density, and flow inputs into signal phase targets.",
    },
    {
      icon: Cpu,
      title: "Optimization Kernels",
      badge: "Metaheuristics",
      description: "Continuous parameter search via Genetic Algorithm, Particle Swarm, Grey Wolf, Differential Evolution, ACO, and Simulated Annealing.",
    },
    {
      icon: Layers,
      title: "Explainability Engine",
      badge: "Transparent AI",
      description: "Step-by-step transparency exposing antecedent membership activations, rule firing strengths, and centroid defuzzification calculations.",
    },
    {
      icon: GitBranch,
      title: "Fair Benchmarking",
      badge: "Statistical Rigor",
      description: "Strict evaluation budget parity (10,000 evaluations), 30 deterministic seed runs, Wilcoxon tests, and 95% confidence intervals.",
    },
  ];

  const roadmapItems = [
    {
      phase: "Phase 1",
      period: "Q3 2026",
      title: "Architecture Refactoring & Design System",
      description: "Clean modularization of backend layers, local typography enforcement, and mobile-first design system release.",
    },
    {
      phase: "Phase 2",
      period: "Q4 2026",
      title: "Adaptive Strategy Metaheuristic (ASM)",
      description: "Closed-loop feedback strategy selector dynamically allocating computational search budgets based on population diversity.",
    },
    {
      phase: "Phase 3",
      period: "Q1 2027",
      title: "Multi-Objective Pareto Engine",
      description: "NSGA-II non-dominated sorting evaluating non-dominated trade-offs between max throughput and min wait latency.",
    },
    {
      phase: "Phase 4",
      period: "Q2 2027",
      title: "Telemetry Stream API & Telemetry Inspector",
      description: "Real-time WebSocket telemetry streamer and interactive signal phase visualizer for live intersection deployments.",
    },
  ];

  return (
    <div className="w-full text-zinc-100 font-normal">
      {/* Hero Section */}
      <Section className="pt-12 sm:pt-16 md:pt-24 pb-16 border-b border-zinc-900">
        <Container size="default" className="flex flex-col items-start gap-6">
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-xs text-zinc-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>Navi Framework v2.0.0 &bull; Adaptive Traffic Intelligence</span>
          </div>

          <h1 className="text-3xl sm:text-5xl md:text-6xl lg:text-7xl text-zinc-100 tracking-tight leading-[1.1] max-w-4xl">
            Adaptive Traffic Signal Optimization & Fuzzy Intelligence
          </h1>

          <p className="text-sm sm:text-base md:text-lg text-zinc-400 max-w-2xl leading-relaxed">
            Navi is an open research platform bridging discrete vehicular telemetry with continuous Mamdani fuzzy inference to dynamically optimize 4-lane signal timing vectors.
          </p>

          <div className="flex flex-wrap items-center gap-3 pt-2">
            <Button
              variant="primary"
              size="lg"
              icon={MoveRight}
              onClick={() => onNavigate("framework")}
            >
              Explore Framework
            </Button>
            <Button
              variant="outline"
              size="lg"
              icon={FileText}
              onClick={() => onNavigate("documentation")}
            >
              Read Architecture Specification
            </Button>
          </div>
        </Container>
      </Section>

      {/* Framework Overview Section */}
      <Section>
        <Container size="default" className="flex flex-col gap-10">
          <div className="flex flex-col gap-2">
            <span className="text-xs text-emerald-400 tracking-wide">Core Modules</span>
            <h2 className="text-2xl sm:text-3xl text-zinc-100 tracking-tight">
              Framework Capabilities
            </h2>
            <p className="text-sm text-zinc-400 max-w-2xl leading-relaxed">
              Navi provides a modular research architecture designed for reproducible traffic signal timing benchmarks.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 sm:gap-6">
            {frameworkOverview.map((item, idx) => (
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
      <Section className="bg-zinc-950/40">
        <Container size="default" className="flex flex-col gap-10">
          <div className="flex flex-col gap-2">
            <span className="text-xs text-emerald-400 tracking-wide">System Blueprint</span>
            <h2 className="text-2xl sm:text-3xl text-zinc-100 tracking-tight">
              Six-Layer Architecture Preview
            </h2>
            <p className="text-sm text-zinc-400 max-w-2xl leading-relaxed">
              Hover over or select any architectural layer below to inspect its sub-system responsibilities and interfaces.
            </p>
          </div>

          <ArchitecturePreview />
        </Container>
      </Section>

      {/* Research Goals Section */}
      <Section>
        <Container size="default" className="grid grid-cols-1 lg:grid-cols-12 gap-8 items-start">
          <div className="lg:col-span-5 flex flex-col gap-4">
            <span className="text-xs text-emerald-400 tracking-wide">Research Vision</span>
            <h2 className="text-2xl sm:text-3xl text-zinc-100 tracking-tight">
              Objectives & Research Goals
            </h2>
            <p className="text-sm text-zinc-400 leading-relaxed">
              Our research targets continuous signal adaptation under fluctuating congestion pressure using parameter optimization.
            </p>
          </div>

          <div className="lg:col-span-7 flex flex-col gap-4">
            <Callout type="note" title="Reproducible Benchmarks">
              Every optimizer is evaluated across identical evaluation budgets and random seed vectors to ensure scientific validity.
            </Callout>
            <Callout type="info" title="Explainable Signal Phase Decisions">
              Fuzzy inference steps expose exact antecedent membership values and centroid defuzzification calculations.
            </Callout>
          </div>
        </Container>
      </Section>

      {/* Roadmap Preview Section */}
      <Section className="bg-zinc-950/40">
        <Container size="default" className="flex flex-col gap-10">
          <div className="flex flex-col gap-2">
            <span className="text-xs text-emerald-400 tracking-wide">Development Milestone</span>
            <h2 className="text-2xl sm:text-3xl text-zinc-100 tracking-tight">
              Framework Roadmap
            </h2>
            <p className="text-sm text-zinc-400 max-w-2xl leading-relaxed">
              Planned development phases for algorithm integration, adaptive strategy switching, and live telemetry streaming.
            </p>
          </div>

          <Timeline items={roadmapItems} />
        </Container>
      </Section>

      {/* Quick Start & Documentation Code Section */}
      <Section>
        <Container size="default" className="flex flex-col gap-8">
          <div className="flex flex-col gap-2">
            <span className="text-xs text-emerald-400 tracking-wide">CLI & Setup</span>
            <h2 className="text-2xl sm:text-3xl text-zinc-100 tracking-tight">
              Backend Execution Setup
            </h2>
            <p className="text-sm text-zinc-400 max-w-2xl leading-relaxed">
              Execute standard optimization benchmarks or fast diagnostic runs directly from the terminal.
            </p>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <CodeBlock
              filename="bash (Fast Benchmark Diagnostic Run)"
              code={`cd backend\npip install -r requirements.txt\npython main.py --fast`}
            />
            <CodeBlock
              filename="bash (Targeted Algorithm Benchmark)"
              code={`cd backend\npython main.py --algorithms GA PSO DE --iter 50`}
            />
          </div>
        </Container>
      </Section>
    </div>
  );
};
