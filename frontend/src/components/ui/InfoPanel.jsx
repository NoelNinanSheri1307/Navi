import React from "react";
import { Info } from "lucide-react";
import { GlassCard } from "./GlassCard";

export const InfoPanel = ({
  title,
  children,
  icon: Icon = Info,
  className = "",
  ...props
}) => {
  return (
    <GlassCard
      className={`flex items-start gap-4 ${className}`}
      hover={false}
      {...props}
    >
      <div className="p-2 rounded-lg bg-zinc-900 border border-zinc-800 text-zinc-300">
        <Icon size={16} />
      </div>
      <div className="flex-1 flex flex-col gap-1">
        {title && (
          <h4 className="text-sm font-normal tracking-tight text-zinc-100 uppercase">
            {title}
          </h4>
        )}
        <div className="text-xs text-zinc-400 leading-relaxed font-normal">
          {children}
        </div>
      </div>
    </GlassCard>
  );
};
