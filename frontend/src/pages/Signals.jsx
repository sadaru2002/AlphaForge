import React, { useState, useEffect } from 'react';
import { TrendingUp, TrendingDown, Activity, Filter, Download, RefreshCw, Target, DollarSign, BarChart3, CheckCircle, XCircle } from 'lucide-react';
import apiService from '../services/api';

const Signals = () => {
  const [signals, setSignals] = useState([]);
  const [loading, setLoading] = useState(false);
  const [filter, setFilter] = useState('all'); // all, active, closed, winners, losers
  const [symbolFilter, setSymbolFilter] = useState('all');
  const [sortBy, setSortBy] = useState('timestamp'); // timestamp, profit, duration
  const [selectedSignal, setSelectedSignal] = useState(null);
  const [serverStats, setServerStats] = useState(null); // Server-calculated statistics

  useEffect(() => {
    fetchSignals();
    // Auto-refresh every 30 seconds
    const interval = setInterval(fetchSignals, 30000);
    return () => clearInterval(interval);
  }, []);

  const fetchSignals = async () => {
    setLoading(true);
    try {
      const response = await apiService.getSignals();
      setSignals(response.signals || []);
      // Use server-calculated statistics if available
      if (response.statistics) {
        setServerStats(response.statistics);
      }
    } catch (error) {
      console.error('Error fetching signals:', error);
    } finally {
      setLoading(false);
    }
  };

  // Filter signals
  const filteredSignals = signals.filter((signal) => {
    // Status filter
    if (filter === 'active' && signal.status !== 'ACTIVE') return false;
    if (filter === 'closed' && signal.status !== 'CLOSED') return false;
    if (filter === 'winners' && signal.status !== 'WON') return false;
    if (filter === 'losers' && signal.status !== 'LOST') return false;

    // Symbol filter
    if (symbolFilter !== 'all' && signal.symbol !== symbolFilter) return false;

    return true;
  });

  // Sort signals
  const sortedSignals = [...filteredSignals].sort((a, b) => {
    if (sortBy === 'timestamp') {
      return new Date(b.timestamp) - new Date(a.timestamp);
    } else if (sortBy === 'profit') {
      return (b.actual_pnl || 0) - (a.actual_pnl || 0);
    } else if (sortBy === 'duration') {
      return (b.duration_hours || 0) - (a.duration_hours || 0);
    }
    return 0;
  });
  // Use server-calculated statistics when available, fallback to local calculation
  const stats = serverStats ? {
    total: serverStats.total || signals.length,
    active: serverStats.active || 0,
    closed: serverStats.closed || 0,
    winners: serverStats.winners || 0,
    losers: serverStats.losers || 0,
    winRate: serverStats.winRate || 0,
    totalProfit: serverStats.totalPnL || 0,
    avgProfit: 0,
    avgLoss: 0,
  } : {
    total: signals.length,
    active: signals.filter(s => s.status === 'ACTIVE' || s.status === 'PENDING').length,
    closed: signals.filter(s => s.status === 'CLOSED' || s.status === 'WON' || s.status === 'LOST' || s.status === 'EXPIRED').length,
    winners: signals.filter(s => s.status === 'WON').length,
    losers: signals.filter(s => s.status === 'LOST').length,
    winRate: (signals.filter(s => s.status === 'WON').length + signals.filter(s => s.status === 'LOST').length) > 0
      ? ((signals.filter(s => s.status === 'WON').length / (signals.filter(s => s.status === 'WON').length + signals.filter(s => s.status === 'LOST').length)) * 100).toFixed(1)
      : 0,
    totalProfit: signals.reduce((sum, s) => sum + (s.actual_pnl || 0), 0),
    avgProfit: signals.filter(s => s.status === 'WON').length > 0
      ? (signals.filter(s => s.status === 'WON').reduce((sum, s) => sum + (s.actual_pnl || 0), 0) / signals.filter(s => s.status === 'WON').length).toFixed(2)
      : 0,
    avgLoss: signals.filter(s => s.status === 'LOST').length > 0
      ? (signals.filter(s => s.status === 'LOST').reduce((sum, s) => sum + (s.actual_pnl || 0), 0) / signals.filter(s => s.status === 'LOST').length).toFixed(2)
      : 0,
  };

  const getUniqueSymbols = () => {
    return ['all', ...new Set(signals.map(s => s.symbol))];
  };

  const handleExportCSV = () => {
    // Define CSV headers
    const headers = [
      'Timestamp',
      'Symbol',
      'Direction',
      'Entry',
      'Stop Loss',
      'Take Profit',
      'Risk/Reward',
      'Confidence',
      'Status',
      'Outcome',
      'P&L',
      'Duration (hours)',
      'Reasoning'
    ];

    // Convert signals to CSV rows
    const rows = sortedSignals.map(signal => [
      new Date(signal.timestamp).toLocaleString(),
      signal.symbol || '',
      signal.direction || '',
      signal.entry || signal.entry_price || '',
      signal.stop_loss || '',
      signal.take_profit || signal.tp1 || '',
      signal.rr_ratio || '',
      signal.confidence_score ? `${signal.confidence_score}%` : '',
      signal.status || '',
      signal.outcome || 'PENDING',
      signal.actual_pnl || '',
      signal.duration_hours || '',
      signal.reasoning || ''
    ]);

    // Combine headers and rows
    const csvContent = [
      headers.join(','),
      ...rows.map(row =>
        row.map(cell =>
          // Escape commas and quotes in cell content
          typeof cell === 'string' && (cell.includes(',') || cell.includes('"'))
            ? `"${cell.replace(/"/g, '""')}"`
            : cell
        ).join(',')
      )
    ].join('\n');

    // Create blob and download
    const blob = new Blob([csvContent], { type: 'text/csv;charset=utf-8;' });
    const link = document.createElement('a');
    const url = URL.createObjectURL(blob);

    link.setAttribute('href', url);
    link.setAttribute('download', `trading_signals_${new Date().toISOString().split('T')[0]}.csv`);
    link.style.visibility = 'hidden';

    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  return (
    <div className="min-h-screen bg-bg-main p-6">
      {/* Header */}
      <div className="mb-6">
        <div className="flex items-center justify-between mb-4">
          <div>
            <h1 className="text-h1 text-gradient-green mb-2">📊 Trading Signals</h1>
            <p className="text-body text-text-secondary">
              All generated trading signals with real-time tracking
            </p>
          </div>
          <div className="flex gap-3">
            <button
              onClick={fetchSignals}
              disabled={loading}
              className="btn-secondary flex items-center gap-2"
            >
              <RefreshCw size={18} className={loading ? 'animate-spin' : ''} />
              Refresh
            </button>
            <button
              onClick={handleExportCSV}
              disabled={sortedSignals.length === 0}
              className="btn-primary flex items-center gap-2"
            >
              <Download size={18} />
              Export CSV
            </button>
          </div>
        </div>
      </div>

      {/* Statistics Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 lg:grid-cols-7 gap-4 mb-6">
        <StatCard
          label="Total Signals"
          value={stats.total}
          icon={<BarChart3 size={20} />}
          color="blue"
        />
        <StatCard
          label="Active"
          value={stats.active}
          icon={<Activity size={20} />}
          color="yellow"
        />
        <StatCard
          label="Closed"
          value={stats.closed}
          icon={<CheckCircle size={20} />}
          color="gray"
        />
        <StatCard
          label="Winners"
          value={stats.winners}
          icon={<TrendingUp size={20} />}
          color="green"
        />
        <StatCard
          label="Losers"
          value={stats.losers}
          icon={<TrendingDown size={20} />}
          color="red"
        />
        <StatCard
          label="Win Rate"
          value={`${stats.winRate}%`}
          icon={<Target size={20} />}
          color="green"
        />
        <StatCard
          label="Total P&L"
          value={`$${stats.totalProfit.toFixed(2)}`}
          icon={<DollarSign size={20} />}
          color={stats.totalProfit >= 0 ? 'green' : 'red'}
        />
      </div>

      {/* Filters */}
      <div className="bg-bg-card border border-border-subtle rounded-lg p-4 mb-6">
        <div className="flex items-center gap-2 mb-3">
          <Filter size={18} className="text-accent-primary" />
          <h3 className="text-h4 text-text-primary">Filters</h3>
        </div>
        <div className="flex flex-wrap gap-3">
          {/* Status Filter */}
          <div className="flex gap-2">
            {['all', 'active', 'closed', 'winners', 'losers'].map((f) => (
              <button
                key={f}
                onClick={() => setFilter(f)}
                className={`px-4 py-2 rounded-lg capitalize transition-smooth ${filter === f
                  ? 'bg-accent-primary text-bg-main'
                  : 'bg-bg-elevated text-text-secondary hover:bg-bg-hover'
                  }`}
              >
                {f}
              </button>
            ))}
          </div>

          {/* Symbol Filter */}
          <select
            value={symbolFilter}
            onChange={(e) => setSymbolFilter(e.target.value)}
            className="px-4 py-2 bg-bg-elevated text-text-primary border border-border-subtle rounded-lg"
          >
            {getUniqueSymbols().map((symbol) => (
              <option key={symbol} value={symbol}>
                {symbol === 'all' ? 'All Symbols' : symbol}
              </option>
            ))}
          </select>

          {/* Sort By */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="px-4 py-2 bg-bg-elevated text-text-primary border border-border-subtle rounded-lg"
          >
            <option value="timestamp">Sort by Time</option>
            <option value="profit">Sort by Profit</option>
            <option value="duration">Sort by Duration</option>
          </select>
        </div>
      </div>

      {/* Signals Table */}
      <div className="bg-bg-card border border-border-subtle rounded-lg overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full">
            <thead className="bg-bg-elevated border-b border-border-subtle">
              <tr>
                <th className="px-4 py-3 text-left text-small font-semibold text-text-secondary">Time</th>
                <th className="px-4 py-3 text-left text-small font-semibold text-text-secondary">Symbol</th>
                <th className="px-4 py-3 text-left text-small font-semibold text-text-secondary">Type</th>
                <th className="px-4 py-3 text-left text-small font-semibold text-text-secondary">Entry</th>
                <th className="px-4 py-3 text-left text-small font-semibold text-text-secondary">TP1</th>
                <th className="px-4 py-3 text-left text-small font-semibold text-text-secondary">SL</th>
                <th className="px-4 py-3 text-left text-small font-semibold text-text-secondary">R:R</th>
                <th className="px-4 py-3 text-left text-small font-semibold text-text-secondary">Status</th>
                <th className="px-4 py-3 text-left text-small font-semibold text-text-secondary">Outcome</th>
                <th className="px-4 py-3 text-left text-small font-semibold text-text-secondary">P&L</th>
                <th className="px-4 py-3 text-left text-small font-semibold text-text-secondary">Duration</th>
                <th className="px-4 py-3 text-left text-small font-semibold text-text-secondary">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-border-subtle">
              {sortedSignals.length === 0 ? (
                <tr>
                  <td colSpan="12" className="px-4 py-12 text-center">
                    <div className="flex flex-col items-center gap-3">
                      <Activity size={48} className="text-text-muted" />
                      <p className="text-body text-text-secondary">No signals found</p>
                      <p className="text-small text-text-muted">
                        {loading ? 'Loading signals...' : 'Signals will appear here when generated'}
                      </p>
                    </div>
                  </td>
                </tr>
              ) : (
                sortedSignals.map((signal) => (
                  <SignalRow
                    key={signal.id}
                    signal={signal}
                    onClick={() => setSelectedSignal(signal)}
                  />
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>

      {/* Signal Details Modal */}
      {selectedSignal && (
        <SignalDetailsModal
          signal={selectedSignal}
          onClose={() => setSelectedSignal(null)}
        />
      )}
    </div>
  );
};

// Stat Card Component
const StatCard = ({ label, value, icon, color }) => {
  const colorClasses = {
    blue: 'text-blue-400',
    yellow: 'text-yellow-400',
    gray: 'text-gray-400',
    green: 'text-accent-primary',
    red: 'text-accent-danger',
  };

  return (
    <div className="bg-bg-card border border-border-subtle rounded-lg p-4">
      <div className="flex items-center justify-between mb-2">
        <span className="text-small text-text-secondary">{label}</span>
        <span className={colorClasses[color]}>{icon}</span>
      </div>
      <p className={`text-h3 font-bold ${colorClasses[color]}`}>{value}</p>
    </div>
  );
};

// Signal Row Component
const SignalRow = ({ signal, onClick }) => {
  const formatTime = (timestamp) => {
    if (!timestamp) return '-';
    const date = new Date(timestamp);
    return date.toLocaleString('en-US', {
      month: 'short',
      day: '2-digit',
      hour: '2-digit',
      minute: '2-digit',
    });
  };

  const getStatusBadge = (status) => {
    const badges = {
      ACTIVE: 'bg-yellow-500/20 text-yellow-400',
      CLOSED: 'bg-gray-500/20 text-gray-400',
      PENDING: 'bg-blue-500/20 text-blue-400',
      WON: 'bg-green-500/20 text-green-400',
      LOST: 'bg-red-500/20 text-red-400',
      EXPIRED: 'bg-orange-500/20 text-orange-400',
    };
    return badges[status] || badges.PENDING;
  };

  const getOutcomeBadge = (outcome) => {
    if (!outcome) return <span className="text-text-muted">-</span>;
    const badges = {
      WIN: { class: 'bg-accent-primary/20 text-accent-primary', icon: <CheckCircle size={14} /> },
      LOSS: { class: 'bg-accent-danger/20 text-accent-danger', icon: <XCircle size={14} /> },
      BREAKEVEN: { class: 'bg-gray-500/20 text-gray-400', icon: <Activity size={14} /> },
    };
    const badge = badges[outcome] || badges.WIN;
    return (
      <span className={`flex items-center gap-1 px-2 py-1 rounded text-small ${badge.class}`}>
        {badge.icon}
        {outcome}
      </span>
    );
  };

  return (
    <tr
      onClick={onClick}
      className="hover:bg-bg-elevated transition-smooth cursor-pointer"
    >
      <td className="px-4 py-3 text-small text-text-primary">{formatTime(signal.timestamp)}</td>
      <td className="px-4 py-3">
        <span className="font-semibold text-text-primary">{signal.symbol}</span>
      </td>
      <td className="px-4 py-3">
        <span className={`flex items-center gap-1 ${signal.direction === 'BUY' ? 'text-accent-primary' : 'text-accent-danger'
          }`}>
          {signal.direction === 'BUY' ? <TrendingUp size={16} /> : <TrendingDown size={16} />}
          {signal.direction}
        </span>
      </td>
      <td className="px-4 py-3 text-small text-text-primary font-mono">{signal.entry?.toFixed(5) || '-'}</td>
      <td className="px-4 py-3 text-small text-accent-primary font-mono">{signal.tp1?.toFixed(5) || '-'}</td>
      <td className="px-4 py-3 text-small text-accent-danger font-mono">{signal.stop_loss?.toFixed(5) || '-'}</td>
      <td className="px-4 py-3 text-small text-text-primary">{signal.rr_ratio || '1:2'}</td>
      <td className="px-4 py-3">
        <span className={`px-2 py-1 rounded text-small ${getStatusBadge(signal.status)}`}>
          {signal.status || 'PENDING'}
        </span>
      </td>
      <td className="px-4 py-3">{getOutcomeBadge(signal.outcome)}</td>
      <td className="px-4 py-3">
        {signal.actual_pnl ? (
          <span className={`font-semibold ${signal.actual_pnl >= 0 ? 'text-accent-primary' : 'text-accent-danger'}`}>
            ${signal.actual_pnl.toFixed(2)}
          </span>
        ) : (
          <span className="text-text-muted">-</span>
        )}
      </td>
      <td className="px-4 py-3 text-small text-text-secondary">
        {signal.duration_hours ? `${signal.duration_hours.toFixed(1)}h` : '-'}
      </td>
      <td className="px-4 py-3">
        <button className="text-accent-primary hover:text-accent-primary/80 text-small">
          View
        </button>
      </td>
    </tr>
  );
};

// Signal Details Modal
const SignalDetailsModal = ({ signal, onClose }) => {
  return (
    <div className="fixed inset-0 bg-black/50 flex items-center justify-center z-50 p-4">
      <div className="bg-bg-card border border-border-subtle rounded-lg max-w-2xl w-full max-h-[90vh] overflow-y-auto">
        <div className="sticky top-0 bg-bg-card border-b border-border-subtle p-6 flex items-center justify-between">
          <h2 className="text-h3 text-text-primary">Signal Details</h2>
          <button onClick={onClose} className="text-text-secondary hover:text-text-primary">
            ✕
          </button>
        </div>

        <div className="p-6 space-y-6">
          {/* Basic Info */}
          <div className="grid grid-cols-2 gap-4">
            <InfoRow label="Symbol" value={signal.symbol} />
            <InfoRow label="Direction" value={signal.direction} />
            <InfoRow label="Entry Price" value={signal.entry?.toFixed(5)} />
            <InfoRow label="Stop Loss" value={signal.stop_loss?.toFixed(5)} />
            <InfoRow label="Take Profit 1" value={signal.tp1?.toFixed(5)} />
            <InfoRow label="Take Profit 2" value={signal.tp2?.toFixed(5)} />
            <InfoRow label="Risk/Reward" value={signal.rr_ratio} />
            <InfoRow label="Confidence" value={`${(signal.confidence_score || 0)}%`} />
          </div>

          {/* Status & Outcome */}
          <div className="border-t border-border-subtle pt-4">
            <h3 className="text-h4 text-text-primary mb-3">Trade Status</h3>
            <div className="grid grid-cols-2 gap-4">
              <InfoRow label="Status" value={signal.status || 'PENDING'} />
              <InfoRow label="Outcome" value={signal.outcome || '-'} />
              <InfoRow label="P&L" value={signal.actual_pnl ? `$${signal.actual_pnl.toFixed(2)}` : '-'} />
              <InfoRow label="Duration" value={signal.duration_hours ? `${signal.duration_hours.toFixed(1)} hours` : '-'} />
            </div>
          </div>

          {/* Analysis */}
          {signal.reasoning && (
            <div className="border-t border-border-subtle pt-4">
              <h3 className="text-h4 text-text-primary mb-3">Analysis</h3>
              <p className="text-body text-text-secondary">{signal.reasoning}</p>
            </div>
          )}

          {/* Timestamps */}
          <div className="border-t border-border-subtle pt-4">
            <h3 className="text-h4 text-text-primary mb-3">Timeline</h3>
            <div className="space-y-2">
              <InfoRow label="Generated" value={new Date(signal.timestamp).toLocaleString()} />
              {signal.entry_time && <InfoRow label="Entered" value={new Date(signal.entry_time).toLocaleString()} />}
              {signal.exit_time && <InfoRow label="Exited" value={new Date(signal.exit_time).toLocaleString()} />}
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

const InfoRow = ({ label, value }) => (
  <div>
    <span className="text-small text-text-secondary">{label}</span>
    <p className="text-body text-text-primary font-semibold">{value}</p>
  </div>
);

export default Signals;
