import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

const ProcessingStatusPanel = () => {
  const [status, setStatus] = useState({
    backend: 'checking',
    oanda: 'checking',
    strategy: 'idle'
  });

  useEffect(() => {
    const checkStatus = async () => {
      try {
        const health = await apiService.health();
        setStatus({
          backend: health.status === 'healthy' ? 'online' : 'offline',
          oanda: health.status === 'healthy' ? 'connected' : 'disconnected',
          strategy: 'ready'
        });
      } catch (error) {
        setStatus({
          backend: 'offline',
          oanda: 'disconnected',
          strategy: 'stopped'
        });
      }
    };

    checkStatus();
    const interval = setInterval(checkStatus, 5000);
    return () => clearInterval(interval);
  }, []);

  const getStatusColor = (st) => {
    if (st === 'online' || st === 'connected' || st === 'ready') return 'text-green-400';
    if (st === 'offline' || st === 'disconnected' || st === 'stopped') return 'text-red-400';
    if (st === 'checking' || st === 'idle') return 'text-yellow-400';
    return 'text-gray-400';
  };

  const getStatusIcon = (st) => {
    if (st === 'online' || st === 'connected' || st === 'ready') return '';
    if (st === 'offline' || st === 'disconnected' || st === 'stopped') return '';
    if (st === 'checking') return '';
    return '';
  };

  return (
    <div className="card card-hover p-6">
      <div className="flex items-center gap-3 mb-6">
        <div className={`w-3 h-3 rounded-full ${status.backend === 'online' ? 'bg-green-400 animate-pulse' : 'bg-red-400'}`}></div>
        <h2 className="text-h3 text-gradient-purple">System Status</h2>
      </div>
      <div className="grid grid-cols-1 gap-4">
        <div className="bg-dark-100/50 border border-dark-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{getStatusIcon(status.backend)}</span>
            <div>
              <p className="text-sm text-gray-400">Backend Server</p>
              <p className={`text-lg font-semibold ${getStatusColor(status.backend)}`}>{status.backend.toUpperCase()}</p>
            </div>
          </div>
        </div>
        <div className="bg-dark-100/50 border border-dark-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{getStatusIcon(status.oanda)}</span>
            <div>
              <p className="text-sm text-gray-400">OANDA API</p>
              <p className={`text-lg font-semibold ${getStatusColor(status.oanda)}`}>{status.oanda.toUpperCase()}</p>
            </div>
          </div>
        </div>
        <div className="bg-dark-100/50 border border-dark-200 rounded-lg p-4">
          <div className="flex items-center gap-3">
            <span className="text-2xl">{getStatusIcon(status.strategy)}</span>
            <div>
              <p className="text-sm text-gray-400">ALGOX Strategy</p>
              <p className={`text-lg font-semibold ${getStatusColor(status.strategy)}`}>{status.strategy.toUpperCase()}</p>
            </div>
          </div>
        </div>
      </div>
      <div className="mt-4 p-3 bg-blue-500/10 border border-blue-500/30 rounded-lg">
        <p className="text-xs text-blue-300"> System checks every 5 sec</p>
      </div>
    </div>
  );
};

export default ProcessingStatusPanel;
