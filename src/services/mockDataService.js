// Mock data service for when backend is unavailable
class MockDataService {
  constructor() {
    this.mockPrices = {
      'XAUUSD': {
        bid: 4070.0,
        ask: 4071.0,
        spread: 1.0,
        spreadPips: 10.0,
        change: 0.05,
        direction: 'up',
        time: new Date().toISOString(),
        volume: { bid: 200, ask: 200 }
      },
      'GBPUSD': {
        bid: 1.3338,
        ask: 1.3340,
        spread: 0.0002,
        spreadPips: 2.0,
        change: -0.01,
        direction: 'down',
        time: new Date().toISOString(),
        volume: { bid: 500000, ask: 500000 }
      },
      'USDJPY': {
        bid: 151.92,
        ask: 151.94,
        spread: 0.02,
        spreadPips: 2.0,
        change: 0.02,
        direction: 'up',
        time: new Date().toISOString(),
        volume: { bid: 500000, ask: 500000 }
      }
    };
  }

  // Add small random variations to simulate real price movement
  addVariation() {
    Object.keys(this.mockPrices).forEach(symbol => {
      const price = this.mockPrices[symbol];
      const variation = (Math.random() - 0.5) * 0.0001;
      
      price.bid += variation;
      price.ask += variation;
      price.time = new Date().toISOString();
      
      // Randomly change direction
      if (Math.random() < 0.3) {
        price.direction = Math.random() < 0.5 ? 'up' : 'down';
        price.change = Math.random() * 0.1;
      }
    });
  }

  getAllPrices() {
    this.addVariation();
    return {
      prices: this.mockPrices,
      timestamp: new Date().toISOString(),
      source: 'mock'
    };
  }

  getPrice(symbol) {
    this.addVariation();
    return {
      data: this.mockPrices[symbol],
      timestamp: new Date().toISOString(),
      source: 'mock'
    };
  }

  health() {
    return {
      status: 'healthy',
      database: 'connected',
      oanda: 'mock',
      gemini: 'mock',
      timestamp: new Date().toISOString()
    };
  }
}

// Export for use in components
window.MockDataService = MockDataService;
