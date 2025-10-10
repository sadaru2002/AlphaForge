import React, { useState, useEffect, useMemo } from 'react';
import apiService from '../services/api';

const UltraFastPrice = () => {
  const [prices, setPrices] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  const symbols = useMemo(() => ['GBPUSD', 'XAUUSD', 'USDJPY'], []);

  useEffect(() => {
    const fetchPrices = async () => {
      try {
        setError(null);
        
        // Fetch prices for all symbols
        const pricePromises = symbols.map(symbol => apiService.getPrice(symbol));
        const priceResults = await Promise.allSettled(pricePromises);
        
        const priceData = {};
        priceResults.forEach((result, index) => {
          if (result.status === 'fulfilled') {
            priceData[symbols[index]] = result.value;
          } else {
            console.error(`Failed to fetch price for ${symbols[index]}:`, result.reason);
          }
        });
        
        setPrices(priceData);
        setLoading(false);
      } catch (error) {
        console.error('Error fetching prices:', error);
        setError('Failed to fetch live prices');
        setLoading(false);
      }
    };

    // Initial fetch
    fetchPrices();

    // Update every 10 seconds for live prices
    const interval = setInterval(fetchPrices, 10000);

    return () => clearInterval(interval);
  }, [symbols]);

  if (loading) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-400 mb-4">Live Prices</h3>
        <div className="text-gray-400">Loading live prices...</div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-gray-800 rounded-lg p-6">
        <h3 className="text-lg font-semibold text-blue-400 mb-4">Live Prices</h3>
        <div className="text-red-400">{error}</div>
      </div>
    );
  }

  return (
    <div className="bg-gray-800 rounded-lg p-6">
      <h3 className="text-lg font-semibold text-blue-400 mb-4">Live Prices</h3>
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        {symbols.map(symbol => {
          const priceData = prices[symbol];
          if (!priceData) return null;

          return (
            <div key={symbol} className="bg-gray-700 rounded-lg p-4">
              <div className="flex justify-between items-center">
                <span className="text-white font-semibold">{symbol}</span>
                <span className="text-green-400 text-sm">
                  {priceData.source}
                </span>
              </div>
              <div className="mt-2">
                <div className="text-2xl font-bold text-white">
                  ${priceData.price?.toFixed(5) || 'N/A'}
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