import React from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { MetricCard } from "../components/ui/MetricCard";
import { InfoPanel } from "../components/ui/InfoPanel";
import { Signal } from "lucide-react";

export const Telemetry = () => {
  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Real-time Stream"
          title="Telemetry Data Stream"
          description="Live visualization of vehicle arrival queues, departure statistics, and phase timing updates."
        />

        <Callout type="info" title="WebSocket Integration">
          This panel is prepared to receive live vehicle and phase timing data streams from the backend simulation model in future phases.
        </Callout>

        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          <MetricCard label="Lanes Streamed" value="4 Lanes" description="Discrete lane telemetries" />
          <MetricCard label="Update Frequency" value="10 Hz" description="Streaming sample rate" />
          <MetricCard label="Active Data Socket" available={false} />
        </div>

        <InfoPanel title="Continuous Observation Model" icon={Signal}>
          Every simulation step records current_fitness, best_fitness, mean_fitness, variance, and active vehicles. This observability profile feeds directly into the telemetry operators.
        </InfoPanel>
      </Container>
    </Section>
  );
};
