#!/usr/bin/env python3
import sqlite3
from datetime import datetime, timedelta

# Connect to database
conn = sqlite3.connect('trading_signals.db')
cursor = conn.cursor()

# Get count
cursor.execute("SELECT COUNT(*) FROM trading_signals")
total = cursor.fetchone()[0]
print(f"\nTotal signals in database: {total}\n")

# Get yesterday's signals
yesterday = datetime.now() - timedelta(days=1)
yesterday_str = yesterday.strftime('%Y-%m-%d')

cursor.execute("""
    SELECT id, timestamp, symbol, direction, entry, stop_loss, tp1, 
           confidence_score, signal_strength, market_condition, notes
    FROM trading_signals 
    WHERE date(timestamp) = ?
    ORDER BY timestamp DESC
""", (yesterday_str,))

signals = cursor.fetchall()
print(f"Signals from {yesterday_str}: {len(signals)}\n")

for signal in signals:
    print(f"ID: {signal[0]}")
    print(f"Time: {signal[1]}")
    print(f"Symbol: {signal[2]}")
    print(f"Direction: {signal[3]}")
    print(f"Entry: {signal[4]}")
    print(f"SL: {signal[5]}")
    print(f"TP1: {signal[6]}")
    print(f"Confidence: {signal[7]}%")
    print(f"Strength: {signal[8]}")
    print(f"Regime: {signal[9]}")
    print(f"Notes: {signal[10]}")
    print("-" * 80)

# Get latest 5 signals
cursor.execute("""
    SELECT timestamp, symbol, direction, entry
    FROM trading_signals 
    ORDER BY timestamp DESC
    LIMIT 5
""")

latest = cursor.fetchall()
print(f"\nLatest 5 signals:")
for sig in latest:
    print(f"  {sig[0]} - {sig[1]} {sig[2]} @ {sig[3]}")

conn.close()
