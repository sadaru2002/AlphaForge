#!/usr/bin/env python3
"""Patch to fix database save in the generate endpoint."""

import re
import sys

APP_FILE = '/home/ubuntu/alphaforge/backend/app.py'

# Read the current app.py
with open(APP_FILE, 'r') as f:
    content = f.read()

# The pattern to find and replace - we need to add db.add() after generate_signal_for_pair returns
# Look for the section where signals are generated and ensure they're saved to DB

# Find the generate_enhanced_signals function
old_pattern = '''                        signal_result = await strategy.generate_signal_for_pair(instrument)
                        
                        if signal_result:
                            signals_generated.append(signal_result)'''

new_pattern = '''                        signal_result = await strategy.generate_signal_for_pair(instrument)
                        
                        if signal_result:
                            signals_generated.append(signal_result)
                            # Save to database
                            try:
                                db_signal = TradingSignal(
                                    symbol=signal_result.get('symbol', instrument.replace('_', '/')),
                                    direction=signal_result.get('direction', 'HOLD'),
                                    entry=signal_result.get('entry', 0),
                                    stop_loss=signal_result.get('stop_loss', 0),
                                    take_profit=signal_result.get('take_profit', 0),
                                    confidence_score=signal_result.get('confidence_score', 0),
                                    risk_reward=signal_result.get('risk_reward', 0),
                                    timeframe=signal_result.get('timeframe', 'M5'),
                                    strategy_type='enhanced',
                                    reasoning=str(signal_result.get('reasoning', {})),
                                    market_regime=signal_result.get('market_regime', 'unknown'),
                                    tradeable=True
                                )
                                db.add(db_signal)
                                db.commit()
                                logger.info(f"✅ Signal saved to database for {instrument}")
                            except Exception as db_err:
                                logger.error(f"Failed to save signal to DB: {db_err}")
                                db.rollback()'''

if old_pattern in content:
    content = content.replace(old_pattern, new_pattern)
    
    with open(APP_FILE, 'w') as f:
        f.write(content)
    print("✅ Successfully patched app.py to save signals to database!")
else:
    # Try alternative pattern
    print("Looking for alternative pattern...")
    
    # Just ensure that any signal returned is saved
    alt_old = 'if signal_result:'
    lines = content.split('\n')
    patched = False
    
    for i, line in enumerate(lines):
        if 'signal_result = await strategy.generate_signal_for_pair' in line:
            # Check if there's already a db.add nearby
            nearby = ''.join(lines[i:i+15])
            if 'db.add' not in nearby and 'db_signal' not in nearby:
                print(f"Found signal generation at line {i+1}, no DB save nearby")
            else:
                print(f"DB save already present near line {i+1}")
            patched = True
            break
    
    if not patched:
        print("❌ Could not find the pattern to patch. Manual intervention needed.")
        sys.exit(1)
