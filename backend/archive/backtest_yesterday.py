#!/usr/bin/env python3
"""
Backtest AlphaForge Strategy for Yesterday's Data
Uses OANDA historical data to test strategy performance
"""

from datetime import datetime, timedelta
from oanda_backtest_engine import OANDAHistoricalBacktester
import json

def run_yesterday_backtest():
    """Run backtest for yesterday's trading data"""
    
    # Calculate yesterday's date
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_str = yesterday.strftime('%Y-%m-%d')
    
    # For forex markets, we might want to go back a few days to ensure we have trading data
    # (weekends have no forex data)
    start_date = (yesterday - timedelta(days=3)).strftime('%Y-%m-%d')
    end_date = yesterday_str
    
    print("="*80)
    print("🚀 ALPHAFORGE YESTERDAY BACKTEST")
    print("="*80)
    print(f"📅 Testing period: {start_date} to {end_date}")
    print(f"🎯 Target date: {yesterday_str} (Yesterday)")
    print("="*80)
    
    try:
        # Initialize backtester
        backtester = OANDAHistoricalBacktester()
        
        # Test multiple instruments
        instruments = ["GBP_USD", "EUR_USD", "XAU_USD", "USD_JPY"]
        all_results = {}
        
        for instrument in instruments:
            print(f"\n🔍 Testing {instrument}...")
            print("-" * 50)
            
            try:
                # Run backtest for this instrument
                results = backtester.run_backtest(
                    instrument=instrument,
                    start_date=start_date,
                    end_date=end_date,
                    granularity="M15"  # 15-minute timeframe for more signals
                )
                
                all_results[instrument] = results
                
                # Display results
                summary = results['summary']
                metadata = results['metadata']
                
                print(f"📊 {instrument} Results:")
                print(f"   Data Points: {metadata['data_points']}")
                print(f"   Signals Generated: {results['signals_generated']}")
                print(f"   Total Trades: {summary['total_trades']}")
                
                if summary['total_trades'] > 0:
                    print(f"   Win Rate: {summary['win_rate']}%")
                    print(f"   Total P&L: ${summary['total_pnl']}")
                    print(f"   Final Balance: ${summary['final_balance']}")
                    print(f"   Profit Factor: {summary['profit_factor']}")
                    
                    # Show recent trades
                    recent_trades = results['trades'][-3:] if results['trades'] else []
                    if recent_trades:
                        print(f"   Recent Trades:")
                        for trade in recent_trades:
                            pnl_symbol = "✅" if trade['pnl'] > 0 else "❌"
                            print(f"     {pnl_symbol} {trade['direction']} | P&L: ${trade['pnl']:.2f} | {trade['exit_reason']}")
                else:
                    print(f"   ⚠️ No trades executed")
                    
            except Exception as e:
                print(f"   ❌ Error testing {instrument}: {e}")
                all_results[instrument] = {"error": str(e)}
        
        # Overall summary
        print("\n" + "="*80)
        print("📈 OVERALL YESTERDAY BACKTEST SUMMARY")
        print("="*80)
        
        total_trades = 0
        total_pnl = 0
        successful_instruments = 0
        
        for instrument, results in all_results.items():
            if "error" not in results and results['summary']['total_trades'] > 0:
                successful_instruments += 1
                total_trades += results['summary']['total_trades']
                total_pnl += results['summary']['total_pnl']
                
                print(f"✅ {instrument}: {results['summary']['total_trades']} trades, "
                      f"${results['summary']['total_pnl']:.2f} P&L, "
                      f"{results['summary']['win_rate']:.1f}% win rate")
            elif "error" not in results:
                print(f"⚪ {instrument}: No trades generated")
            else:
                print(f"❌ {instrument}: Error - {results['error']}")
        
        print(f"\n🎯 COMBINED RESULTS:")
        print(f"   Instruments Tested: {len(instruments)}")
        print(f"   Successful Tests: {successful_instruments}")
        print(f"   Total Trades: {total_trades}")
        print(f"   Combined P&L: ${total_pnl:.2f}")
        
        if total_trades > 0:
            avg_pnl = total_pnl / total_trades
            print(f"   Average P&L per Trade: ${avg_pnl:.2f}")
        
        # Save results to file
        results_file = f"backtest_results_{yesterday_str}.json"
        with open(results_file, 'w') as f:
            json.dump(all_results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        print("="*80)
        
        return all_results
        
    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        return None

if __name__ == "__main__":
    run_yesterday_backtest()
