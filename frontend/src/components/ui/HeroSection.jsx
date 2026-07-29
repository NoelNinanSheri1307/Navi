import React from "react";
import { Container } from "./Container";
import { Section } from "./Section";

export const HeroSection = ({
  eyebrow,
  title,
  description,
  actions,
  className = "",
  ...props
}) => {
  return (
    <Section className={`pt-12 sm:pt-16 md:pt-24 pb-16 border-b border-zinc-900 ${className}`} {...props}>
      <Container size="default" className="flex flex-col items-start gap-6">
        {eyebrow && (
          <div className="inline-flex items-center gap-2 px-3 py-1 rounded-full bg-zinc-900 border border-zinc-800 text-xs text-zinc-300">
            <span className="w-2 h-2 rounded-full bg-emerald-400" />
            <span>{eyebrow}</span>
          </div>
        )}

        <h1 className="text-3xl sm:text-5xl md:text-6xl lg:text-7xl text-zinc-100 tracking-tight leading-[1.1] max-w-4xl font-normal">
          {title}
        </h1>

        {description && (
          <p className="text-sm sm:text-base md:text-lg text-zinc-400 max-w-2xl leading-relaxed font-normal">
            {description}
          </p>
        )}

        {actions && (
          <div className="flex flex-wrap items-center gap-3 pt-2">
            {actions}
          </div>
        )}
      </Container>
    </Section>
  );
};
