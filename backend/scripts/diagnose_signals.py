"""
Quick diagnostic to see what signals are being generated
"""
import asyncio
import pandas as pd
from datetime import datetime
from backtest_oanda import OANDABacktestEngine
from dotenv import load_dotenv
import os

load_dotenv()

async def diagnose():
    api_key = os.getenv("OANDA_API_KEY")
    
    print("🔍 Diagnostic Mode - Checking Signal Generation\n")
    
    engine = OANDABacktestEngine(api_key, 10000, min_votes_required=2.0)
    
    # Fetch October Gold data
    df = await engine.fetch_historical_data('XAU_USD', '2024-10-15', '2024-10-22', 'M5')
    
    print(f"✅ Fetched {len(df)} candles\n")
    
    # Prepare multi-timeframe data
    df_m15 = df.resample('15T').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    df_h1 = df.resample('1H').agg({
        'open': 'first',
        'high': 'max',
        'low': 'min',
        'close': 'last',
        'volume': 'sum'
    }).dropna()
    
    # Check signals at different points
    check_points = [600, 800, 1000, 1200, 1400]
    
    for i in check_points:
        if i >= len(df):
            continue
            
        current_time = df.index[i]
        
        m5_data = df.iloc[:i+1].tail(500)
        m15_data = df_m15[df_m15.index <= current_time].tail(300)
        h1_data = df_h1[df_h1.index <= current_time].tail(200)
        
        mtf_data = {
            'M5': m5_data,
            'M15': m15_data,
            'H1': h1_data
        }
        
        # Generate signal
        signal = engine.signal_generator.mtf_engine.generate_multi_timeframe_signal(
            mtf_data,
            market_regime='unknown'
        )
        
        print(f"\n{'='*80}")
        print(f"Time: {current_time}")
        print(f"{'='*80}")
        print(f"Signal: {signal['signal']}")
        print(f"Buy Votes: {signal['buy_votes']:.2f} / Sell Votes: {signal['sell_votes']:.2f}")
        print(f"Strength: {signal['strength']:.1f}%")
        print(f"Passed Filters: {signal['passed_filters']}")
        
        print(f"\nTimeframe Breakdown:")
        for tf, data in signal['timeframe_signals'].items():
            buy_v = data.get('buy_votes', 0)
            sell_v = data.get('sell_votes', 0)
            print(f"  {tf}: Buy={buy_v:.1f} Sell={sell_v:.1f} Strength={data.get('strength', 0):.1f}%")
            if data.get('signal_details'):
                for detail in data['signal_details'][:3]:  # Show first 3
                    print(f"    {detail}")
        
        print(f"\nFilter Results:")
        for key, value in signal['filter_results'].items():
            print(f"  {key}: {value}")

asyncio.run(diagnose())
