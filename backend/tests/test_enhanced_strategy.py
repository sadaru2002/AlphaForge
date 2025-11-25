"""
Quick Test Script for Enhanced AlphaForge Strategy
Tests signal generation for all 3 pairs: GBP/USD, XAU/USD, USD/JPY
"""
import asyncio
import sys
from enhanced_strategy_integration import get_enhanced_strategy

async def main():
    print("="*70)
    print("AlphaForge Enhanced Strategy Test")
    print("="*70)
    print("\nInitializing enhanced strategy with AlphaForge components...")
    
    try:
        strategy = get_enhanced_strategy()
        print("✅ Strategy initialized successfully!")
        print(f"   - Regime Detection: Active")
        print(f"   - Kelly Criterion: Active")
        print(f"   - Multi-Timeframe: M5/M15/H1")
        print(f"   - Supported Pairs: {', '.join(strategy.instruments)}")
        
        # Test signal generation for all pairs
        print("\n" + "="*70)
        print("Testing Signal Generation")
        print("="*70)
        
        for pair in strategy.instruments:
            print(f"\n📊 Generating signal for {pair}...")
            print("-"*70)
            
            try:
                signal = await strategy.generate_signal_for_pair(pair)
                
                if signal:
                    print(f"✅ SIGNAL GENERATED!")
                    print(f"   Direction: {signal['direction']}")
                    print(f"   Entry: {signal['entry']:.5f}")
                    print(f"   Stop Loss: {signal['stop_loss']:.5f}")
                    print(f"   Take Profit: {signal['take_profit']:.5f}")
                    print(f"   Confidence: {signal['confidence_score']:.1%}")
                    print(f"   Market Regime: {signal['market_regime']}")
                    print(f"   Recommended Risk: {signal['recommended_risk']:.2%}")
                    print(f"   Position Multiplier: {signal['position_multiplier']:.2f}")
                    print(f"   Session Weight: {signal['session_weight']:.2f}")
                    print(f"\n   Multi-Timeframe Breakdown:")
                    print(f"   - M5:  {signal['mtf_m5']:.3f}")
                    print(f"   - M15: {signal['mtf_m15']:.3f}")
                    print(f"   - H1:  {signal['mtf_h1']:.3f}")
                    print(f"   Agreement: {signal['agreement']:.1%}")
                else:
                    print(f"⏭️  No tradeable signal (filtered)")
                    print(f"   Signal passed initial checks but was filtered by:")
                    print(f"   - Regime detection (unfavorable market)")
                    print(f"   - Low confidence (<60%)")
                    print(f"   - Poor timeframe agreement (<67%)")
                    
            except Exception as e:
                print(f"❌ Error: {str(e)}")
        
        # Get statistics
        print("\n" + "="*70)
        print("Strategy Statistics")
        print("="*70)
        
        stats = strategy.get_statistics()
        
        print(f"\n📈 Performance Metrics:")
        print(f"   Total Signals Attempted: {stats['strategy']['total_signals']}")
        print(f"   Tradeable Signals: {stats['strategy']['tradeable_signals']}")
        print(f"   Filter Efficiency: {stats['strategy']['filter_efficiency']}")
        print(f"   Regime Filtered: {stats['strategy']['regime_filtered']}")
        print(f"   Confidence Filtered: {stats['strategy']['confidence_filtered']}")
        print(f"   Agreement Filtered: {stats['strategy']['agreement_filtered']}")
        
        print(f"\n💰 Kelly Criterion:")
        print(f"   Win Rate: {stats['kelly_criterion']['win_rate']:.1%}")
        print(f"   Avg Win: ${stats['kelly_criterion']['avg_win']:.2f}")
        print(f"   Avg Loss: ${stats['kelly_criterion']['avg_loss']:.2f}")
        print(f"   Win/Loss Ratio: {stats['kelly_criterion']['win_loss_ratio']:.2f}")
        print(f"   Recommended Risk: {stats['kelly_criterion']['recommended_risk']:.2%}")
        print(f"   Trade Count: {stats['kelly_criterion']['trade_count']}")
        
        if stats['regime_detection']['regime_distribution']:
            print(f"\n🎯 Regime Distribution:")
            for regime, count in stats['regime_detection']['regime_distribution'].items():
                print(f"   {regime}: {count}")
        
        print("\n" + "="*70)
        print("✅ Test Complete!")
        print("="*70)
        print("\nNext Steps:")
        print("1. Start backend server: python app.py")
        print("2. Test API endpoint: POST /api/signals/enhanced/generate")
        print("3. Update frontend to use new endpoints")
        print("4. Run backtest on 5-year data")
        
    except Exception as e:
        print(f"\n❌ Error during test: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())

