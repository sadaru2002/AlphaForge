import React from 'react';
import { XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, AreaChart, Area } from 'recharts';
import { TrendingUp, TrendingDown, Clock, Target, Activity } from 'lucide-react';

const Dashboard = ({ signals, stats }) => {
  // Get active/running signal OR the most recent pending signal
  const activeSignal = signals.find(s => s.status === 'ACTIVE') || signals[0];
  
  // Get 2 most recent signals (excluding the active one being displayed)
  const recentSignals = signals
    .filter(s => s.id !== activeSignal?.id)
    .slice(0, 2); // Show 2 most recent signals

  // Process signals for chart
  const chartData = signals.slice(-20).map((signal, index) => ({
    name: `#${index + 1}`,
    entry: signal.entry,
    tp1: signal.tp1,
    sl: signal.stop_loss
  }));

  // Calculate cumulative P&L for area chart
  const pnlData = signals.slice(-20).map((signal, index) => {
    const prevPnl = index > 0 ? chartData[index - 1]?.pnl || 0 : 0;
    const currentPnl = signal.outcome === 'WIN' ? (signal.actual_pnl || 50) : 
                       signal.outcome === 'LOSS' ? (signal.actual_pnl || -25) : 0;
    return {
      name: `#${index + 1}`,
      pnl: prevPnl + currentPnl
    };
  });

  const formatTime = (timestamp) => {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  return (
    <div className="space-y-6">
      {/* Signals Panel */}
      <div className="card card-hover p-6">
        <h2 className="text-h2 text-gradient-green mb-6">📡 Live Signals</h2>
        
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
          {/* Current Running Signal Card */}
          <div>
            <h3 className="text-h4 mb-4 text-text-primary flex items-center gap-2">
              <Activity size={20} className="text-accent-primary animate-pulse" />
              Current Signal
            </h3>
            {activeSignal ? (
              <div className="bg-gradient-to-br from-accent-primary/10 to-transparent border border-accent-primary/30 rounded-lg p-6 relative overflow-hidden">
                {/* Animated pulse effect */}
                <div className="absolute top-0 right-0 w-32 h-32 bg-accent-primary/10 rounded-full blur-3xl animate-pulse"></div>
                
                <div className="relative z-10">
                  {/* Header */}
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center gap-3">
                      <span className="text-h2 font-bold text-text-primary">{activeSignal.symbol}</span>
                      <span className={`flex items-center gap-1 px-3 py-1 rounded-full text-small font-semibold ${
                        activeSignal.direction === 'BUY' 
                          ? 'bg-accent-primary/20 text-accent-primary' 
                          : 'bg-accent-danger/20 text-accent-danger'
                      }`}>
                        {activeSignal.direction === 'BUY' ? <TrendingUp size={14} /> : <TrendingDown size={14} />}
                        {activeSignal.direction}
                      </span>
                    </div>
                    <span className="px-3 py-1 bg-yellow-500/20 text-yellow-400 rounded text-small font-semibold flex items-center gap-1">
                      <Clock size={14} />
                      LIVE
                    </span>
                  </div>

                  {/* Price Levels */}
                  <div className="space-y-3 mb-4">
                    <div className="flex justify-between items-center">
                      <span className="text-small text-text-secondary">Entry Price</span>
                      <span className="text-body font-mono font-semibold text-text-primary">
                        {activeSignal.entry_price?.toFixed(5) || activeSignal.entry?.toFixed(5)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-small text-text-secondary flex items-center gap-1">
                        <Target size={14} className="text-accent-primary" />
                        Take Profit
                      </span>
                      <span className="text-body font-mono font-semibold text-accent-primary">
                        {activeSignal.tp1?.toFixed(5)}
                      </span>
                    </div>
                    <div className="flex justify-between items-center">
                      <span className="text-small text-text-secondary flex items-center gap-1">
                        <Target size={14} className="text-accent-danger" />
                        Stop Loss
                      </span>
                      <span className="text-body font-mono font-semibold text-accent-danger">
                        {activeSignal.stop_loss?.toFixed(5)}
                      </span>
                    </div>
                  </div>

                  {/* Meta Info */}
                  <div className="pt-3 border-t border-border-subtle">
                    <div className="flex justify-between text-small">
                      <span className="text-text-muted">Started: {formatTime(activeSignal.entry_time || activeSignal.timestamp)}</span>
                      <span className="text-text-muted">R:R {activeSignal.rr_ratio || '1:2'}</span>
                    </div>
                  </div>
                </div>
              </div>
            ) : (
              <div className="bg-bg-elevated border border-border-subtle rounded-lg p-8 text-center">
                <Activity size={48} className="mx-auto mb-3 text-text-muted opacity-50" />
                <p className="text-body text-text-secondary">No active signal</p>
                <p className="text-small text-text-muted mt-1">Waiting for next opportunity...</p>
              </div>
            )}
          </div>

          {/* Recent Signals List */}
          <div>
            <h3 className="text-h4 mb-4 text-text-primary">Recent Signals</h3>
            {recentSignals.length > 0 ? (
              <div className="bg-bg-elevated rounded-lg p-4 space-y-3 max-h-[400px] overflow-y-auto">
                {recentSignals.map((signal, index) => (
                  <div
                    key={signal.id}
                    className="flex items-center gap-3 p-3 bg-bg-main rounded-lg hover:bg-bg-hover transition-smooth cursor-pointer border border-transparent hover:border-border-subtle"
                  >
                    {/* Number Badge */}
                    <div className="flex-shrink-0 w-8 h-8 rounded-full bg-accent-primary/20 text-accent-primary flex items-center justify-center font-bold text-small">
                      {index + 1}
                    </div>

                    {/* Signal Info */}
                    <div className="flex-1 min-w-0">
                      <div className="flex items-center gap-2 mb-1">
                        <span className="font-semibold text-text-primary">{signal.symbol}</span>
                        <span className={`text-small ${signal.direction === 'BUY' ? 'text-accent-primary' : 'text-accent-danger'}`}>
                          {signal.direction}
                        </span>
                        <span className="text-tiny text-text-muted">
                          {formatTime(signal.timestamp)}
                        </span>
                      </div>
                      <div className="flex items-center gap-2 text-small">
                        <span className="text-text-secondary">
                          Entry: {signal.entry?.toFixed(5)}
                        </span>
                      </div>
                      <div className="flex items-center gap-3 text-tiny mt-1">
                        <span className="text-accent-primary">
                          TP: {signal.tp1?.toFixed(5)}
                        </span>
                        <span className="text-accent-danger">
                          SL: {signal.stop_loss?.toFixed(5)}
                        </span>
                      </div>
                    </div>

                    {/* Status Badge */}
                    <div className="flex-shrink-0">
                      {signal.status === 'PENDING' ? (
                        <span className="px-2 py-1 bg-yellow-500/20 text-yellow-400 rounded text-tiny font-semibold">
                          PENDING
                        </span>
                      ) : signal.outcome === 'WIN' ? (
                        <span className="px-2 py-1 bg-accent-primary/20 text-accent-primary rounded text-tiny font-semibold">
                          WIN
                        </span>
                      ) : signal.outcome === 'LOSS' ? (
                        <span className="px-2 py-1 bg-accent-danger/20 text-accent-danger rounded text-tiny font-semibold">
                          LOSS
                        </span>
                      ) : (
                        <span className="px-2 py-1 bg-gray-500/20 text-gray-400 rounded text-tiny font-semibold">
                          {signal.status}
                        </span>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            ) : (
              <div className="bg-bg-elevated border border-border-subtle rounded-lg p-8 text-center">
                <TrendingUp size={48} className="mx-auto mb-3 text-text-muted opacity-50" />
                <p className="text-body text-text-secondary">No recent signals</p>
                <p className="text-small text-text-muted mt-1">Signals will appear here once generated</p>
              </div>
            )}
          </div>
        </div>
      </div>

      {/* Performance Overview */}
      <div className="card card-hover p-6">
      <h2 className="text-h2 text-gradient-green mb-6">Performance Overview</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Statistics Table */}
        <div>
          <h3 className="text-h4 mb-4 text-text-primary">Detailed Statistics</h3>
          <div className="bg-bg-elevated rounded-lg p-6 space-y-4">
            <div className="flex justify-between items-center py-3 border-b border-border-subtle">
              <span className="text-body text-text-secondary">Total Signals</span>
              <span className="text-body-lg font-bold text-text-primary">{stats.total_signals || 0}</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-border-subtle">
              <span className="text-body text-text-secondary">Winning Trades</span>
              <span className="text-body-lg font-bold text-accent-primary">{stats.wins || 0}</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-border-subtle">
              <span className="text-body text-text-secondary">Losing Trades</span>
              <span className="text-body-lg font-bold text-accent-danger">{stats.losses || 0}</span>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-border-subtle">
              <span className="text-body text-text-secondary">Win Rate</span>
              <div className="flex items-center gap-2">
                <span className={`text-body-lg font-bold ${stats.win_rate >= 70 ? 'text-accent-primary' : 'text-accent-warning'}`}>
                  {stats.win_rate || 0}%
                </span>
                {stats.win_rate >= 70 && <span className="text-accent-primary">✓</span>}
              </div>
            </div>
            <div className="flex justify-between items-center py-3 border-b border-border-subtle">
              <span className="text-body text-text-secondary">Profit Factor</span>
              <span className="text-body-lg font-bold text-accent-warning">{stats.profit_factor || 0}</span>
            </div>
            <div className="flex justify-between items-center pt-4">
              <span className="text-body text-text-secondary">Net Profit</span>
              <span className={`text-h3 font-bold ${stats.net_profit >= 0 ? 'text-accent-success' : 'text-accent-danger'}`}>
                ${stats.net_profit || 0}
              </span>
            </div>
          </div>
        </div>

        {/* P&L Chart */}
        <div>
          <h3 className="text-h4 mb-4 text-text-primary">Cumulative P&L</h3>
          <ResponsiveContainer width="100%" height={350}>
            <AreaChart data={pnlData}>
              <defs>
                <linearGradient id="colorPnl" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#7FFF00" stopOpacity={0.5}/>
                  <stop offset="95%" stopColor="#7FFF00" stopOpacity={0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1E293B" />
              <XAxis 
                dataKey="name" 
                stroke="#718096" 
                style={{ fontSize: '12px' }}
              />
              <YAxis 
                stroke="#718096" 
                style={{ fontSize: '12px' }}
              />
              <Tooltip
                contentStyle={{ 
                  backgroundColor: '#131825', 
                  border: '1px solid #1E293B',
                  borderRadius: '8px',
                  color: '#FFFFFF'
                }}
                labelStyle={{ color: '#A0AEC0' }}
              />
              <Area 
                type="monotone" 
                dataKey="pnl" 
                stroke="#7FFF00" 
                strokeWidth={3}
                fillOpacity={1} 
                fill="url(#colorPnl)" 
              />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>
      </div>
    </div>
  );
};

export default Dashboard;

