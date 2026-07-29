import React from "react";

export const GlassCard = ({
  children,
  className = "",
  hover = true,
  padding = "md",
  ...props
}) => {
  const paddings = {
    none: "p-0",
    sm: "p-4",
    md: "p-6",
    lg: "p-8",
  };

  return (
    <div
      className={`bg-zinc-950/40 backdrop-blur-md border border-zinc-800/40 rounded-xl transition-all duration-200 ${
        hover ? "hover:border-zinc-700/60 hover:bg-zinc-900/20" : ""
      } ${paddings[padding]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
