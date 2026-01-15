import React, { useState } from 'react';
import moment from 'moment';

const SignalCard = ({ signal }) => {
  const [copied, setCopied] = useState(false);
  const isBuy = signal.direction === 'BUY';
  const isNoTrade = signal.direction === 'NO_TRADE';

  // Calculate pips for display
  const calculatePips = (price1, price2) => {
    return Math.abs((price1 - price2) * 10000).toFixed(1);
  };

  const slPips = calculatePips(signal.entry, signal.stop_loss);
  const tp1Pips = calculatePips(signal.entry, signal.tp1);
  const tp2Pips = calculatePips(signal.entry, signal.tp2);

  // Determine confidence badge color
  const getConfidenceBadge = (confidence) => {
    if (confidence >= 85) return 'badge badge-success';
    if (confidence >= 70) return 'badge badge-warning';
    return 'badge badge-neutral';
  };

  const handleCopy = () => {
    const text = `
${signal.direction} ${signal.symbol || 'XAUUSD'}
Entry: ${signal.entry.toFixed(5)}
Stop Loss: ${signal.stop_loss.toFixed(5)}
TP1: ${signal.tp1.toFixed(5)}
TP2: ${signal.tp2.toFixed(5)}
${signal.tp3 ? `TP3: ${signal.tp3.toFixed(5)}` : ''}
Confidence: ${signal.confidence_score}%
Strength: ${signal.signal_strength}
${signal.reasoning ? `\nAnalysis: ${signal.reasoning}` : ''}
    `.trim();

    navigator.clipboard.writeText(text);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };

  const borderClass = isBuy ? 'signal-buy' : isNoTrade ? 'signal-neutral' : 'signal-sell';
  const directionColor = isBuy ? 'text-accent-primary' : isNoTrade ? 'text-text-muted' : 'text-accent-danger';

  // Status badge
  const getStatusBadge = () => {
    const status = signal.status || 'PENDING';
    const badges = {
      'PENDING': 'badge badge-warning',
      'ACTIVE': 'badge badge-success',
      'CLOSED': 'badge badge-neutral',
      'CANCELLED': 'badge badge-error',
      'EXPIRED': 'badge badge-neutral'
    };
    return badges[status] || 'badge badge-neutral';
  };

  return (
    <div className={`card card-hover p-6 ${borderClass} relative overflow-hidden group`}>
      {/* Live Indicator */}
      {signal.status === 'PENDING' && !isNoTrade && (
        <div className="absolute top-4 left-4">
          <div className="live-indicator">
            <div className="live-dot"></div>
            <span className="text-tiny font-bold text-accent-danger uppercase">NEW SIGNAL</span>
          </div>
        </div>
      )}

      {/* Header */}
      <div className="flex justify-between items-start mb-4 mt-8">
        <div className="flex-1">
          <div className="flex items-center gap-3 mb-2">
            <span className={`text-h2 font-bold ${directionColor}`}>
              {isBuy ? '🟢' : isNoTrade ? '⚪' : '🔴'} {signal.direction}
            </span>
            <span className={getConfidenceBadge(signal.confidence_score || 0)}>
              {signal.confidence_score || 0}% Confidence
            </span>
            <span className="badge badge-info">
              {signal.symbol || 'UNKNOWN'}
            </span>
            <span className={getStatusBadge()}>
              {signal.status || 'PENDING'}
            </span>
          </div>
          <p className="text-small text-text-muted">
            {moment(signal.timestamp).fromNow()} • {moment(signal.timestamp).format('HH:mm:ss')}
          </p>
        </div>
        <div className="text-right">
          <p className="text-small text-text-secondary mb-1">Entry Price</p>
          <p className="text-h3 font-mono font-bold text-text-primary">
            {signal.entry.toFixed(5)}
          </p>
        </div>
      </div>

      {/* Levels - Horizontal Row */}
      {!isNoTrade && (
        <div className="grid grid-cols-3 gap-4 mb-4">
          <div className="bg-bg-elevated rounded-lg p-4 border border-border-subtle hover:border-accent-danger transition-smooth">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-accent-danger">⭕</span>
              <p className="text-small text-accent-danger font-semibold">Stop Loss</p>
            </div>
            <p className="text-body-lg font-mono font-bold text-text-primary mb-1">
              {signal.stop_loss.toFixed(5)}
            </p>
            <p className="text-tiny text-text-muted">
              {slPips} pips
            </p>
          </div>

          <div className="bg-bg-elevated rounded-lg p-4 border border-border-subtle hover:border-accent-primary transition-smooth">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-accent-primary">📍</span>
              <p className="text-small text-accent-primary font-semibold">TP1</p>
            </div>
            <p className="text-body-lg font-mono font-bold text-text-primary mb-1">
              {signal.tp1.toFixed(5)}
            </p>
            <p className="text-tiny text-text-muted">
              {tp1Pips} pips • {signal.rr_ratio || '1:2'} RR
            </p>
          </div>

          <div className="bg-bg-elevated rounded-lg p-4 border border-border-subtle hover:border-accent-success transition-smooth">
            <div className="flex items-center gap-2 mb-2">
              <span className="text-accent-success">📍</span>
              <p className="text-small text-accent-success font-semibold">TP2</p>
            </div>
            <p className="text-body-lg font-mono font-bold text-text-primary mb-1">
              {signal.tp2.toFixed(5)}
            </p>
            <p className="text-tiny text-text-muted">
              {tp2Pips} pips
            </p>
          </div>
        </div>
      )}

      {/* Details */}
      <div className="border-t border-border-subtle pt-4 mb-4 space-y-2">
        <div className="flex justify-between items-center">
          <span className="text-body text-text-secondary">Signal Strength</span>
          <span className="text-body font-semibold text-accent-info">
            {signal.signal_strength || 'MEDIUM'}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-body text-text-secondary">Market Condition</span>
          <span className={`text-body font-semibold ${isBuy ? 'text-accent-primary' : 'text-accent-danger'}`}>
            {signal.market_condition || 'TRENDING'}
          </span>
        </div>
        <div className="flex justify-between items-center">
          <span className="text-body text-text-secondary">Session</span>
          <span className="text-body font-semibold text-accent-warning">
            {signal.session || 'LONDON'}
          </span>
        </div>
        {signal.volatility_level && (
          <div className="flex justify-between items-center">
            <span className="text-body text-text-secondary">ATR Volatility</span>
            <span className="text-body font-bold text-text-primary">
              {signal.volatility_level.toFixed(5)}
            </span>
          </div>
        )}
      </div>

      {/* AI Reasoning */}
      {signal.reasoning && (
        <div className="border-t border-border-subtle pt-4 mb-4">
          <p className="text-small font-semibold text-accent-primary mb-2">
            🤖 Gemini AI Analysis:
          </p>
          <p className="text-small text-text-secondary leading-relaxed">
            {signal.reasoning.length > 200
              ? `${signal.reasoning.substring(0, 200)}...`
              : signal.reasoning}
          </p>
        </div>
      )}

      {/* Status Update Buttons - Only show for PENDING signals */}
      {(signal.status === 'PENDING' || signal.status === 'pending') && !isNoTrade && (
        <div className="border-t border-border-subtle pt-4 mb-4">
          <p className="text-small font-semibold text-text-secondary mb-3">
            📊 Mark Signal Result:
          </p>
          <div className="grid grid-cols-3 gap-2">
            <button
              onClick={() => {
                if (window.confirm('Mark this signal as WON?')) {
                  import('../services/api').then(module => {
                    module.default.updateSignalStatus(signal.id, 'WON')
                      .then(() => window.location.reload())
                      .catch(err => alert('Error: ' + err.message));
                  });
                }
              }}
              className="btn bg-accent-success text-white text-small font-semibold py-2 px-3 rounded-lg hover:opacity-80 transition-smooth"
            >
              ✅ WON
            </button>
            <button
              onClick={() => {
                if (window.confirm('Mark this signal as LOST?')) {
                  import('../services/api').then(module => {
                    module.default.updateSignalStatus(signal.id, 'LOST')
                      .then(() => window.location.reload())
                      .catch(err => alert('Error: ' + err.message));
                  });
                }
              }}
              className="btn bg-accent-danger text-white text-small font-semibold py-2 px-3 rounded-lg hover:opacity-80 transition-smooth"
            >
              ❌ LOST
            </button>
            <button
              onClick={() => {
                if (window.confirm('Mark this signal as EXPIRED?')) {
                  import('../services/api').then(module => {
                    module.default.updateSignalStatus(signal.id, 'EXPIRED')
                      .then(() => window.location.reload())
                      .catch(err => alert('Error: ' + err.message));
                  });
                }
              }}
              className="btn bg-text-muted text-white text-small font-semibold py-2 px-3 rounded-lg hover:opacity-80 transition-smooth"
            >
              ⏰ EXPIRED
            </button>
          </div>
        </div>
      )}

      {/* Action Button */}
      {!isNoTrade && (
        <button
          onClick={handleCopy}
          className="btn-primary w-full text-body font-semibold"
        >
          {copied ? '✓ Copied!' : 'Copy Signal Details'}
        </button>
      )}
    </div>
  );
};

export default SignalCard;

