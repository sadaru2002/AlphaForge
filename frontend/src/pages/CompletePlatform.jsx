import React, { useState, useEffect } from 'react';
import StrategyEditor from '../components/StrategyEditor';
import BacktestInterface from '../components/BacktestInterface';

const CompletePlatform = () => {
  const [activeTab, setActiveTab] = useState('backtest');
  const [strategies, setStrategies] = useState([]);
  const [signals, setSignals] = useState([]);
  const [prices, setPrices] = useState({});
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    loadStrategies();
    loadPrices();
  }, []);

  const loadStrategies = async () => {
    try {
      // Try to load from backend, fallback to mock data if endpoint doesn't exist
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001'}/api/strategies`);
      
      if (response.ok) {
        const data = await response.json();
        if (data.success) {
          setStrategies(data.strategies);
        }
      } else if (response.status === 404) {
        // Endpoint doesn't exist, use mock data
        setStrategies([
          {
            id: 1,
            name: 'AlphaForge Enhanced',
            description: 'AI-powered trading strategy with technical indicators',
            status: 'ACTIVE',
            performance: 15.2,
            signals_today: 8,
            win_rate: 67.5
          },
          {
            id: 2,
            name: 'Momentum Breakout',
            description: 'Breakout strategy with momentum confirmation', 
            status: 'PAUSED',
            performance: 12.8,
            signals_today: 5,
            win_rate: 72.1
          }
        ]);
      }
    } catch (error) {
      console.error('Error loading strategies:', error);
      // Use mock data as fallback
      setStrategies([
        {
          id: 1,
          name: 'AlphaForge Enhanced',
          description: 'AI-powered trading strategy with technical indicators',
          status: 'ACTIVE',
          performance: 15.2,
          signals_today: 8,
          win_rate: 67.5
        }
      ]);
    }
  };

  const loadPrices = async () => {
    try {
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001'}/api/prices/live/EUR_USD`);
      const data = await response.json();
      if (data.success) {
        setPrices(data.prices);
      }
    } catch (error) {
      console.error('Error loading prices:', error);
    }
  };

  const loadSignals = async () => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001'}/api/signals/today`);
      const data = await response.json();
      if (data.success) {
        setSignals(data.signals);
      }
    } catch (error) {
      console.error('Error loading signals:', error);
    } finally {
      setLoading(false);
    }
  };

  const generateSignals = async (strategyId) => {
    setLoading(true);
    try {
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001'}/api/signals/generate`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_id: strategyId,
          symbols: ['GBPUSD', 'USDJPY', 'XAUUSD'],
          min_confidence: 70
        }),
      });
      
      const data = await response.json();
      if (data.success) {
        // Convert signals object to array
        const allSignals = [];
        Object.entries(data.signals).forEach(([symbol, signalList]) => {
          allSignals.push(...signalList);
        });
        setSignals(allSignals);
      }
    } catch (error) {
      console.error('Error generating signals:', error);
    } finally {
      setLoading(false);
    }
  };

  const tabs = [
    { id: 'backtest', name: 'Strategy Backtesting', icon: '📊' },
    { id: 'strategies', name: 'My Strategies', icon: '💼' },
    { id: 'signals', name: 'Live Signals', icon: '📡' },
    { id: 'prices', name: 'Live Prices', icon: '💰' }
  ];

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white shadow-sm border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center py-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                AlphaForge Complete Trading Platform
              </h1>
              <p className="text-gray-600">
                User-customizable strategy backtesting + signal generation + live trading
              </p>
            </div>
            <div className="flex items-center space-x-4">
              <div className="text-sm text-gray-500">
                Last updated: {new Date().toLocaleTimeString()}
              </div>
              <div className="w-3 h-3 bg-green-400 rounded-full"></div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="bg-white border-b">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <nav className="flex space-x-8">
            {tabs.map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id)}
                className={`py-4 px-1 border-b-2 font-medium text-sm ${
                  activeTab === tab.id
                    ? 'border-blue-500 text-blue-600'
                    : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.name}
              </button>
            ))}
          </nav>
        </div>
      </div>

      {/* Main Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'backtest' && (
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Strategy Backtesting</h2>
            <BacktestInterface />
          </div>
        )}

        {activeTab === 'strategies' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-3xl font-bold text-gray-900">My Strategies</h2>
              <button className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700">
                Create New Strategy
              </button>
            </div>
            
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
              {strategies.map((strategy) => (
                <div key={strategy.id} className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex justify-between items-start mb-4">
                    <h3 className="text-lg font-semibold text-gray-900">{strategy.name}</h3>
                    <span className={`px-2 py-1 rounded text-xs font-medium ${
                      strategy.active 
                        ? 'bg-green-100 text-green-800' 
                        : 'bg-gray-100 text-gray-800'
                    }`}>
                      {strategy.active ? 'Active' : 'Inactive'}
                    </span>
                  </div>
                  
                  <p className="text-gray-600 text-sm mb-4">{strategy.description}</p>
                  
                  <div className="mb-4">
                    <div className="text-sm text-gray-500 mb-1">Symbols:</div>
                    <div className="flex flex-wrap gap-1">
                      {strategy.symbols.map((symbol) => (
                        <span key={symbol} className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded">
                          {symbol}
                        </span>
                      ))}
                    </div>
                  </div>
                  
                  <div className="flex space-x-2">
                    <button
                      onClick={() => generateSignals(strategy.id)}
                      disabled={loading}
                      className="flex-1 bg-green-600 text-white px-3 py-2 rounded text-sm hover:bg-green-700 disabled:bg-gray-400"
                    >
                      {loading ? 'Generating...' : 'Generate Signals'}
                    </button>
                    <button className="flex-1 bg-blue-600 text-white px-3 py-2 rounded text-sm hover:bg-blue-700">
                      Edit
                    </button>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}

        {activeTab === 'signals' && (
          <div>
            <div className="flex justify-between items-center mb-6">
              <h2 className="text-3xl font-bold text-gray-900">Live Signals</h2>
              <button
                onClick={loadSignals}
                disabled={loading}
                className="bg-blue-600 text-white px-4 py-2 rounded hover:bg-blue-700 disabled:bg-gray-400"
              >
                {loading ? 'Loading...' : 'Refresh Signals'}
              </button>
            </div>
            
            {signals.length === 0 ? (
              <div className="text-center py-12">
                <div className="text-gray-400 text-6xl mb-4">📡</div>
                <h3 className="text-lg font-medium text-gray-900 mb-2">No signals available</h3>
                <p className="text-gray-500">Generate signals using your strategies or wait for market conditions.</p>
              </div>
            ) : (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                {signals.map((signal, index) => (
                  <div key={index} className="bg-white rounded-lg shadow-md p-6">
                    <div className="flex justify-between items-start mb-4">
                      <div className="flex items-center space-x-2">
                        <span className="text-lg font-bold">{signal.symbol}</span>
                        <span className={`px-2 py-1 rounded text-xs font-medium ${
                          signal.signal === 'BUY' 
                            ? 'bg-green-100 text-green-800' 
                            : 'bg-red-100 text-red-800'
                        }`}>
                          {signal.signal}
                        </span>
                      </div>
                      <div className="text-sm text-gray-500">
                        {new Date(signal.timestamp).toLocaleString()}
                      </div>
                    </div>
                    
                    <div className="space-y-2 mb-4">
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Entry Price:</span>
                        <span className="text-sm font-medium">{signal.entry_price}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Stop Loss:</span>
                        <span className="text-sm font-medium">{signal.stop_loss}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Take Profit:</span>
                        <span className="text-sm font-medium">{signal.take_profit}</span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-sm text-gray-600">Confidence:</span>
                        <span className="text-sm font-medium">{signal.confidence}%</span>
                      </div>
                    </div>
                    
                    <div className="flex justify-between items-center">
                      <div className="text-sm text-gray-500">
                        {signal.predicted_pips} pips • {signal.risk_reward} RR
                      </div>
                      <div className="text-xs text-gray-400">
                        {signal.session}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            )}
          </div>
        )}

        {activeTab === 'prices' && (
          <div>
            <h2 className="text-3xl font-bold text-gray-900 mb-6">Live Prices</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              {Object.entries(prices).map(([symbol, price]) => (
                <div key={symbol} className="bg-white rounded-lg shadow-md p-6">
                  <div className="flex justify-between items-center mb-4">
                    <h3 className="text-xl font-bold text-gray-900">{symbol}</h3>
                    <div className="text-sm text-gray-500">
                      {new Date(price.timestamp).toLocaleTimeString()}
                    </div>
                  </div>
                  
                  <div className="space-y-2">
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Bid:</span>
                      <span className="text-lg font-semibold text-gray-900">{price.bid}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Ask:</span>
                      <span className="text-lg font-semibold text-gray-900">{price.ask}</span>
                    </div>
                    <div className="flex justify-between">
                      <span className="text-sm text-gray-600">Spread:</span>
                      <span className="text-sm font-medium text-gray-700">{price.spread}</span>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default CompletePlatform;
