#!/usr/bin/env python3
"""Expire stale PENDING signals that are older than 24 hours."""
import sqlite3
from datetime import datetime, timedelta

DB_PATH = "/app/backend/data/trading_signals.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Find all PENDING signals older than 24 hours
cutoff = (datetime.utcnow() - timedelta(hours=24)).isoformat()

cursor.execute("""
    SELECT id, symbol, direction, status, timestamp 
    FROM trading_signals 
    WHERE status = 'PENDING' AND timestamp < ?
""", (cutoff,))

stale_signals = cursor.fetchall()

print(f"Found {len(stale_signals)} stale PENDING signals (older than 24 hours):")

for signal in stale_signals:
    print(f"  ID={signal[0]} | {signal[1]} | {signal[2]} | {signal[3]} | {signal[4]}")

if stale_signals:
    # Update them to EXPIRED
    ids = [s[0] for s in stale_signals]
    cursor.execute(f"""
        UPDATE trading_signals 
        SET status = 'EXPIRED' 
        WHERE id IN ({','.join(map(str, ids))})
    """)
    updated = cursor.rowcount
    conn.commit()
    print(f"\n✅ Updated {updated} signals from PENDING to EXPIRED")
else:
    print("\nNo stale signals to update")

# Show current pending count
cursor.execute("SELECT COUNT(*) FROM trading_signals WHERE status = 'PENDING'")
pending_count = cursor.fetchone()[0]
print(f"\n📊 Current PENDING signals: {pending_count}")

conn.close()
