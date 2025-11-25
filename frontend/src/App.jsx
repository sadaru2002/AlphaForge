import React, { useState, useEffect, useRef } from 'react';
import Dashboard from './components/Dashboard';
import Chart from './components/Chart';
import Stats from './components/Stats';
import Navbar from './components/Navbar';
import Sidebar from './components/Sidebar';
import Toasts from './components/Toasts';
import LivePriceTicker from './components/LivePriceTicker';
import apiService from './services/api';
import './App.css';
import { Routes, Route } from 'react-router-dom';
import Journal from './pages/Journal';
import Analytics from './pages/Analytics';
import Signals from './pages/Signals';

function App() {
  const [signals, setSignals] = useState([]);
  const [stats, setStats] = useState({});
  const [status, setStatus] = useState({});
  const [loading, setLoading] = useState(true);
  const [toasts, setToasts] = useState([]);
  const hasShownConnectionToast = useRef(false);
  const wasBackendOnline = useRef(false);

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
        
        // Get system status
        const statusRes = await apiService.getStatus();
        console.log('System status:', statusRes);
        
        // Set status with clear online indicator
        const isBackendOnline = healthRes.status === 'healthy';
        
        setStatus({
          ...healthRes,
          ...statusRes,
          backend: statusRes.backend || 'online',
          oanda: statusRes.oanda || 'disconnected',
          strategy: statusRes.strategy || 'stopped',
          total_signals_today: statusRes.statistics?.supported_symbols || 0,
          status: healthRes.status || 'unknown',
          live_pricing: healthRes.features?.live_data || 'enabled',
          apis: healthRes.services || {},
          running: isBackendOnline  // Set to true when backend is healthy
        });
        
        // Show success toast only on first connection or when reconnecting after disconnect
        if (isBackendOnline && !hasShownConnectionToast.current) {
          pushToast({
            type: 'success',
            title: 'Backend Connected',
            message: 'Successfully connected to AlphaForge API server'
          });
          hasShownConnectionToast.current = true;
          wasBackendOnline.current = true;
        } else if (isBackendOnline && !wasBackendOnline.current) {
          // Backend reconnected after being offline
          pushToast({
            type: 'success',
            title: 'Backend Reconnected',
            message: 'Connection to AlphaForge API server restored'
          });
          wasBackendOnline.current = true;
        } else if (!isBackendOnline && wasBackendOnline.current) {
          // Backend went offline
          wasBackendOnline.current = false;
        }
        
        // Get today's signals
        const signalsRes = await apiService.getSignals();
        console.log('Signals fetched:', signalsRes);
        
        const allSignals = signalsRes.signals || [];
        setSignals(allSignals);

        // Calculate stats from signals
        const calculatedStats = {
          total_signals: allSignals.length,
          wins: allSignals.filter(s => s.outcome === 'WIN').length,
          losses: allSignals.filter(s => s.outcome === 'LOSS').length,
          win_rate: allSignals.length > 0 
            ? Math.round((allSignals.filter(s => s.outcome === 'WIN').length / allSignals.length) * 100) 
            : 0,
          profit_factor: 2.3,
          net_profit: allSignals.reduce((sum, s) => sum + (s.actual_pnl || 0), 0)
        };
        setStats(calculatedStats);

        setLoading(false);
        console.log('Data fetch completed successfully');
      } catch (error) {
        console.error('Error fetching data:', error);
        
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
      <div className="min-h-screen bg-bg-main flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 border-4 border-accent-primary border-t-transparent rounded-full animate-spin mx-auto mb-4"></div>
          <div className="text-h3 text-text-primary">Loading Dashboard...</div>
          <p className="text-body text-text-muted mt-2">Initializing Trading System</p>
        </div>
      </div>
    );
  }

  const DashboardPage = (
    <div className="flex min-h-screen bg-bg-main">
      {/* Sidebar - Desktop */}
      <Sidebar />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col">
        {/* Top Navbar */}
        <Navbar status={status} />

        {/* Toast Notifications */}
        <Toasts toasts={toasts} remove={removeToast} />

        {/* Main Content */}
        <main className="flex-1 p-6 overflow-y-auto">
          <div className="max-w-7xl mx-auto space-y-6">
            {/* KPI Stats Cards */}
            <section id="stats">
              <Stats stats={stats} todaySignals={status.total_signals_today} />
            </section>

            {/* Live Price Ticker */}
            <LivePriceTicker symbols={['XAUUSD', 'GBPUSD', 'USDJPY']} />

            {/* Dashboard Chart - Full Width */}
            <section id="chart">
              <Chart />
            </section>

            {/* Performance Overview */}
            <Dashboard signals={signals} stats={stats} />
          </div>
        </main>

        {/* Footer */}
        <footer className="bg-bg-card border-t border-border-subtle p-6">
          <div className="max-w-7xl mx-auto text-center">
            <p className="text-body text-text-secondary">
              <span className="text-gradient-green font-bold">AlphaForge</span> Trading System
            </p>
            <p className="text-tiny text-text-muted mt-1">
              Powered by AI • Real-time Analysis • Professional Risk Management
            </p>
          </div>
        </footer>
      </div>
    </div>
  );

  return (
    <Routes>
      <Route path="/signals" element={<Signals />} />
      <Route path="/journal" element={<Journal />} />
      <Route path="/analytics" element={<Analytics />} />
      <Route path="/" element={DashboardPage} />
    </Routes>
  );
}

export default App;

