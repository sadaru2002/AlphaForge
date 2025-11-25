import React, { useState, useEffect } from 'react';
import { Activity, Database, Cpu, Brain } from 'lucide-react';
import API_BASE_URL from '../config/api';

const ApiStatus = () => {
  const [status, setStatus] = useState({
    backend: 'unknown',
    oanda: 'unknown',
    gemini: 'unknown',
    database: 'unknown'
  });

  useEffect(() => {
    const fetchStatus = async () => {
      try {
        const response = await fetch(`${API_BASE_URL}/api/status`);
        const data = await response.json();
        setStatus({
          backend: data.backend || 'unknown',
          oanda: data.oanda || 'unknown',
          gemini: data.gemini || 'unknown',
          database: data.database || 'unknown'
        });
      } catch (error) {
        console.error('Error fetching status:', error);
      }
    };

    fetchStatus();
    const interval = setInterval(fetchStatus, 5000); // Update every 5 seconds
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (statusValue) => {
    switch (statusValue) {
      case 'online':
      case 'connected':
      case 'configured':
        return 'bg-green-600';
      case 'disconnected':
      case 'not configured':
        return 'bg-red-600';
      case 'stopped':
        return 'bg-yellow-600';
      default:
        return 'bg-gray-600';
    }
  };

  const getStatusLabel = (statusValue) => {
    switch (statusValue) {
      case 'online':
      case 'connected':
        return 'ACTIVE';
      case 'configured':
        return 'ACTIVE';
      case 'disconnected':
        return 'INACTIVE';
      case 'not configured':
        return 'NOT SET';
      case 'stopped':
        return 'MIXED';
      default:
        return 'UNKNOWN';
    }
  };

  const getStatusDescription = (service, statusValue) => {
    if (service === 'gemini') {
      return statusValue === 'configured' ? 'AI Validation Ready' : 'No API Key';
    }
    if (service === 'oanda') {
      return statusValue === 'connected' ? 'Market Data Live' : 'Not Connected';
    }
    if (service === 'backend') {
      return statusValue === 'online' ? 'Server Running' : 'Offline';
    }
    if (service === 'database') {
      return statusValue === 'connected' ? 'PostgreSQL Active' : 'Disconnected';
    }
    return statusValue;
  };

  return (
    <div className="bg-gray-800 rounded-lg p-4 mb-6">
      <h3 className="text-lg font-semibold text-blue-400 mb-3">API Status</h3>
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
        <div className="bg-gray-700 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <span className="text-white font-medium">Gemini AI</span>
            <span className={`text-xs px-2 py-1 rounded ${getStatusColor(status.gemini)} text-white`}>
              {getStatusLabel(status.gemini)}
            </span>
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {getStatusDescription('gemini', status.gemini)}
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <span className="text-white font-medium">OANDA API</span>
            <span className={`text-xs px-2 py-1 rounded ${getStatusColor(status.oanda)} text-white`}>
              {getStatusLabel(status.oanda)}
            </span>
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {getStatusDescription('oanda', status.oanda)}
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <span className="text-white font-medium">Backend</span>
            <span className={`text-xs px-2 py-1 rounded ${getStatusColor(status.backend)} text-white`}>
              {getStatusLabel(status.backend)}
            </span>
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {getStatusDescription('backend', status.backend)}
          </div>
        </div>

        <div className="bg-gray-700 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <span className="text-white font-medium">Database</span>
            <span className={`text-xs px-2 py-1 rounded ${getStatusColor(status.database)} text-white`}>
              {getStatusLabel(status.database)}
            </span>
          </div>
          <div className="text-xs text-gray-400 mt-1">
            {getStatusDescription('database', status.database)}
          </div>
        </div>
      </div>
    </div>
  );
};

export default ApiStatus;
