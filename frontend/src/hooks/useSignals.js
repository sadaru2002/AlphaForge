/**
 * Custom React Hook for Signals Management
 * Implements React Query for intelligent caching and background updates
 */
import { useQuery, useQueryClient } from '@tanstack/react-query';
import { useCallback, useMemo } from 'react';
import apiService from '../services/api';

const QUERY_KEYS = {
  signals: ['signals'],
  activeSignals: ['signals', 'active'],
  statistics: ['signals', 'statistics'],
  performance: (symbol) => ['signals', 'performance', symbol],
};

// Stale time: 30 seconds (data is considered fresh for 30s)
// Cache time: 5 minutes (data stays in cache for 5m after becoming stale)
const DEFAULT_OPTIONS = {
  staleTime: 30 * 1000,
  cacheTime: 5 * 60 * 1000,
  refetchOnWindowFocus: true,
  refetchOnReconnect: true,
};

/**
 * Hook for fetching all signals with intelligent caching
 */
export const useSignals = (options = {}) => {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: QUERY_KEYS.signals,
    queryFn: async () => {
      const response = await apiService.getSignals();
      return response.data || response;
    },
    ...DEFAULT_OPTIONS,
    ...options,
  });

  // Optimistic update helper
  const updateSignalOptimistically = useCallback((signalId, updates) => {
    queryClient.setQueryData(QUERY_KEYS.signals, (oldData) => {
      if (!oldData) return oldData;
      return oldData.map(signal => 
        signal.id === signalId ? { ...signal, ...updates } : signal
      );
    });
  }, [queryClient]);

  // Prefetch next page or related data
  const prefetchStatistics = useCallback(() => {
    queryClient.prefetchQuery({
      queryKey: QUERY_KEYS.statistics,
      queryFn: () => apiService.getSignalStatistics(),
      staleTime: 60 * 1000, // 1 minute
    });
  }, [queryClient]);

  return {
    ...query,
    updateSignalOptimistically,
    prefetchStatistics,
  };
};

/**
 * Hook for active signals only
 */
export const useActiveSignals = (options = {}) => {
  return useQuery({
    queryKey: QUERY_KEYS.activeSignals,
    queryFn: async () => {
      const response = await apiService.getActiveSignals();
      return response.data || response;
    },
    ...DEFAULT_OPTIONS,
    refetchInterval: 10 * 1000, // Auto-refresh every 10 seconds for active trades
    ...options,
  });
};

/**
 * Hook for signal statistics with memoization
 */
export const useSignalStatistics = (options = {}) => {
  const query = useQuery({
    queryKey: QUERY_KEYS.statistics,
    queryFn: async () => {
      const response = await apiService.getSignalStatistics();
      return response.data || response;
    },
    staleTime: 60 * 1000, // Statistics can be stale for 1 minute
    cacheTime: 10 * 60 * 1000, // Keep in cache for 10 minutes
    ...options,
  });

  // Memoized computed values
  const computedStats = useMemo(() => {
    if (!query.data) return null;

    const stats = query.data;
    return {
      ...stats,
      winRate: stats.total_trades > 0 
        ? ((stats.winning_trades / stats.total_trades) * 100).toFixed(2)
        : 0,
      avgWin: stats.winning_trades > 0
        ? (stats.total_profit / stats.winning_trades).toFixed(2)
        : 0,
      avgLoss: stats.losing_trades > 0
        ? (Math.abs(stats.total_loss) / stats.losing_trades).toFixed(2)
        : 0,
      profitFactor: stats.total_loss !== 0
        ? Math.abs(stats.total_profit / stats.total_loss).toFixed(2)
        : stats.total_profit > 0 ? '∞' : '0',
    };
  }, [query.data]);

  return {
    ...query,
    stats: computedStats,
  };
};

/**
 * Hook for symbol performance with automatic prefetching
 */
export const useSymbolPerformance = (symbol, options = {}) => {
  const queryClient = useQueryClient();

  const query = useQuery({
    queryKey: QUERY_KEYS.performance(symbol),
    queryFn: async () => {
      const response = await apiService.getSymbolPerformance(symbol);
      return response.data || response;
    },
    enabled: !!symbol, // Only run if symbol is provided
    staleTime: 2 * 60 * 1000, // 2 minutes
    ...options,
  });

  // Prefetch related symbols
  const prefetchRelatedSymbols = useCallback((symbols) => {
    symbols.forEach(sym => {
      queryClient.prefetchQuery({
        queryKey: QUERY_KEYS.performance(sym),
        queryFn: () => apiService.getSymbolPerformance(sym),
      });
    });
  }, [queryClient]);

  return {
    ...query,
    prefetchRelatedSymbols,
  };
};

/**
 * Hook for filtered and sorted signals with memoization
 */
export const useFilteredSignals = (filters = {}) => {
  const { data: signals, isLoading, error } = useSignals();

  const filteredSignals = useMemo(() => {
    if (!signals) return [];

    let result = [...signals];

    // Apply status filter
    if (filters.status && filters.status !== 'all') {
      result = result.filter(s => s.status === filters.status);
    }

    // Apply symbol filter
    if (filters.symbol && filters.symbol !== 'all') {
      result = result.filter(s => s.symbol === filters.symbol);
    }

    // Apply outcome filter
    if (filters.outcome && filters.outcome !== 'all') {
      result = result.filter(s => s.outcome === filters.outcome);
    }

    // Apply date range filter
    if (filters.startDate) {
      const start = new Date(filters.startDate);
      result = result.filter(s => new Date(s.timestamp) >= start);
    }
    if (filters.endDate) {
      const end = new Date(filters.endDate);
      result = result.filter(s => new Date(s.timestamp) <= end);
    }

    // Apply sorting
    if (filters.sortBy) {
      result.sort((a, b) => {
        switch (filters.sortBy) {
          case 'timestamp':
            return new Date(b.timestamp) - new Date(a.timestamp);
          case 'profit':
            return (b.actual_pnl || 0) - (a.actual_pnl || 0);
          case 'pips':
            return (b.pips_gained || 0) - (a.pips_gained || 0);
          case 'duration':
            return (b.duration_hours || 0) - (a.duration_hours || 0);
          default:
            return 0;
        }
      });
    }

    return result;
  }, [signals, filters]);

  return {
    signals: filteredSignals,
    isLoading,
    error,
    totalCount: signals?.length || 0,
    filteredCount: filteredSignals.length,
  };
};

export default {
  useSignals,
  useActiveSignals,
  useSignalStatistics,
  useSymbolPerformance,
  useFilteredSignals,
};
