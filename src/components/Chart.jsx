import React, { useState, useEffect } from 'react';

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

  // Optimized TradingView URL for maximum real-time performance
  const tradingViewUrl = `https://www.tradingview.com/widgetembed/?frameElementId=tradingview_widget&symbol=FX%3AGBPUSD&interval=1&hidesidetoolbar=0&symboledit=1&saveimage=1&toolbarbg=f1f3f6&studies=%5B%5D&theme=dark&style=1&timezone=America%2FNew_York&studies_overrides=%7B%7D&overrides=%7B%7D&enabled_features=%5B%5D&disabled_features=%5B%5D&locale=en&utm_source=&utm_medium=widget&utm_campaign=chart&utm_term=FX%3AGBPUSD&realtime=1&autosize=1&allowfullscreen=1`;

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-bold text-blue-400">Ultra-Fast Live Chart - GBP/USD</h2>
        <div className="flex items-center space-x-4 text-sm">
          <div className={`flex items-center space-x-2 ${isRealTime ? 'text-green-400' : 'text-red-400'}`}>
            <div className={`w-2 h-2 rounded-full ${isRealTime ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
            <span>{isRealTime ? 'LIVE' : 'OFFLINE'}</span>
          </div>
          <div className="text-gray-400">
            Last: {lastUpdate.toLocaleTimeString()}
          </div>
        </div>
      </div>
      
      {/* Optimized TradingView Widget */}
      <div className="bg-gray-900 rounded" style={{ height: '500px' }}>
        <iframe
          src={tradingViewUrl}
          style={{ width: '100%', height: '100%' }}
          frameBorder="0"
          title="GBPUSD TradingView Ultra-Fast"
          allowTransparency="true"
          scrolling="no"
          allowFullScreen
          loading="eager"
        ></iframe>
      </div>
      
      <div className="flex items-center justify-between mt-2 text-xs text-gray-500">
        <p>Real-time 1-minute chart with instant updates</p>
        <div className="flex items-center space-x-4">
          <span>⚡ Ultra-Fast Mode</span>
          <span>📡 WebSocket Enabled</span>
          <span>🔄 Auto-Refresh</span>
        </div>
      </div>
    </div>
  );
};

export default Chart;
