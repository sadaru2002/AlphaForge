import asyncio
import os
import logging
from datetime import datetime, timedelta
from dotenv import load_dotenv
from backtest_oanda import OANDABacktestEngine

# Load environment
load_dotenv()

logging.basicConfig(level=logging.WARNING)  # Less verbose for long test
logger = logging.getLogger(__name__)

async def run_1year_upgraded_test():
    """Run 1-year backtest with UPGRADED system."""
    
    api_key = os.getenv("OANDA_API_KEY")
    if not api_key:
        print("Error: OANDA_API_KEY not found")
        return
    
    # Test period: Last 365 days
    end_date = datetime.now()
    start_date = end_date - timedelta(days=365)
    
    instruments = ['GBP_USD', 'XAU_USD', 'USD_JPY']
    
    print("="*80)
    print("UPGRADED STRATEGY - 1 YEAR FULL BACKTEST")
    print("="*80)
    print(f"Period: {start_date.strftime('%Y-%m-%d')} to {end_date.strftime('%Y-%m-%d')}")
    print(f"\nUPGRADED PARAMETERS (Validated on 30-day test):")
    print(f"  • Win Rate Target: 50%+ (Achieved: 56% on GBP_USD)")
    print(f"  • Drawdown Target: <10% (Achieved: 5.88% on GBP_USD)")
    print(f"  • ADX Threshold: 22 (was 15)")
    print(f"  • ATR Minimum: 0.05% (was 0.02%)")
    print(f"  • Min Votes: 2.5 (was 2.0)")
    print(f"  • Min Strength: 35% (was 30%)")
    print("="*80)
    
    all_results = {}
    
    for instrument in instruments:
        print(f"\n{'='*80}")
        print(f"Testing {instrument} (This will take several minutes)...")
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
                print(f"\n{instrument} RESULTS (1 YEAR):")
                print(f"  Final Balance: ${results['final_balance']:,.2f}")
                print(f"  Net Profit: ${results['net_profit']:+,.2f}")
                print(f"  Return: {results['return_pct']:+.2f}%")
                print(f"  Total Trades: {results['total_trades']}")
                print(f"  Win Rate: {results['win_rate']:.2f}%")
                print(f"  Profit Factor: {results['profit_factor']:.2f}")
                print(f"  Max Drawdown: {results['max_drawdown']:.2f}%")
                print(f"  Avg Win: ${results['avg_win']:.2f}")
                print(f"  Avg Loss: ${results['avg_loss']:.2f}")
                
                # Win Rate Assessment
                if results['win_rate'] >= 50:
                    print(f"  ✅ WIN RATE TARGET MET: {results['win_rate']:.2f}% >= 50%")
                else:
                    print(f"  ⚠️  Win Rate: {results['win_rate']:.2f}% (Target: 50%+)")
                
                # Drawdown Assessment
                if results['max_drawdown'] < 10:
                    print(f"  ✅ DRAWDOWN TARGET MET: {results['max_drawdown']:.2f}% < 10%")
                else:
                    print(f"  ⚠️  Max Drawdown: {results['max_drawdown']:.2f}% (Target: <10%)")
                
                # Save to file
                filename = f"backtest_UPGRADED_{instrument}_1YEAR.json"
                import json
                with open(filename, 'w') as f:
                    json.dump(results, f, indent=2, default=str)
                print(f"\n  📄 Results saved to {filename}")
                
        except Exception as e:
            print(f"  ❌ Error testing {instrument}: {e}")
            logger.error(f"Backtest error for {instrument}: {e}", exc_info=True)
    
    # Summary
    print(f"\n{'='*80}")
    print("1-YEAR BACKTEST SUMMARY")
    print(f"{'='*80}")
    
    for instrument, results in all_results.items():
        status = "✅" if results['win_rate'] >= 50 and results['max_drawdown'] < 10 else "⚠️"
        print(f"\n{status} {instrument}:")
        print(f"    Win Rate: {results['win_rate']:.2f}% | Trades: {results['total_trades']} | Return: {results['return_pct']:+.2f}%")
        print(f"    Max DD: {results['max_drawdown']:.2f}% | Profit Factor: {results['profit_factor']:.2f}")
    
    print(f"\n{'='*80}")
    print("Test complete! Check JSON files for full trade details.")
    print(f"{'='*80}")

if __name__ == "__main__":
    asyncio.run(run_1year_upgraded_test())
