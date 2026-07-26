import React from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { MetricCard } from "../components/ui/MetricCard";

export const Framework = () => {
  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Architecture Specification"
          title="Framework Overview"
          description="Detailed modular architecture of Navi, covering dataset loaders, Mamdani FIS, multi-objective fitness evaluation, and search kernels."
        />

        <Callout type="info" title="Future Integration Stage">
          The framework module definition is established in docs/architecture_master_blueprint.md. Full API and interactive system wiring will be integrated in subsequent phases.
        </Callout>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard label="Fuzzy Rules Count" value="9 Rules" description="Mamdani inference matrix" />
          <MetricCard label="Decision Vector Dimensions" value="35 Dimensions" description="MF Breakpoint continuous space" />
          <MetricCard label="Active Experiments" available={false} />
        </div>
      </Container>
    </Section>
  );
};
