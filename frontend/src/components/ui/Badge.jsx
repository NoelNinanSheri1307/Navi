import React from "react";

export const Badge = ({
  children,
  variant = "zinc",
  className = "",
  ...props
}) => {
  const variants = {
    zinc: "bg-zinc-900/80 text-zinc-300 border-zinc-800/80",
    emerald: "bg-emerald-500/10 text-emerald-400 border-emerald-500/20",
    blue: "bg-blue-500/10 text-blue-400 border-blue-500/20",
    amber: "bg-amber-500/10 text-amber-400 border-amber-500/20",
    rose: "bg-rose-500/10 text-rose-400 border-rose-500/20",
  };

  return (
    <span
      className={`inline-flex items-center px-2 py-0.5 rounded text-[10px] font-normal tracking-wide border uppercase ${variants[variant]} ${className}`}
      {...props}
    >
      {children}
    </span>
  );
};
