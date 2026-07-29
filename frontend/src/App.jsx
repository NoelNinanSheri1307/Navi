import React, { useState } from "react";
import { Layout } from "./components/layout/Layout";
import { Home } from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import { Simulation } from "./pages/Simulation";
import { Architecture } from "./pages/Architecture";
import { Algorithms } from "./pages/Algorithms";
import { AsmIntelligence } from "./pages/AsmIntelligence";
import { Telemetry } from "./pages/Telemetry";
import { BenchmarkCenter } from "./pages/BenchmarkCenter";
import { Documentation } from "./pages/Documentation";
import { About } from "./pages/About";

function App() {
  const [activePage, setActivePage] = useState("home");

  const renderPage = () => {
    switch (activePage) {
      case "home":
        return <Home onNavigate={setActivePage} />;
      case "dashboard":
        return <Dashboard onBack={() => setActivePage("home")} />;
      case "simulation":
        return <Simulation />;
      case "architecture":
        return <Architecture />;
      case "algorithms":
        return <Algorithms />;
      case "asm":
        return <AsmIntelligence />;
      case "telemetry":
        return <Telemetry />;
      case "benchmarks":
        return <BenchmarkCenter />;
      case "documentation":
        return <Documentation />;
      case "about":
        return <About />;
      default:
        return <Home onNavigate={setActivePage} />;
    }
  };

  return (
    <Layout activePage={activePage} onNavigate={setActivePage}>
      {renderPage()}
    </Layout>
  );
}

export default App;
