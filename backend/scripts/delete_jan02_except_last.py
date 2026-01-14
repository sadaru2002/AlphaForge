#!/usr/bin/env python3
"""Delete all January 02 signals EXCEPT the last one generated."""
import sqlite3

DB_PATH = "/app/backend/data/trading_signals.db"

conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# Get all January 02, 2026 signals (UTC date)
cursor.execute("""
    SELECT id, symbol, direction, timestamp 
    FROM trading_signals 
    WHERE date(timestamp) = '2026-01-02'
    ORDER BY timestamp DESC
""")
jan02_signals = cursor.fetchall()

print(f"Found {len(jan02_signals)} signals from January 02")

if len(jan02_signals) > 1:
    # Keep the last (most recent) one, delete the rest
    last_signal = jan02_signals[0]
    signals_to_delete = jan02_signals[1:]
    
    print(f"\n✅ KEEPING (last signal): ID={last_signal[0]} | {last_signal[1]} | {last_signal[2]} | {last_signal[3]}")
    
    print(f"\n❌ DELETING {len(signals_to_delete)} signals:")
    ids_to_delete = []
    for signal in signals_to_delete:
        print(f"   ID={signal[0]} | {signal[1]} | {signal[2]} | {signal[3]}")
        ids_to_delete.append(signal[0])
    
    # Delete them
    cursor.execute(f"DELETE FROM trading_signals WHERE id IN ({','.join(map(str, ids_to_delete))})")
    deleted = cursor.rowcount
    conn.commit()
    
    print(f"\n🗑️  Deleted {deleted} signals")
else:
    print("Only 1 or 0 signals from January 02 - nothing to delete")

# Count remaining
cursor.execute("SELECT COUNT(*) FROM trading_signals")
remaining = cursor.fetchone()[0]
print(f"📊 Remaining total signals: {remaining}")

conn.close()
