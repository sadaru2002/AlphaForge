#!/usr/bin/env python3
"""Delete signals by ID directly from database."""
import sqlite3

DB_PATH = "/app/backend/data/trading_signals.db"
IDS_TO_DELETE = [9, 10]

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Delete the signals
cursor.execute(f"DELETE FROM trading_signals WHERE id IN ({','.join(map(str, IDS_TO_DELETE))})")
deleted = cursor.rowcount
conn.commit()

# Count remaining
cursor.execute("SELECT COUNT(*) FROM trading_signals")
remaining = cursor.fetchone()[0]

print(f"Deleted {deleted} signals (IDs: {IDS_TO_DELETE})")
print(f"Remaining signals: {remaining}")

conn.close()
