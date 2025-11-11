import React from 'react';

const Stats = ({ stats, todaySignals }) => {
  const statCards = [
    {
      title: 'Win Rate',
      value: `${stats.win_rate || 0}%`,
      icon: '🎯',
      color: 'text-accent-primary',
      bgColor: 'bg-accent-primary',
      target: 'Target: 70%+',
      trend: stats.win_rate > 0 ? `${stats.win_rate >= 70 ? '✓' : '→'} Live` : '-',
      trendColor: stats.win_rate >= 70 ? 'text-accent-success' : stats.win_rate > 0 ? 'text-accent-info' : 'text-text-muted'
    },
    {
      title: 'Profit Factor',
      value: stats.profit_factor?.toFixed(1) || '0.0',
      icon: '📊',
      color: 'text-accent-warning',
      bgColor: 'bg-accent-warning',
      target: 'Target: >2.0',
      trend: stats.profit_factor > 0 ? `${stats.profit_factor >= 2.0 ? '✓' : '→'} Live` : '-',
      trendColor: stats.profit_factor >= 2.0 ? 'text-accent-success' : stats.profit_factor > 0 ? 'text-accent-info' : 'text-text-muted'
    },
    {
      title: 'Net Profit',
      value: `$${stats.net_profit || 0}`,
      icon: '💰',
      color: stats.net_profit > 0 ? 'text-accent-success' : stats.net_profit < 0 ? 'text-accent-danger' : 'text-text-primary',
      bgColor: stats.net_profit > 0 ? 'bg-accent-success' : stats.net_profit < 0 ? 'bg-accent-danger' : 'bg-text-primary',
      target: 'Live Trading',
      trend: stats.net_profit > 0 ? '↗ Profit' : stats.net_profit < 0 ? '↘ Loss' : '-',
      trendColor: stats.net_profit > 0 ? 'text-accent-success' : stats.net_profit < 0 ? 'text-accent-danger' : 'text-text-muted'
    },
    {
      title: 'Today\'s Signals',
      value: todaySignals || 0,
      icon: '📡',
      color: 'text-accent-info',
      bgColor: 'bg-accent-info',
      target: 'Target: 3-8 daily',
      trend: todaySignals > 0 ? `${todaySignals >= 3 ? '✓' : '→'} Active` : '-',
      trendColor: todaySignals >= 3 ? 'text-accent-success' : todaySignals > 0 ? 'text-accent-info' : 'text-text-muted'
    }
  ];

  return (
    <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
      {statCards.map((card, index) => (
        <div
          key={index}
          className="card card-hover p-6 relative overflow-hidden group"
        >
          {/* Decorative gradient overlay on hover */}
          <div className="absolute inset-0 bg-gradient-to-br from-accent-primary/5 to-transparent opacity-0 group-hover:opacity-100 transition-opacity duration-300"></div>
          
          {/* Content */}
          <div className="relative z-10">
            {/* Icon and Label */}
            <div className="flex items-start justify-between mb-4">
              <div>
                <div className={`text-4xl mb-2 ${card.color}`}>
                  {card.icon}
                </div>
                <h3 className="text-body text-text-secondary font-medium">
                  {card.title}
                </h3>
              </div>
            </div>
            
            {/* Main Value */}
            <div className="mb-3">
              <p className="text-h1 font-bold text-text-primary leading-none">
                {card.value}
              </p>
            </div>
            
            {/* Target and Trend */}
            <div className="flex items-center justify-between">
              <span className="text-small text-text-muted">
                {card.target}
              </span>
              <span className={`text-small font-medium ${card.trendColor}`}>
                {card.trend}
              </span>
            </div>
          </div>
          
          {/* Accent bar at bottom */}
          <div className={`absolute bottom-0 left-0 right-0 h-1 ${card.bgColor} opacity-50 group-hover:opacity-100 transition-opacity`}></div>
        </div>
      ))}
    </div>
  );
};

export default Stats;

