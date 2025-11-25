#!/usr/bin/env python3
"""
Backtest AlphaForge Strategy for Last Week's Data
Extended backtest to see signal generation patterns
"""

from datetime import datetime, timedelta
from oanda_backtest_engine import OANDAHistoricalBacktester
import json
import pandas as pd

def run_last_week_backtest():
    """Run backtest for last week's trading data"""
    
    # Calculate last week's date range
    today = datetime.now()
    last_week_end = today - timedelta(days=1)
    last_week_start = today - timedelta(days=7)
    
    start_date = last_week_start.strftime('%Y-%m-%d')
    end_date = last_week_end.strftime('%Y-%m-%d')
    
    print("="*80)
    print("🚀 ALPHAFORGE LAST WEEK BACKTEST")
    print("="*80)
    print(f"📅 Testing period: {start_date} to {end_date}")
    print(f"🎯 Looking for signal patterns over 7 days")
    print("="*80)
    
    try:
        # Initialize backtester
        backtester = OANDAHistoricalBacktester()
        
        # Test with more sensitive settings
        instrument = "GBP_USD"  # Focus on one instrument first
        
        print(f"\n🔍 Testing {instrument} with detailed analysis...")
        print("-" * 60)
        
        # Get raw data first to analyze market conditions
        print("📊 Fetching market data...")
        df = backtester.get_historical_data(instrument, start_date, end_date, "M15")
        
        if df.empty:
            print("❌ No data available")
            return
        
        print(f"✅ Retrieved {len(df)} candles")
        print(f"   Date range: {df.index[0]} to {df.index[-1]}")
        print(f"   Price range: {df['close'].min():.5f} - {df['close'].max():.5f}")
        print(f"   Average volume: {df['volume'].mean():.0f}")
        
        # Calculate indicators
        df = backtester.calculate_technical_indicators(df)
        
        # Analyze market conditions
        print(f"\n📈 Market Analysis:")
        latest = df.iloc[-1]
        print(f"   Latest Close: {latest['close']:.5f}")
        print(f"   RSI: {latest['rsi']:.1f}")
        print(f"   MACD: {latest['macd']:.6f}")
        print(f"   SMA 20: {latest['sma_20']:.5f}")
        print(f"   SMA 50: {latest['sma_50']:.5f}")
        print(f"   ATR: {latest['atr']:.5f}")
        
        # Check signal conditions manually
        print(f"\n🔍 Signal Condition Analysis (Latest Bar):")
        print(f"   Price > SMA20: {latest['close'] > latest['sma_20']} ({latest['close']:.5f} vs {latest['sma_20']:.5f})")
        print(f"   SMA20 > SMA50: {latest['sma_20'] > latest['sma_50']} ({latest['sma_20']:.5f} vs {latest['sma_50']:.5f})")
        print(f"   RSI in range: {30 < latest['rsi'] < 70} (RSI: {latest['rsi']:.1f})")
        print(f"   MACD bullish: {latest['macd'] > latest['macd_signal']} ({latest['macd']:.6f} vs {latest['macd_signal']:.6f})")
        
        # Run the full backtest
        print(f"\n🚀 Running full backtest...")
        results = backtester.run_backtest(
            instrument=instrument,
            start_date=start_date,
            end_date=end_date,
            granularity="M15"
        )
        
        # Display results
        summary = results['summary']
        metadata = results['metadata']
        
        print(f"\n📊 {instrument} Backtest Results:")
        print(f"   Data Points: {metadata['data_points']}")
        print(f"   Signals Generated: {results['signals_generated']}")
        print(f"   Total Trades: {summary['total_trades']}")
        
        if summary['total_trades'] > 0:
            print(f"   Win Rate: {summary['win_rate']}%")
            print(f"   Total P&L: ${summary['total_pnl']}")
            print(f"   Final Balance: ${summary['final_balance']}")
            print(f"   Profit Factor: {summary['profit_factor']}")
            print(f"   Average Win: ${summary['avg_win']}")
            print(f"   Average Loss: ${summary['avg_loss']}")
            
            # Show all trades
            print(f"\n📋 Trade Details:")
            for i, trade in enumerate(results['trades'], 1):
                pnl_symbol = "✅" if trade['pnl'] > 0 else "❌"
                entry_time = pd.to_datetime(trade['entry_time']).strftime('%m-%d %H:%M')
                exit_time = pd.to_datetime(trade['exit_time']).strftime('%m-%d %H:%M')
                print(f"   {i}. {pnl_symbol} {trade['direction']} | "
                      f"{entry_time} → {exit_time} | "
                      f"P&L: ${trade['pnl']:.2f} | "
                      f"{trade['exit_reason']} | "
                      f"Conf: {trade['confidence']:.1%}")
        else:
            print(f"   ⚠️ No trades executed")
            
            # Let's check why no signals were generated
            print(f"\n🔍 Debugging: Why no signals?")
            
            # Look at the last 50 bars and check conditions
            recent_data = df.tail(50)
            signal_count = 0
            
            for i in range(len(recent_data)):
                row = recent_data.iloc[i]
                
                # Check bullish conditions
                bullish_conditions = [
                    row['close'] > row['sma_20'],
                    row['sma_20'] > row['sma_50'],
                    30 < row['rsi'] < 70,
                    row['macd'] > row['macd_signal'],
                    row['close'] > row['bb_lower'],
                ]
                
                # Check bearish conditions  
                bearish_conditions = [
                    row['close'] < row['sma_20'],
                    row['sma_20'] < row['sma_50'],
                    30 < row['rsi'] < 70,
                    row['macd'] < row['macd_signal'],
                    row['close'] < row['bb_upper'],
                ]
                
                bullish_score = sum(bullish_conditions)
                bearish_score = sum(bearish_conditions)
                
                if bullish_score >= 3 or bearish_score >= 3:  # Lower threshold for debugging
                    signal_count += 1
                    signal_type = "BULLISH" if bullish_score > bearish_score else "BEARISH"
                    score = max(bullish_score, bearish_score)
                    timestamp = row.name.strftime('%m-%d %H:%M')
                    print(f"   {timestamp}: {signal_type} potential (score: {score}/5)")
            
            print(f"   Potential signals found: {signal_count} (with score ≥3/5)")
            print(f"   Current threshold requires: 4/5 conditions")
        
        # Save results
        results_file = f"backtest_results_week_{start_date}_to_{end_date}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        print(f"\n💾 Results saved to: {results_file}")
        print("="*80)
        
        return results
        
    except Exception as e:
        print(f"❌ Backtest failed: {e}")
        import traceback
        traceback.print_exc()
        return None

if __name__ == "__main__":
    run_last_week_backtest()
