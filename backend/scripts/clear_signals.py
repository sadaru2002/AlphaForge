#!/usr/bin/env python3
"""Clear all signals from database"""
import sys
import os

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database.database import get_db
from database.signal_models import TradingSignal

def clear_signals():
    db = next(get_db())
    
    # Count existing signals
    existing = db.query(TradingSignal).count()
    print(f"\nExisting signals in database: {existing}")
    
    if existing > 0:
        # Delete all signals
        db.query(TradingSignal).delete()
        db.commit()
        print(f"✅ Cleared {existing} signal(s)")
    else:
        print("No signals to clear")
    
    db.close()

if __name__ == "__main__":
    clear_signals()
