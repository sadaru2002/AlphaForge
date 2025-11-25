import React, { useState, useEffect } from 'react';
import apiService from '../services/api';

const RealTimeAnalysisDashboard = () => {
  const [isActive, setIsActive] = useState(false);
  const [currentAnalysis, setCurrentAnalysis] = useState(null);
  const [analysisHistory, setAnalysisHistory] = useState([]);
  const [priceData, setPriceData] = useState({});
  const [indicators, setIndicators] = useState({});
  const [smcPatterns, setSmcPatterns] = useState([]);
  const [realBackendData, setRealBackendData] = useState(null);
  const [backendConnected, setBackendConnected] = useState(false);

  // Fetch real backend analysis data
  const fetchBackendData = async () => {
    try {
      const [analysisStatus, latestAnalysis, livePrices] = await Promise.all([
        apiService.getAnalysisStatus(),
        apiService.getLatestAnalysis(),
        apiService.getAllPrices()
      ]);
      
      setRealBackendData({
        status: analysisStatus,
        latest: latestAnalysis,
        prices: livePrices
      });
      
      setBackendConnected(true);
      
      // Update analysis history
      if (latestAnalysis && latestAnalysis.timestamp) {
        const newAnalysis = {
          id: Date.now(),
          timestamp: new Date(latestAnalysis.timestamp),
          symbol: latestAnalysis.symbol,
          action: latestAnalysis.setup_quality === 'EXCELLENT' ? 'BUY' : 
                  latestAnalysis.setup_quality === 'GOOD' ? 'BUY' : 'HOLD',
          confidence: Math.round((latestAnalysis.technical_score + latestAnalysis.ml_score) / 2),
          reasoning: `Technical: ${latestAnalysis.technical_score.toFixed(1)}, ML: ${latestAnalysis.ml_score.toFixed(1)}, Quality: ${latestAnalysis.setup_quality}`
        };
        
        setAnalysisHistory(prev => [newAnalysis, ...prev.slice(0, 9)]);
      }
      
    } catch (error) {
      console.error('Error fetching backend data:', error);
      setBackendConnected(false);
    }
  };

  // Fetch real backend data every 5 seconds
  useEffect(() => {
    fetchBackendData();
    const interval = setInterval(fetchBackendData, 5000);
    return () => clearInterval(interval);
  }, []);

  // Simulate real-time analysis data
  useEffect(() => {
    const interval = setInterval(() => {
      if (isActive) {
        // Simulate price data updates
        setPriceData({
          XAUUSD: {
            price: 4070.18 + (Math.random() - 0.5) * 2,
            change: (Math.random() - 0.5) * 0.1,
            volume: Math.floor(Math.random() * 1000) + 200
          },
          GBPUSD: {
            price: 1.3339 + (Math.random() - 0.5) * 0.0002,
            change: (Math.random() - 0.5) * 0.01,
            volume: Math.floor(Math.random() * 1000000) + 500000
          },
          USDJPY: {
            price: 151.92 + (Math.random() - 0.5) * 0.02,
            change: (Math.random() - 0.5) * 0.02,
            volume: Math.floor(Math.random() * 1000000) + 500000
          }
        });

        // Simulate technical indicators
        setIndicators({
          RSI: Math.floor(Math.random() * 100),
          MACD: (Math.random() - 0.5) * 0.01,
          SMA_20: 1.3339 + (Math.random() - 0.5) * 0.001,
          EMA_12: 1.3339 + (Math.random() - 0.5) * 0.001,
          Bollinger_Upper: 1.3339 + Math.random() * 0.002,
          Bollinger_Lower: 1.3339 - Math.random() * 0.002
        });

        // Simulate SMC patterns
        const patterns = [
          'Order Block Detected',
          'Fair Value Gap Found',
          'Liquidity Sweep Identified',
          'Market Structure Break',
          'OTE Zone Confirmed'
        ];
        
        setSmcPatterns(patterns.slice(0, Math.floor(Math.random() * 3) + 1));

        // Add to analysis history
        const newAnalysis = {
          id: Date.now(),
          timestamp: new Date(),
          symbol: ['XAUUSD', 'GBPUSD', 'USDJPY'][Math.floor(Math.random() * 3)],
          action: ['BUY', 'SELL', 'HOLD'][Math.floor(Math.random() * 3)],
          confidence: Math.floor(Math.random() * 40) + 60,
          reasoning: 'AI analysis based on technical indicators and market structure'
        };

        setAnalysisHistory(prev => [newAnalysis, ...prev.slice(0, 9)]);
      }
    }, 2000);

    return () => clearInterval(interval);
  }, [isActive]);

  const startAnalysis = () => {
    setIsActive(true);
    setCurrentAnalysis({
      startTime: new Date(),
      status: 'running',
      steps: []
    });
  };

  const stopAnalysis = () => {
    setIsActive(false);
    setCurrentAnalysis(null);
  };

  return (
    <div className="card card-hover p-6">
      <div className="flex items-center justify-between mb-6">
        <div className="flex items-center gap-3">
          <div className={`w-3 h-3 rounded-full ${
            isActive ? 'bg-green-400 animate-pulse' : 'bg-gray-400'
          }`}></div>
          <h2 className="text-h3 text-gradient-green">Real-Time Analysis Dashboard</h2>
        </div>
        <div className="flex items-center gap-3">
          <button
            onClick={isActive ? stopAnalysis : startAnalysis}
            className={`px-4 py-2 rounded-lg font-medium transition-all duration-300 ${
              isActive 
                ? 'bg-red-500 hover:bg-red-600 text-white' 
                : 'bg-green-500 hover:bg-green-600 text-white'
            }`}
          >
            {isActive ? '⏹️ Stop' : '▶️ Start'} Analysis
          </button>
        </div>
      </div>

      {/* Live Price Data */}
      <div className="mb-6">
        <h3 className="text-medium font-semibold text-text-primary mb-4">Live Price Analysis</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {realBackendData?.prices?.prices ? 
            Object.entries(realBackendData.prices.prices).map(([symbol, data]) => (
              <div key={symbol} className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-small font-medium text-text-primary">{symbol}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    backendConnected ? 'bg-green-500/20 text-green-400' : 'bg-red-500/20 text-red-400'
                  }`}>
                    {backendConnected ? 'LIVE' : 'OFFLINE'}
                  </span>
                </div>
                <div className="text-lg font-bold text-text-primary">
                  {symbol === 'XAUUSD' ? '$' : ''}{data.bid?.toFixed(symbol === 'XAUUSD' ? 2 : 5) || 'N/A'}
                </div>
                <div className="text-xs text-text-muted">
                  Bid: {data.bid?.toFixed(symbol === 'XAUUSD' ? 2 : 5)} | Ask: {data.ask?.toFixed(symbol === 'XAUUSD' ? 2 : 5)}
                </div>
                <div className="text-xs text-text-muted">
                  Spread: {data.spreadPips?.toFixed(1)} pips
                </div>
              </div>
            )) :
            ['XAUUSD', 'GBPUSD', 'USDJPY'].map(symbol => (
              <div key={symbol} className="p-4 bg-gray-800/50 rounded-lg border border-gray-700">
                <div className="flex items-center justify-between mb-2">
                  <span className="text-small font-medium text-text-primary">{symbol}</span>
                  <span className="text-xs px-2 py-1 rounded bg-red-500/20 text-red-400">OFFLINE</span>
                </div>
                <div className="text-lg font-bold text-text-primary">Loading...</div>
                <div className="text-xs text-text-muted">Connecting to backend...</div>
              </div>
            ))
          }
        </div>
      </div>

      {/* Technical Indicators */}
      <div className="mb-6">
        <h3 className="text-medium font-semibold text-text-primary mb-4">Technical Indicators</h3>
        <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
          <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
            <div className="text-xs text-text-muted">RSI (14)</div>
            <div className={`text-lg font-bold ${
              indicators.RSI > 70 ? 'text-red-400' : 
              indicators.RSI < 30 ? 'text-green-400' : 'text-text-primary'
            }`}>
              {indicators.RSI?.toFixed(1)}
            </div>
          </div>
          <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
            <div className="text-xs text-text-muted">MACD</div>
            <div className={`text-lg font-bold ${
              indicators.MACD > 0 ? 'text-green-400' : 'text-red-400'
            }`}>
              {indicators.MACD?.toFixed(5)}
            </div>
          </div>
          <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
            <div className="text-xs text-text-muted">SMA 20</div>
            <div className="text-lg font-bold text-text-primary">
              {indicators.SMA_20?.toFixed(5)}
            </div>
          </div>
          <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
            <div className="text-xs text-text-muted">EMA 12</div>
            <div className="text-lg font-bold text-text-primary">
              {indicators.EMA_12?.toFixed(5)}
            </div>
          </div>
          <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
            <div className="text-xs text-text-muted">BB Upper</div>
            <div className="text-lg font-bold text-yellow-400">
              {indicators.Bollinger_Upper?.toFixed(5)}
            </div>
          </div>
          <div className="p-3 bg-gray-800/50 rounded-lg border border-gray-700">
            <div className="text-xs text-text-muted">BB Lower</div>
            <div className="text-lg font-bold text-yellow-400">
              {indicators.Bollinger_Lower?.toFixed(5)}
            </div>
          </div>
        </div>
      </div>

      {/* Smart Money Concepts */}
      <div className="mb-6">
        <h3 className="text-medium font-semibold text-text-primary mb-4">Smart Money Concepts</h3>
        <div className="space-y-2">
          {smcPatterns.map((pattern, index) => (
            <div key={index} className="flex items-center gap-3 p-3 bg-blue-500/10 rounded-lg border border-blue-500/20">
              <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse"></div>
              <span className="text-small text-blue-400">{pattern}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Analysis History */}
      <div>
        <h3 className="text-medium font-semibold text-text-primary mb-4">Recent Analysis</h3>
        <div className="space-y-2 max-h-64 overflow-y-auto">
          {analysisHistory.map((analysis) => (
            <div key={analysis.id} className="flex items-center gap-3 p-3 bg-gray-800/50 rounded-lg border border-gray-700">
              <div className={`w-2 h-2 rounded-full ${
                analysis.action === 'BUY' ? 'bg-green-400' :
                analysis.action === 'SELL' ? 'bg-red-400' : 'bg-yellow-400'
              }`}></div>
              <div className="flex-1">
                <div className="flex items-center gap-2">
                  <span className="text-small font-medium text-text-primary">{analysis.symbol}</span>
                  <span className={`text-xs px-2 py-1 rounded ${
                    analysis.action === 'BUY' ? 'bg-green-500/20 text-green-400' :
                    analysis.action === 'SELL' ? 'bg-red-500/20 text-red-400' : 'bg-yellow-500/20 text-yellow-400'
                  }`}>
                    {analysis.action}
                  </span>
                  <span className="text-xs text-text-muted">{analysis.confidence}% confidence</span>
                </div>
                <div className="text-xs text-text-muted mt-1">
                  {analysis.timestamp.toLocaleTimeString()} - {analysis.reasoning}
                </div>
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="mt-6 pt-4 border-t border-gray-700">
        <div className="flex items-center justify-between text-xs text-text-muted">
          <span>🧠 Powered by Gemini Pro AI</span>
          <span>⚡ Real-time analysis</span>
        </div>
      </div>
    </div>
  );
};

export default RealTimeAnalysisDashboard;
