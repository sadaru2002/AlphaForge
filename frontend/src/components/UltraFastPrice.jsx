import React, { useState, useEffect, useMemo } from 'react';
import apiService from '../services/api';

const UltraFastPrice = () => {
  const [prices, setPrices] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [retryCount, setRetryCount] = useState(0);
  const [isConnected, setIsConnected] = useState(false);

  const symbols = useMemo(() => ['GBPUSD', 'XAUUSD', 'USDJPY'], []);

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        setError(null);
        
        // Fetch all prices from OANDA backend
        const pricesRes = await apiService.getAllPrices();
        
        if (pricesRes.prices) {
          setPrices(pricesRes.prices);
          setIsConnected(true);
          setRetryCount(0); // Reset retry count on success
        } else {
          throw new Error('Failed to fetch prices from OANDA');
        }
        
        setLoading(false);
      } catch (error) {
        console.error('Error fetching prices:', error);
        setIsConnected(false);
        setRetryCount(prev => prev + 1);
        
        // Only show error after multiple failures
        if (retryCount >= 3) {
          setError(`Connection issue: ${error.message}`);
        }
        
        setLoading(false);
      }
    };

    // Initial fetch
    fetchPrices();

    // Update every 1 second for ultra-fast live prices (increased to reduce load)
    const interval = setInterval(fetchPrices, 1000);

    return () => clearInterval(interval);
  }, [symbols, retryCount]);

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-400 mb-4">Ultra-Fast Live Prices (1s)</h3>
        <div className="text-gray-400">Loading live prices...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-400 mb-4">Ultra-Fast Live Prices (1s)</h3>
        <div className="text-red-400">{error}</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-blue-400 mb-4">Ultra-Fast Live Prices (300ms)</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {symbols.map(symbol => {
          const priceData = prices[symbol];
          if (!priceData) return null;

          return (
            <div key={symbol} className="bg-gray-700 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <span className="text-white font-semibold">{symbol}</span>
                <div className="flex flex-col items-end">
                  <span className={`text-sm ${isConnected ? 'text-green-400' : 'text-red-400'}`}>
                    {isConnected ? 'OANDA Live' : 'Connecting...'}
                  </span>
                  <span className={`text-xs ${isConnected ? 'text-green-500 animate-pulse' : 'text-red-500'}`}>
                    ⚡ 1s
                  </span>
                </div>
              </div>
              <div className="mt-2">
                <div className="text-2xl font-bold text-white">
                  {symbol === 'XAUUSD' ? '$' : ''}{priceData.price?.toFixed(symbol === 'XAUUSD' ? 2 : (symbol.includes('JPY') ? 3 : 5)) || 'N/A'}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  Bid: {priceData.bid?.toFixed(symbol === 'XAUUSD' ? 2 : (symbol.includes('JPY') ? 3 : 5))} | Ask: {priceData.ask?.toFixed(symbol === 'XAUUSD' ? 2 : (symbol.includes('JPY') ? 3 : 5))}
                </div>
                <div className="text-xs text-gray-400 mt-1">
                  Updated: {new Date(priceData.timestamp).toLocaleTimeString()}
                </div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default UltraFastPrice;