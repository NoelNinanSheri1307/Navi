import React from "react";
import { Card } from "./Card";

export const FeatureCard = ({
  icon: Icon,
  title,
  description,
  badge,
  className = "",
  onClick,
}) => {
  return (
    <Card
      className={`flex flex-col gap-3 group text-left ${
        onClick ? "cursor-pointer" : ""
      } ${className}`}
      onClick={onClick}
    >
      <div className="flex items-center justify-between">
        {Icon && (
          <div className="p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300 group-hover:text-emerald-400 group-hover:border-zinc-700 transition-all shrink-0">
            <Icon size={18} strokeWidth={1.75} />
          </div>
        )}
        {badge && (
          <span className="text-[11px] text-emerald-400 bg-emerald-500/10 border border-emerald-500/20 px-2 py-0.5 rounded-full">
            {badge}
          </span>
        )}
      </div>
      <h3 className="text-base text-zinc-100 font-normal tracking-tight mt-1">
        {title}
      </h3>
      <p className="text-xs text-zinc-400 leading-relaxed font-normal">
        {description}
      </p>
    </Card>
  );
};
