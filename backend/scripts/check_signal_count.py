import sys
import os
from datetime import datetime, timedelta
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from database.database import get_db
from database.signal_models import TradingSignal

def count_signals():
    db = next(get_db())
    try:
        # Get yesterday's date
        yesterday = datetime.now() - timedelta(days=1)
        start = yesterday.replace(hour=0, minute=0, second=0)
        end = yesterday.replace(hour=23, minute=59, second=59)
        
        count = db.query(TradingSignal).filter(
            TradingSignal.timestamp >= start,
            TradingSignal.timestamp <= end
        ).count()
        
        print(f"Signals generated for {yesterday.date()}: {count}")
        
        # List them
        signals = db.query(TradingSignal).filter(
            TradingSignal.timestamp >= start,
            TradingSignal.timestamp <= end
        ).all()
        
        for s in signals:
            print(f"- {s.symbol} {s.direction} @ {s.timestamp.strftime('%H:%M')}")
            
    finally:
        db.close()

if __name__ == "__main__":
    count_signals()
