import React from "react";
import { Container } from "../components/ui/Container";
import { Section } from "../components/ui/Section";
import { PageHeader } from "../components/ui/PageHeader";
import { Callout } from "../components/ui/Callout";
import { Accordion } from "../components/ui/Accordion";
import { CodeBlock } from "../components/ui/CodeBlock";

export const Documentation = () => {
  const docFaqs = [
    {
      title: "What is Navi Framework?",
      content:
        "Navi is a research platform for optimizing traffic signal timing at road intersections using parameterized Mamdani fuzzy logic and metaheuristic optimization algorithms.",
    },
    {
      title: "Where is the Master Architecture Specification stored?",
      content:
        "The complete technical design specification, 11-layer architecture, ASM blueprint, and scientific benchmarking protocol are documented in docs/architecture_master_blueprint.md.",
    },
    {
      title: "How do I run backend benchmarks?",
      content:
        "Navigate to the backend directory, install requirements via `pip install -r requirements.txt`, and execute `python main.py --fast`.",
    },
    {
      title: "How is the 35-dimensional decision vector structured?",
      content:
        "The 35-dimensional continuous decision vector params ∈ [0, 1]^35 parameterizes 5 antecedent membership functions (7 breakpoints each: Congestion Pressure, Density, Queue Length, Wait Time, Flow Rate).",
    },
  ];

  return (
    <Section>
      <Container size="default" className="flex flex-col gap-8">
        <PageHeader
          eyebrow="Research Specification"
          title="Documentation & Master Blueprint"
          description="Complete developer guide, architectural specifications, and execution instructions for Navi Framework."
        />

        <Callout type="note" title="Master Architecture Document">
          Refer to docs/architecture_master_blueprint.md in the root directory for the complete 11-layer design, ASM specifications, and multi-objective Pareto formulations.
        </Callout>

        <div className="flex flex-col gap-4 mt-2">
          <h3 className="text-lg text-zinc-100 font-normal">Framework Setup & Execution</h3>
          <CodeBlock
            filename="bash (Backend Execution)"
            code={`cd backend\npip install -r requirements.txt\npython main.py --fast`}
          />
        </div>

        <div className="flex flex-col gap-4 mt-4">
          <h3 className="text-lg text-zinc-100 font-normal">Frequently Asked Questions</h3>
          <Accordion items={docFaqs} />
        </div>
      </Container>
    </Section>
  );
};
