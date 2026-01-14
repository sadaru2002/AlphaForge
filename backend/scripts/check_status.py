#!/usr/bin/env python3
"""Check signal statuses in database."""
import sqlite3

DB_PATH = "/app/backend/data/trading_signals.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

cursor.execute("SELECT id, symbol, status FROM trading_signals ORDER BY id DESC LIMIT 15")
signals = cursor.fetchall()

print("Signal Status Report:")
print("-" * 50)
for s in signals:
    print(f"ID: {s[0]:3} | {s[1]:10} | Status: {s[2]}")

# Count by status
cursor.execute("SELECT status, COUNT(*) FROM trading_signals GROUP BY status")
counts = cursor.fetchall()
print("\n" + "-" * 50)
print("Status Counts:")
for c in counts:
    print(f"  {c[0]}: {c[1]}")

conn.close()
