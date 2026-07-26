import React from "react";
import { Navbar } from "./Navbar";
import { Footer } from "./Footer";

export const Layout = ({ children, activePage, onNavigate }) => {
  return (
    <div className="min-h-screen flex flex-col bg-[#09090b] text-zinc-100 selection:bg-emerald-500/20 selection:text-emerald-300">
      <Navbar activePage={activePage} onNavigate={onNavigate} />
      <main className="flex-1 w-full">{children}</main>
      <Footer onNavigate={onNavigate} />
    </div>
  );
};
