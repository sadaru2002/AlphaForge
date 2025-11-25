# AlphaForge Backtesting Guide

## Overview
Test the AlphaForge-enhanced strategy on real historical data from OANDA.

## Quick Start

### Run the August 2024 monthly backtest (multi-instrument)
If you want to run a ready-made August 2024 backtest for GBP_USD, XAU_USD, and USD_JPY with the current lowered thresholds:

```powershell
# From repo root (PowerShell)
./run_august_backtest.ps1
```

This will prompt for your OANDA API key if not already set, run the backtest for all three instruments, and save per-instrument results plus an aggregated summary under `backend/backtest_results/`.

### 1. Set OANDA API Key
```powershell
# Windows PowerShell
$env:OANDA_API_KEY = "your-api-key-here"

# Or add to your system environment variables
```

### 2. Run Backtest
```bash
cd backend
python backtest_oanda.py
```

## Configuration

### Default Settings (in `backtest_oanda.py`)
```python
instrument = 'GBP_USD'
start_date = '2024-10-01'
end_date = '2024-11-01'
initial_balance = 10000
risk_per_trade = 0.02  # 2% per trade
```

### Customize Your Backtest
Edit these variables in `backtest_oanda.py`:

```python
# Test different pairs
instrument = 'XAU_USD'  # Gold
instrument = 'USD_JPY'  # Yen

# Test different periods
start_date = '2024-08-01'  # August 2024
end_date = '2024-11-01'    # November 2024

# Test different capital
initial_balance = 5000   # $5k account
initial_balance = 50000  # $50k account

# Test different risk levels
risk_per_trade = 0.01  # Conservative (1%)
risk_per_trade = 0.02  # Moderate (2%)
risk_per_trade = 0.03  # Aggressive (3%)
```

## What the Backtest Does

### 1. Fetches Historical Data
- Downloads M5 (5-minute) candles from OANDA
- Automatically handles API rate limits
- Converts to multi-timeframe (M5, M15, H1)

### 2. Simulates Trading
- Uses **AlphaForge indicator voting system**
- Requires **3+ indicator agreement**
- Applies **4 quality filters**:
  - Volatility check (0.05% ≤ ATR% ≤ 0.25%)
  - Minimum strength (≥50%)
  - ADX trend strength (≥15)
  - Spread check (≤2 pips)

### 3. Risk Management
- Position sizing based on risk percentage
- Stop loss: 1.5× ATR from entry
- Take profit: 3.0× ATR from entry (2:1 risk/reward)
- Tracks max drawdown

### 4. Performance Metrics
- **Win Rate**: % of winning trades
- **Profit Factor**: Total profit ÷ Total loss
- **Expectancy**: Average $ per trade
- **Max Drawdown**: Largest equity decline
- **Return %**: Total return on initial balance

## Expected Output

```
🚀 AlphaForge Backtest Engine
================================================================================
Strategy: AlphaForge Enhanced (Indicator Voting System)
Instrument: GBP_USD
Period: 2024-10-01 to 2024-11-01
Initial Balance: $10,000.00
Risk per Trade: 2.0%
================================================================================

Fetching GBP_USD data from 2024-10-01 to 2024-11-01...
Fetched 5000 candles, total: 5000
Total candles fetched: 8640

Running backtest simulation...

📈 OPENED BUY @ 1.26543 | SL: 1.26321 | TP: 1.27087 | Size: 90.09 | Strength: 75.0%
✅ CLOSED BUY @ 1.27087 | P&L: +$49.00 (+122.5%) | Reason: Take Profit | Balance: $10,049.00

📈 OPENED SELL @ 1.26789 | SL: 1.27011 | TP: 1.26345 | Size: 90.09 | Strength: 68.5%
❌ CLOSED SELL @ 1.27011 | P&L: -$20.00 (-100.0%) | Reason: Stop Loss | Balance: $10,029.00

================================================================================
BACKTEST RESULTS
================================================================================
Period: 2024-10-01 to 2024-11-01

📊 PERFORMANCE SUMMARY
────────────────────────────────────────────────────────────────────────────────
Initial Balance:     $  10,000.00
Final Balance:       $  11,250.00
Net Profit:          $   1,250.00
Return:                     12.50%

📈 TRADE STATISTICS
────────────────────────────────────────────────────────────────────────────────
Total Trades:                  25
Winning Trades:                17 (68.0%)
Losing Trades:                  8 (32.0%)

💰 PROFIT METRICS
────────────────────────────────────────────────────────────────────────────────
Average Win:         $     110.29
Average Loss:        $      50.00
Profit Factor:              3.75
Expectancy:          $      50.00

📉 RISK METRICS
────────────────────────────────────────────────────────────────────────────────
Max Drawdown:                 8.50%
================================================================================

✅ Backtest complete! Results saved to backtest_results_GBP_USD_20241112_143022.json
```

## Results File Structure

```json
{
  "start_date": "2024-10-01",
  "end_date": "2024-11-01",
  "initial_balance": 10000,
  "final_balance": 11250.0,
  "net_profit": 1250.0,
  "return_pct": 12.5,
  "total_trades": 25,
  "winning_trades": 17,
  "losing_trades": 8,
  "win_rate": 68.0,
  "avg_win": 110.29,
  "avg_loss": 50.0,
  "profit_factor": 3.75,
  "max_drawdown": 8.5,
  "expectancy": 50.0,
  "trades": [
    {
      "entry_time": "2024-10-05 14:35:00",
      "exit_time": "2024-10-05 16:20:00",
      "direction": "BUY",
      "entry_price": 1.26543,
      "exit_price": 1.27087,
      "position_size": 90.09,
      "pnl": 49.0,
      "pnl_pct": 0.49,
      "balance": 10049.0,
      "reason": "Take Profit",
      "signal_strength": 75.0,
      "buy_votes": 4.5,
      "sell_votes": 1.0
    }
  ]
}
```

## Analyzing Results

### Good Performance Indicators
✅ **Win Rate**: 60-70% (AlphaForge target)
✅ **Profit Factor**: ≥2.0 (making $2 for every $1 lost)
✅ **Max Drawdown**: <15% (capital preservation)
✅ **Expectancy**: Positive (profitable over time)

### Warning Signs
⚠️ **Win Rate**: <50% (strategy not working)
⚠️ **Profit Factor**: <1.5 (barely profitable)
⚠️ **Max Drawdown**: >20% (too risky)
⚠️ **Total Trades**: <10 (not enough data)

## Advanced Usage

### Test Multiple Pairs
Create a script to test all 3 pairs:

```python
async def test_all_pairs():
    pairs = ['GBP_USD', 'XAU_USD', 'USD_JPY']
    
    for pair in pairs:
        engine = OANDABacktestEngine(api_key, 10000)
        results = await engine.run_backtest(pair, '2024-10-01', '2024-11-01')
        
        if results:
            engine.print_results(results)
            engine.save_results(results, f'backtest_{pair}.json')
```

### Test Different Risk Levels
```python
risk_levels = [0.01, 0.02, 0.03]  # 1%, 2%, 3%

for risk in risk_levels:
    engine = OANDABacktestEngine(api_key, 10000)
    results = await engine.run_backtest('GBP_USD', '2024-10-01', '2024-11-01', risk)
    print(f"Risk {risk*100}%: Win Rate = {results['win_rate']:.1f}%")
```

### Compare Before/After AlphaForge
1. **Backup old strategy** (if you have it)
2. Run backtest with old strategy → save results
3. Run backtest with AlphaForge → save results
4. Compare win rates and profit factors

## Troubleshooting

### Error: "OANDA_API_KEY not found"
```powershell
# Set in PowerShell
$env:OANDA_API_KEY = "your-key-here"

# Verify
echo $env:OANDA_API_KEY
```

### Error: "No data fetched"
- Check date range (must be historical data)
- Verify instrument format ('GBP_USD' not 'GBPUSD')
- Check OANDA API key is valid

### Error: "No trades executed"
- Filters may be too strict
- Try longer time period (2-3 months)
- Check if data has sufficient volatility

### Low Win Rate (<50%)
- Check if filters are working correctly
- Verify indicator calculations
- Test on different market conditions

## Next Steps

1. **Run Initial Test** (1 month)
   ```bash
   python backtest_oanda.py
   ```

2. **Analyze Results**
   - Check win rate vs target (60-70%)
   - Review trade distribution
   - Identify best/worst trades

3. **Optimize Parameters** (if needed)
   - Adjust filter thresholds
   - Test different risk levels
   - Try different timeframes

4. **Extended Backtest** (3-6 months)
   - More data = more reliable results
   - Test across different market regimes
   - Validate consistency

5. **Forward Test** (paper trading)
   - Test on live data (no real money)
   - Verify results match backtest
   - Build confidence before live trading

## Performance Expectations

Based on AlphaForge methodology:

| Metric | Target | Acceptable |
|--------|--------|------------|
| Win Rate | 60-70% | 55-75% |
| Profit Factor | 2.0-3.0 | 1.5-4.0 |
| Max Drawdown | <15% | <20% |
| Signals/Day | 5-7 | 3-10 |
| Avg Risk/Reward | 1:2 | 1:1.5 |

## Important Notes

⚠️ **Past Performance ≠ Future Results**
- Backtest shows what WOULD have happened
- Market conditions change
- Use as guidance, not guarantee

⚠️ **Data Quality**
- OANDA practice data may differ from live
- Spread/slippage simplified in backtest
- Real trading will have additional costs

⚠️ **Strategy Validation**
- Test on multiple periods (different market conditions)
- Compare to baseline (buy & hold, simple MA)
- Look for consistent performance, not just high returns

✅ **Use Backtest To**
- Validate AlphaForge indicator voting works
- Identify optimal risk settings
- Build confidence in strategy
- Understand drawdown expectations

❌ **Don't Use Backtest To**
- Predict exact future returns
- Over-optimize parameters (curve fitting)
- Replace forward testing
- Guarantee profits

