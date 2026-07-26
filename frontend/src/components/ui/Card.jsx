import React from "react";

export const Card = ({
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
      className={`bg-zinc-950/60 border border-zinc-800/80 rounded-xl transition-all duration-200 ${
        hover ? "hover:border-zinc-700 hover:bg-zinc-900/40" : ""
      } ${paddings[padding]} ${className}`}
      {...props}
    >
      {children}
    </div>
  );
};
