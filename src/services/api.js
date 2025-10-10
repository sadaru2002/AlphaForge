// API service for backend communication
const API_BASE_URL = process.env.REACT_APP_API_BASE_URL || 'http://161.118.218.33:5000';

// Remove any trailing /api from the URL
const cleanApiUrl = API_BASE_URL.replace(/\/api$/, '');

class ApiService {
  constructor() {
    this.baseURL = cleanApiUrl;
  }

  async request(endpoint, options = {}) {
    try {
      const url = `${this.baseURL}${endpoint}`;
      console.log(`API Request: ${url}`); // Debug log
      
      const response = await fetch(url, {
        headers: {
          'Content-Type': 'application/json',
          ...options.headers,
        },
        ...options,
      });

      if (!response.ok) {
        const errorText = await response.text();
        console.error(`API Error ${response.status}: ${errorText}`);
        throw new Error(`HTTP error! status: ${response.status} - ${errorText}`);
      }

      const data = await response.json();
      console.log(`API Response: ${endpoint}`, data); // Debug log
      return data;
    } catch (error) {
      console.error(`API request failed for ${endpoint}:`, error);
      throw error;
    }
  }

  // Health check
  async health() {
    return this.request('/health');
  }

  // Get available symbols
  async getSymbols() {
    return this.request('/symbols');
  }

  // Get current price for symbol
  async getPrice(symbol) {
    return this.request(`/price/${symbol}`);
  }

  // Get live price from Alpha Vantage
  async getLivePrice(symbol, source = 'fx') {
    return this.request(`/live_price/${symbol}?source=${source}`);
  }

  // Get trading signals
  async getSignals(symbol) {
    return this.request(`/signals/${symbol}`);
  }

  // Run quick backtest
  async runBacktest(symbol, days = 30) {
    return this.request(`/backtest/quick?symbol=${symbol}&days=${days}`);
  }

  // Run full backtest
  async runFullBacktest(symbol, startDate, endDate) {
    const params = new URLSearchParams({
      symbol,
      ...(startDate && { start_date: startDate }),
      ...(endDate && { end_date: endDate }),
    });
    return this.request(`/backtest/full?${params}`);
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
}

// Create singleton instance
const apiService = new ApiService();

export default apiService;
