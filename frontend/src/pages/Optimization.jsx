import React from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { MetricCard } from "../components/ui/MetricCard";

export const Optimization = () => {
  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Metaheuristic Search Kernels"
          title="Optimization Algorithms"
          description="Continuous parameter search framework integrating Genetic Algorithm, Particle Swarm, Grey Wolf, Differential Evolution, ACO, and Simulated Annealing."
        />

        <Callout type="info" title="Adaptive Strategy Metaheuristic (ASM)">
          The upcoming ASM module dynamically selects optimization kernels based on real-time population diversity and entropy feedback.
        </Callout>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard label="Search Kernels" value="6 Standard + 1 ASM" description="Continuous space search" />
          <MetricCard label="Function Evaluation Budget" value="10,000 N_eval" description="Strict budget parity" />
          <MetricCard label="Live Convergence Data" available={false} />
        </div>
      </Container>
    </Section>
  );
};
