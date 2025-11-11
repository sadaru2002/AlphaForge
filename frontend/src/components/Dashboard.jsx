import React from 'react';

const Dashboard = ({ signals, stats }) => {
  // Get active/running signal OR pending signal
  const activeSignal = signals.find(s => s.status === 'ACTIVE') || signals.find(s => s.status === 'PENDING');
  
  // Get 2 most recent signals
  const recentSignals = signals.slice(0, 2);

  const formatTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { hour: '2-digit', minute: '2-digit' });
  };

  return (
    <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
      {/* Live Signal */}
      <div className="bg-bg-card border border-border-subtle rounded-lg p-6">
        <h3 className="text-h4 font-semibold text-text-primary mb-4">🔴 Live Signal</h3>
        {activeSignal ? (
          <div className="space-y-3">
            <div className="flex justify-between">
              <span className="text-text-secondary">Symbol</span>
              <span className="font-semibold text-text-primary">{activeSignal.symbol}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Direction</span>
              <span className={`font-semibold ${activeSignal.direction === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                {activeSignal.direction}
              </span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">Entry</span>
              <span className="font-semibold text-text-primary">{activeSignal.entry?.toFixed(5)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">TP</span>
              <span className="font-semibold text-green-400">{activeSignal.take_profit?.toFixed(5)}</span>
            </div>
            <div className="flex justify-between">
              <span className="text-text-secondary">SL</span>
              <span className="font-semibold text-red-400">{activeSignal.stop_loss?.toFixed(5)}</span>
            </div>
          </div>
        ) : (
          <p className="text-text-muted">No active signals at the moment</p>
        )}
      </div>

      {/* Recent Signals */}
      <div className="bg-bg-card border border-border-subtle rounded-lg p-6">
        <h3 className="text-h4 font-semibold text-text-primary mb-4">📊 Recent Signals</h3>
        <div className="space-y-3">
          {recentSignals.length > 0 ? (
            recentSignals.map((signal, index) => (
              <div key={signal.id || index} className="flex items-center gap-3 p-3 bg-bg-main rounded-lg">
                <div className="w-8 h-8 rounded-full bg-accent-primary/20 text-accent-primary flex items-center justify-center font-bold">
                  {index + 1}
                </div>
                <div className="flex-1">
                  <div className="flex items-center gap-2 mb-1">
                    <span className="font-semibold text-text-primary">{signal.symbol}</span>
                    <span className={`text-small ${signal.direction === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                      {signal.direction}
                    </span>
                    <span className="text-tiny text-text-muted">{formatTime(signal.timestamp)}</span>
                  </div>
                  <div className="flex items-center gap-2 text-small">
                    <span className="text-text-secondary">Entry: {signal.entry?.toFixed(5)}</span>
                    <span className="text-text-muted">•</span>
                    <span className="text-green-400">TP: {signal.take_profit?.toFixed(5)}</span>
                    <span className="text-text-muted">•</span>
                    <span className="text-red-400">SL: {signal.stop_loss?.toFixed(5)}</span>
                  </div>
                </div>
                <span className={`px-2 py-1 rounded text-tiny font-semibold ${
                  signal.status === 'ACTIVE' ? 'bg-green-500/20 text-green-400' :
                  signal.status === 'PENDING' ? 'bg-yellow-500/20 text-yellow-400' :
                  'bg-gray-500/20 text-gray-400'
                }`}>
                  {signal.status}
                </span>
              </div>
            ))
          ) : (
            <p className="text-text-muted">No recent signals</p>
          )}
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
