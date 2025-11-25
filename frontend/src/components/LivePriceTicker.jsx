import React, { useEffect, useState } from 'react';
import apiService from '../services/api';

const LivePriceTicker = ({ symbols = ['XAUUSD', 'GBPUSD', 'USDJPY'] }) => {
  const [prices, setPrices] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdate, setLastUpdate] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);

  // Calculate price change and direction
  const calculateChange = (currentPrice, previousPrice) => {
    if (!previousPrice || !currentPrice) return { change: 0, direction: 'neutral' };
    
    const change = ((currentPrice.bid - previousPrice.bid) / previousPrice.bid) * 100;
    return {
      change: Math.abs(change),
      direction: change > 0 ? 'up' : change < 0 ? 'down' : 'neutral'
    };
  };

  // Fetch real-time prices from OANDA backend with retry logic
  useEffect(() => {
    const fetchPrices = async () => {
      try {
        setError(null);
        const response = await apiService.getAllPrices();
        
        if (response.prices) {
          // Calculate changes for each symbol
          const updatedPrices = {};
          Object.keys(response.prices).forEach(symbol => {
            const currentPrice = response.prices[symbol];
            const previousPrice = prices[symbol];
            const changeData = calculateChange(currentPrice, previousPrice);
            
            updatedPrices[symbol] = {
              ...currentPrice,
              ...changeData
            };
          });
          
          setPrices(updatedPrices);
          setLastUpdate(new Date());
          setLoading(false);
          setIsConnected(true);
          setRetryCount(0); // Reset retry count on success
          
          // Log data source
          if (response.source === 'OANDA_REAL') {
            console.log('✅ Live prices updated with REAL OANDA data');
          } else {
            console.log('⚠️ Live prices updated with mock data');
          }
        }
      } catch (err) {
        console.error('Error fetching live prices:', err);
        setIsConnected(false);
        setRetryCount(prev => prev + 1);
        
        // Only show error after multiple failures
        if (retryCount >= 2) {
          setError(`Connection issue: ${err.message}`);
        }
        
        setLoading(false);
      }
    };

    // Initial fetch
    fetchPrices();

    // Set up interval for real-time updates (every 3 seconds for better responsiveness)
    const interval = setInterval(fetchPrices, 3000);

    return () => clearInterval(interval);
  }, [prices, retryCount]); // Include retryCount in dependency

  // Format time for display
  const formatTime = (timestamp) => {
    if (!timestamp) return 'N/A';
    const date = new Date(timestamp);
    return date.toLocaleTimeString('en-US', { 
      hour12: false, 
      hour: '2-digit', 
      minute: '2-digit', 
      second: '2-digit' 
    });
  };

  if (loading) {
    return (
      <div className="card border-t-2 border-accent-primary p-0 overflow-hidden">
        <div className="flex items-center justify-center p-8">
          <div className="text-center">
            <div className="w-8 h-8 border-4 border-accent-primary border-t-transparent rounded-full animate-spin mx-auto mb-2"></div>
            <p className="text-small text-text-muted">Connecting to OANDA...</p>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="card border-t-2 border-accent-danger p-0 overflow-hidden">
        <div className="flex items-center justify-center p-8">
          <div className="text-center">
            <div className="text-4xl mb-2">⚠️</div>
            <p className="text-small text-accent-danger">{error}</p>
            <p className="text-tiny text-text-muted mt-2">Check backend connection</p>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="card border-t-2 border-accent-primary p-0 overflow-hidden">
      <div className="flex items-center justify-between bg-bg-elevated px-4 py-2 border-b border-border-subtle">
        <div className="flex items-center gap-2">
          <div className="live-indicator">
            <div className={`live-dot ${isConnected ? 'animate-pulse' : ''}`}></div>
                <span className={`text-tiny font-bold uppercase ${
                  isConnected ? 'text-accent-primary' : 'text-accent-danger'
                }`}>
                  {isConnected ? 'OANDA REAL-TIME' : 'CONNECTING...'}
                </span>

          </div>
          {retryCount > 0 && (
            <span className="text-tiny text-text-muted">
              (Retry: {retryCount})
            </span>
          )}
        </div>
        <div className="flex items-center gap-4">
          <span className="text-small text-text-muted">
            {lastUpdate ? `Updated: ${formatTime(lastUpdate)}` : 'Real-time Prices'}
          </span>
        </div>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-3 divide-y md:divide-y-0 md:divide-x divide-border-subtle">
        {symbols.map((symbol) => {
          const price = prices[symbol];
          if (!price) return null;

          const isPriceUp = price.direction === 'up';
          const isPriceDown = price.direction === 'down';
          const decimals = symbol === 'XAUUSD' ? 2 : 4;

          return (
            <div key={symbol} className="p-6 hover:bg-bg-elevated transition-smooth">
              {/* Symbol and Change */}
              <div className="flex items-center justify-between mb-3">
                <h3 className="text-body-lg font-bold text-text-primary">
                  {symbol}
                </h3>
                <div className={`px-2 py-1 rounded text-tiny font-bold ${
                  isPriceUp ? 'bg-accent-primary/20 text-accent-primary' : 
                  isPriceDown ? 'bg-accent-danger/20 text-accent-danger' :
                  'bg-text-muted/20 text-text-muted'
                }`}>
                  {isPriceUp ? '↗' : isPriceDown ? '↘' : '→'} {price.change.toFixed(2)}%
                </div>
              </div>

              {/* Main Price */}
              <div className={`text-h2 font-mono font-bold mb-2 ${
                isPriceUp ? 'text-accent-primary' : 
                isPriceDown ? 'text-accent-danger' : 
                'text-text-primary'
              }`}>
                {price.bid.toFixed(decimals)}
              </div>

              {/* Bid/Ask */}
              <div className="flex items-center gap-4 text-small mb-2">
                <div>
                  <span className="text-text-muted">Bid: </span>
                  <span className="text-text-primary font-mono">
                    {price.bid.toFixed(decimals)}
                  </span>
                </div>
                <div>
                  <span className="text-text-muted">Ask: </span>
                  <span className="text-text-primary font-mono">
                    {price.ask.toFixed(decimals)}
                  </span>
                </div>
              </div>

              {/* Spread and Volume */}
              <div className="flex items-center justify-between text-tiny text-text-muted">
                <div>
                  Spread: {price.spreadPips.toFixed(1)} pips
                </div>
                <div>
                  Vol: {price.volume?.bid ? `${(price.volume.bid / 1000).toFixed(0)}K` : 'N/A'}
                </div>
              </div>

              {/* Data Source */}
              <div className="mt-2 text-tiny text-text-muted">
                Source: OANDA • {formatTime(price.time)}
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default LivePriceTicker;
