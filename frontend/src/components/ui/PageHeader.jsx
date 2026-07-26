import React from "react";

export const PageHeader = ({
  eyebrow,
  title,
  description,
  actions,
  className = "",
}) => {
  return (
    <div className={`flex flex-col gap-3 pb-8 md:pb-12 border-b border-zinc-900 ${className}`}>
      {eyebrow && (
        <span className="text-xs text-emerald-400 font-normal tracking-wide">
          {eyebrow}
        </span>
      )}
      <div className="flex flex-col md:flex-row md:items-end justify-between gap-4">
        <h1 className="text-2xl sm:text-3xl md:text-4xl text-zinc-100 font-normal tracking-tight leading-tight">
          {title}
        </h1>
        {actions && <div className="flex items-center gap-3 shrink-0">{actions}</div>}
      </div>
      {description && (
        <p className="text-sm sm:text-base text-zinc-400 max-w-3xl leading-relaxed mt-1">
          {description}
        </p>
      )}
    </div>
  );
};
