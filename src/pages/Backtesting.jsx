import React, { useState, useEffect } from 'react';
import { Play, RotateCcw, BarChart3, TrendingUp, AlertTriangle, DollarSign, Eye, FileText, Download, Settings } from 'lucide-react';
import { Line, Bar, Doughnut } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend } from 'chart.js';
import axios from 'axios';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, Tooltip, Legend);

const API_BASE_URL = 'http://161.118.218.33:5000/api';

const Backtesting = () => {
  const [results, setResults] = useState(null);
  const [loading, setLoading] = useState(false);
  const [history, setHistory] = useState([]);
  const [isRunning, setIsRunning] = useState(false);
  const [selectedTrade, setSelectedTrade] = useState(null);
  const [tradeReplay, setTradeReplay] = useState(null);
  
  // Backtest parameters
  const [params, setParams] = useState({
    name: 'Premium Strategy Test',
    symbol: 'GBPUSD',
    startDate: '2025-09-01',  // September 1, 2025
    endDate: '2025-09-30',    // September 30, 2025 (1 month)
    timeframe: '5min',
    initialBalance: 10000,
    riskPercent: 0.5,
    minConfirmations: 7,  // Premium quality: 7/10 confluence required
    useVectorBT: true  // NEW: Use VectorBT by default (ULTRA-FAST!)
  });

  const darkCard = 'bg-[#1A1F35] border border-[#2A2F45]';

  useEffect(() => {
    fetchHistory();
  }, []);

  const fetchHistory = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/backtest/history`);
      if (response.data.success) {
        setHistory(response.data.history);
      }
    } catch (error) {
      console.error('Error fetching history:', error);
    }
  };

  const runBacktest = async () => {
    setLoading(true);
    setIsRunning(true);
    
    try {
      const response = await axios.post(`${API_BASE_URL}/backtest/advanced/run`, params);
      if (response.data) {
        if (response.data.error) {
          console.error('Backtest error:', response.data.error);
          // Show error message to user
          alert(`Backtest failed: ${response.data.error}`);
        } else {
          setResults(response.data);
        }
      }
    } catch (error) {
      console.error('Error running backtest:', error);
      alert('Failed to run backtest. Please try again.');
    } finally {
      setLoading(false);
      setIsRunning(false);
    }
  };

  const runVectorBTBacktest = async () => {
    setLoading(true);
    setIsRunning(true);
    
    try {
      console.log('Running VectorBT backtest (ULTRA FAST!)...');
      const response = await axios.post(`${API_BASE_URL}/backtest/vectorbt/run`, params);
      if (response.data) {
        if (response.data.error) {
          console.error('VectorBT backtest error:', response.data.error);
          alert(`VectorBT backtest failed: ${response.data.error}`);
        } else {
          console.log('VectorBT backtest completed!', response.data);
          setResults(response.data);
        }
      }
    } catch (error) {
      console.error('Error running VectorBT backtest:', error);
      alert('Failed to run VectorBT backtest. Please try again.');
    } finally {
      setLoading(false);
      setIsRunning(false);
    }
  };

  const viewTradeReplay = async (tradeNumber) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/backtest/trade/${tradeNumber}/replay`);
      if (response.data) {
        setSelectedTrade(tradeNumber);
        setTradeReplay(response.data);
      }
    } catch (error) {
      console.error('Error fetching trade replay:', error);
    }
  };

  const exportTradeReport = async (tradeNumber) => {
    try {
      const response = await axios.get(`${API_BASE_URL}/backtest/trade/${tradeNumber}/export`, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `trade_${tradeNumber}_report.html`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error exporting trade report:', error);
    }
  };

  const exportResults = async (format = 'csv') => {
    try {
      const response = await axios.post(`${API_BASE_URL}/backtest/export`, {
        backtest_id: `${params.symbol}_${params.startDate}_${params.endDate}`,
        format: format
      }, {
        responseType: 'blob'
      });
      
      const url = window.URL.createObjectURL(new Blob([response.data]));
      const link = document.createElement('a');
      link.href = url;
      link.setAttribute('download', `backtest_results.${format}`);
      document.body.appendChild(link);
      link.click();
      link.remove();
    } catch (error) {
      console.error('Error exporting results:', error);
    }
  };

  const equityChartData = results?.equity_curve ? {
    labels: results.equity_curve.map((_, i) => `Day ${i + 1}`),
    datasets: [
      {
        label: 'Account Balance',
        data: results.equity_curve.map(point => point.balance),
        borderColor: 'rgb(6, 182, 212)',
        backgroundColor: 'rgba(6, 182, 212, 0.1)',
        fill: true,
        tension: 0.1
      }
    ]
  } : null;

  const monthlyChartData = results?.monthly_returns ? {
    labels: results.monthly_returns.map(m => m.month),
    datasets: [
      {
        label: 'Monthly Profit',
        data: results.monthly_returns.map(m => m.profit),
        backgroundColor: results.monthly_returns.map(m => 
          m.profit >= 0 ? 'rgba(6, 182, 212, 0.8)' : 'rgba(239, 68, 68, 0.8)'
        ),
        borderColor: results.monthly_returns.map(m => 
          m.profit >= 0 ? 'rgb(6, 182, 212)' : 'rgb(239, 68, 68)'
        ),
        borderWidth: 1
      }
    ]
  } : null;

  const winLossData = results?.summary ? {
    labels: ['Wins', 'Losses'],
    datasets: [{
      data: [results.summary.winning_trades || 0, results.summary.losing_trades || 0],
      backgroundColor: ['#06B6D4', '#EF4444'],
      borderWidth: 0
    }]
  } : null;

  return (
    <div className="min-h-screen bg-[#0F1419] text-[#E5E7EB] p-6">
      <div className="max-w-7xl mx-auto">
        {/* Header */}
        <div className="mb-8">
          <h1 className="text-3xl font-bold text-blue-400 mb-2">Advanced Strategy Backtesting</h1>
          <p className="text-gray-400">Test your trading strategies with real historical data and 9-point confirmation analysis</p>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
          {/* Left: Parameters & Controls */}
          <div className="space-y-6">
            {/* Backtest Parameters */}
            <div className={`${darkCard} rounded-xl p-6`}>
              <h2 className="text-xl font-semibold mb-4 flex items-center">
                <Settings className="mr-2" size={20} />
                Test Parameters
              </h2>
              
              <div className="space-y-4">
                <div>
                  <label className="block text-sm font-medium mb-2">Strategy Name</label>
                  <input
                    type="text"
                    value={params.name}
                    onChange={(e) => setParams({...params, name: e.target.value})}
                    className="w-full bg-[#1E2139] border border-[#2A2F45] rounded-lg px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Symbol</label>
                  <select
                    value={params.symbol}
                    onChange={(e) => setParams({...params, symbol: e.target.value})}
                    className="w-full bg-[#1E2139] border border-[#2A2F45] rounded-lg px-3 py-2"
                  >
                    <option value="GBPUSD">GBP/USD</option>
                    <option value="EURUSD">EUR/USD</option>
                    <option value="USDJPY">USD/JPY</option>
                    <option value="AUDUSD">AUD/USD</option>
                  </select>
                </div>

                <div className="grid grid-cols-2 gap-4">
                  <div>
                    <label className="block text-sm font-medium mb-2">Start Date</label>
                    <input
                      type="date"
                      value={params.startDate}
                      onChange={(e) => setParams({...params, startDate: e.target.value})}
                      className="w-full bg-[#1E2139] border border-[#2A2F45] rounded-lg px-3 py-2"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium mb-2">End Date</label>
                    <input
                      type="date"
                      value={params.endDate}
                      onChange={(e) => setParams({...params, endDate: e.target.value})}
                      className="w-full bg-[#1E2139] border border-[#2A2F45] rounded-lg px-3 py-2"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Timeframe</label>
                  <select
                    value={params.timeframe}
                    onChange={(e) => setParams({...params, timeframe: e.target.value})}
                    className="w-full bg-[#1E2139] border border-[#2A2F45] rounded-lg px-3 py-2"
                  >
                    <option value="1min">1 Minute</option>
                    <option value="5min">5 Minutes</option>
                    <option value="15min">15 Minutes</option>
                    <option value="30min">30 Minutes</option>
                    <option value="60min">1 Hour</option>
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Initial Balance ($)</label>
                  <input
                    type="number"
                    value={params.initialBalance}
                    onChange={(e) => setParams({...params, initialBalance: parseFloat(e.target.value)})}
                    className="w-full bg-[#1E2139] border border-[#2A2F45] rounded-lg px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Risk Per Trade (%)</label>
                  <input
                    type="number"
                    step="0.1"
                    value={params.riskPercent}
                    onChange={(e) => setParams({...params, riskPercent: parseFloat(e.target.value)})}
                    className="w-full bg-[#1E2139] border border-[#2A2F45] rounded-lg px-3 py-2"
                  />
                </div>

                <div>
                  <label className="block text-sm font-medium mb-2">Min Confirmations (2-9)</label>
                  <input
                    type="number"
                    min="2"
                    max="9"
                    value={params.minConfirmations}
                    onChange={(e) => setParams({...params, minConfirmations: parseInt(e.target.value)})}
                    className="w-full bg-[#1E2139] border border-[#2A2F45] rounded-lg px-3 py-2"
                  />
                  <p className="text-xs text-gray-400 mt-1">Higher = Better quality signals</p>
                </div>

                {/* VectorBT Toggle */}
                <div className="col-span-2">
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={params.useVectorBT}
                      onChange={(e) => setParams({...params, useVectorBT: e.target.checked})}
                      className="w-5 h-5 text-cyan-600 bg-[#1E2139] border-[#2A2F45] rounded focus:ring-cyan-500"
                    />
                    <div>
                      <span className="text-sm font-medium">⚡ Use VectorBT (Ultra-Fast!)</span>
                      <p className="text-xs text-gray-400">10-100x faster with 50+ professional metrics</p>
                    </div>
                  </label>
                </div>

                {/* Premium Backtest Button */}
                <button
                  onClick={runBacktest}
                  disabled={loading}
                  className={`w-full col-span-2 py-3 px-4 rounded-lg font-semibold flex items-center justify-center ${
                    loading 
                      ? 'bg-gray-600 cursor-not-allowed' 
                      : params.useVectorBT 
                        ? 'bg-gradient-to-r from-cyan-600 to-blue-600 hover:from-cyan-700 hover:to-blue-700'
                        : 'bg-blue-600 hover:bg-blue-700'
                  }`}
                >
                  {loading ? (
                    <>
                      <RotateCcw className="mr-2 animate-spin" size={20} />
                      Running Backtest...
                    </>
                  ) : (
                    <>
                      <Play className="mr-2" size={20} />
                      {params.useVectorBT ? '⚡ Run VectorBT Backtest' : 'Run Premium Backtest'}
                    </>
                  )}
                </button>
              </div>
            </div>

            {/* Quick Stats */}
            {results && !results.error && (
              <div className={`${darkCard} rounded-xl p-6`}>
                <h3 className="text-lg font-semibold mb-4">Quick Results</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-400">Total Return</span>
                    <span className={`font-semibold ${(results.summary?.total_return || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                      {(results.summary?.total_return || 0) >= 0 ? '+' : ''}{(results.summary?.total_return || 0).toFixed(2)}%
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Win Rate</span>
                    <span className="text-cyan-400 font-semibold">{(results.summary?.win_rate || 0).toFixed(1)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Max Drawdown</span>
                    <span className="text-red-400 font-semibold">{(results.summary?.max_drawdown || 0).toFixed(2)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-400">Profit Factor</span>
                    <span className="text-green-400 font-semibold">{(results.summary?.profit_factor || 0).toFixed(2)}</span>
                  </div>
                </div>
              </div>
            )}
          </div>

          {/* Right: Results & Charts */}
          <div className="lg:col-span-2 space-y-6">
            {results && !results.error ? (
              <>
                {/* Summary Cards */}
                <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                  <div className={`${darkCard} rounded-lg p-4`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-400">Final Balance</p>
                        <p className="text-2xl font-bold text-green-400">${(results.summary?.final_balance || 0).toLocaleString()}</p>
                      </div>
                      <DollarSign className="text-green-400" size={24} />
                    </div>
                  </div>

                  <div className={`${darkCard} rounded-lg p-4`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-400">Total Trades</p>
                        <p className="text-2xl font-bold text-blue-400">{results.summary?.total_trades || 0}</p>
                      </div>
                      <BarChart3 className="text-blue-400" size={24} />
                    </div>
                  </div>

                  <div className={`${darkCard} rounded-lg p-4`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-400">Win Rate</p>
                        <p className="text-2xl font-bold text-cyan-400">{(results.summary?.win_rate || 0).toFixed(1)}%</p>
                      </div>
                      <TrendingUp className="text-cyan-400" size={24} />
                    </div>
                  </div>

                  <div className={`${darkCard} rounded-lg p-4`}>
                    <div className="flex items-center justify-between">
                      <div>
                        <p className="text-sm text-gray-400">Max DD</p>
                        <p className="text-2xl font-bold text-red-400">{(results.summary?.max_drawdown || 0).toFixed(2)}%</p>
                      </div>
                      <AlertTriangle className="text-red-400" size={24} />
                    </div>
                  </div>
                </div>

                {/* Export Controls */}
                <div className={`${darkCard} rounded-xl p-4`}>
                  <div className="flex items-center justify-between">
                    <h3 className="text-lg font-semibold">Export Results</h3>
                    <div className="flex gap-2">
                      <button
                        onClick={() => exportResults('csv')}
                        className="px-4 py-2 bg-green-600 hover:bg-green-700 rounded-lg text-sm font-medium flex items-center"
                      >
                        <Download className="mr-2" size={16} />
                        CSV
                      </button>
                      <button
                        onClick={() => exportResults('json')}
                        className="px-4 py-2 bg-blue-600 hover:bg-blue-700 rounded-lg text-sm font-medium flex items-center"
                      >
                        <Download className="mr-2" size={16} />
                        JSON
                      </button>
                    </div>
                  </div>
                </div>

                {/* Equity Curve Chart */}
                {equityChartData && (
                  <div className={`${darkCard} rounded-xl p-6`}>
                    <h3 className="text-lg font-semibold mb-4">Equity Curve</h3>
                    <div className="h-80">
                      <Line 
                        data={equityChartData} 
                        options={{
                          responsive: true,
                          maintainAspectRatio: false,
                          plugins: {
                            legend: { labels: { color: '#E5E7EB' } }
                          },
                          scales: {
                            x: { ticks: { color: '#94a3b8' } },
                            y: { ticks: { color: '#94a3b8' } }
                          }
                        }} 
                      />
                    </div>
                  </div>
                )}

                {/* Monthly Returns & Win/Loss Charts */}
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  {monthlyChartData && (
                    <div className={`${darkCard} rounded-xl p-6`}>
                      <h3 className="text-lg font-semibold mb-4">Monthly Returns</h3>
                      <div className="h-64">
                        <Bar 
                          data={monthlyChartData} 
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                              legend: { labels: { color: '#E5E7EB' } }
                            },
                            scales: {
                              x: { ticks: { color: '#94a3b8' } },
                              y: { ticks: { color: '#94a3b8' } }
                            }
                          }} 
                        />
                      </div>
                    </div>
                  )}

                  {winLossData && (
                    <div className={`${darkCard} rounded-xl p-6`}>
                      <h3 className="text-lg font-semibold mb-4">Win/Loss Ratio</h3>
                      <div className="h-64">
                        <Doughnut 
                          data={winLossData} 
                          options={{
                            responsive: true,
                            maintainAspectRatio: false,
                            plugins: {
                              legend: { labels: { color: '#E5E7EB' } }
                            }
                          }} 
                        />
                      </div>
                    </div>
                  )}
                </div>

                {/* Trades Table with Replay */}
                <div className={`${darkCard} rounded-xl p-6`}>
                  <h3 className="text-lg font-semibold mb-4">Trades with Visual Replay</h3>
                  <div className="overflow-x-auto">
                    <table className="w-full text-sm">
                      <thead>
                        <tr className="border-b border-[#2A2F45]">
                          <th className="text-left py-2">Trade #</th>
                          <th className="text-left py-2">Date</th>
                          <th className="text-left py-2">Type</th>
                          <th className="text-left py-2">Entry</th>
                          <th className="text-left py-2">Exit</th>
                          <th className="text-left py-2">Pips</th>
                          <th className="text-left py-2">P&L</th>
                          <th className="text-left py-2">Score</th>
                          <th className="text-left py-2">Actions</th>
                        </tr>
                      </thead>
                      <tbody>
                        {results.trades?.slice(0, 20).map((trade, index) => (
                          <tr key={index} className="border-b border-[#2A2F45]/50">
                            <td className="py-2">{trade.trade_number || index + 1}</td>
                            <td className="py-2">{new Date(trade.entry_time || trade.date).toLocaleDateString()}</td>
                            <td className={`py-2 ${(trade.direction || trade.type) === 'BUY' ? 'text-green-400' : 'text-red-400'}`}>
                              {trade.direction || trade.type}
                            </td>
                            <td className="py-2">{(trade.entry || 0).toFixed(5)}</td>
                            <td className="py-2">{(trade.exit || 0).toFixed(5)}</td>
                            <td className={`py-2 ${(trade.pips || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                              {(trade.pips || 0) >= 0 ? '+' : ''}{(trade.pips || 0).toFixed(1)}
                            </td>
                            <td className={`py-2 ${(trade.pnl || trade.profit || 0) >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                              ${(trade.pnl || trade.profit || 0).toFixed(2)}
                            </td>
                            <td className="py-2">
                              <span className="px-2 py-1 bg-blue-600 rounded text-xs">
                                {trade.confirmation_score || trade.signal_strength || 0}/9
                              </span>
                            </td>
                            <td className="py-2">
                              <div className="flex gap-2">
                                <button
                                  onClick={() => viewTradeReplay(trade.trade_number || index + 1)}
                                  className="px-2 py-1 bg-blue-600 hover:bg-blue-700 rounded text-xs flex items-center"
                                >
                                  <Eye className="mr-1" size={12} />
                                  Replay
                                </button>
                                <button
                                  onClick={() => exportTradeReport(trade.trade_number || index + 1)}
                                  className="px-2 py-1 bg-green-600 hover:bg-green-700 rounded text-xs flex items-center"
                                >
                                  <FileText className="mr-1" size={12} />
                                  Export
                                </button>
                              </div>
                            </td>
                          </tr>
                        ))}
                      </tbody>
                    </table>
                  </div>
                </div>

                {/* Trade Replay Modal */}
                {tradeReplay && (
                  <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50 p-4">
                    <div className="bg-[#1A1F35] rounded-xl p-6 max-w-6xl w-full max-h-[90vh] overflow-y-auto">
                      <div className="flex justify-between items-center mb-4">
                        <h3 className="text-xl font-semibold">Trade #{selectedTrade} Replay</h3>
                        <button
                          onClick={() => setTradeReplay(null)}
                          className="text-gray-400 hover:text-white"
                        >
                          ✕
                        </button>
                      </div>
                      <div dangerouslySetInnerHTML={{ __html: tradeReplay.chart_html }} />
                      <div className="mt-4" dangerouslySetInnerHTML={{ __html: tradeReplay.confirmations_html }} />
                    </div>
                  </div>
                )}
              </>
            ) : results && results.error ? (
              <div className={`${darkCard} rounded-xl p-12 text-center`}>
                <AlertTriangle className="mx-auto mb-4 text-red-400" size={48} />
                <h3 className="text-xl font-semibold mb-2 text-red-400">Backtest Failed</h3>
                <p className="text-gray-400 mb-4">{results.error}</p>
                <p className="text-sm text-gray-500">
                  This usually happens when historical data cannot be downloaded. 
                  Try using a shorter date range or check your internet connection.
                </p>
              </div>
            ) : (
              <div className={`${darkCard} rounded-xl p-12 text-center`}>
                <BarChart3 className="mx-auto mb-4 text-gray-400" size={48} />
                <h3 className="text-xl font-semibold mb-2">No Backtest Results</h3>
                <p className="text-gray-400">Configure your parameters and run a backtest to see results here.</p>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default Backtesting;