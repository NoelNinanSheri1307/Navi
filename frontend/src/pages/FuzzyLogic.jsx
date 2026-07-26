import React from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { MetricCard } from "../components/ui/MetricCard";

export const FuzzyLogic = () => {
  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Mamdani Inference Engine"
          title="Fuzzy Logic System"
          description="Parameterized Mamdani fuzzy inference system mapping 5 antecedent variables to green-time signal duration output."
        />

        <Callout type="info" title="Antecedent Membership Functions">
          Antecedent membership functions (Congestion Pressure, Density, Queue Length, Wait Time, Flow Rate) are parameterized by 35 continuous breakpoints in [0, 1].
        </Callout>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard label="Mamdani Rules" value="9 Rules" description="Linguistic decision matrix" />
          <MetricCard label="Defuzzification" value="Centroid Method" description="Center of area calculation" />
          <MetricCard label="Live Firing Inspector" available={false} />
        </div>
      </Container>
    </Section>
  );
};
