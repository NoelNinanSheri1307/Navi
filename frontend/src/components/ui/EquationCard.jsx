import React from "react";
import { GlassCard } from "./GlassCard";

export const EquationCard = ({
  title,
  equation,
  description,
  className = "",
  ...props
}) => {
  return (
    <GlassCard
      className={`border-l-2 border-l-emerald-500/80 flex flex-col gap-3 ${className}`}
      hover={false}
      {...props}
    >
      {title && (
        <span className="text-[10px] uppercase tracking-widest text-zinc-400 font-normal">
          {title}
        </span>
      )}
      <div className="py-4 px-6 my-2 bg-zinc-950/80 border border-zinc-900 rounded-lg overflow-x-auto flex justify-center items-center">
        <code className="text-zinc-100 text-sm font-mono whitespace-nowrap">
          {equation}
        </code>
      </div>
      {description && (
        <p className="text-xs text-zinc-400 leading-relaxed font-normal">
          {description}
        </p>
      )}
    </GlassCard>
  );
};
