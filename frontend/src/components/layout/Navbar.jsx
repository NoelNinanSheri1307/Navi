import React, { useState } from "react";
import { Menu, X, Terminal } from "lucide-react";
import { Container } from "../ui/Container";

export const Navbar = ({ activePage, onNavigate }) => {
  const [mobileOpen, setMobileOpen] = useState(false);

  const navItems = [
    { id: "home", label: "Home" },
    { id: "framework", label: "Framework" },
    { id: "traffic-model", label: "Traffic Model" },
    { id: "fuzzy-logic", label: "Fuzzy Logic" },
    { id: "optimization", label: "Optimization" },
    { id: "simulation", label: "Simulation" },
    { id: "experiments", label: "Experiments" },
    { id: "documentation", label: "Documentation" },
  ];

  const handleNav = (id) => {
    onNavigate(id);
    setMobileOpen(false);
  };

  return (
    <header className="sticky top-0 z-50 bg-[#09090b]/80 backdrop-blur-md border-b border-zinc-800/80">
      <Container size="wide">
        <div className="flex items-center justify-between h-16">
          {/* Brand Logo */}
          <button
            onClick={() => handleNav("home")}
            className="flex items-center gap-2 text-zinc-100 hover:text-white transition-colors"
          >
            <div className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-emerald-400">
              <Terminal size={16} />
            </div>
            <span className="text-base font-normal tracking-tight">Navi</span>
            <span className="text-xs text-zinc-500 font-normal hidden sm:inline-block">
              • Traffic Intelligence
            </span>
          </button>

          {/* Desktop Nav Links */}
          <nav className="hidden lg:flex items-center gap-1">
            {navItems.map((item) => {
              const active = activePage === item.id;
              return (
                <button
                  key={item.id}
                  onClick={() => handleNav(item.id)}
                  className={`px-3 py-1.5 text-xs font-normal transition-all rounded-md ${
                    active
                      ? "text-zinc-100 bg-zinc-800/60"
                      : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900/40"
                  }`}
                >
                  {item.label}
                </button>
              );
            })}
          </nav>

          {/* Mobile Menu Button */}
          <button
            onClick={() => setMobileOpen(!mobileOpen)}
            className="p-2 text-zinc-400 hover:text-zinc-100 lg:hidden rounded-lg hover:bg-zinc-900 transition-colors"
            aria-label="Toggle Navigation Menu"
          >
            {mobileOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
        </div>
      </Container>

      {/* Mobile Drawer */}
      {mobileOpen && (
        <div className="lg:hidden border-b border-zinc-800 bg-zinc-950 px-4 py-4 flex flex-col gap-1 animate-in fade-in slide-in-from-top-2 duration-200">
          {navItems.map((item) => {
            const active = activePage === item.id;
            return (
              <button
                key={item.id}
                onClick={() => handleNav(item.id)}
                className={`px-3 py-2.5 text-sm font-normal text-left transition-all rounded-md ${
                  active
                    ? "text-zinc-100 bg-zinc-800/80 font-normal"
                    : "text-zinc-400 hover:text-zinc-200 hover:bg-zinc-900"
                }`}
              >
                {item.label}
              </button>
            );
          })}
        </div>
      )}
    </header>
  );
};
