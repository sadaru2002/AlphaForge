#!/usr/bin/env python3
"""
Patch app.py on the VM to use AlphaForgeEnhancedStrategy instead of EnhancedSignalGenerator
This enables Telegram notifications for signals
"""

import sys

def patch_app_py(filepath):
    with open(filepath, 'r') as f:
        lines = f.readlines()
    
    # Find the generate_enhanced_signals function (around line 1256)
    found_function = False
    start_idx = None
    end_idx = None
   
    for i, line in enumerate(lines):
        if '@app.post("/api/signals/enhanced/generate")' in line:
            found_function = True
            start_idx = i
        elif found_function and line.strip().startswith('except Exception as e:') and 'Error in signal generation endpoint' in lines[i+1]:
            # Find the end of the function
            for j in range(i, min(i+10, len(lines))):
                if lines[j].strip().startswith('raise HTTPException'):
                    end_idx = j + 1
                    break
            break
    
    if not found_function:
        print("❌ Could not find the function to patch")
        return False
    
    # New implementation
    new_impl = '''@app.post("/api/signals/enhanced/generate")
async def generate_enhanced_signals(db: Session = Depends(get_db)):
    """Generate signals using Enhanced Strategy with Telegram (called by scheduler)"""
    
    results = []
    signals_generated = 0
    
    try:
        from enhanced_strategy_integration import get_enhanced_strategy
        
        strategy = get_enhanced_strategy()
        instruments = ['GBP_USD', 'XAU_USD', 'USD_JPY']
        
        # Generate for all supported instruments
        for pair in instruments:
            logger.info(f"🎯 Generating enhanced signal for {pair}...")
            
            # This calls the AlphaForgeEnhancedStrategy which includes Telegram
            signal = await strategy.generate_signal_for_pair(pair)
            
            if signal:
                # Save to database (AlphaForgeEnhancedStrategy returns formatted signal)
                db_signal = TradingSignal(
                    pair=signal['pair'],
                    symbol=signal['symbol'],
                    direction=signal['direction'],
                    entry_price=signal['entry'],
                    stop_loss=signal['stop_loss'],
                    take_profit=signal['take_profit'],
                    confidence_score=signal['confidence_score'],
                    status=SignalStatus.PENDING,
                    metadata={
                        'regime': signal['market_regime'],
                        'regime_tradeable': signal.get('regime_tradeable', True),
                        'position_multiplier': signal.get('position_multiplier', 1.0),
                        'kelly_fraction': signal.get('kelly_fraction', 0.0),
                        'recommended_risk': signal.get('recommended_risk', 0.02),
                        'agreement': signal.get('agreement', 0.0),
                        'reasoning': signal.get('reasoning', '')
                    }
                )
                db.add(db_signal)
                db.commit()
                db.refresh(db_signal)
                
                logger.info(f"✅ Enhanced signal saved & sent to Telegram: {pair} {signal['direction']} (ID: {db_signal.id})")
                
                results.append({
                    "pair": pair,
                    "generated": True,
                    "signal_id": db_signal.id,
                    "direction": signal['direction']
                })
                signals_generated += 1
            else:
                logger.info(f"❌ {pair}: No tradeable signal")
                results.append({
                    "pair": pair,
                    "generated": False,
                    "reason": "No tradeable signal (filtered by regime/confidence/agreement)"
                })
        
        # Get strategy statistics
        try:
            stats = strategy.get_statistics()
        except Exception:
            stats = {}
        
        return {
            "signals_generated": signals_generated,
            "results": results,
            "statistics": stats
        }
        
    except Exception as e:
        logger.error(f"Error in signal generation endpoint: {e}")
        raise HTTPException(status_code=500, detail=str(e))

'''
    
    # Replace the old implementation
    new_lines = lines[:start_idx] + [new_impl + '\n'] + lines[end_idx:]
    
    # Write back
    with open(filepath, 'w') as f:
        f.writelines(new_lines)
    
    print(f"✅ Successfully patched {filepath}")
    print(f"   Replaced lines {start_idx+1} to {end_idx}")
    return True

if __name__ == "__main__":
    if len(sys.argv) > 1:
        filepath = sys.argv[1]
    else:
        filepath = "/home/ubuntu/alphaforge/backend/app.py"
    
    success = patch_app_py(filepath)
    sys.exit(0 if success else 1)
