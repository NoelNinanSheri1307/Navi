import React, { useState } from "react";
import { 
  Home as HomeIcon, 
  LayoutGrid, 
  Play, 
  Layers, 
  Cpu, 
  Zap, 
  Signal, 
  BarChart3, 
  FileText, 
  Info, 
  Search, 
  Menu, 
  X, 
  ChevronRight, 
  Terminal 
} from "lucide-react";
import { Footer } from "./Footer";
import { Container } from "../ui/Container";

export const Layout = ({ children, activePage, onNavigate }) => {
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);

  const navItems = [
    { id: "home", label: "Home", icon: HomeIcon, desc: "Landing Page" },
    { id: "dashboard", label: "Dashboard", icon: LayoutGrid, desc: "Interactive workspace" },
    { id: "simulation", label: "Simulation", icon: Play, desc: "Traffic Inspector" },
    { id: "architecture", label: "Architecture", icon: Layers, desc: "System structure" },
    { id: "algorithms", label: "Algorithms", icon: Cpu, desc: "Search kernels" },
    { id: "asm", label: "ASM Intelligence", icon: Zap, desc: "Adaptive Metaheuristic" },
    { id: "telemetry", label: "Telemetry", icon: Signal, desc: "Data streaming" },
    { id: "benchmarks", label: "Benchmark Center", icon: BarChart3, desc: "Experiment sweeps" },
    { id: "documentation", label: "Documentation", icon: FileText, desc: "APIs & Specifications" },
    { id: "about", label: "About", icon: Info, desc: "Project overview" }
  ];

  const handleNav = (id) => {
    onNavigate(id);
    setMobileSidebarOpen(false);
  };

  const activeItem = navItems.find((item) => item.id === activePage) || navItems[0];

  return (
    <div className="min-h-screen flex bg-[#000000] text-zinc-100 selection:bg-emerald-500/20 selection:text-emerald-300 antialiased">
      {/* Sidebar - Desktop */}
      <aside className="hidden lg:flex flex-col w-64 shrink-0 border-r border-zinc-900 bg-[#09090b]/40 backdrop-blur-xl sticky top-0 h-screen select-none z-30">
        {/* Brand Container */}
        <div className="h-16 flex items-center px-6 border-b border-zinc-900 gap-3">
          <div className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-emerald-400">
            <Terminal size={16} />
          </div>
          <div className="flex flex-col">
            <span className="text-sm font-semibold tracking-tight text-zinc-200">Navi</span>
            <span className="text-[10px] text-zinc-500 uppercase tracking-widest font-medium">Traffic Intelligence</span>
          </div>
        </div>

        {/* Navigation Area */}
        <nav className="flex-1 overflow-y-auto px-4 py-6 flex flex-col gap-1.5 custom-scrollbar">
          <div className="text-[10px] uppercase tracking-widest text-zinc-500 px-3 mb-2 font-semibold">
            Platform Modules
          </div>
          {navItems.map((item) => {
            const active = activePage === item.id;
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => handleNav(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-normal transition-all text-left ${
                  active
                    ? "text-zinc-100 bg-zinc-900/80 border border-zinc-800 shadow-sm"
                    : "text-zinc-400 border border-transparent hover:text-zinc-200 hover:bg-zinc-900/30"
                }`}
              >
                <Icon size={14} className={active ? "text-emerald-400" : "text-zinc-500"} />
                <div className="flex flex-col">
                  <span>{item.label}</span>
                </div>
              </button>
            );
          })}
        </nav>

        {/* Footer info/status */}
        <div className="p-4 border-t border-zinc-900/80 flex items-center justify-between text-[10px] text-zinc-500">
          <span>Engine Status:</span>
          <div className="flex items-center gap-1.5">
            <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse" />
            <span className="text-zinc-400 uppercase tracking-wider">v2.0 Stable</span>
          </div>
        </div>
      </aside>

      {/* Mobile Drawer Backdrop */}
      {mobileSidebarOpen && (
        <div 
          onClick={() => setMobileSidebarOpen(false)}
          className="lg:hidden fixed inset-0 bg-black/60 backdrop-blur-sm z-40 transition-opacity duration-300"
        />
      )}

      {/* Sidebar - Mobile Drawer */}
      <aside className={`lg:hidden fixed top-0 bottom-0 left-0 w-64 bg-[#09090b] border-r border-zinc-900 z-50 transition-transform duration-300 select-none flex flex-col ${
        mobileSidebarOpen ? "translate-x-0" : "-translate-x-full"
      }`}>
        <div className="h-16 flex items-center justify-between px-6 border-b border-zinc-900">
          <div className="flex items-center gap-3">
            <div className="p-1.5 rounded-lg bg-zinc-900 border border-zinc-800 text-emerald-400">
              <Terminal size={16} />
            </div>
            <span className="text-sm font-semibold tracking-tight text-zinc-200">Navi</span>
          </div>
          <button 
            onClick={() => setMobileSidebarOpen(false)}
            className="p-1 rounded-md text-zinc-400 hover:text-zinc-100"
          >
            <X size={18} />
          </button>
        </div>

        <nav className="flex-1 overflow-y-auto px-4 py-6 flex flex-col gap-1.5">
          {navItems.map((item) => {
            const active = activePage === item.id;
            const Icon = item.icon;
            return (
              <button
                key={item.id}
                onClick={() => handleNav(item.id)}
                className={`w-full flex items-center gap-3 px-3 py-2.5 rounded-lg text-xs font-normal transition-all text-left ${
                  active
                    ? "text-zinc-100 bg-zinc-900/80 border border-zinc-800"
                    : "text-zinc-400 border border-transparent hover:text-zinc-200 hover:bg-zinc-900/30"
                }`}
              >
                <Icon size={14} className={active ? "text-emerald-400" : "text-zinc-500"} />
                <span>{item.label}</span>
              </button>
            );
          })}
        </nav>
      </aside>

      {/* Main Container */}
      <div className="flex-1 flex flex-col min-w-0 h-screen overflow-y-auto">
        {/* Top Navbar */}
        <header className="h-16 border-b border-zinc-900 bg-[#09090b]/40 backdrop-blur-xl flex items-center justify-between px-6 sticky top-0 z-20 shrink-0">
          {/* Left section: Hamburger (Mobile) or Breadcrumbs (Desktop) */}
          <div className="flex items-center gap-3">
            <button
              onClick={() => setMobileSidebarOpen(true)}
              className="lg:hidden p-1.5 rounded-lg text-zinc-400 hover:text-zinc-100 hover:bg-zinc-900 transition-colors"
              aria-label="Open Sidebar"
            >
              <Menu size={18} />
            </button>

            {/* Breadcrumbs */}
            <div className="hidden sm:flex items-center gap-1.5 text-xs text-zinc-400">
              <span className="text-zinc-500 font-medium">Navi</span>
              <ChevronRight size={10} className="text-zinc-600" />
              <span className="text-zinc-200 font-medium">{activeItem.label}</span>
            </div>
            {/* Mobile title */}
            <span className="sm:hidden text-xs text-zinc-200 font-medium">{activeItem.label}</span>
          </div>

          {/* Right section: Status */}
          <div className="flex items-center gap-4">

            {/* Telemetry Status Indicator */}
            <div className="flex items-center gap-2 px-2.5 py-1 rounded-full bg-zinc-950 border border-zinc-900 text-[10px] uppercase tracking-wider text-zinc-400">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-400 shadow-[0_0_8px_rgba(52,211,153,0.5)] animate-pulse" />
              <span className="hidden sm:inline">Telemetry Live</span>
            </div>
          </div>
        </header>

        {/* Content Container */}
        <main className="flex-1 w-full flex flex-col min-w-0 bg-[#000000]">
          <div className="flex-1">
            {children}
          </div>
          <Footer onNavigate={handleNav} />
        </main>
      </div>
    </div>
  );
};
