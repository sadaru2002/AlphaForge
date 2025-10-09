import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import SignalCard from './components/SignalCard';
import Chart from './components/Chart';
import Stats from './components/Stats';
import Navbar from './components/Navbar';
import SignalsTable from './components/SignalsTable';
import Toasts from './components/Toasts';
import UltraFastPrice from './components/UltraFastPrice';
import axios from 'axios';
import './App.css';
import { Routes, Route } from 'react-router-dom';
import Journal from './pages/Journal';
import Backtesting from './pages/Backtesting';

const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://161.118.218.33:5000/api';

function App() {
  const [signals, setSignals] = useState([]);
  const [stats, setStats] = useState({});
  const [status, setStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [toasts, setToasts] = useState([]);

  const pushToast = (t) => {
    const id = `${Date.now()}-${Math.random().toString(36).slice(2)}`;
    setToasts((prev) => [...prev, { id, ...t }]);
  };
  const removeToast = (id) => setToasts((prev) => prev.filter((t) => t.id !== id));

  // Fetch data from backend API
  useEffect(() => {
    const fetchData = async () => {
      try {
        // Get latest signals
        const signalsRes = await axios.get(`${API_BASE_URL}/signals/latest`);
        setSignals(signalsRes.data);

        // Get performance stats
        const statsRes = await axios.get(`${API_BASE_URL}/stats`);
        setStats(statsRes.data);

        // Get bot status
        const statusRes = await axios.get(`${API_BASE_URL}/status`);
        setStatus(statusRes.data);

        setLoading(false);
      } catch (error) {
        console.error('Error fetching data:', error);
        // Show toast and ensure UI renders even if initial fetch fails
        pushToast({ type: 'error', title: 'Failed to fetch data', message: 'Backend API is unreachable or returned an error.' });
        setLoading(false);
      }
    };

    // Initial fetch
    fetchData();

    // Auto-refresh every 1 second for ultra-fast updates
    const interval = setInterval(fetchData, 1000);

    return () => clearInterval(interval);
  }, []);

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-900 flex items-center justify-center">
        <div className="text-white text-2xl">Loading Dashboard...</div>
      </div>
    );
  }

  const DashboardPage = (
    <div className="min-h-screen bg-gray-900 text-white">
      <Navbar status={status} />
      <Toasts toasts={toasts} remove={removeToast} />

      {/* Main Content */}
      <main className="container mx-auto p-6">
        {/* Stats Overview */}
        <section id="stats">
          <Stats stats={stats} todaySignals={status.total_signals_today} />
        </section>

        {/* Ultra-Fast Price Display */}
        <div className="mt-6">
          <UltraFastPrice />
        </div>

        {/* Dashboard Grid */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mt-6">
          {/* Left: Chart */}
          <div className="lg:col-span-2">
            <section id="chart">
              <Chart />
            </section>
          </div>

          {/* Right: Recent Signals */}
          <div className="space-y-4">
            <h2 className="text-xl font-bold text-blue-400 mb-4">
              Latest Signals
            </h2>
            {signals.length === 0 ? (
              <div className="bg-gray-800 rounded-lg p-6 text-center text-gray-400">
                No signals yet. Waiting for setup...
              </div>
            ) : (
              signals.map((signal, index) => (
                <SignalCard key={index} signal={signal} />
              ))
            )}
          </div>
        </div>

        {/* Full Dashboard */}
        <div className="mt-6">
          <Dashboard signals={signals} stats={stats} />
        </div>

        {/* Signals Table */}
        <section id="signals" className="mt-6">
          <h2 className="text-xl font-bold text-blue-400 mb-4">Signals Table</h2>
          <SignalsTable signals={signals} />
        </section>
      </main>

      {/* Footer */}
      <footer className="bg-gray-800 border-t border-gray-700 p-4 mt-12">
        <div className="container mx-auto text-center text-gray-400 text-sm">
          <p>GBP/USD Advanced Trading System | Free & Open Source</p>
          <p className="mt-1">
            ⚠️ Trading involves risk. Past performance does not guarantee future
            results.
          </p>
        </div>
      </footer>
    </div>
  );

  return (
    <Routes>
      <Route path="/journal" element={<Journal />} />
      <Route path="/backtesting" element={<Backtesting />} />
      <Route path="/" element={DashboardPage} />
    </Routes>
  );
}

export default App;
