#!/usr/bin/env python3
"""
Quick script to run AlphaForge with any specific date
Usage: python run_date_signals.py [YYYY-MM-DD]
Example: python run_date_signals.py 2025-11-20
"""
import sys
import os
import asyncio
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db, init_database
from enhanced_signal_generator import EnhancedSignalGenerator
from database.signal_crud import SignalCRUD
from database.signal_models import TradingSignal

async def generate_signals_for_date(date_str=None):
    """Generate signals for a specific date"""
    
    print("\n" + "="*80)
    print("ALPHAFORGE - GENERATE SIGNALS FOR SPECIFIC DATE")
    print("="*80)
    
    # Parse target date
    if date_str:
        try:
            target_date = datetime.strptime(date_str, '%Y-%m-%d')
        except ValueError:
            print(f"❌ Invalid date format: {date_str}")
            print("   Use format: YYYY-MM-DD (e.g., 2025-11-20)")
            return
    else:
        # Default to yesterday
        target_date = datetime.now() - timedelta(days=1)
    
    target_start = target_date.replace(hour=0, minute=0, second=0, microsecond=0)
    target_end = target_date.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    print(f"\nTarget Date: {target_date.strftime('%Y-%m-%d')}")
    print(f"   From: {target_start.strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"   To:   {target_end.strftime('%Y-%m-%d %H:%M:%S')}")
    
    # Initialize database
    print("\nInitializing database...")
    init_database()
    db = next(get_db())
    
    # Pairs to analyze
    pairs = ['GBP_USD', 'XAU_USD', 'USD_JPY']
    
    # Initialize signal generator
    print("\nInitializing Enhanced Signal Generator...")
    generator = EnhancedSignalGenerator()
    
    # Generate signals for each hour
    print(f"\nGenerating signals for {target_date.strftime('%Y-%m-%d')}...")
    print("   Note: Using REAL OANDA data\n")
    
    total_signals = 0
    hours_to_check = list(range(24))
    
    for hour in hours_to_check:
        check_time = target_start.replace(hour=hour)
        
        print(f"\n{'-'*80}")
        print(f"Analyzing at {check_time.strftime('%Y-%m-%d %H:%M')}")
        print(f"{'-'*80}")
        
        for pair in pairs:
            try:
                print(f"\n   {pair}:")
                
                result = await generator.generate_signal(pair, timestamp=check_time)
                
                if result and result.get('signal') in ['BUY', 'SELL'] and result.get('tradeable', False):
                    # Save signal
                    signal_dict = {
                        'timestamp': check_time,
                        'symbol': pair,
                        'direction': result.get('signal', 'NO_ACTION'),
                        'entry': float(result.get('entry_price', 0.0) or 0.0),
                        'stop_loss': float(result.get('stop_loss', 0.0) or 0.0),
                        'tp1': float(result.get('take_profit', 0.0) or 0.0),
                        'rr_ratio': f"1:{int(result.get('risk_reward_ratio', 2.0))}",
                        'confidence_score': float(result.get('strength', 0.0) or 0.0),
                        'signal_strength': 'STRONG' if result.get('strength', 0) >= 70 else 'MEDIUM' if result.get('strength', 0) >= 50 else 'WEAK',
                        'market_condition': result.get('regime', 'unknown'),
                        'notes': f'Generated for {target_date.strftime("%Y-%m-%d")} (real OANDA data)'
                    }
                    
                    SignalCRUD.create_signal(db, signal_dict)
                    total_signals += 1
                    
                    print(f"      [OK] SIGNAL GENERATED!")
                    print(f"         Type: {result.get('signal')}")
                    print(f"         Entry: {signal_dict['entry']:.5f}")
                else:
                    reason = result.get('reason', 'No signal') if result else 'Analysis failed'
                    print(f"      [X] No signal - {reason}")
                    
            except Exception as e:
                print(f"      [!] Error: {str(e)}")
    
    # Summary
    print("\n" + "="*80)
    print("GENERATION SUMMARY")
    print("="*80)
    print(f"\n[OK] Total Signals Generated: {total_signals}")
    print(f"Date: {target_date.strftime('%Y-%m-%d')}")
    print(f"Pairs Analyzed: {', '.join(pairs)}")
    
    if total_signals > 0:
        print(f"\nSignals saved to database: trading_signals table")
    else:
        print("\nNo signals met quality criteria")
    
    print("\n" + "="*80)
    print("[OK] COMPLETE")
    print("="*80 + "\n")
    
    db.close()
    return total_signals

if __name__ == "__main__":
    # Get date from command line argument or use yesterday
    date_arg = sys.argv[1] if len(sys.argv) > 1 else None
    
    try:
        total = asyncio.run(generate_signals_for_date(date_arg))
        print(f"\n✅ Successfully generated {total} signal(s)")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error: {str(e)}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
