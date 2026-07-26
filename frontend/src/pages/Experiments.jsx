import React from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { MetricCard } from "../components/ui/MetricCard";

export const Experiments = () => {
  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Benchmark Trial Suite"
          title="Experiments & Benchmarks"
          description="Standardized multi-run benchmark execution suite enforcing 30-seed runs and statistical hypothesis testing."
        />

        <Callout type="info" title="Scientific Benchmarking Protocol">
          All trials apply equal function evaluation budgets (N_eval = 10,000) and fixed seed vectors. Results will be stored in standardized JSON artifacts.
        </Callout>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard label="Independent Trials" value="30 Runs" description="Fixed random seeds" />
          <MetricCard label="Significance Tests" value="Wilcoxon & Friedman" description="Non-parametric hypothesis tests" />
          <MetricCard label="Experiment Execution Run" available={false} />
        </div>
      </Container>
    </Section>
  );
};
