import React from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { MetricCard } from "../components/ui/MetricCard";

export const Simulation = () => {
  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Interactive Telemetry Inspector"
          title="Traffic Simulation"
          description="Visual simulation container for intersection phase changes and vehicular arrival queues."
        />

        <Callout type="info" title="Simulation Engine Redesign">
          The canvas simulation interface will be rewired to WebSocket telemetry streams from the backend microscopic model in future stages.
        </Callout>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard label="Intersection Lanes" value="4 Lanes" description="North, South, East, West" />
          <MetricCard label="Frame Rate Sync" value="60 FPS" description="Physics update loop" />
          <MetricCard label="Active Simulation Stream" available={false} />
        </div>
      </Container>
    </Section>
  );
};
