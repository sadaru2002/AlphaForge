import os
import sys
sys.path.append('/app/backend')
from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker

# Use environment variable or default path
DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:////app/backend/data/trading_signals.db")
engine = create_engine(DATABASE_URL)
Session = sessionmaker(bind=engine)
session = Session()

try:
    print(f"Connecting to database: {DATABASE_URL}")
    
    # Delete all signals
    result = session.execute(text("DELETE FROM trading_signals"))
    print(f"Deleted {result.rowcount} signals.")
    
    # Reset ID counter (sqlite_sequence)
    try:
        session.execute(text("DELETE FROM sqlite_sequence WHERE name='trading_signals'"))
        print("Reset auto-increment counter.")
    except Exception as e:
        print(f"Warning: Could not reset sequence (might be empty): {e}")

    session.commit()
    print("✅ Database cleared successfully.")

except Exception as e:
    print(f"❌ Error clearing database: {e}")
    session.rollback()
finally:
    session.close()
