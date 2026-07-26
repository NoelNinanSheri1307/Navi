import React, { useState } from "react";
import { Layout } from "./components/layout/Layout";
import { Home } from "./pages/Home";
import { Framework } from "./pages/Framework";
import { TrafficModel } from "./pages/TrafficModel";
import { FuzzyLogic } from "./pages/FuzzyLogic";
import { Optimization } from "./pages/Optimization";
import { Simulation } from "./pages/Simulation";
import { Experiments } from "./pages/Experiments";
import { Documentation } from "./pages/Documentation";

function App() {
  const [activePage, setActivePage] = useState("home");

  const renderPage = () => {
    switch (activePage) {
      case "home":
        return <Home onNavigate={setActivePage} />;
      case "framework":
        return <Framework />;
      case "traffic-model":
        return <TrafficModel />;
      case "fuzzy-logic":
        return <FuzzyLogic />;
      case "optimization":
        return <Optimization />;
      case "simulation":
        return <Simulation />;
      case "experiments":
        return <Experiments />;
      case "documentation":
        return <Documentation />;
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
