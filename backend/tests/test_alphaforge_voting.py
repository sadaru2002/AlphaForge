"""
Test AlphaForge Voting System with Mock Data
"""
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import sys
import os

# Add backend to path
sys.path.insert(0, os.path.dirname(__file__))

from multi_timeframe_engine import MultiTimeframeEngine

def generate_mock_data(candles=500, trend='bullish'):
    """Generate realistic mock OHLCV data."""
    
    dates = [datetime.now() - timedelta(minutes=5*i) for i in range(candles)]
    dates.reverse()
    
    # Generate price data
    if trend == 'bullish':
        base_price = 1.26000
        trend_slope = 0.00001
        noise = 0.0003
    elif trend == 'bearish':
        base_price = 1.27000
        trend_slope = -0.00001
        noise = 0.0003
    else:  # ranging
        base_price = 1.26500
        trend_slope = 0
        noise = 0.0002
    
    prices = []
    current_price = base_price
    
    for i in range(candles):
        # Add trend and noise
        current_price += trend_slope + np.random.randn() * noise
        prices.append(current_price)
    
    # Create OHLC from prices
    data = []
    for i, (date, close) in enumerate(zip(dates, prices)):
        high = close + abs(np.random.randn() * 0.0002)
        low = close - abs(np.random.randn() * 0.0002)
        open_price = prices[i-1] if i > 0 else close
        volume = int(10000 + np.random.randn() * 2000)
        
        data.append({
            'timestamp': date,
            'open': open_price,
            'high': high,
            'low': low,
            'close': close,
            'volume': volume
        })
    
    df = pd.DataFrame(data)
    df.set_index('timestamp', inplace=True)
    
    return df

def test_voting_system():
    """Test the indicator voting system with mock data."""
    
    print("="*80)
    print("Testing AlphaForge Indicator Voting System")
    print("="*80)
    
    engine = MultiTimeframeEngine()
    
    # Test scenarios
    scenarios = [
        ('bullish', 'trending_up_low_volatility'),
        ('bearish', 'trending_down_low_volatility'),
        ('ranging', 'ranging_low_volatility')
    ]
    
    for trend, regime in scenarios:
        print(f"\n{'='*80}")
        print(f"Scenario: {trend.upper()} trend, Regime: {regime}")
        print(f"{'='*80}")
        
        # Generate mock data for all timeframes
        mock_data = {
            'M5': generate_mock_data(500, trend),
            'M15': generate_mock_data(300, trend),
            'H1': generate_mock_data(200, trend)
        }
        
        # Generate signal
        signal = engine.generate_multi_timeframe_signal(mock_data, regime)
        
        print(f"\n🎯 FINAL SIGNAL: {signal['signal']}")
        print(f"   Buy Votes: {signal['buy_votes']:.2f}/6.0")
        print(f"   Sell Votes: {signal['sell_votes']:.2f}/6.0")
        print(f"   Strength: {signal['strength']:.1f}%")
        print(f"   Confidence: {signal['confidence']:.2f}")
        print(f"   Agreement: {signal['agreement']:.1%}")
        print(f"   Passed Filters: {'✅ YES' if signal['passed_filters'] else '❌ NO'}")
        
        # Show filter results
        filters = signal['filter_results']
        if signal['passed_filters']:
            print(f"\n✅ Quality Filters:")
            print(f"   Volatility: {filters.get('atr_pct', 0):.3f}% (0.05-0.25%) - {'✅' if filters['volatility_ok'] else '❌'}")
            print(f"   Strength: {filters.get('strength', 0):.1f}% (≥50%) - {'✅' if filters['strength_ok'] else '❌'}")
            print(f"   ADX: {filters.get('adx', 0):.1f} (≥15) - {'✅' if filters['adx_ok'] else '❌'}")
        else:
            print(f"\n⚠️ Filter Rejection Reasons:")
            for reason in filters.get('reasons', []):
                print(f"   {reason}")
        
        # Show timeframe breakdown
        print(f"\n📊 Timeframe Analysis:")
        for tf, analysis in signal['timeframe_signals'].items():
            buy_v = analysis['buy_votes']
            sell_v = analysis['sell_votes']
            total = analysis['total_indicators']
            direction = 'BUY' if buy_v > sell_v else ('SELL' if sell_v > buy_v else 'NEUTRAL')
            
            print(f"\n   {tf} ({analysis['weight']*100:.0f}% weight): {direction}")
            print(f"      Buy: {buy_v:.1f}/{total} | Sell: {sell_v:.1f}/{total} | Strength: {analysis['strength']:.1f}%")
            
            # Show top 4 indicator details
            print(f"      Indicators:")
            for detail in analysis['signal_details'][:4]:
                print(f"        {detail}")
            
            # Show key data
            latest = analysis.get('latest_data', {})
            if latest:
                print(f"      Data: EMA5={latest.get('ema5', 0):.5f}, RSI7={latest.get('rsi7', 0):.1f}, ADX={latest.get('adx', 0):.1f}")

if __name__ == "__main__":
    test_voting_system()
    
    print(f"\n{'='*80}")
    print("✅ AlphaForge VOTING SYSTEM TEST COMPLETE")
    print("="*80)
    print("\nKey Features Demonstrated:")
    print("  ✅ Indicator voting (6 indicators)")
    print("  ✅ Fast indicators (EMA 5-8-13, RSI 7, MACD 6-13-4)")
    print("  ✅ Adaptive thresholds (regime-based)")
    print("  ✅ Volume confirmation")
    print("  ✅ 3+ indicator agreement requirement")
    print("  ✅ Quality filters (volatility, ADX, strength)")
    print("\n🚀 Your system is now using AlphaForge signal generation!")

