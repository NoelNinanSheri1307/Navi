import React from "react";

export const IconButton = ({
  icon: Icon,
  variant = "outline",
  size = "md",
  className = "",
  disabled = false,
  ...props
}) => {
  const baseStyles =
    "inline-flex items-center justify-center font-normal transition-all duration-200 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed rounded-lg border aspect-square";

  const variants = {
    primary:
      "bg-zinc-100 text-zinc-950 border-zinc-100 hover:bg-white hover:border-white shadow-sm",
    secondary:
      "bg-zinc-900 text-zinc-200 border-zinc-800 hover:bg-zinc-800 hover:border-zinc-700",
    outline:
      "bg-transparent text-zinc-400 border-zinc-800 hover:text-zinc-100 hover:bg-zinc-900/60 hover:border-zinc-700",
    ghost:
      "bg-transparent text-zinc-400 border-transparent hover:text-zinc-100 hover:bg-zinc-900",
  };

  const sizes = {
    sm: "w-8 h-8 p-1.5",
    md: "w-10 h-10 p-2.5",
    lg: "w-12 h-12 p-3.5",
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled}
      {...props}
    >
      <Icon className="w-full h-full shrink-0" />
    </button>
  );
};
