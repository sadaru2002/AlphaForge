import React from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend, ResponsiveContainer } from 'recharts';

const Dashboard = ({ signals, stats }) => {
  // Process signals for chart
  const chartData = signals.slice(-20).map((signal, index) => ({
    name: `#${index + 1}`,
    entry: signal.entry,
    tp1: signal.tp1,
    sl: signal.stop_loss
  }));

  return (
    <div className="bg-gray-800 rounded-lg p-6 border border-gray-700">
      <h2 className="text-2xl font-bold text-blue-400 mb-6">Performance Overview</h2>
      
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Trade History Chart */}
        <div>
          <h3 className="text-lg font-semibold mb-4">Recent Signals</h3>
          <ResponsiveContainer width="100%" height={300}>
            <LineChart data={chartData}>
              <CartesianGrid strokeDasharray="3 3" stroke="#374151" />
              <XAxis dataKey="name" stroke="#9CA3AF" />
              <YAxis stroke="#9CA3AF" />
              <Tooltip
                contentStyle={{ backgroundColor: '#1F2937', border: 'none' }}
              />
              <Legend />
              <Line type="monotone" dataKey="entry" stroke="#3B82F6" strokeWidth={2} />
              <Line type="monotone" dataKey="tp1" stroke="#10B981" strokeWidth={2} />
              <Line type="monotone" dataKey="sl" stroke="#EF4444" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        </div>

        {/* Statistics Table */}
        <div>
          <h3 className="text-lg font-semibold mb-4">Detailed Statistics</h3>
          <div className="bg-gray-900 rounded-lg p-4 space-y-3">
            <div className="flex justify-between border-b border-gray-700 pb-2">
              <span className="text-gray-400">Total Signals:</span>
              <span className="font-bold">{stats.total_signals || 0}</span>
            </div>
            <div className="flex justify-between border-b border-gray-700 pb-2">
              <span className="text-gray-400">Winning Trades:</span>
              <span className="font-bold text-green-400">{stats.wins || 0}</span>
            </div>
            <div className="flex justify-between border-b border-gray-700 pb-2">
              <span className="text-gray-400">Losing Trades:</span>
              <span className="font-bold text-red-400">{stats.losses || 0}</span>
            </div>
            <div className="flex justify-between border-b border-gray-700 pb-2">
              <span className="text-gray-400">Win Rate:</span>
              <span className="font-bold text-blue-400">{stats.win_rate || 0}%</span>
            </div>
            <div className="flex justify-between border-b border-gray-700 pb-2">
              <span className="text-gray-400">Profit Factor:</span>
              <span className="font-bold text-yellow-400">{stats.profit_factor || 0}</span>
            </div>
            <div className="flex justify-between pt-2">
              <span className="text-gray-400">Net Profit:</span>
              <span className={`font-bold text-xl ${stats.net_profit >= 0 ? 'text-green-400' : 'text-red-400'}`}>
                ${stats.net_profit || 0}
              </span>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default Dashboard;
