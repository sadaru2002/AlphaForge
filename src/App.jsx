import React, { useState, useEffect } from 'react';
import Dashboard from './components/Dashboard';
import SignalCard from './components/SignalCard';
import Chart from './components/Chart';
import Stats from './components/Stats';
import Navbar from './components/Navbar';
import SignalsTable from './components/SignalsTable';
import Toasts from './components/Toasts';
import UltraFastPrice from './components/UltraFastPrice';
import apiService from './services/api';
import './App.css';
import { Routes, Route } from 'react-router-dom';
import Journal from './pages/Journal';
import Backtesting from './pages/Backtesting';

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
        console.log('Fetching data from backend...');
        
        // Get health status first
        const healthRes = await apiService.health();
        console.log('Health check successful:', healthRes);
        
        setStatus({
          ...healthRes,
          total_signals_today: healthRes.records || 0,
          status: healthRes.status || 'unknown'
        });

        // Get symbols
        const symbolsRes = await apiService.getSymbols();
        console.log('Symbols fetched:', symbolsRes);
        const symbols = symbolsRes.symbols || ['GBPUSD', 'XAUUSD', 'USDJPY'];
        
        // Get signals for all symbols
        const signalsPromises = symbols.map(symbol => apiService.getSignals(symbol));
        const signalsResults = await Promise.allSettled(signalsPromises);
        
        const allSignals = signalsResults
          .map((result, index) => {
            if (result.status === 'fulfilled') {
              return {
                ...result.value,
                symbol: symbols[index],
                timestamp: new Date().toISOString()
              };
            } else {
              console.error(`Failed to fetch signals for ${symbols[index]}:`, result.reason);
              return null;
            }
          })
          .filter(signal => signal !== null);

        console.log('Signals fetched:', allSignals);
        setSignals(allSignals);

        // Calculate stats from signals
        const calculatedStats = {
          total_signals: allSignals.length,
          buy_signals: allSignals.filter(s => s.signal === 'BUY').length,
          sell_signals: allSignals.filter(s => s.signal === 'SELL').length,
          hold_signals: allSignals.filter(s => s.signal === 'HOLD').length,
          avg_confidence: allSignals.reduce((sum, s) => sum + (s.confidence || 0), 0) / allSignals.length || 0
        };
        setStats(calculatedStats);

        setLoading(false);
        console.log('Data fetch completed successfully');
      } catch (error) {
        console.error('Error fetching data:', error);
        
        // Show more specific error message
        let errorMessage = 'Backend API is unreachable or returned an error.';
        if (error.message.includes('Failed to fetch')) {
          errorMessage = 'Cannot connect to backend server. Check if the server is running.';
        } else if (error.message.includes('404')) {
          errorMessage = 'Backend endpoint not found. Check API configuration.';
        } else if (error.message.includes('500')) {
          errorMessage = 'Backend server error. Please try again later.';
        }
        
        pushToast({ 
          type: 'error', 
          title: 'Failed to fetch data', 
          message: errorMessage
        });
        setLoading(false);
      }
    };

    // Initial fetch
    fetchData();

    // Auto-refresh every 30 seconds for live updates
    const interval = setInterval(fetchData, 30000);

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
