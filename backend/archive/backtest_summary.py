#!/usr/bin/env python3
"""
Quick Backtest Summary for Yesterday's OANDA Data
"""

from datetime import datetime, timedelta
from oanda_backtest_engine import OANDAHistoricalBacktester
import json

def quick_backtest_summary():
    """Run a quick backtest and show summary"""
    
    # Calculate date range (last 3 days to ensure we have data)
    end_date = (datetime.now() - timedelta(days=1)).strftime('%Y-%m-%d')
    start_date = (datetime.now() - timedelta(days=4)).strftime('%Y-%m-%d')
    
    print("="*60)
    print("🚀 ALPHAFORGE BACKTEST SUMMARY")
    print("="*60)
    print(f"📅 Period: {start_date} to {end_date}")
    print(f"🎯 Instrument: GBP_USD (15-minute timeframe)")
    print("="*60)
    
    try:
        backtester = OANDAHistoricalBacktester()
        
        # Run backtest
        results = backtester.run_backtest(
            instrument="GBP_USD",
            start_date=start_date,
            end_date=end_date,
            granularity="M15"
        )
        
        summary = results['summary']
        
        print(f"\n📊 PERFORMANCE RESULTS:")
        print(f"   Signals Generated: {results['signals_generated']}")
        print(f"   Trades Executed: {summary['total_trades']}")
        
        if summary['total_trades'] > 0:
            print(f"   Win Rate: {summary['win_rate']}%")
            print(f"   Winning Trades: {summary['winning_trades']}")
            print(f"   Losing Trades: {summary['losing_trades']}")
            print(f"   Total P&L: ${summary['total_pnl']}")
            print(f"   Final Balance: ${summary['final_balance']}")
            print(f"   Profit Factor: {summary['profit_factor']}")
            print(f"   Average Win: ${summary['avg_win']}")
            print(f"   Average Loss: ${summary['avg_loss']}")
            
            # Performance rating
            if summary['win_rate'] >= 60 and summary['total_pnl'] > 0:
                rating = "🟢 EXCELLENT"
            elif summary['win_rate'] >= 50 and summary['total_pnl'] > 0:
                rating = "🟡 GOOD"
            elif summary['total_pnl'] > 0:
                rating = "🟠 FAIR"
            else:
                rating = "🔴 POOR"
            
            print(f"\n🎯 Strategy Performance: {rating}")
            
            # Show last few trades
            if len(results['trades']) > 0:
                print(f"\n📋 Recent Trades (Last 5):")
                recent_trades = results['trades'][-5:]
                for i, trade in enumerate(recent_trades, 1):
                    pnl_symbol = "✅" if trade['pnl'] > 0 else "❌"
                    entry_time = datetime.fromisoformat(trade['entry_time'].replace('Z', '+00:00'))
                    print(f"   {i}. {pnl_symbol} {trade['direction']} | "
                          f"{entry_time.strftime('%m-%d %H:%M')} | "
                          f"P&L: ${trade['pnl']:.2f} | "
                          f"{trade['exit_reason']}")
        else:
            print(f"   ⚠️ No trades executed")
            print(f"   📝 This could indicate:")
            print(f"      - Market conditions didn't meet signal criteria")
            print(f"      - Low volatility period")
            print(f"      - Weekend/holiday period")
        
        print("="*60)
        
        return results
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None

if __name__ == "__main__":
    quick_backtest_summary()
