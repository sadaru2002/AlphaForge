#!/usr/bin/env python3
"""Check signals in database"""
import sys
import os
from datetime import datetime, timedelta

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db
from database.signal_models import TradingSignal

def main():
    db = next(get_db())
    
    # Get all signals
    all_signals = db.query(TradingSignal).all()
    print(f"\n{'='*80}")
    print(f"TOTAL SIGNALS IN DATABASE: {len(all_signals)}")
    print(f"{'='*80}\n")
    
    if len(all_signals) == 0:
        print("No signals found in database")
        return
    
    # Get yesterday's signals
    yesterday = datetime.now() - timedelta(days=1)
    yesterday_start = yesterday.replace(hour=0, minute=0, second=0, microsecond=0)
    yesterday_end = yesterday.replace(hour=23, minute=59, second=59, microsecond=999999)
    
    yesterday_signals = [s for s in all_signals if s.timestamp and yesterday_start <= s.timestamp <= yesterday_end]
    
    print(f"YESTERDAY'S SIGNALS ({yesterday.strftime('%Y-%m-%d')}): {len(yesterday_signals)}\n")
    
    if yesterday_signals:
        for signal in yesterday_signals:
            print(f"  ID: {signal.id}")
            print(f"  Time: {signal.timestamp}")
            print(f"  Symbol: {signal.symbol}")
            print(f"  Direction: {signal.direction}")
            print(f"  Entry: {signal.entry:.5f}")
            print(f"  SL: {signal.stop_loss:.5f}")
            print(f"  TP: {signal.tp1:.5f}")
            print(f"  Confidence: {signal.confidence_score}%")
            print(f"  Strength: {signal.signal_strength}")
            print(f"  Regime: {signal.market_condition}")
            print(f"  Notes: {signal.notes}")
            print(f"  {'-'*80}")
    
    # Show latest 10 signals
    print(f"\nLATEST 10 SIGNALS:")
    for signal in sorted(all_signals, key=lambda x: x.timestamp or datetime.min, reverse=True)[:10]:
        print(f"  {signal.timestamp} - {signal.symbol} {signal.direction} @ {signal.entry:.5f}")
    
    db.close()

if __name__ == "__main__":
    main()
