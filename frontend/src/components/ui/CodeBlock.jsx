import React, { useState } from "react";
import { Copy, Check } from "lucide-react";

export const CodeBlock = ({ code, language = "bash", filename, className = "" }) => {
  const [copied, setCopied] = useState(false);

  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  return (
    <div className={`bg-zinc-950 border border-zinc-800 rounded-xl overflow-hidden ${className}`}>
      {filename && (
        <div className="flex items-center justify-between px-4 py-2 bg-zinc-900/80 border-b border-zinc-800 text-xs text-zinc-400 font-mono">
          <span>{filename}</span>
          <button
            onClick={handleCopy}
            className="flex items-center gap-1 text-zinc-400 hover:text-zinc-200 transition-colors"
          >
            {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
            <span className="text-[11px]">{copied ? "Copied" : "Copy"}</span>
          </button>
        </div>
      )}
      <div className="relative p-4 font-mono text-xs text-zinc-300 overflow-x-auto custom-scrollbar">
        {!filename && (
          <button
            onClick={handleCopy}
            className="absolute top-3 right-3 p-1.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400 hover:text-zinc-200 transition-colors"
            title="Copy code"
          >
            {copied ? <Check size={14} className="text-emerald-400" /> : <Copy size={14} />}
          </button>
        )}
        <pre><code>{code}</code></pre>
      </div>
    </div>
  );
};
