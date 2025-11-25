#!/usr/bin/env python3
"""
Generate signals from yesterday's data using real OANDA data
This runs the actual system workflow - no simulation
"""

import sys
import os
import asyncio
from datetime import datetime, timedelta
from sqlalchemy.orm import Session

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db, init_database
from enhanced_signal_generator import EnhancedSignalGenerator
from database.signal_crud import SignalCRUD
from database.signal_models import TradingSignal

async def generate_yesterday_signals():
    """Generate signals for yesterday using real OANDA data"""
    
    print("\n" + "="*80)
    print("ALPHAFORGE - GENERATING YESTERDAY'S SIGNALS")
    print("="*80)
    
    # Calculate yesterday's date range
    now = datetime.now()
    yesterday = now - timedelta(days=1)
    yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    print(f"\nTarget Date: {yesterday.strftime('%Y-%m-%d')}")
    print(f"   From: {yesterday_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   To:   {yesterday_end.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize database
    print("\nInitializing database...")
    init_database()
    db = next(get_db())
    
    # Clear existing signals for clean test
    print("Clearing existing signals...")
    try:
        db.query(TradingSignal).delete()
        db.commit()
    except Exception as e:
        print(f"Warning: Could not clear table: {e}")
        db.rollback()
    
    # Pairs to analyze
    pairs = ['GBP_USD', 'XAU_USD', 'USD_JPY']
    
    # Initialize signal generator
    print("\nInitializing Enhanced Signal Generator...")
    generator = EnhancedSignalGenerator()
    
    # Generate signals for each hour of yesterday
    # This simulates the scheduler running every 5 minutes by checking selected hours
    print(f"\nGenerating signals for yesterday (hourly intervals)...")
    print("   Note: Using REAL OANDA data from yesterday\n")
    
    total_signals = 0
    hour_results = []
    
    # Check every hour for accurate daily count
    hours_to_check = list(range(24))
    
    for hour in hours_to_check:
        check_time = yesterday_start.replace(hour=hour)
        
        print(f"\n{'-'*80}")
        print(f"Analyzing at {check_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"{'-'*80}")
        
        signals_this_hour = []
        
        for pair in pairs:
            try:
                print(f"\n   {pair}:")
                
                # Generate signal using real OANDA data
                # The generator will fetch M5, M15, H1 data from OANDA
                result = await generator.generate_signal(pair, timestamp=check_time)
                
                if result and result.get('signal') in ['BUY', 'SELL'] and result.get('tradeable', False):
                    # Map EnhancedSignalGenerator result to TradingSignal model fields
                    direction = result.get('signal', 'NO_ACTION')
                    entry = float(result.get('entry_price', 0.0) or 0.0)
                    stop_loss = float(result.get('stop_loss', 0.0) or 0.0)
                    take_profit = float(result.get('take_profit', 0.0) or 0.0)
                    strength_pct = float(result.get('strength', 0.0) or 0.0)  # 0-100
                    regime = result.get('regime', 'unknown')
                    rr = result.get('risk_reward_ratio', 2.0)

                    # Derive signal strength label
                    if strength_pct >= 70:
                        strength_label = 'STRONG'
                    elif strength_pct >= 50:
                        strength_label = 'MEDIUM'
                    else:
                        strength_label = 'WEAK'

                    # Create TradingSignal payload
                    signal_dict = {
                        'timestamp': check_time,
                        'symbol': pair,
                        'direction': direction,
                        'entry': entry,
                        'stop_loss': stop_loss,
                        'tp1': take_profit,
                        'rr_ratio': f"1:{int(rr)}" if isinstance(rr, (int, float)) else str(rr),
                        'confidence_score': strength_pct,  # using strategy strength as 0-100
                        'signal_strength': strength_label,
                        'market_condition': regime,
                        'notes': 'Auto-generated from yesterday run (real OANDA data)'
                    }

                    # Save to database
                    saved_signal = SignalCRUD.create_signal(db, signal_dict)

                    signals_this_hour.append({
                        'pair': pair,
                        'signal': direction,
                        'confidence_pct': strength_pct,
                        'entry': entry,
                        'regime': regime
                    })

                    total_signals += 1

                    print(f"      [OK] SIGNAL GENERATED!")
                    print(f"         Type: {direction}")
                    print(f"         Entry: {entry:.5f}")
                    print(f"         SL: {stop_loss:.5f}")
                    print(f"         TP: {take_profit:.5f}")
                    print(f"         Strength: {strength_pct:.1f}% ({strength_label})")
                    print(f"         Regime: {regime}")
                else:
                    reason = result.get('reason', 'No signal generated') if result else 'Analysis failed'
                    print(f"      [X] No signal - {reason}")
                    
            except Exception as e:
                print(f"      [!] Error: {str(e)}")
        
        hour_results.append({
            'hour': hour,
            'signals': signals_this_hour
        })
    
    # Summary
    print("\n" + "="*80)
    print("GENERATION SUMMARY")
    print("="*80)
    print(f"\n[OK] Total Signals Generated: {total_signals}")
    print(f"Date: {yesterday.strftime('%Y-%m-%d')}")
    print(f"Time Intervals Checked: {len(hours_to_check)} hours")
    print(f"Pairs Analyzed: {', '.join(pairs)}")
    
    if total_signals > 0:
        print(f"\nSignals saved to database: trading_signals table")
        
        # Show signal breakdown
        print("\nSignals by Hour:")
        for hr in hour_results:
            if hr['signals']:
                print(f"\n   {hr['hour']:02d}:00 - {len(hr['signals'])} signal(s):")
                for sig in hr['signals']:
                    print(f"      - {sig['pair']}: {sig['signal']} @ {sig['entry']:.5f} ({sig['confidence_pct']:.1f}% confidence)")
    else:
        print("\nNo signals met quality criteria")
        print("   This is normal - quality filters protect capital")
    
    print("\n" + "="*80)
    print("[OK] GENERATION COMPLETE")
    print("="*80 + "\n")
    
    db.close()
    return total_signals

if __name__ == "__main__":
    try:
        total = asyncio.run(generate_yesterday_signals())
        sys.exit(0)
    except Exception as e:
        print(f"\n[X] Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
