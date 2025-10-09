import React from 'react';

const Stats = ({ stats, todaySignals }) => {
  const statCards = [
    {
      title: 'Win Rate',
      value: `${stats.win_rate || 0}%`,
      icon: '🎯',
      color: 'bg-green-600',
      target: '80%+'
    },
    {
      title: 'Profit Factor',
      value: stats.profit_factor || 0,
      icon: '💰',
      color: 'bg-blue-600',
      target: '>2.0'
    },
    {
      title: 'Net Profit',
      value: `$${stats.net_profit || 0}`,
      icon: '📈',
      color: stats.net_profit >= 0 ? 'bg-green-600' : 'bg-red-600',
      target: 'Growing'
    },
    {
      title: 'Today\'s Signals',
      value: todaySignals || 0,
      icon: '⚡',
      color: 'bg-purple-600',
      target: '3-8 daily'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {statCards.map((card, index) => (
        <div
          key={index}
          className="bg-gray-800 rounded-lg p-6 border border-gray-700 hover:border-blue-500 transition-all"
        >
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-gray-400 text-sm font-semibold">{card.title}</h3>
            <span className="text-3xl">{card.icon}</span>
          </div>
          <div className="flex items-end justify-between">
            <div>
              <p className="text-3xl font-bold text-white">{card.value}</p>
              <p className="text-xs text-gray-500 mt-1">Target: {card.target}</p>
            </div>
            <div className={`${card.color} w-2 h-12 rounded`}></div>
          </div>
        </div>
      ))}
    </div>
  );
};

export default Stats;
