#!/usr/bin/env python3
"""
Detailed test to debug why signals are not being generated
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def debug_signal_generation():
    """Debug the signal generation process step by step"""
    print("🔍 Debugging Signal Generation Process")
    print("="*50)

    # Import components
    from multi_timeframe_engine import MultiTimeframeEngine
    from regime_detector import MarketRegimeDetector

    # Check API key
    api_key = os.getenv("OANDA_API_KEY")
    if not api_key or len(api_key) < 60:
        print("❌ OANDA API key not loaded properly")
        return

    print("✅ OANDA API key loaded")

    # Initialize components
    engine = MultiTimeframeEngine(api_key=api_key, min_votes_required=1.0, min_strength=15.0)
    regime_detector = MarketRegimeDetector()

    print("✅ Components initialized")

    # Test data fetching
    print("\n📊 Testing data fetching for GBP_USD...")
    try:
        mtf_data = await engine.fetch_multi_timeframe("GBP_USD")
        if not mtf_data:
            print("❌ Failed to fetch multi-timeframe data")
            return

        print("✅ Multi-timeframe data fetched:")
        for tf, df in mtf_data.items():
            print(f"   {tf}: {len(df)} candles")

        # Check M5 data specifically
        df_m5 = mtf_data.get('M5')
        if df_m5 is None or df_m5.empty:
            print("❌ No M5 data available")
            return

        print(f"✅ M5 data: {len(df_m5)} candles")
        print(f"   Latest close: {df_m5['close'].iloc[-1]:.5f}")

    except Exception as e:
        print(f"❌ Data fetching failed: {e}")
        return

    # Test regime detection
    print("\n🎯 Testing regime detection...")
    try:
        regime = regime_detector.detect_regime(df_m5, "GBP_USD")
        should_trade = regime_detector.should_trade(regime)

        print(f"✅ Regime detected: {regime.value}")
        print(f"   Tradeable: {should_trade}")

    except Exception as e:
        print(f"❌ Regime detection failed: {e}")
        return

    # Test multi-timeframe signal generation
    print("\n📈 Testing multi-timeframe signal generation...")
    try:
        mtf_signal = engine.generate_multi_timeframe_signal(mtf_data, regime.value)

        print("✅ Multi-timeframe signal generated:")
        print(f"   Signal: {mtf_signal['signal']}")
        print(f"   Buy votes: {mtf_signal['buy_votes']:.2f}")
        print(f"   Sell votes: {mtf_signal['sell_votes']:.2f}")
        print(f"   Strength: {mtf_signal['strength']:.1f}%")
        print(f"   Confidence: {mtf_signal['confidence']:.2f}")
        print(f"   Agreement: {mtf_signal['agreement']:.1%}")
        print(f"   Passed filters: {mtf_signal['passed_filters']}")

        # Show timeframe breakdown
        print("\n📊 Timeframe breakdown:")
        for tf, analysis in mtf_signal['timeframe_signals'].items():
            buy_v = analysis['buy_votes']
            sell_v = analysis['sell_votes']
            total = analysis['total_indicators']
            direction = 'BUY' if buy_v > sell_v else ('SELL' if sell_v > buy_v else 'NEUTRAL')

            print(f"   {tf}: {direction} ({buy_v:.1f}/{sell_v:.1f}/{total}) - Strength: {analysis['strength']:.1f}%")

            # Show indicator details
            if analysis.get('signal_details'):
                print("      Indicators:")
                for detail in analysis['signal_details'][:2]:  # Show first 2
                    print(f"         {detail}")

        # Show filter results
        if not mtf_signal['passed_filters']:
            print("\n⚠️ Filter rejection reasons:")
            for reason in mtf_signal['filter_results']['reasons']:
                print(f"   {reason}")
        else:
            print("\n✅ All filters passed")

    except Exception as e:
        print(f"❌ Multi-timeframe signal generation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    # Test enhanced signal generation
    print("\n🚀 Testing enhanced signal generation...")
    try:
        from enhanced_signal_generator import EnhancedSignalGenerator
        enhanced_gen = EnhancedSignalGenerator(oanda_api_key=api_key)

        signal = await enhanced_gen.generate_signal("GBP_USD")

        if signal:
            print("✅ Enhanced signal generated:")
            print(f"   Direction: {signal['signal']}")
            print(f"   Strength: {signal.get('strength', 0):.1f}%")
            print(f"   Confidence: {signal.get('confidence', 0):.2f}")
            print(f"   Agreement: {signal.get('agreement', 0):.1%}")
            print(f"   Tradeable: {signal.get('tradeable', False)}")

            if not signal.get('tradeable', False):
                print(f"   Reason: {signal.get('reason', 'Unknown')}")
        else:
            print("❌ Enhanced signal generation returned None")

    except Exception as e:
        print(f"❌ Enhanced signal generation failed: {e}")
        import traceback
        traceback.print_exc()
        return

    print("\n🎉 Debug complete!")

if __name__ == "__main__":
    asyncio.run(debug_signal_generation())