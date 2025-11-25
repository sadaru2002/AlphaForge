
import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'http://localhost:5000/api';

const WebSocketPrice = () => {
  const [price, setPrice] = useState(null);
  const [change, setChange] = useState(0);
  const [isConnected, setIsConnected] = useState(false);
  const [lastUpdate, setLastUpdate] = useState(new Date());

  useEffect(() => {
    // Fetch real price from OANDA via backend API
    const fetchRealPrice = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/price/current`);
        
        if (response.data.success) {
          setPrice(response.data.price.toFixed(5));
          setChange(response.data.change_pips);
          setLastUpdate(new Date(response.data.timestamp));
          setIsConnected(true);
        } else {
          setIsConnected(false);
        }
      } catch (error) {
        console.error('Error fetching price:', error);
        setIsConnected(false);
      }
    };

    // Initial price fetch
    fetchRealPrice();

    // Update price every 500ms for ultra-fast updates
    const interval = setInterval(fetchRealPrice, 500);

    return () => clearInterval(interval);
  }, []);

  return (
    <div className="bg-gray-800 rounded-lg p-4 border border-gray-700">
      <div className="flex items-center justify-between mb-2">
        <h3 className="text-lg font-semibold text-blue-400">GBP/USD Live Price</h3>
        <div className="flex items-center space-x-2">
          <div className={`w-2 h-2 rounded-full ${isConnected ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
          <span className="text-xs text-gray-400">
            {isConnected ? 'CONNECTED' : 'DISCONNECTED'}
          </span>
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
        Last update: {lastUpdate.toLocaleTimeString()}
      </div>
    </div>
  );
};

export default WebSocketPrice;

