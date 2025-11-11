/**
 * Optimized Dashboard Component with React Performance Techniques
 * - Memoization with useMemo
 * - Callback optimization with useCallback
 * - Component memoization with React.memo
 */
import React, { useMemo, useCallback } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { TrendingUp, TrendingDown, Clock, Target, Activity } from 'lucide-react';

const Dashboard = React.memo(({ signals, stats }) => {
  // Memoized signal selectors - only recompute when signals change
  const activeSignal = useMemo(() => 
    signals.find(s => s.status === 'ACTIVE'),
    [signals]
  );
  
  const recentSignals = useMemo(() => 
    signals
      .filter(s => s.status === 'CLOSED')
      .slice(0, 5),
    [signals]
  );

  // Memoized chart data - expensive computation cached
  const chartData = useMemo(() => 
    signals.slice(-20).map((signal, index) => ({
      name: `#${index + 1}`,
      entry: signal.entry,
      tp1: signal.tp1,
      sl: signal.stop_loss
    })),
    [signals]
  );

  // Memoized P&L data with cumulative calculation
  const pnlData = useMemo(() => {
    let cumulative = 0;
    return signals.slice(-20).map((signal, index) => {
      const pnl = signal.outcome === 'WIN' ? (signal.actual_pnl || 50) : 
                   signal.outcome === 'LOSS' ? (signal.actual_pnl || -25) : 0;
      cumulative += pnl;
      return {
        name: `#${index + 1}`,
        pnl: cumulative
      };
    });
  }, [signals]);

  // Memoized time formatter - stable reference
  const formatTime = useCallback((timestamp) => {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  }, []);

  return (
    <div className="space-y-6">
      {/* Signals Panel */}
      <SignalsPanel 
        activeSignal={activeSignal}
        recentSignals={recentSignals}
        formatTime={formatTime}
      />

      {/* Charts Section */}
      <ChartsSection chartData={chartData} pnlData={pnlData} />
    </div>
  );
});

// Memoized sub-component for signals panel
const SignalsPanel = React.memo(({ activeSignal, recentSignals, formatTime }) => (
  <div className="card card-hover p-6">
    <h2 className="text-h2 text-gradient-green mb-6">📡 Live Signals</h2>
    
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Current Signal Card */}
      <CurrentSignalCard signal={activeSignal} formatTime={formatTime} />
      
      {/* Recent Signals List */}
      <RecentSignalsList signals={recentSignals} formatTime={formatTime} />
    </div>
  </div>
));

// Memoized current signal card
const CurrentSignalCard = React.memo(({ signal, formatTime }) => {
  if (!signal) {
    return (
      <div>
        <h3 className="text-h4 mb-4 text-text-primary flex items-center gap-2">
          <Activity size={20} className="text-accent-primary" />
          Current Signal
        </h3>
        <div className="bg-dark-card-secondary border border-dark-border rounded-lg p-8 text-center">
          <Activity size={48} className="mx-auto mb-4 text-text-tertiary opacity-30" />
          <p className="text-text-secondary">No active signal</p>
          <p className="text-small text-text-tertiary mt-2">Waiting for next trading opportunity</p>
        </div>
      </div>
    );
  }

  return (
    <div>
      <h3 className="text-h4 mb-4 text-text-primary flex items-center gap-2">
        <Activity size={20} className="text-accent-primary animate-pulse" />
        Current Signal
      </h3>
      <div className="bg-gradient-to-br from-accent-primary/10 to-transparent border border-accent-primary/30 rounded-lg p-6 relative overflow-hidden">
        <div className="absolute top-0 right-0 w-32 h-32 bg-accent-primary/10 rounded-full blur-3xl animate-pulse"></div>
        
        <div className="relative z-10">
          <div className="flex items-center justify-between mb-4">
            <div className="flex items-center gap-3">
              <span className="text-h2 font-bold text-text-primary">{signal.symbol}</span>
              <span className={`flex items-center gap-1 px-3 py-1 rounded-full text-small font-semibold ${
                signal.direction === 'BUY' 
                  ? 'bg-accent-primary/20 text-accent-primary' 
                  : 'bg-accent-danger/20 text-accent-danger'
              }`}>
                {signal.direction === 'BUY' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                {signal.direction}
              </span>
            </div>
            <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded text-small font-semibold flex items-center gap-1">
              <Clock size={14} />
              LIVE
            </span>
          </div>

          <div className="space-y-3 mb-4">
            <PriceLevel 
              label="Entry Price" 
              value={signal.entry_price?.toFixed(5) || signal.entry?.toFixed(5)} 
            />
            <PriceLevel 
              label="Take Profit" 
              value={signal.tp1?.toFixed(5)}
              icon={<Target size={14} className="text-accent-primary" />}
              className="text-accent-primary"
            />
            <PriceLevel 
              label="Stop Loss" 
              value={signal.stop_loss?.toFixed(5)}
              className="text-accent-danger"
            />
          </div>

          <div className="flex items-center justify-between text-small text-text-secondary pt-3 border-t border-dark-border">
            <span>Started: {formatTime(signal.entry_time)}</span>
            <span className="text-accent-primary font-semibold">
              R:R {signal.rr_ratio || '1:2'}
            </span>
          </div>
        </div>
      </div>
    </div>
  );
});

// Memoized price level component
const PriceLevel = React.memo(({ label, value, icon, className = '' }) => (
  <div className="flex justify-between items-center">
    <span className="text-small text-text-secondary flex items-center gap-1">
      {icon}
      {label}
    </span>
    <span className={`text-body font-mono font-semibold ${className || 'text-text-primary'}`}>
      {value}
    </span>
  </div>
));

// Memoized recent signals list
const RecentSignalsList = React.memo(({ signals, formatTime }) => (
  <div>
    <h3 className="text-h4 mb-4 text-text-primary flex items-center gap-2">
      <TrendingUp size={20} className="text-accent-primary" />
      Recent Signals
    </h3>
    
    {signals.length === 0 ? (
      <div className="bg-dark-card-secondary border border-dark-border rounded-lg p-8 text-center">
        <TrendingUp size={48} className="mx-auto mb-4 text-text-tertiary opacity-30" />
        <p className="text-text-secondary">No recent signals</p>
        <p className="text-small text-text-tertiary mt-2">Closed signals will appear here</p>
      </div>
    ) : (
      <div className="space-y-2 max-h-96 overflow-y-auto custom-scrollbar">
        {signals.map((signal, index) => (
          <SignalListItem 
            key={signal.id} 
            signal={signal} 
            index={index + 1}
            formatTime={formatTime}
          />
        ))}
      </div>
    )}
  </div>
));

// Memoized signal list item
const SignalListItem = React.memo(({ signal, index, formatTime }) => (
  <div className="bg-dark-card-secondary border border-dark-border rounded-lg p-4 hover:border-accent-primary/30 transition-all duration-200">
    <div className="flex items-center gap-4">
      <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent-primary/20 flex items-center justify-center">
        <span className="text-small font-bold text-accent-primary">{index}</span>
      </div>
      
      <div className="flex-1 min-w-0">
        <div className="flex items-center gap-2 mb-1">
          <span className="font-semibold text-text-primary">{signal.symbol}</span>
          <span className={`flex items-center gap-1 text-xs ${
            signal.direction === 'BUY' ? 'text-accent-primary' : 'text-accent-danger'
          }`}>
            {signal.direction === 'BUY' ? <TrendingUp size={12} /> : <TrendingDown size={12} />}
            {signal.direction}
          </span>
        </div>
        <div className="flex items-center gap-2 text-xs text-text-secondary">
          <span>{formatTime(signal.timestamp)}</span>
          <span>•</span>
          <span className="font-mono">
            {signal.entry?.toFixed(5)} → {signal.exit_price?.toFixed(5)}
          </span>
        </div>
      </div>
      
      <div className="flex-shrink-0 text-right">
        <div className={`text-small font-semibold ${
          signal.pips_gained > 0 ? 'text-accent-primary' : 'text-accent-danger'
        }`}>
          {signal.pips_gained > 0 ? '+' : ''}{signal.pips_gained?.toFixed(1)} pips
        </div>
        <span className={`inline-block px-2 py-0.5 rounded text-xs font-semibold mt-1 ${
          signal.outcome === 'WIN' 
            ? 'bg-accent-primary/20 text-accent-primary' 
            : 'bg-accent-danger/20 text-accent-danger'
        }`}>
          {signal.outcome}
        </span>
      </div>
    </div>
  </div>
));

// Memoized charts section
const ChartsSection = React.memo(({ chartData, pnlData }) => (
  <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
    <div className="card p-6">
      <h3 className="text-h3 mb-4 text-gradient-green">📊 Price Levels</h3>
      <ResponsiveContainer width="100%" height={300}>
        <LineChart data={chartData}>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="name" stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
            labelStyle={{ color: '#F3F4F6' }}
          />
          <Legend />
          <Line type="monotone" dataKey="entry" stroke="#10B981" strokeWidth={2} />
          <Line type="monotone" dataKey="tp1" stroke="#3B82F6" strokeWidth={2} />
          <Line type="monotone" dataKey="sl" stroke="#EF4444" strokeWidth={2} />
        </LineChart>
      </ResponsiveContainer>
    </div>

    <div className="card p-6">
      <h3 className="text-h3 mb-4 text-gradient-green">💰 Cumulative P&L</h3>
      <ResponsiveContainer width="100%" height={300}>
        <AreaChart data={pnlData}>
          <defs>
            <linearGradient id="colorPnl" x1="0" y1="0" x2="0" y2="1">
              <stop offset="5%" stopColor="#10B981" stopOpacity={0.3}/>
              <stop offset="95%" stopColor="#10B981" stopOpacity={0}/>
            </linearGradient>
          </defs>
          <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
          <XAxis dataKey="name" stroke="#9CA3AF" />
          <YAxis stroke="#9CA3AF" />
          <Tooltip 
            contentStyle={{ backgroundColor: '#1F2937', border: '1px solid #374151' }}
            labelStyle={{ color: '#F3F4F6' }}
          />
          <Area 
            type="monotone" 
            dataKey="pnl" 
            stroke="#10B981" 
            strokeWidth={2}
            fillOpacity={1} 
            fill="url(#colorPnl)" 
          />
        </AreaChart>
      </ResponsiveContainer>
    </div>
  </div>
));

Dashboard.displayName = 'Dashboard';
SignalsPanel.displayName = 'SignalsPanel';
CurrentSignalCard.displayName = 'CurrentSignalCard';
PriceLevel.displayName = 'PriceLevel';
RecentSignalsList.displayName = 'RecentSignalsList';
SignalListItem.displayName = 'SignalListItem';
ChartsSection.displayName = 'ChartsSection';

export default Dashboard;
