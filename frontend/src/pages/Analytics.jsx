import React, { useState } from 'react';
import { TrendingUp, TrendingDown, Activity, Target, BarChart3, PieChart, Zap, DollarSign, Clock, ArrowUpRight } from 'lucide-react';
import { Line, Bar, Doughnut, Radar } from 'react-chartjs-2';
import { Chart as ChartJS, CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, RadialLinearScale, Tooltip, Legend } from 'chart.js';

ChartJS.register(CategoryScale, LinearScale, PointElement, LineElement, BarElement, ArcElement, RadialLinearScale, Tooltip, Legend);

const Analytics = () => {
  const [timeframe, setTimeframe] = useState('7d');

  // Performance metrics - all start at zero for live trading
  const metrics = {
    totalTrades: 0,
    winRate: 0,
    profitFactor: 0,
    sharpeRatio: 0,
    maxDrawdown: 0,
    avgWin: 0,
    avgLoss: 0,
    riskRewardRatio: 0,
    winStreak: 0,
    lossStreak: 0,
    totalProfit: 0,
    totalLoss: 0,
    netProfit: 0,
    avgHoldTime: '0h 0m',
    bestTrade: 0,
    worstTrade: 0,
  };

  // Equity curve data - starts at initial balance
  const equityCurveData = {
    labels: ['Start'],
    datasets: [
      {
        label: 'Account Balance',
        data: [10000],
        borderColor: '#00D8A0',
        backgroundColor: 'rgba(0, 216, 160, 0.1)',
        fill: true,
        tension: 0.4,
      },
      {
        label: 'Drawdown',
        data: [10000],
        borderColor: '#FF6B9D',
        backgroundColor: 'rgba(255, 107, 157, 0.1)',
        fill: true,
        tension: 0.4,
      },
    ],
  };

  // Win/Loss distribution - starts at zero
  const winLossData = {
    labels: ['Wins', 'Losses', 'Breakeven'],
    datasets: [
      {
        data: [0, 0, 0],
        backgroundColor: ['#00D8A0', '#FF6B9D', '#FFD700'],
        borderWidth: 0,
      },
    ],
  };

  // Performance by hour - all zeros
  const hourlyPerformanceData = {
    labels: ['00:00', '04:00', '08:00', '12:00', '16:00', '20:00', '24:00'],
    datasets: [
      {
        label: 'Profit by Hour',
        data: [0, 0, 0, 0, 0, 0, 0],
        backgroundColor: '#00D8A0',
      },
    ],
  };

  // Performance by symbol - all zeros
  const symbolPerformanceData = {
    labels: ['GBPUSD', 'XAUUSD', 'EURUSD', 'USDJPY', 'AUDUSD'],
    datasets: [
      {
        label: 'Win Rate %',
        data: [0, 0, 0, 0, 0],
        backgroundColor: 'rgba(0, 216, 160, 0.6)',
        borderColor: '#00D8A0',
        pointBackgroundColor: '#00D8A0',
      },
    ],
  };

  // Risk metrics radar - all zeros
  const riskMetricsData = {
    labels: ['Win Rate', 'Profit Factor', 'Sharpe Ratio', 'Risk/Reward', 'Consistency', 'Recovery'],
    datasets: [
      {
        label: 'Current Performance',
        data: [0, 0, 0, 0, 0, 0],
        backgroundColor: 'rgba(0, 216, 160, 0.2)',
        borderColor: '#00D8A0',
        pointBackgroundColor: '#00D8A0',
      },
      {
        label: 'Target Performance',
        data: [80, 90, 85, 85, 80, 75],
        backgroundColor: 'rgba(255, 107, 157, 0.2)',
        borderColor: '#FF6B9D',
        pointBackgroundColor: '#FF6B9D',
      },
    ],
  };

  const chartOptions = {
    responsive: true,
    maintainAspectRatio: false,
    plugins: {
      legend: {
        labels: { color: '#E1E8ED' },
      },
    },
    scales: {
      x: { ticks: { color: '#8B98A5' }, grid: { color: 'rgba(139, 152, 165, 0.1)' } },
      y: { ticks: { color: '#8B98A5' }, grid: { color: 'rgba(139, 152, 165, 0.1)' } },
    },
  };

  const radarOptions = {
    responsive: true,
    maintainAspectRatio: false,
    scales: {
      r: {
        ticks: { color: '#8B98A5', backdropColor: 'transparent' },
        grid: { color: 'rgba(139, 152, 165, 0.2)' },
        pointLabels: { color: '#E1E8ED' },
      },
    },
    plugins: {
      legend: { labels: { color: '#E1E8ED' } },
    },
  };

  return (
    <div className="min-h-screen bg-bg-main p-6">
      {/* Header */}
      <div className="mb-6">
        <h1 className="text-h1 text-gradient-green mb-2">📈 Analytics Dashboard</h1>
        <p className="text-body text-text-secondary">
          Comprehensive performance analysis and trading insights
        </p>
      </div>

      {/* Timeframe Filter */}
      <div className="flex gap-3 mb-6">
        {['24h', '7d', '30d', '90d', 'All'].map((tf) => (
          <button
            key={tf}
            onClick={() => setTimeframe(tf)}
            className={`px-4 py-2 rounded-lg transition-smooth ${timeframe === tf
                ? 'bg-accent-primary text-bg-main'
                : 'bg-bg-card text-text-secondary hover:bg-bg-elevated'
              }`}
          >
            {tf}
          </button>
        ))}
      </div>

      {/* Key Metrics Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
        <div className="bg-bg-card border border-border-subtle rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-body text-text-secondary">Total Trades</span>
            <BarChart3 className="text-accent-primary" size={20} />
          </div>
          <p className="text-h2 text-text-primary font-bold">{metrics.totalTrades}</p>
          <p className="text-small text-accent-primary flex items-center gap-1 mt-1">
            <ArrowUpRight size={16} /> +12 this week
          </p>
        </div>

        <div className="bg-bg-card border border-border-subtle rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-body text-text-secondary">Win Rate</span>
            <Target className="text-accent-primary" size={20} />
          </div>
          <p className="text-h2 text-text-primary font-bold">{metrics.winRate}%</p>
          <p className="text-small text-accent-primary flex items-center gap-1 mt-1">
            <ArrowUpRight size={16} /> +2.3% vs last month
          </p>
        </div>

        <div className="bg-bg-card border border-border-subtle rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-body text-text-secondary">Net Profit</span>
            <DollarSign className="text-accent-primary" size={20} />
          </div>
          <p className="text-h2 text-accent-primary font-bold">${metrics.netProfit.toLocaleString()}</p>
          <p className="text-small text-accent-primary flex items-center gap-1 mt-1">
            <ArrowUpRight size={16} /> +{((metrics.netProfit / 10000) * 100).toFixed(1)}% ROI
          </p>
        </div>

        <div className="bg-bg-card border border-border-subtle rounded-lg p-6">
          <div className="flex items-center justify-between mb-2">
            <span className="text-body text-text-secondary">Profit Factor</span>
            <Zap className="text-accent-primary" size={20} />
          </div>
          <p className="text-h2 text-text-primary font-bold">{metrics.profitFactor}</p>
          <p className="text-small text-accent-primary flex items-center gap-1 mt-1">
            <ArrowUpRight size={16} /> Excellent
          </p>
        </div>
      </div>

      {/* Charts Row 1 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Equity Curve */}
        <div className="bg-bg-card border border-border-subtle rounded-lg p-6">
          <h3 className="text-h4 text-text-primary mb-4 flex items-center gap-2">
            <TrendingUp size={20} className="text-accent-primary" />
            Equity Curve
          </h3>
          <div style={{ height: '300px' }}>
            <Line data={equityCurveData} options={chartOptions} />
          </div>
        </div>

        {/* Win/Loss Distribution */}
        <div className="bg-bg-card border border-border-subtle rounded-lg p-6">
          <h3 className="text-h4 text-text-primary mb-4 flex items-center gap-2">
            <PieChart size={20} className="text-accent-primary" />
            Win/Loss Distribution
          </h3>
          <div style={{ height: '300px' }}>
            <Doughnut data={winLossData} options={{ ...chartOptions, scales: undefined }} />
          </div>
        </div>
      </div>

      {/* Charts Row 2 */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
        {/* Performance by Hour */}
        <div className="bg-bg-card border border-border-subtle rounded-lg p-6">
          <h3 className="text-h4 text-text-primary mb-4 flex items-center gap-2">
            <Clock size={20} className="text-accent-primary" />
            Performance by Hour
          </h3>
          <div style={{ height: '300px' }}>
            <Bar data={hourlyPerformanceData} options={chartOptions} />
          </div>
        </div>

        {/* Risk Metrics Radar */}
        <div className="bg-bg-card border border-border-subtle rounded-lg p-6">
          <h3 className="text-h4 text-text-primary mb-4 flex items-center gap-2">
            <Activity size={20} className="text-accent-primary" />
            Risk Metrics Analysis
          </h3>
          <div style={{ height: '300px' }}>
            <Radar data={riskMetricsData} options={radarOptions} />
          </div>
        </div>
      </div>

      {/* Performance by Symbol */}
      <div className="bg-bg-card border border-border-subtle rounded-lg p-6 mb-6">
        <h3 className="text-h4 text-text-primary mb-4 flex items-center gap-2">
          <BarChart3 size={20} className="text-accent-primary" />
          Performance by Symbol
        </h3>
        <div style={{ height: '300px' }}>
          <Radar data={symbolPerformanceData} options={radarOptions} />
        </div>
      </div>

      {/* Detailed Metrics Table */}
      <div className="bg-bg-card border border-border-subtle rounded-lg p-6">
        <h3 className="text-h4 text-text-primary mb-4">Detailed Performance Metrics</h3>
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
          <MetricRow label="Sharpe Ratio" value={metrics.sharpeRatio} trend="up" />
          <MetricRow label="Max Drawdown" value={`${metrics.maxDrawdown}%`} trend="neutral" />
          <MetricRow label="Risk/Reward Ratio" value={`1:${metrics.riskRewardRatio}`} trend="up" />
          <MetricRow label="Avg Win" value={`$${metrics.avgWin}`} trend="up" />
          <MetricRow label="Avg Loss" value={`$${metrics.avgLoss}`} trend="down" />
          <MetricRow label="Avg Hold Time" value={metrics.avgHoldTime} trend="neutral" />
          <MetricRow label="Win Streak" value={metrics.winStreak} trend="up" />
          <MetricRow label="Loss Streak" value={metrics.lossStreak} trend="neutral" />
          <MetricRow label="Best Trade" value={`$${metrics.bestTrade}`} trend="up" />
          <MetricRow label="Worst Trade" value={`$${metrics.worstTrade}`} trend="down" />
          <MetricRow label="Total Profit" value={`$${metrics.totalProfit}`} trend="up" />
          <MetricRow label="Total Loss" value={`$${metrics.totalLoss}`} trend="down" />
        </div>
      </div>
    </div>
  );
};

const MetricRow = ({ label, value, trend }) => {
  const getTrendColor = () => {
    if (trend === 'up') return 'text-accent-primary';
    if (trend === 'down') return 'text-accent-danger';
    return 'text-text-secondary';
  };

  const TrendIcon = trend === 'up' ? TrendingUp : trend === 'down' ? TrendingDown : Activity;

  return (
    <div className="flex items-center justify-between p-3 bg-bg-elevated rounded-lg">
      <span className="text-body text-text-secondary">{label}</span>
      <div className="flex items-center gap-2">
        <span className={`text-body-lg font-bold ${getTrendColor()}`}>{value}</span>
        <TrendIcon size={16} className={getTrendColor()} />
      </div>
    </div>
  );
};

export default Analytics;
