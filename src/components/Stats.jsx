import React from 'react';

const Stats = ({ stats, todaySignals }) => {
  const statCards = [
    { label: 'Total Signals', value: stats.total_signals || 0, icon: '📊', color: 'text-blue-400' },
    { label: 'Win Rate', value: `${stats.win_rate || 0}%`, icon: '🎯', color: 'text-green-400' },
    { label: 'Wins', value: stats.wins || 0, icon: '✅', color: 'text-green-400' },
    { label: 'Losses', value: stats.losses || 0, icon: '❌', color: 'text-red-400' },
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
      {statCards.map((stat, index) => (
        <div key={index} className="bg-bg-card border border-border-subtle rounded-lg p-6 hover:border-accent-primary transition-smooth">
          <div className="flex items-center justify-between mb-2">
            <span className="text-text-muted text-small">{stat.label}</span>
            <span className="text-2xl">{stat.icon}</span>
          </div>
          <div className={`text-h2 font-bold ${stat.color}`}>{stat.value}</div>
        </div>
      ))}
    </div>
  );
};

export default Stats;
