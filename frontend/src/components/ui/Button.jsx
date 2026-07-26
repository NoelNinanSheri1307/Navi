import React from "react";

export const Button = ({
  children,
  variant = "primary",
  size = "md",
  icon: Icon,
  className = "",
  disabled = false,
  ...props
}) => {
  const baseStyles =
    "inline-flex items-center justify-center font-normal transition-all duration-200 focus:outline-none disabled:opacity-50 disabled:cursor-not-allowed rounded-lg border";

  const variants = {
    primary:
      "bg-zinc-100 text-zinc-950 border-zinc-100 hover:bg-white hover:border-white shadow-sm",
    secondary:
      "bg-zinc-900 text-zinc-200 border-zinc-800 hover:bg-zinc-800 hover:border-zinc-700",
    outline:
      "bg-transparent text-zinc-200 border-zinc-800 hover:bg-zinc-900 hover:border-zinc-700",
    ghost:
      "bg-transparent text-zinc-400 border-transparent hover:text-zinc-100 hover:bg-zinc-900",
  };

  const sizes = {
    sm: "text-xs px-3 py-1.5 gap-1.5",
    md: "text-sm px-4 py-2 gap-2",
    lg: "text-base px-5 py-2.5 gap-2.5",
  };

  return (
    <button
      className={`${baseStyles} ${variants[variant]} ${sizes[size]} ${className}`}
      disabled={disabled}
      {...props}
    >
      {Icon && <Icon className="w-4 h-4 shrink-0" />}
      <span>{children}</span>
    </button>
  );
};
