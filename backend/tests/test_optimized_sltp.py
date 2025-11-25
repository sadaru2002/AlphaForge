import asyncio
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from backtest_oanda import OANDABacktestEngine

# Load environment
load_dotenv()

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def run_optimized_test():
    """
    Run 30-day backtest with OPTIMIZED SL/TP levels.
    New: SL = 2.5x ATR, TP = 5.0x ATR (was 1.5x/3.0x)
    """
    
    api_key = os.getenv("OANDA_API_KEY")
    if not api_key:
        print("Error: OANDA_API_KEY not found")
        return
    
    # Test period: Last 30 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=30)
    
    instruments = ['GBP_USD', 'XAU_USD', 'USD_JPY']
    
    print("="*80)
    print("OPTIMIZED SL/TP - 30 DAY VALIDATION TEST")
    print("="*80)
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"\nOPTIMIZED SL/TP LEVELS (H1 Day Trading):")
    print(f"  • Stop Loss: 2.5x ATR (was 1.5x - scalping level)")
    print(f"  • Take Profit: 5.0x ATR (was 3.0x - scalping level)")
    print(f"  • Risk:Reward: 1:2 maintained")
    print(f"\nEXPECTED IMPROVEMENTS:")
    print(f"  • Win Rate: Should increase (less premature stops)")
    print(f"  • Profit Factor: Should increase (better execution)")
    print("="*80)
    
    all_results = {}
    
    for instrument in instruments:
        print(f"\n{'='*80}")
        print(f"Testing {instrument}...")
        print(f"{'='*80}")
        
        try:
            engine = OANDABacktestEngine(api_key, initial_balance=10000)
            
            # Run backtest
            results = await engine.run_backtest(
                instrument=instrument,
                start_date=start_date.strftime('%Y-%m-%d'),
                end_date=end_date.strftime('%Y-%m-%d')
            )
            
            if results:
                all_results[instrument] = results
                
                # Display results
                print(f"\n{instrument} RESULTS:")
                print(f"  Final Balance: ${results['final_balance']:,.2f}")
                print(f"  Net Profit: ${results['net_profit']:+,.2f}")
                print(f"  Return: {results['return_pct']:+.2f}%")
                print(f"  Total Trades: {results['total_trades']}")
                print(f"  Win Rate: {results['win_rate']:.2f}%")
                print(f"  Profit Factor: {results['profit_factor']:.2f}")
                print(f"  Max Drawdown: {results['max_drawdown']:.2f}%")
                
                # Save to file
                filename = f"backtest_OPTIMIZED_{instrument}_30days.json"
                import json
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                print(f"\n  ✅ Results saved to {filename}")
                
        except Exception as e:
            print(f"  ❌ Error testing {instrument}: {e}")
            logger.error(f"Backtest error for {instrument}: {e}", exc_info=True)
    
    # Comparison
    print(f"\n{'='*80}")
    print("COMPARISON: Old SL/TP vs Optimized SL/TP")
    print(f"{'='*80}")
    print("\nExpected: Higher win rate, better profit factor")
    print("Check results against previous 30-day test (1.5x/3.0x levels)")
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(run_optimized_test())
