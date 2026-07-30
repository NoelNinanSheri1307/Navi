import React from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { InfoPanel } from "../components/ui/InfoPanel";
import { GlassCard } from "../components/ui/GlassCard";
import { Globe } from "lucide-react";
import noelPhoto from "../assets/noel.jpg";

export const About = () => {
  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8 bg-black">
        <PageHeader
          eyebrow="System Context"
          title="About Navi"
          description="Adaptive Traffic Intelligence Framework designed to bridge discrete telemetry with continuous metaheuristic parameter optimizations."
        />

        <Callout type="info" title="Framework Identity">
          Navi is an open research platform designed for reproducible traffic signal timing benchmarks, explainable Mamdani fuzzy logic activations, and adaptive strategy orchestration.
        </Callout>

        <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
          <GlassCard className="flex flex-col gap-3 border-zinc-900" hover={false}>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-250">
              Core Contributions
            </h3>
            <ul className="flex flex-col gap-2.5 text-xs text-zinc-400 leading-relaxed font-normal">
              <li>
                <strong>Reproducible Testbed</strong>: Unified dataset schemas, simulation constraints, and evaluations ensure comparison integrity.
              </li>
              <li>
                <strong>Adaptive Swapping</strong>: Telemetry feedback channels monitor optimization states to route execution to the best strategy.
              </li>
              <li>
                <strong>Centroid Defuzzification</strong>: Decoupled antecedent logic provides step-by-step transparency for phase decisions.
              </li>
            </ul>
          </GlassCard>

          <GlassCard className="flex flex-col gap-3 border-zinc-900" hover={false}>
            <h3 className="text-sm font-semibold uppercase tracking-wider text-zinc-250">
              Project Parameters
            </h3>
            <div className="grid grid-cols-2 gap-4">
              <div>
                <span className="text-[10px] text-zinc-500 uppercase font-medium">Platform</span>
                <p className="text-xs text-zinc-300 font-semibold">Web-Simulation / CLI</p>
              </div>
              <div>
                <span className="text-[10px] text-zinc-500 uppercase font-medium">Optimization Target</span>
                <p className="text-xs text-zinc-300 font-semibold">Signal Timings</p>
              </div>
              <div>
                <span className="text-[10px] text-zinc-500 uppercase font-medium">Antecedents</span>
                <p className="text-xs text-zinc-300 font-semibold">5 Continuous Vars</p>
              </div>
              <div>
                <span className="text-[10px] text-zinc-500 uppercase font-medium">Core Registry</span>
                <p className="text-xs text-zinc-300 font-semibold">6 Optimizers</p>
              </div>
            </div>
          </GlassCard>
        </div>

        {/* About the Developer */}
        <GlassCard className="flex flex-col sm:flex-row items-center gap-6 border-zinc-900" hover={false}>
          <div className="shrink-0">
            <img
              src={noelPhoto}
              alt="Noel Ninan Sheri"
              className="w-28 h-28 sm:w-32 sm:h-32 rounded-full object-cover border-2 border-zinc-700 shadow-lg shadow-emerald-500/10"
            />
          </div>
          <div className="flex flex-col gap-3 text-center sm:text-left">
            <div>
              <h3 className="text-lg font-semibold text-zinc-100 tracking-tight">Noel Ninan Sheri</h3>
              <span className="text-[11px] uppercase tracking-widest text-zinc-500 font-medium">Developer and Researcher</span>
            </div>
            <p className="text-xs text-zinc-400 leading-relaxed font-normal max-w-lg">
              Navi was conceived and built as a hands-on exploration into the intersection of metaheuristic optimization algorithms and fuzzy inference systems. Born from a genuine interest in soft computing, this project serves as both a personal research endeavour and a practical demonstration of how nature-inspired search strategies — Genetic Algorithms, Particle Swarm Optimization, Grey Wolf Optimization, Differential Evolution, Ant Colony Optimization, and Simulated Annealing — can be unified under a single adaptive orchestration framework to solve real-world signal control problems. The goal was never just to build a dashboard, but to understand, implement, and benchmark these algorithms from first principles, and to present the results through a modern, interactive interface that makes the underlying mathematics accessible and verifiable.
            </p>
          </div>
        </GlassCard>

        <InfoPanel title="Research Vision" icon={Globe}>
          Establishing mathematical foundations and practical models for explainable AI in urban traffic management systems.
        </InfoPanel>
      </Container>
    </Section>
  );
};
