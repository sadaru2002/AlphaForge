import sqlite3
import os
from datetime import datetime

db_path = 'backend/trading_signals.db'

if not os.path.exists(db_path):
    print(f"Database not found at {db_path}")
    exit(1)

conn = sqlite3.connect(db_path)
cursor = conn.cursor()

print(f"Checking database: {db_path}")

# Check table existence
cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='trading_signals';")
if not cursor.fetchone():
    print("Table 'trading_signals' does not exist!")
    exit(1)

# Count signals
cursor.execute("SELECT count(*) FROM trading_signals")
count = cursor.fetchone()[0]
print(f"Total signals: {count}")

# List last 5 signals
cursor.execute("SELECT id, symbol, direction, status, timestamp, created_at FROM trading_signals ORDER BY timestamp DESC LIMIT 5")
rows = cursor.fetchall()

print("\nLast 5 signals:")
for row in rows:
    print(row)

conn.close()
