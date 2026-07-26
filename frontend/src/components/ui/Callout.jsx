import React from "react";
import { Info, AlertCircle, CheckCircle, Lightbulb } from "lucide-react";

export const Callout = ({
  type = "info",
  title,
  children,
  className = "",
}) => {
  const styles = {
    info: {
      bg: "bg-zinc-900/60 border-zinc-700/80 text-zinc-300",
      icon: Info,
      iconColor: "text-zinc-400",
    },
    note: {
      bg: "bg-emerald-950/30 border-emerald-800/40 text-emerald-200/90",
      icon: Lightbulb,
      iconColor: "text-emerald-400",
    },
    warning: {
      bg: "bg-amber-950/30 border-amber-800/40 text-amber-200/90",
      icon: AlertCircle,
      iconColor: "text-amber-400",
    },
    success: {
      bg: "bg-emerald-950/40 border-emerald-700/50 text-emerald-200",
      icon: CheckCircle,
      iconColor: "text-emerald-400",
    },
  };

  const config = styles[type] || styles.info;
  const Icon = config.icon;

  return (
    <div
      className={`p-4 rounded-lg border-l-2 flex gap-3 text-xs sm:text-sm leading-relaxed ${config.bg} ${className}`}
    >
      <Icon className={`w-4 h-4 shrink-0 mt-0.5 ${config.iconColor}`} />
      <div className="flex flex-col gap-1">
        {title && <span className="font-normal text-zinc-100">{title}</span>}
        <div className="text-zinc-400">{children}</div>
      </div>
    </div>
  );
};
