import React, { useState, useEffect, useRef, useCallback } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://161.118.218.33:5000/api';

const UltraFastPrice = () => {
  const [price, setPrice] = useState(null);
  const [change, setChange] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());
  const [isUpdating, setIsUpdating] = useState(false);
  const [dataSource, setDataSource] = useState('');
  const [updateCount, setUpdateCount] = useState(0);
  const [errorCount, setErrorCount] = useState(0);
  const [responseTime, setResponseTime] = useState(0);
  const intervalRef = useRef(null);

  const fetchRealPrice = useCallback(async () => {
    try {
      setIsUpdating(true);
      const startTime = Date.now();
      
      const response = await axios.get(`${API_BASE_URL}/price/current`, {
        timeout: 2000, // 2 second timeout
        headers: {
          'Cache-Control': 'no-cache',
          'Pragma': 'no-cache',
          'If-Modified-Since': '0'
        }
      });
      
      const endTime = Date.now();
      const responseTime = endTime - startTime;
      setResponseTime(responseTime);
      
      if (response.data.success) {
        const newPrice = response.data.price;
        const newChange = response.data.change_pips;
        
        // Always update to ensure real-time feel
        setPrice(newPrice.toFixed(5));
        setChange(newChange);
        setLastUpdate(new Date(response.data.timestamp));
        setDataSource(response.data.source || 'Real Market Data');
        setIsConnected(true);
        setUpdateCount(prev => prev + 1);
        setErrorCount(0);
        
        console.log(`🔄 ULTRA-FAST Update #${updateCount + 1}: ${newPrice.toFixed(5)} (${newChange >= 0 ? '+' : ''}${newChange.toFixed(1)} pips) - ${responseTime}ms`);
      } else {
        setIsConnected(false);
        setErrorCount(prev => prev + 1);
        console.error('❌ API Error:', response.data.error);
      }
    } catch (error) {
      setIsConnected(false);
      setErrorCount(prev => prev + 1);
      console.error('❌ Network Error:', error.message);
    } finally {
      setIsUpdating(false);
    }
  }, [updateCount]);

  useEffect(() => {
    // Initial fetch
    fetchRealPrice();

    // ULTRA-FAST updates every 100ms (0.1 seconds) - 10 times per second!
    intervalRef.current = setInterval(fetchRealPrice, 100);

    return () => {
      if (intervalRef.current) {
        clearInterval(intervalRef.current);
      }
    };
  }, [fetchRealPrice]);

  // Force refresh every 3 seconds to prevent stale data
  useEffect(() => {
    const forceRefresh = setInterval(() => {
      console.log('🔄 Force refresh triggered');
      fetchRealPrice();
    }, 3000);

    return () => clearInterval(forceRefresh);
  }, [fetchRealPrice]);

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold text-blue-400">GBP/USD ULTRA-FAST Price</h3>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
          <span className="text-xs text-gray-400">
            {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
          </span>
          {isUpdating && (
            <div className="w-2 h-2 rounded-full bg-yellow-400 animate-pulse"></div>
          )}
        </div>
      </div>
      
      <div className="flex items-center justify-between">
        <div className="text-3xl font-bold text-white">
          {price || '1.27000'}
        </div>
        <div className={`text-lg font-semibold ${change >= 0 ? 'text-green-400' : 'text-red-400'}`}>
          {change >= 0 ? '+' : ''}{change.toFixed(1)} pips
        </div>
      </div>
      
      <div className="text-xs text-gray-400 mt-2">
        <div>Last update: {lastUpdate.toLocaleTimeString()}</div>
        {dataSource && (
          <div className="text-xs text-blue-400 mt-1">
            Source: {dataSource}
          </div>
        )}
        <div className="text-xs text-gray-500 mt-1">
          Updates: {updateCount} | Errors: {errorCount} | Response: {responseTime}ms
        </div>
      </div>
    </div>
  );
};

export default UltraFastPrice;