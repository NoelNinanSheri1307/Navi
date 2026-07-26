import React from "react";

export const Timeline = ({ items = [], className = "" }) => {
  return (
    <div className={`flex flex-col gap-6 relative border-l border-zinc-800 ml-3 sm:ml-4 pl-6 sm:pl-8 ${className}`}>
      {items.map((item, idx) => (
        <div key={idx} className="flex flex-col gap-1.5 relative group">
          <div className="absolute -left-[31px] sm:-left-[39px] top-1 w-3.5 h-3.5 rounded-full bg-zinc-900 border border-zinc-700 group-hover:border-emerald-400 group-hover:bg-emerald-400/20 transition-all" />
          <div className="flex items-center gap-2">
            <span className="text-xs text-emerald-400 font-normal">{item.phase}</span>
            <span className="text-xs text-zinc-500 font-normal">• {item.period}</span>
          </div>
          <h4 className="text-sm text-zinc-200 font-normal tracking-tight">
            {item.title}
          </h4>
          <p className="text-xs text-zinc-400 leading-relaxed max-w-2xl">
            {item.description}
          </p>
        </div>
      ))}
    </div>
  );
};
