import React from "react";

export const StatusChip = ({
  status = "online",
  label = "Active",
  className = "",
  ...props
}) => {
  const dotColors = {
    online: "bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)]",
    idle: "bg-amber-400 shadow-[0_0_8px_rgba(251,191,36,0.5)]",
    offline: "bg-zinc-600",
    error: "bg-rose-400 shadow-[0_0_8px_rgba(251,113,133,0.5)]",
  };

  return (
    <div
      className={`inline-flex items-center gap-2 px-2.5 py-1 rounded-full bg-zinc-950/60 backdrop-blur-md border border-zinc-800/80 text-[10px] uppercase tracking-widest text-zinc-400 font-normal ${className}`}
      {...props}
    >
      <span className={`w-1.5 h-1.5 rounded-full ${dotColors[status]}`} />
      <span>{label}</span>
    </div>
  );
};
