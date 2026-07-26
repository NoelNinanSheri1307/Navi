import React, { useState, useMemo } from "react";
import Home from "./pages/Home";
import Dashboard from "./pages/Dashboard";
import CustomBackground from "./components/CustomBackground";
import data from "./data/data.json";

function App() {
  const [activePage, setActivePage] = useState("home");
  const [theme, setTheme] = useState({ type: "GA", color: "#10b981" });

  const dataVolume = useMemo(() => {
    if (!Array.isArray(data)) return 0;
    return data.reduce((acc, curr) => acc + (curr.convergence_history?.length || 0), 0);
  }, []);

  const bestPerf = useMemo(() => {
    if (!Array.isArray(data) || data.length === 0) return "0.0";
    const scores = data.map(item => Math.min(100, Math.max(0, (1 - Math.abs(item.fitness || 0)) * 100)));
    return Math.max(...scores).toFixed(1);
  }, []);

  const bgType = activePage === "home" ? "HOME" : theme.type;

  return (
    <div className="bg-black min-h-screen text-white selection:bg-emerald-500/30 selection:text-emerald-400 overflow-x-hidden">
      <CustomBackground type={bgType} color={theme.color} />
      
      {activePage === "home" ? (
        <Home onNavigate={() => setActivePage("dashboard")} dataVolume={dataVolume} bestPerf={bestPerf} />
      ) : (
        <Dashboard onBack={() => setActivePage("home")} onThemeChange={setTheme} />
      )}
    </div>
  );
}

export default App;
