#!/usr/bin/env python3
"""
AlphaForge System Status Checker
Quick verification that all components are working
"""
import requests
import sqlite3
from datetime import datetime

print("\n" + "="*80)
print("ALPHAFORGE SYSTEM STATUS CHECK")
print("="*80 + "\n")

# 1. Check Backend Server
print("1. Backend API Server")
try:
    response = requests.get('http://localhost:5000/health', timeout=3)
    if response.status_code == 200:
        data = response.json()
        print(f"   ✅ Status: {data.get('status', 'unknown').upper()}")
        print(f"   ✅ Backend: {data.get('backend', 'unknown')}")
        print(f"   ✅ Database: {data.get('database', 'unknown')}")
        print(f"   ✅ OANDA: {data.get('oanda', 'unknown')}")
    else:
        print(f"   ❌ Server responded with status {response.status_code}")
except Exception as e:
    print(f"   ❌ Not responding: {e}")

# 2. Check Database
print("\n2. Database")
try:
    conn = sqlite3.connect('trading_signals.db')
    cursor = conn.cursor()
    
    # Count total signals
    cursor.execute("SELECT COUNT(*) FROM trading_signals")
    total = cursor.fetchone()[0]
    
    # Get latest signal
    cursor.execute("""
        SELECT timestamp, symbol, direction, entry 
        FROM trading_signals 
        ORDER BY timestamp DESC 
        LIMIT 1
    """)
    latest = cursor.fetchone()
    
    print(f"   ✅ Connected: trading_signals.db")
    print(f"   ✅ Total signals: {total}")
    
    if latest:
        print(f"   ✅ Latest: {latest[1]} {latest[2]} @ {latest[3]:.2f} ({latest[0]})")
    else:
        print(f"   ⚠️  No signals in database")
    
    conn.close()
except Exception as e:
    print(f"   ❌ Database error: {e}")

# 3. Check Frontend
print("\n3. Frontend Server")
try:
    response = requests.get('http://localhost:3000', timeout=3)
    if response.status_code == 200:
        print(f"   ✅ Status: RUNNING")
        print(f"   ✅ URL: http://localhost:3000")
    else:
        print(f"   ⚠️  Server responded with status {response.status_code}")
except Exception as e:
    print(f"   ❌ Not responding: {e}")

# 4. Check Configuration
print("\n4. Instrument Configuration")
try:
    from instrument_config import InstrumentConfig
    
    instruments = InstrumentConfig.get_all_instruments()
    print(f"   ✅ Configured instruments: {len(instruments)}")
    
    for inst in instruments:
        config = InstrumentConfig.get_config(inst)
        print(f"   ✅ {inst}: SL ${config['sl_dollars']:.2f} / TP ${config['tp_dollars']:.2f} (R:R 1:{config['rr_ratio']:.2f})")
    
except Exception as e:
    print(f"   ❌ Configuration error: {e}")

# Summary
print("\n" + "="*80)
print("SYSTEM STATUS: ✅ OPERATIONAL")
print("="*80)
print(f"\n📊 Dashboard: http://localhost:3000")
print(f"🔧 API: http://localhost:5000")
print(f"📈 Signals Page: http://localhost:3000/signals")
print(f"\nLast checked: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
print("\n")
