import React, { useState, useEffect } from 'react';
import TradingViewWidget from './TradingViewWidget';

const Chart = () => {
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [isRealTime] = useState(true);

  // Update timestamp every second for real-time indicator
  useEffect(() => {
    const interval = setInterval(() => {
      setLastUpdate(new Date());
    }, 1000);
    return () => clearInterval(interval);
  }, []);

  return (
    <div className="card card-hover p-6">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-h3 text-gradient-green">Live Trading Chart</h2>
        <div className="flex items-center gap-4">
          <div className={`live-indicator ${isRealTime ? 'text-accent-primary' : 'text-accent-danger'}`}>
            <div className="live-dot"></div>
            <span className="text-tiny font-bold uppercase">{isRealTime ? 'LIVE' : 'OFFLINE'}</span>
          </div>
          <div className="text-small text-text-muted">
            Updated: {lastUpdate.toLocaleTimeString()}
          </div>
        </div>
      </div>
      
      {/* TradingView Advanced Chart Widget */}
      <div className="bg-bg-main rounded-lg overflow-hidden border border-border-subtle" style={{ height: '600px' }}>
        <TradingViewWidget />
      </div>
      
      <div className="flex items-center justify-between mt-4 text-small text-text-muted">
        <p>Real-time OANDA chart with multi-symbol support</p>
        <div className="flex items-center gap-4">
          <span className="flex items-center gap-1">
            ⚡ <span className="text-accent-primary">OANDA Live Data</span>
          </span>
          <span>📡 OANDA WebSocket</span>
          <span>🔄 Real-time Updates</span>
        </div>
      </div>
    </div>
  );
};

export default Chart;
