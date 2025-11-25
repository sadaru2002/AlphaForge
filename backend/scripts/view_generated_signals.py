#!/usr/bin/env python3
"""
View generated signals from the database
"""
import sys
import os
from datetime import datetime

# Add backend to path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db
from database.signal_crud import SignalCRUD

def view_signals():
    print("\n" + "="*80)
    print("LATEST GENERATED SIGNALS")
    print("="*80)
    
    db = next(get_db())
    try:
        # Get last 20 signals
        signals = SignalCRUD.get_all_signals(db, limit=20)
        
        if not signals:
            print("\nNo signals found in database.")
            return
            
        print(f"\nFound {len(signals)} recent signals:\n")
        print(f"{'ID':<5} {'TIME':<20} {'PAIR':<10} {'TYPE':<6} {'ENTRY':<10} {'CONFIDENCE':<12} {'REGIME'}")
        print("-" * 90)
        
        for sig in signals:
            # Handle different date formats or objects
            ts = sig.timestamp
            if isinstance(ts, str):
                try:
                    ts = datetime.fromisoformat(ts)
                except:
                    pass
            
            ts_str = ts.strftime('%Y-%m-%d %H:%M') if hasattr(ts, 'strftime') else str(ts)
            
            # Extract metadata safely
            # meta = sig.metadata or {}  # 'metadata' is reserved by SQLAlchemy
            regime = sig.market_condition or 'N/A'
            
            entry = sig.entry if sig.entry is not None else 0.0
            conf = sig.confidence_score if sig.confidence_score is not None else 0.0
            
            print(f"{sig.id:<5} {ts_str:<20} {sig.symbol:<10} {sig.direction:<6} {entry:<10.5f} {conf:<12.1f} {regime}")
            
    except Exception as e:
        print(f"Error: {e}")
    finally:
        db.close()
        print("\n" + "="*80 + "\n")

if __name__ == "__main__":
    view_signals()
