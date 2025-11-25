// Trading Pairs Configuration
// Focus on 3 major pairs: GBP/USD, XAU/USD (Gold), USD/JPY

export const TRADING_PAIRS = [
  {
    id: 'GBP_USD',
    symbol: 'GBP/USD',
    name: 'British Pound / US Dollar',
    displayName: 'GBP/USD',
    category: 'Major',
    pipValue: 0.0001,
    spreadTypical: 1.5,
    volatility: 'Medium',
    description: 'Cable - Popular for day trading',
    icon: '🇬🇧🇺🇸',
    color: '#3B82F6',  // Blue
    chartColor: '#60A5FA',
    enabled: true
  },
  {
    id: 'XAU_USD',
    symbol: 'XAU/USD',
    name: 'Gold / US Dollar',
    displayName: 'GOLD',
    category: 'Commodity',
    pipValue: 0.01,
    spreadTypical: 3.0,
    volatility: 'High',
    description: 'Safe haven asset - trending markets',
    icon: '🥇',
    color: '#F59E0B',  // Gold/Amber
    chartColor: '#FBBF24',
    enabled: true
  },
  {
    id: 'USD_JPY',
    symbol: 'USD/JPY',
    name: 'US Dollar / Japanese Yen',
    displayName: 'USD/JPY',
    category: 'Major',
    pipValue: 0.01,
    spreadTypical: 1.0,
    volatility: 'Low-Medium',
    description: 'Most liquid Asian pair',
    icon: '🇺🇸🇯🇵',
    color: '#10B981',  // Green
    chartColor: '#34D399',
    enabled: true
  }
];

// Default pair for initial load
export const DEFAULT_PAIR = 'GBP_USD';

// Timeframe configuration
export const TIMEFRAMES = [
  { id: 'M5', label: '5m', minutes: 5, weight: 0.40 },
  { id: 'M15', label: '15m', minutes: 15, weight: 0.35 },
  { id: 'H1', label: '1h', minutes: 60, weight: 0.25 }
];

// Market sessions (GMT)
export const TRADING_SESSIONS = {
  LONDON: { start: 8, end: 16, label: 'London', color: '#3B82F6' },
  NEW_YORK: { start: 13, end: 21, label: 'New York', color: '#10B981' },
  TOKYO: { start: 0, end: 8, label: 'Tokyo', color: '#F59E0B' },
  SYDNEY: { start: 22, end: 6, label: 'Sydney', color: '#8B5CF6' }
};

// Signal strength thresholds
export const SIGNAL_THRESHOLDS = {
  STRONG: 0.7,
  MEDIUM: 0.5,
  WEAK: 0.3
};

// Regime types
export const MARKET_REGIMES = {
  TRENDING_UP_HIGH_VOL: {
    label: 'Trending Up (High Vol)',
    color: '#10B981',
    icon: '📈⚡',
    tradeable: true
  },
  TRENDING_UP_LOW_VOL: {
    label: 'Trending Up (Low Vol)',
    color: '#34D399',
    icon: '📈✨',
    tradeable: true,
    recommended: true
  },
  TRENDING_DOWN_HIGH_VOL: {
    label: 'Trending Down (High Vol)',
    color: '#EF4444',
    icon: '📉⚡',
    tradeable: true
  },
  TRENDING_DOWN_LOW_VOL: {
    label: 'Trending Down (Low Vol)',
    color: '#F87171',
    icon: '📉✨',
    tradeable: true,
    recommended: true
  },
  RANGING_HIGH_VOL: {
    label: 'Ranging (High Vol)',
    color: '#F59E0B',
    icon: '↔️⚡',
    tradeable: false,
    warning: 'Choppy market - avoid trading'
  },
  RANGING_LOW_VOL: {
    label: 'Ranging (Low Vol)',
    color: '#FBBF24',
    icon: '↔️',
    tradeable: true,
    caution: true
  },
  TRANSITIONAL: {
    label: 'Transitional',
    color: '#6B7280',
    icon: '🔄',
    tradeable: false,
    warning: 'Uncertain direction - wait for clarity'
  },
  UNKNOWN: {
    label: 'Unknown',
    color: '#9CA3AF',
    icon: '❓',
    tradeable: false
  }
};

// Helper functions
export const getPairConfig = (pairId) => {
  return TRADING_PAIRS.find(p => p.id === pairId) || TRADING_PAIRS[0];
};

export const getActiveSession = (hourGMT) => {
  for (const [key, session] of Object.entries(TRADING_SESSIONS)) {
    if (session.start <= hourGMT && hourGMT < session.end) {
      return { name: key, ...session };
    }
  }
  return null;
};

export const getSignalStrength = (score) => {
  const absScore = Math.abs(score);
  if (absScore >= SIGNAL_THRESHOLDS.STRONG) return 'STRONG';
  if (absScore >= SIGNAL_THRESHOLDS.MEDIUM) return 'MEDIUM';
  if (absScore >= SIGNAL_THRESHOLDS.WEAK) return 'WEAK';
  return 'NONE';
};

export const getRegimeConfig = (regime) => {
  return MARKET_REGIMES[regime] || MARKET_REGIMES.UNKNOWN;
};

export default {
  TRADING_PAIRS,
  DEFAULT_PAIR,
  TIMEFRAMES,
  TRADING_SESSIONS,
  SIGNAL_THRESHOLDS,
  MARKET_REGIMES,
  getPairConfig,
  getActiveSession,
  getSignalStrength,
  getRegimeConfig
};
