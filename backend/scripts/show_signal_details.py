#!/usr/bin/env python3
import sqlite3

conn = sqlite3.connect('trading_signals.db')
cursor = conn.cursor()

cursor.execute("""
    SELECT id, timestamp, symbol, direction, entry, stop_loss, tp1, 
           confidence_score, market_condition
    FROM trading_signals 
    WHERE date(timestamp) = '2025-11-20'
    ORDER BY timestamp DESC
""")

signals = cursor.fetchall()

print(f"\n{'='*80}")
print(f"SIGNALS FROM 2025-11-20 WITH NEW SL/TP CONFIGURATION")
print(f"{'='*80}\n")

for signal in signals:
    id, timestamp, symbol, direction, entry, sl, tp, conf, regime = signal
    
    # Calculate pip distances
    sl_distance = abs(entry - sl)
    tp_distance = abs(entry - tp)
    rr_ratio = tp_distance / sl_distance if sl_distance > 0 else 0
    
    print(f"Signal ID: {id}")
    print(f"Time: {timestamp}")
    print(f"Symbol: {symbol}")
    print(f"Direction: {direction}")
    print(f"")
    print(f"Entry:       {entry:.5f}")
    print(f"Stop Loss:   {sl:.5f}  (Distance: ${sl_distance:.2f})")
    print(f"Take Profit: {tp:.5f}  (Distance: ${tp_distance:.2f})")
    print(f"")
    print(f"Risk/Reward Ratio: 1:{rr_ratio:.2f}")
    print(f"Confidence: {conf}%")
    print(f"Regime: {regime}")
    print(f"{'-'*80}\n")

# Show expected values for reference
print(f"EXPECTED VALUES FOR XAU_USD:")
print(f"  SL Distance: $4.50 (45 pips)")
print(f"  TP Distance: $10.50 (105 pips)")
print(f"  R:R Ratio: 1:2.33")
print(f"{'='*80}\n")

conn.close()
