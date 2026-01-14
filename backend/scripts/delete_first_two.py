#!/usr/bin/env python3
"""Delete the first 2 signals from today."""
import requests
from datetime import datetime, timedelta

API_URL = "http://localhost:5000"

# Get all signals
response = requests.get(f"{API_URL}/api/signals")
signals = response.json().get('signals', [])

# Filter today's signals (last 24 hours)
cutoff = datetime.utcnow() - timedelta(hours=24)
cutoff_str = cutoff.isoformat()

today_signals = [s for s in signals if s['timestamp'] >= cutoff_str]

# Sort by timestamp (oldest first)
today_signals.sort(key=lambda x: x['timestamp'])

print(f"Found {len(today_signals)} signals from today")

if len(today_signals) >= 2:
    # Delete first 2
    for i, signal in enumerate(today_signals[:2]):
        signal_id = signal['id']
        print(f"Deleting signal ID: {signal_id} ({signal['symbol']} {signal['direction']} at {signal['timestamp']})")
        
        # Delete via API
        del_response = requests.delete(f"{API_URL}/api/signals/{signal_id}")
        if del_response.status_code == 200:
            print(f"  ✅ Deleted successfully")
        else:
            print(f"  ❌ Failed: {del_response.text}")
else:
    print("Not enough signals to delete")
