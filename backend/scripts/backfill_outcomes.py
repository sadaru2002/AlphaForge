#!/usr/bin/env python3
"""
Backfill Historical Signal Outcomes
Analyzes historical signals to determine if they were WON or LOST.
Uses sqlite3 directly to avoid import issues.
"""
import os
import sys
import sqlite3
from datetime import datetime, timedelta
from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsCandles

# OANDA Configuration
OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
OANDA_ENVIRONMENT = os.getenv("OANDA_ENVIRONMENT", "practice")

# Database path
DB_PATH = "/app/backend/data/trading_signals.db"

# Symbol mapping
SYMBOL_TO_INSTRUMENT = {
    'GBP/USD': 'GBP_USD',
    'GOLD': 'XAU_USD',
    'USD/JPY': 'USD_JPY'
}


def get_historical_candles(api, instrument: str, from_time: datetime, to_time: datetime):
    """Fetch historical candles from OANDA."""
    try:
        params = {
            "from": from_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "to": to_time.strftime("%Y-%m-%dT%H:%M:%SZ"),
            "granularity": "M1",
            "price": "M"
        }
        r = InstrumentsCandles(instrument=instrument, params=params)
        response = api.request(r)
        
        if response and 'candles' in response:
            return response['candles']
    except Exception as e:
        print(f"Error fetching candles for {instrument}: {e}")
    
    return []


def check_historical_outcome(direction, entry, tp, sl, candles):
    """Check if signal hit TP or SL based on historical candles."""
    for candle in candles:
        if candle.get('complete', False):
            high = float(candle['mid']['h'])
            low = float(candle['mid']['l'])
            
            if direction == 'BUY':
                if high >= tp:
                    return 'WON', float(candle['mid']['c']), candle['time']
                if low <= sl:
                    return 'LOST', float(candle['mid']['c']), candle['time']
            
            elif direction == 'SELL':
                if low <= tp:
                    return 'WON', float(candle['mid']['c']), candle['time']
                if high >= sl:
                    return 'LOST', float(candle['mid']['c']), candle['time']
    
    return 'EXPIRED', None, None


def calculate_pips(symbol, direction, entry, exit_price):
    """Calculate pips gained/lost."""
    if exit_price is None:
        return 0
    
    if direction == 'BUY':
        pips = (exit_price - entry)
    else:
        pips = (entry - exit_price)
    
    if 'JPY' in symbol:
        pips *= 100
    else:
        pips *= 10000
    
    return pips


def main():
    api = API(access_token=OANDA_API_KEY, environment=OANDA_ENVIRONMENT)
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # Get all signals
    cursor.execute("""
        SELECT id, symbol, direction, entry, stop_loss, tp1, timestamp, status 
        FROM trading_signals
        ORDER BY timestamp DESC
    """)
    signals = cursor.fetchall()
    
    print(f"📊 Analyzing {len(signals)} signals...")
    print("-" * 80)
    
    stats = {'won': 0, 'lost': 0, 'expired': 0}
    total_pips = 0
    results = []
    
    for signal in signals:
        sig_id, symbol, direction, entry, stop_loss, tp1, timestamp, status = signal
        
        instrument = SYMBOL_TO_INSTRUMENT.get(symbol)
        if not instrument:
            print(f"⚠️  Unknown symbol: {symbol}")
            continue
        
        # Parse timestamp
        try:
            from_time = datetime.fromisoformat(timestamp.replace('Z', ''))
        except:
            from_time = datetime.strptime(timestamp[:19], "%Y-%m-%dT%H:%M:%S")
        
        to_time = from_time + timedelta(hours=4)
        
        print(f"\n🔍 Signal ID: {sig_id} | {symbol} | {direction}")
        print(f"   Entry: {entry:.5f} | SL: {stop_loss:.5f} | TP: {tp1:.5f}")
        print(f"   Time: {timestamp}")
        
        # Fetch historical candles
        candles = get_historical_candles(api, instrument, from_time, to_time)
        
        if not candles:
            print(f"   ⚠️  No candle data available")
            continue
        
        print(f"   📈 Fetched {len(candles)} candles")
        
        # Check outcome
        outcome, exit_price, exit_time = check_historical_outcome(
            direction.upper(), entry, tp1, stop_loss, candles
        )
        
        if outcome == 'WON':
            stats['won'] += 1
            pips = calculate_pips(symbol, direction.upper(), entry, tp1)
            total_pips += pips
            new_status = 'WON'
            print(f"   ✅ WON: +{pips:.1f} pips")
            
        elif outcome == 'LOST':
            stats['lost'] += 1
            pips = calculate_pips(symbol, direction.upper(), entry, stop_loss)
            total_pips += pips
            new_status = 'LOST'
            print(f"   ❌ LOST: {pips:.1f} pips")
            
        else:
            stats['expired'] += 1
            pips = 0
            new_status = 'EXPIRED'
            print(f"   ⏰ EXPIRED (no TP/SL hit in 4 hours)")
        
        # Store result
        results.append({
            'id': sig_id,
            'symbol': symbol,
            'direction': direction,
            'outcome': new_status,
            'pips': pips
        })
        
        # Update database
        cursor.execute("""
            UPDATE trading_signals 
            SET status = ?, exit_price = ?
            WHERE id = ?
        """, (new_status, exit_price, sig_id))
        conn.commit()
    
    # Print summary
    print("\n" + "=" * 80)
    print("📊 PERFORMANCE SUMMARY")
    print("=" * 80)
    print(f"   Total Signals: {len(signals)}")
    print(f"   ✅ Won: {stats['won']}")
    print(f"   ❌ Lost: {stats['lost']}")
    print(f"   ⏰ Expired: {stats['expired']}")
    
    if stats['won'] + stats['lost'] > 0:
        win_rate = stats['won'] / (stats['won'] + stats['lost']) * 100
        print(f"   📈 Win Rate: {win_rate:.1f}%")
    
    print(f"   💰 Total Pips: {total_pips:+.1f}")
    print("=" * 80)
    
    conn.close()


if __name__ == "__main__":
    main()
