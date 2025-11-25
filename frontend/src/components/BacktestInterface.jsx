import React, { useState, useEffect } from 'react';
import StrategyEditor from './StrategyEditor';

const BacktestInterface = () => {
  const [strategyCode, setStrategyCode] = useState('');
  const [backtestParams, setBacktestParams] = useState({
    symbol: 'GBPUSD',
    startDate: '2025-09-01',
    endDate: '2025-09-30',
    initialCapital: 10000,
    spreadPips: 2.0,
    lotSize: 0.1
  });
  const [isRunning, setIsRunning] = useState(false);
  const [results, setResults] = useState(null);
  const [error, setError] = useState('');

  const handleStrategySave = (code) => {
    setStrategyCode(code);
  };

  const runBacktest = async () => {
    if (!strategyCode) {
      setError('Please enter strategy code first');
      return;
    }

    setIsRunning(true);
    setError('');
    setResults(null);

    try {
      const response = await fetch(`${process.env.REACT_APP_API_BASE_URL || 'http://localhost:5001'}/api/backtest/run`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          strategy_code: strategyCode,
          symbol: backtestParams.symbol,
          start_date: backtestParams.startDate,
          end_date: backtestParams.endDate,
          initial_capital: backtestParams.initialCapital,
          spread_pips: backtestParams.spreadPips,
          lot_size: backtestParams.lotSize
        }),
      });

      const data = await response.json();

      if (data.success) {
        setResults(data.results);
      } else {
        setError(data.error || 'Backtest failed');
      }
    } catch (err) {
      setError('Error running backtest: ' + err.message);
    } finally {
      setIsRunning(false);
    }
  };

  const formatNumber = (num, decimals = 2) => {
    return typeof num === 'number' ? num.toFixed(decimals) : num;
  };

  const formatCurrency = (amount) => {
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'USD'
    }).format(amount);
  };

  return (
    <div className="backtest-interface">
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Strategy Editor */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <StrategyEditor onSave={handleStrategySave} />
        </div>

        {/* Backtest Parameters */}
        <div className="bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Backtest Parameters</h3>
          
          <div className="space-y-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Symbol
              </label>
              <select
                value={backtestParams.symbol}
                onChange={(e) => setBacktestParams({...backtestParams, symbol: e.target.value})}
                className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              >
                <option value="GBPUSD">GBP/USD</option>
                <option value="USDJPY">USD/JPY</option>
                <option value="XAUUSD">XAU/USD (Gold)</option>
              </select>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Start Date
                </label>
                <input
                  type="date"
                  value={backtestParams.startDate}
                  onChange={(e) => setBacktestParams({...backtestParams, startDate: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  End Date
                </label>
                <input
                  type="date"
                  value={backtestParams.endDate}
                  onChange={(e) => setBacktestParams({...backtestParams, endDate: e.target.value})}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div className="grid grid-cols-2 gap-4">
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Initial Capital ($)
                </label>
                <input
                  type="number"
                  value={backtestParams.initialCapital}
                  onChange={(e) => setBacktestParams({...backtestParams, initialCapital: parseFloat(e.target.value)})}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
              <div>
                <label className="block text-sm font-medium text-gray-700 mb-1">
                  Spread (pips)
                </label>
                <input
                  type="number"
                  step="0.1"
                  value={backtestParams.spreadPips}
                  onChange={(e) => setBacktestParams({...backtestParams, spreadPips: parseFloat(e.target.value)})}
                  className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
                />
              </div>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-1">
                Lot Size
              </label>
              <input
                type="number"
                step="0.01"
                value={backtestParams.lotSize}
                onChange={(e) => setBacktestParams({...backtestParams, lotSize: parseFloat(e.target.value)})}
                className="w-full p-2 border border-gray-300 rounded focus:ring-2 focus:ring-blue-500 focus:border-blue-500"
              />
            </div>

            <button
              onClick={runBacktest}
              disabled={isRunning || !strategyCode}
              className={`w-full py-3 px-4 rounded font-semibold ${
                isRunning || !strategyCode
                  ? 'bg-gray-400 cursor-not-allowed text-white'
                  : 'bg-blue-600 hover:bg-blue-700 text-white'
              }`}
            >
              {isRunning ? 'Running Backtest...' : 'Run VectorBT Backtest'}
            </button>
          </div>
        </div>
      </div>

      {/* Results */}
      {error && (
        <div className="mt-6 bg-red-100 border border-red-400 text-red-700 px-4 py-3 rounded">
          {error}
        </div>
      )}

      {results && (
        <div className="mt-6 bg-white rounded-lg shadow-md p-6">
          <h3 className="text-xl font-bold text-gray-800 mb-4">Backtest Results</h3>
          
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
            <div className="bg-blue-50 p-4 rounded">
              <div className="text-sm text-blue-600 font-medium">Total Return</div>
              <div className="text-2xl font-bold text-blue-800">
                {formatNumber(results.total_return_pct)}%
              </div>
            </div>
            
            <div className="bg-green-50 p-4 rounded">
              <div className="text-sm text-green-600 font-medium">Total Profit</div>
              <div className="text-2xl font-bold text-green-800">
                {formatCurrency(results.total_profit)}
              </div>
            </div>
            
            <div className="bg-purple-50 p-4 rounded">
              <div className="text-sm text-purple-600 font-medium">Win Rate</div>
              <div className="text-2xl font-bold text-purple-800">
                {formatNumber(results.win_rate_pct)}%
              </div>
            </div>
            
            <div className="bg-orange-50 p-4 rounded">
              <div className="text-sm text-orange-600 font-medium">Total Trades</div>
              <div className="text-2xl font-bold text-orange-800">
                {results.total_trades}
              </div>
            </div>
          </div>

          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
            <div className="bg-gray-50 p-4 rounded">
              <div className="text-sm text-gray-600 font-medium">Sharpe Ratio</div>
              <div className="text-lg font-bold text-gray-800">
                {formatNumber(results.sharpe_ratio)}
              </div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded">
              <div className="text-sm text-gray-600 font-medium">Max Drawdown</div>
              <div className="text-lg font-bold text-gray-800">
                {formatNumber(results.max_drawdown_pct)}%
              </div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded">
              <div className="text-sm text-gray-600 font-medium">Profit Factor</div>
              <div className="text-lg font-bold text-gray-800">
                {formatNumber(results.profit_factor)}
              </div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded">
              <div className="text-sm text-gray-600 font-medium">Best Trade</div>
              <div className="text-lg font-bold text-gray-800">
                {formatNumber(results.best_trade_pct)}%
              </div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded">
              <div className="text-sm text-gray-600 font-medium">Worst Trade</div>
              <div className="text-lg font-bold text-gray-800">
                {formatNumber(results.worst_trade_pct)}%
              </div>
            </div>
            
            <div className="bg-gray-50 p-4 rounded">
              <div className="text-sm text-gray-600 font-medium">Final Capital</div>
              <div className="text-lg font-bold text-gray-800">
                {formatCurrency(results.final_capital)}
              </div>
            </div>
          </div>

          {results.trades && results.trades.length > 0 && (
            <div className="mt-6">
              <h4 className="text-lg font-semibold text-gray-800 mb-3">Trade Details</h4>
              <div className="overflow-x-auto">
                <table className="min-w-full bg-white border border-gray-200">
                  <thead className="bg-gray-50">
                    <tr>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Entry Time</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Type</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Entry Price</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Exit Price</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">PnL</th>
                      <th className="px-4 py-2 text-left text-xs font-medium text-gray-500 uppercase">Return %</th>
                    </tr>
                  </thead>
                  <tbody className="divide-y divide-gray-200">
                    {results.trades.slice(0, 10).map((trade, index) => (
                      <tr key={index}>
                        <td className="px-4 py-2 text-sm text-gray-900">
                          {new Date(trade.entry_time).toLocaleString()}
                        </td>
                        <td className="px-4 py-2 text-sm">
                          <span className={`px-2 py-1 rounded text-xs font-medium ${
                            trade.trade_type === 'BUY' 
                              ? 'bg-green-100 text-green-800' 
                              : 'bg-red-100 text-red-800'
                          }`}>
                            {trade.trade_type}
                          </span>
                        </td>
                        <td className="px-4 py-2 text-sm text-gray-900">
                          {formatNumber(trade.entry_price, 4)}
                        </td>
                        <td className="px-4 py-2 text-sm text-gray-900">
                          {formatNumber(trade.exit_price, 4)}
                        </td>
                        <td className={`px-4 py-2 text-sm font-medium ${
                          trade.pnl >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatCurrency(trade.pnl)}
                        </td>
                        <td className={`px-4 py-2 text-sm font-medium ${
                          trade.pnl_pct >= 0 ? 'text-green-600' : 'text-red-600'
                        }`}>
                          {formatNumber(trade.pnl_pct)}%
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          )}
        </div>
      )}
    </div>
  );
};

export default BacktestInterface;
