import React from "react";
import { Card } from "./Card";

export const MetricCard = ({
  label,
  value,
  unit,
  description,
  available = true,
  className = "",
}) => {
  return (
    <Card className={`flex flex-col gap-2 ${className}`}>
      <span className="text-xs text-zinc-400 font-normal">{label}</span>
      {available && value !== undefined && value !== null ? (
        <div className="flex items-baseline gap-1.5 my-1">
          <span className="text-2xl sm:text-3xl text-zinc-100 font-normal tracking-tight">
            {value}
          </span>
          {unit && <span className="text-xs text-zinc-500 font-normal">{unit}</span>}
        </div>
      ) : (
        <div className="my-2 text-xs text-zinc-500 italic bg-zinc-900/60 p-2.5 rounded border border-zinc-800/60">
          No experiment data available.
        </div>
      )}
      {description && (
        <span className="text-xs text-zinc-500 leading-normal">{description}</span>
      )}
    </Card>
  );
};
