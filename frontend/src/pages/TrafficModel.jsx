import React from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { MetricCard } from "../components/ui/MetricCard";

export const TrafficModel = () => {
  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Physics Engine"
          title="Traffic Simulation Model"
          description="Microscopic traffic dynamics implementing Greenshields speed-density relations and Webster signal delay formulations."
        />

        <Callout type="info" title="Physics Model Overview">
          The microscopic model simulates 4-lane intersection telemetry over 5-cycle intervals, evaluating arrival queues, departure rates, and speed-density ratios.
        </Callout>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard label="Free Flow Speed" value="60 km/h" description="Theoretical maximum speed" />
          <MetricCard label="Jam Density" value="120 veh/km" description="Maximum congestion density" />
          <MetricCard label="Simulation Execution Output" available={false} />
        </div>
      </Container>
    </Section>
  );
};
