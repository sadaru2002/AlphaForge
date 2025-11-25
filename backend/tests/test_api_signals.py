#!/usr/bin/env python3
"""Test API endpoint to fetch signals"""
import requests
import json

try:
    # Test the signals endpoint
    response = requests.get('http://localhost:5000/signals')
    response.raise_for_status()
    
    data = response.json()
    
    print("\n" + "="*80)
    print("API RESPONSE - /signals")
    print("="*80)
    print(f"\nStatus Code: {response.status_code}")
    print(f"Signal Count: {data.get('count', 0)}")
    print(f"\nSignals:")
    
    for signal in data.get('signals', []):
        print(f"\n  ID: {signal.get('id')}")
        print(f"  Symbol: {signal.get('symbol')}")
        print(f"  Direction: {signal.get('direction')}")
        print(f"  Entry: {signal.get('entry')}")
        print(f"  SL: {signal.get('stop_loss')}")
        print(f"  TP1: {signal.get('tp1')}")
        print(f"  Timestamp: {signal.get('timestamp')}")
        print(f"  Confidence: {signal.get('confidence_score')}")
        print(f"  Status: {signal.get('status')}")
        print(f"  " + "-"*60)
    
    print("\nAPI is working correctly! ✅")
    
except Exception as e:
    print(f"\n❌ Error: {e}")
    print("Make sure the backend server is running on http://localhost:5000")
