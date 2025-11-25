import asyncio
import os
import sys
from datetime import datetime, timedelta
from backtest_oanda import OANDABacktestEngine

async def run_30day_backtest():
    # Configuration
    api_key = os.getenv("OANDA_API_KEY")
    if not api_key:
        print("Error: OANDA_API_KEY not found")
        return

    # Last 30 days
    end_date = datetime.now().strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=30)).strftime('%Y-%m-%d')
    
    instruments = ['GBP_USD', 'XAU_USD', 'USD_JPY']
    
    print(f"Running 30-Day Backtest ({start_date} to {end_date})")
    print("Strategy: H1 Day Trading (Votes: 1.5, Strength: 25%, Cooldown: 4h)")
    
    for instrument in instruments:
        print(f"\n{'='*60}")
        print(f"Testing {instrument}...")
        print(f"{'='*60}")
        
        engine = OANDABacktestEngine(
            api_key=api_key,
            initial_balance=10000,
            min_votes_required=1.5,
            min_strength=25.0
        )
        
        results = await engine.run_backtest(
            instrument,
            start_date,
            end_date,
            risk_per_trade=0.02
        )
        
        if results:
            engine.print_results(results)
            filename = f"backtest_{instrument}_30days.json"
            engine.save_results(results, filename)

if __name__ == "__main__":
    asyncio.run(run_30day_backtest())
