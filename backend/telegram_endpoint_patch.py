# ===== ENHANCED SIGNAL GENERATION ENDPOINT =====

@app.post("/api/signals/enhanced/generate")
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
                
                logger.info(f"✅ Enhanced signal saved: {pair} {signal['direction']} (ID: {db_signal.id})")
                
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
