// API service for backend communication
// Use environment variable or fallback to localhost:5000 (AlphaForge backend port)
const API_BASE_URL = process.env.REACT_APP_API_URL || 'http://localhost:5000';

// Debug logging
console.log('🔧 API Configuration:');
console.log('  - Environment:', process.env.NODE_ENV);
console.log('  - API Base URL:', API_BASE_URL);
console.log('  - Current Origin:', window.location.origin);
console.log('  - Protocol:', window.location.protocol);

// Remove any trailing slashes or /api (but keep '/' for relative paths)
const cleanApiUrl = API_BASE_URL === '/' ? '' : API_BASE_URL.replace(/\/api$/, '').replace(/\/$/, '');

class ApiService {
  constructor() {
    // For Vercel proxy, use empty string as base URL (relative paths)
    // Otherwise try multiple backend URLs for better reliability
    this.baseURLs = API_BASE_URL === '/' ? [''] : [
      cleanApiUrl,              // Primary backend
      'http://127.0.0.1:5000',  // Alternative localhost
      'http://localhost:5000'    // Explicit localhost
    ];
    this.currentURLIndex = 0;
    this.baseURL = this.baseURLs[this.currentURLIndex];
    this.maxRetries = 3;
    this.retryDelay = 1000; // 1 second
  }

  // Switch to next available backend URL
  switchToNextURL() {
    this.currentURLIndex = (this.currentURLIndex + 1) % this.baseURLs.length;
    this.baseURL = this.baseURLs[this.currentURLIndex];
    console.log(`🔄 Switched to backend: ${this.baseURL}`);
  }

  // Reset to primary URL
  resetToPrimaryURL() {
    this.currentURLIndex = 0;
    this.baseURL = this.baseURLs[this.currentURLIndex];
    console.log(`🔄 Reset to primary backend: ${this.baseURL}`);
  }

  // Data transformation functions
  transformSignal(backendSignal) {
    // Backend now sends correct field names, so just pass through with minor adjustments
    return {
      id: backendSignal.id,
      direction: backendSignal.direction || backendSignal.signal_type, // Support both old and new
      symbol: backendSignal.symbol,
      entry: backendSignal.entry || backendSignal.entry_price, // Support both old and new
      tp1: backendSignal.tp1 || backendSignal.take_profit_1, // Support both old and new
      tp2: backendSignal.tp2 || backendSignal.take_profit_2, // Support both old and new
      sl: backendSignal.stop_loss,
      stop_loss: backendSignal.stop_loss,
      ml_probability: backendSignal.ml_probability || (backendSignal.confidence_score || 0) / 100,
      confidence_score: backendSignal.confidence_score,
      timestamp: backendSignal.timestamp,
      setup_type: backendSignal.setup_type,
      daily_bias: backendSignal.daily_bias,
      position_size: backendSignal.position_size,
      outcome: backendSignal.outcome,
      actual_pnl: backendSignal.actual_pnl,
      was_traded: backendSignal.was_traded,
      // Use pips from backend if available, otherwise calculate
      tp1_pips: backendSignal.tp1_pips || (backendSignal.tp1 ? Math.abs(backendSignal.tp1 - backendSignal.entry) * 10000 : 0),
      tp2_pips: backendSignal.tp2_pips || (backendSignal.tp2 ? Math.abs(backendSignal.tp2 - backendSignal.entry) * 10000 : 0),
      sl_pips: backendSignal.sl_pips || (backendSignal.stop_loss ? Math.abs(backendSignal.stop_loss - backendSignal.entry) * 10000 : 0),
      rr_ratio: backendSignal.rr_ratio || backendSignal.risk_reward_1 || '1:2',
      strategies: backendSignal.strategies || (backendSignal.strategy_used ? [backendSignal.strategy_used] : ['SMC', 'ICT']),
      reasoning: backendSignal.reasoning || backendSignal.gemini_reasoning
    };
  }

  transformPrices(backendPrices) {
    const transformed = {};

    // OANDA to MT5 symbol mapping
    const symbolMapping = {
      'XAU_USD': 'XAUUSD',
      'GBP_USD': 'GBPUSD',
      'USD_JPY': 'USDJPY',
      'EUR_USD': 'EURUSD',
      'AUD_USD': 'AUDUSD',
      'USD_CAD': 'USDCAD',
      'USD_CHF': 'USDCHF',
      'NZD_USD': 'NZDUSD',
      'EUR_JPY': 'EURJPY',
      'GBP_JPY': 'GBPJPY',
      'EUR_GBP': 'EURGBP',
      'AUD_JPY': 'AUDJPY'
    };

    for (const [oandaSymbol, data] of Object.entries(backendPrices)) {
      // Convert OANDA symbol to MT5 format
      const mt5Symbol = symbolMapping[oandaSymbol] || oandaSymbol.replace('_', '');

      // Calculate spread in pips
      const spread = data.ask - data.bid;
      const spreadPips = mt5Symbol === 'XAUUSD' ? spread * 10 : spread * 10000;

      transformed[mt5Symbol] = {
        bid: data.bid,
        ask: data.ask,
        spread: spread,
        spreadPips: spreadPips,
        change: 0, // Will be calculated when we have previous prices
        direction: 'up', // Will be calculated when we have previous prices
        time: data.time,
        volume: {
          bid: data.bid_volume || 0,
          ask: data.ask_volume || 0
        },
        // Keep original OANDA symbol for reference
        oandaSymbol: oandaSymbol
      };
    }
    return transformed;
  }

  async request(endpoint, options = {}) {
    let lastError = null;

    // Try each backend URL
    for (let attempt = 0; attempt < this.maxRetries; attempt++) {
      try {
        const url = `${this.baseURL}${endpoint}`;
        console.log(`📡 API Request (attempt ${attempt + 1}): ${url}`);

        const response = await fetch(url, {
          headers: {
            'Content-Type': 'application/json',
            'Accept': 'application/json',
            ...options.headers,
          },
          mode: 'cors',
          credentials: 'omit',
          // Add timeout and retry logic
          signal: AbortSignal.timeout(5000), // 5 second timeout
          ...options,
        });

        console.log(`✅ Response Status: ${response.status}`);

        if (!response.ok) {
          const errorText = await response.text();
          console.error(`❌ API Error ${response.status}: ${errorText}`);
          throw new Error(`HTTP ${response.status}: ${errorText || response.statusText}`);
        }

        const data = await response.json();
        console.log(`📦 API Response Data:`, data);

        // Reset to primary URL on success
        if (this.currentURLIndex !== 0) {
          this.resetToPrimaryURL();
        }

        return data;
      } catch (error) {
        console.error(`❌ API Request Failed (attempt ${attempt + 1}): ${endpoint}`, error);
        lastError = error;

        // Switch to next URL if this attempt failed
        if (attempt < this.maxRetries - 1) {
          this.switchToNextURL();
          // Wait before retrying
          await new Promise(resolve => setTimeout(resolve, this.retryDelay));
        }
      }
    }

    // All attempts failed, throw the last error with enhanced messaging
    console.error(`❌ All API attempts failed for: ${endpoint}`);

    if (lastError.message.includes('Failed to fetch')) {
      throw new Error(`Cannot connect to any backend server. Tried: ${this.baseURLs.join(', ')}`);
    } else if (lastError.message.includes('NetworkError') || lastError.message.includes('CORS')) {
      throw new Error(`CORS error: Backend servers are not allowing requests from ${window.location.origin}`);
    } else if (window.location.protocol === 'https:' && this.baseURLs.some(url => url.startsWith('http:'))) {
      throw new Error(`Mixed Content: Cannot connect to HTTP backends from HTTPS frontend. Use HTTPS backends or HTTP frontend.`);
    } else if (lastError.name === 'TimeoutError') {
      throw new Error(`Request timeout: All backend servers are not responding within 5 seconds.`);
    }

    throw lastError;
  }

  // Health check
  async health() {
    return this.request('/health');
  }

  // Get available symbols
  async getSymbols() {
    return this.request('/api/symbols');
  }

  // Get current price for symbol with fallback to mock data
  async getPrice(symbol) {
    try {
      return await this.request(`/api/prices/live/${symbol}`);
    } catch (error) {
      console.warn('🔄 Backend unavailable, using mock data:', error.message);
      return this.getMockPrice(symbol);
    }
  }

  // Get all prices with fallback to mock data
  async getAllPrices() {
    try {
      // First try to get real OANDA data directly
      const realData = await this.getRealOandaPrices();
      if (realData.source === 'OANDA_REAL') {
        console.log('✅ Using REAL OANDA data');
        return realData;
      }

      // Fallback to backend
      const response = await this.request('/api/prices/live');
      if (response.prices) {
        response.prices = this.transformPrices(response.prices);
      }
      return response;
    } catch (error) {
      console.warn('🔄 Backend unavailable, using mock data:', error.message);
      return this.getMockPrices();
    }
  }

  // Get trading signals
  async getSignals(symbol) {
    const endpoint = symbol ? `/api/signals?symbol=${symbol}` : '/api/signals';
    const response = await this.request(endpoint);
    if (response.signals) {
      response.signals = response.signals.map(signal => this.transformSignal(signal));
    }
    return response;
  }

  // Journal API methods
  async getJournalEntries() {
    return this.request('/api/journal/entries');
  }

  async createJournalEntry(entry) {
    return this.request('/api/journal/entries', {
      method: 'POST',
      body: JSON.stringify(entry)
    });
  }

  async updateJournalEntry(entryId, entry) {
    return this.request(`/api/journal/entries/${entryId}`, {
      method: 'PUT',
      body: JSON.stringify(entry)
    });
  }

  async deleteJournalEntry(entryId) {
    return this.request(`/api/journal/entries/${entryId}`, {
      method: 'DELETE'
    });
  }

  async getJournalStatistics() {
    return this.request('/api/journal/statistics');
  }

  // Analytics and Stats API methods
  async getPerformanceStats() {
    return this.request('/api/signals/performance');
  }

  async getSignalStatistics() {
    return this.request('/api/signals/statistics');
  }

  async getSystemStats() {
    return this.request('/api/stats');
  }

  // Signal management
  async createSignal(signalData) {
    return this.request('/api/signals', {
      method: 'POST',
      body: JSON.stringify(signalData)
    });
  }

  async updateSignalStatus(signalId, status) {
    return this.request(`/api/signals/${signalId}/status`, {
      method: 'PUT',
      body: JSON.stringify({ status })
    });
  }

  async getActiveSignals() {
    return this.request('/api/signals/active');
  }

  async getPendingSignals() {
    return this.request('/api/signals/pending');
  }

  // Strategy control
  async startStrategy() {
    return this.request('/api/strategy/start', {
      method: 'POST'
    });
  }

  async stopStrategy() {
    return this.request('/api/strategy/stop', {
      method: 'POST'
    });
  }

  // Signal generation
  async generateSignals(instrument = null) {
    const endpoint = instrument ? `/api/signals/generate/${instrument}` : '/api/signals/generate';
    return this.request(endpoint, {
      method: 'POST'
    });
  }

  // Run backtest with user strategy
  async runBacktest(strategyCode, symbol, startDate, endDate) {
    return this.request('/api/backtest/run', {
      method: 'POST',
      body: JSON.stringify({
        strategy_code: strategyCode,
        symbol: symbol,
        start_date: startDate,
        end_date: endDate,
        initial_capital: 10000,
        spread_pips: 2.0
      })
    });
  }

  // Get strategy template
  async getStrategyTemplate() {
    return this.request('/api/backtest/template');
  }

  // Get available symbols
  async getAvailableSymbols() {
    return this.request('/api/backtest/symbols');
  }

  // Save strategy (for backtesting)
  async saveStrategy(name, description, strategyCode, symbols) {
    return this.request('/api/backtest/strategy', {
      method: 'POST',
      body: JSON.stringify({
        name: name,
        description: description,
        strategy_code: strategyCode,
        symbols: symbols
      })
    });
  }

  // Get system status
  async getStatus() {
    return this.request('/health');
  }

  // Get analysis status from enhanced backend
  async getAnalysisStatus() {
    return this.request('/api/analysis/status');
  }

  // Get latest analysis results
  async getLatestAnalysis() {
    return this.request('/api/analysis/latest');
  }

  // Get analysis history
  async getAnalysisHistory() {
    return this.request('/api/analysis/history');
  }

  // Get multiple symbol prices
  async getMultiplePrices(symbols) {
    const promises = symbols.map(symbol => this.getPrice(symbol));
    return Promise.allSettled(promises);
  }

  // Get multiple symbol signals
  async getMultipleSignals(symbols) {
    const promises = symbols.map(symbol => this.getSignals(symbol));
    return Promise.allSettled(promises);
  }

  // Real OANDA data methods
  async getRealOandaPrices() {
    try {
      // Use your actual OANDA credentials for real data
      const response = await fetch('https://api-fxpractice.oanda.com/v3/accounts/101-001-37260967-001/pricing?instruments=XAU_USD%2CGBP_USD%2CUSD_JPY', {
        headers: {
          'Authorization': 'Bearer 11bacc1becaf8df27bfd105a828ba70b-c9f535661ccd35bbd1310bffe8b79595',
          'Content-Type': 'application/json'
        }
      });

      if (response.ok) {
        const data = await response.json();
        const prices = {};

        if (data.prices) {
          data.prices.forEach(price => {
            const symbol = price.instrument.replace('_', '');
            prices[symbol] = {
              bid: parseFloat(price.bids[0].price),
              ask: parseFloat(price.asks[0].price),
              spread: parseFloat(price.asks[0].price) - parseFloat(price.bids[0].price),
              spreadPips: symbol === 'XAUUSD' ?
                ((parseFloat(price.asks[0].price) - parseFloat(price.bids[0].price)) * 10) :
                ((parseFloat(price.asks[0].price) - parseFloat(price.bids[0].price)) * 10000),
              time: price.time,
              volume: {
                bid: parseFloat(price.bids[0].liquidity),
                ask: parseFloat(price.asks[0].liquidity)
              }
            };
          });
        }

        return {
          prices: prices,
          timestamp: new Date().toISOString(),
          source: 'OANDA_REAL'
        };
      }
    } catch (error) {
      console.warn('Real OANDA fetch failed:', error);
    }

    // Fallback to realistic mock data
    return this.getMockPrices();
  }

  // Mock data fallback methods
  getMockPrices() {
    const mockPrices = {
      'XAUUSD': {
        bid: 4070.0 + (Math.random() - 0.5) * 2,
        ask: 4071.0 + (Math.random() - 0.5) * 2,
        spread: 1.0,
        spreadPips: 10.0,
        change: (Math.random() - 0.5) * 0.1,
        direction: Math.random() < 0.5 ? 'up' : 'down',
        time: new Date().toISOString(),
        volume: { bid: 200, ask: 200 }
      },
      'GBPUSD': {
        bid: 1.3338 + (Math.random() - 0.5) * 0.0002,
        ask: 1.3340 + (Math.random() - 0.5) * 0.0002,
        spread: 0.0002,
        spreadPips: 2.0,
        change: (Math.random() - 0.5) * 0.01,
        direction: Math.random() < 0.5 ? 'up' : 'down',
        time: new Date().toISOString(),
        volume: { bid: 500000, ask: 500000 }
      },
      'USDJPY': {
        bid: 151.92 + (Math.random() - 0.5) * 0.02,
        ask: 151.94 + (Math.random() - 0.5) * 0.02,
        spread: 0.02,
        spreadPips: 2.0,
        change: (Math.random() - 0.5) * 0.02,
        direction: Math.random() < 0.5 ? 'up' : 'down',
        time: new Date().toISOString(),
        volume: { bid: 500000, ask: 500000 }
      }
    };

    return {
      prices: mockPrices,
      timestamp: new Date().toISOString(),
      source: 'mock'
    };
  }

  getMockPrice(symbol) {
    const mockPrices = this.getMockPrices();
    return {
      data: mockPrices.prices[symbol],
      timestamp: new Date().toISOString(),
      source: 'mock'
    };
  }
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;
