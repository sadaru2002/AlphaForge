import asyncio
import os
import sys
from datetime import datetime, timedelta

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend', 'backtesting'))

from backtest_oanda import OANDABacktestEngine

async def test_today_signals():
    # Configuration
    api_key = os.getenv("OANDA_API_KEY")
    if not api_key:
        print("Error: OANDA_API_KEY not found")
        return

    # Set dates
    today = datetime.now().strftime('%Y-%m-%d')
    # Start 5 days ago to ensure enough data for indicators (lookback=500 candles)
    start_date = (datetime.now() - timedelta(days=5)).strftime('%Y-%m-%d')
    # End date is tomorrow to include all of today
    end_date = (datetime.now() + timedelta(days=1)).strftime('%Y-%m-%d')
    
    instruments = ['GBP_USD', 'XAU_USD', 'USD_JPY']
    
    print(f"\n{'='*80}")
    print(f"TESTING SIGNAL GENERATION FOR TODAY ({today})")
    print(f"{'='*80}")
    
    for instrument in instruments:
        print(f"\nChecking {instrument}...")
        
        engine = OANDABacktestEngine(
            api_key=api_key,
            initial_balance=10000,
            min_votes_required=2.0,  # Standard setting
            min_strength=30.0        # Standard setting
        )
        
        # Run backtest focused on today
        results = await engine.run_backtest(
            instrument,
            start_date,
            end_date,
            risk_per_trade=0.02,
            focus_date=today
        )
        
        if results:
            print(f"\nResults for {instrument}:")
            print(f"Signals Generated: {results['total_trades']}")
            if results['trades']:
                for trade in results['trades']:
                    print(f"  - {trade['direction']} @ {trade['entry_time']} (P&L: ${trade['pnl']:.2f})")
            else:
                print("  - No trades executed today.")
        else:
            print(f"  - No data or error for {instrument}")

if __name__ == "__main__":
    asyncio.run(test_today_signals())
