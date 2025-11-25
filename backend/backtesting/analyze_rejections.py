#!/usr/bin/env python3
"""Quick script to analyze rejection patterns from the report."""
import json

with open('reports/rejected_signals_2025-11-12.json', 'r') as f:
    data = json.load(f)

print("\n" + "="*60)
print("REJECTION ANALYSIS - 2025-11-12")
print("="*60)

print(f"\nTotal Rejections: {data['summary']['total']}")
print(f"By Reason: {data['summary']['by_reason']}")
print(f"By Instrument: {data['summary']['by_instrument']}")

print("\n" + "-"*60)
print("SAMPLE REJECTION DETAILS (First 6)")
print("-"*60)

for i, r in enumerate(data['rejections'][:6], 1):
    m = r['metrics']
    print(f"\n{i}. {r['instrument']} @ {r['hour']:02d}:00")
    print(f"   Regime: {r['regime']}")
    print(f"   Reason: {r['reason']}")
    print(f"   Filter reasons: {', '.join(m.get('filter_reasons', ['N/A']))}")
    print(f"   Strength: {m.get('strength', 'N/A')}%")
    print(f"   Buy votes: {m.get('buy_votes', 'N/A')}, Sell votes: {m.get('sell_votes', 'N/A')}")
    print(f"   ADX: {m.get('adx', 'N/A')}, ATR%: {m.get('atr_pct', 'N/A')}")
    print(f"   Volatility OK: {m.get('volatility_ok')}, Strength OK: {m.get('strength_ok')}, ADX OK: {m.get('adx_ok')}")

print("\n" + "="*60)
print("THRESHOLD ANALYSIS")
print("="*60)

# Count specific rejection patterns
strength_fails = 0
volatility_fails = 0
adx_fails = 0
no_signal = 0

for r in data['rejections']:
    reasons = r['metrics'].get('filter_reasons', [])
    for reason in reasons:
        if 'strength too weak' in reason.lower():
            strength_fails += 1
        if 'volatility' in reason.lower():
            volatility_fails += 1
        if 'adx' in reason.lower() or 'weak trend' in reason.lower():
            adx_fails += 1
        if 'no signal' in reason.lower():
            no_signal += 1

print(f"\nStrength failures: {strength_fails}")
print(f"Volatility failures: {volatility_fails}")
print(f"ADX/Trend failures: {adx_fails}")
print(f"No signal generated: {no_signal}")

print("\n" + "="*60 + "\n")
