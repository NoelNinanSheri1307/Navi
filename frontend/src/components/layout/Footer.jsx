import React from "react";
import { Container } from "../ui/Container";

export const Footer = ({ onNavigate }) => {
  return (
    <footer className="border-t border-zinc-900 bg-[#09090b] py-12 text-xs text-zinc-500 font-normal">
      <Container size="wide">
        <div className="flex flex-col md:flex-row items-start md:items-center justify-between gap-6">
          <div className="flex flex-col gap-1">
            <span className="text-zinc-300 font-normal text-sm">
              Navi — Adaptive Traffic Intelligence Framework
            </span>
            <span>
              Research platform for signal control optimization & fuzzy logic inference.
            </span>
          </div>

          <div className="flex flex-wrap gap-4 text-zinc-400">
            <button onClick={() => onNavigate("home")} className="hover:text-zinc-200 transition-colors">
              Home
            </button>
            <button onClick={() => onNavigate("framework")} className="hover:text-zinc-200 transition-colors">
              Framework
            </button>
            <button onClick={() => onNavigate("traffic-model")} className="hover:text-zinc-200 transition-colors">
              Traffic Model
            </button>
            <button onClick={() => onNavigate("fuzzy-logic")} className="hover:text-zinc-200 transition-colors">
              Fuzzy Logic
            </button>
            <button onClick={() => onNavigate("documentation")} className="hover:text-zinc-200 transition-colors">
              Documentation
            </button>
          </div>
        </div>

        <div className="mt-8 pt-6 border-t border-zinc-900/80 flex items-center justify-between">
          <span>&copy; {new Date().getFullYear()} Navi Framework. All rights reserved.</span>
          <span className="px-2 py-0.5 rounded bg-zinc-900 border border-zinc-800 text-zinc-400">
            v2.0.0-Research
          </span>
        </div>
      </Container>
    </footer>
  );
};
