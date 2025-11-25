#!/usr/bin/env python3
"""
Test script to verify the enhanced strategy integration fix
"""
import asyncio
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

async def test_api_vs_direct():
    """Test API endpoint vs direct call to verify fix"""
    print("🔧 Testing Enhanced Strategy Integration Fix")
    print("="*50)

    # Test 1: Direct call (should work)
    print("\n1️⃣ Testing Direct Call...")
    try:
        from enhanced_strategy_integration import get_enhanced_strategy

        strategy = get_enhanced_strategy()
        print("✅ Strategy instance created successfully")

        # Check if API key is loaded
        api_key = os.getenv("OANDA_API_KEY")
        if api_key and len(api_key) > 60:
            print(f"✅ OANDA API key loaded (length: {len(api_key)})")
        else:
            print("❌ OANDA API key not loaded properly")
            return

        # Test signal generation for one pair
        signal = await strategy.generate_signal_for_pair('GBP_USD')
        if signal:
            print("✅ Direct signal generation: SUCCESS")
            print(f"   Direction: {signal['direction']}")
            print(f"   Confidence: {signal['confidence_score']:.1%}")
            print(f"   Regime: {signal['market_regime']}")
        else:
            print("❌ Direct signal generation: FAILED (filtered)")

    except Exception as e:
        print(f"❌ Direct call failed: {e}")
        return

    # Test 2: Simulate API call (should now work)
    print("\n2️⃣ Testing API-style Call...")
    try:
        # Reset global instance to simulate fresh API call
        import enhanced_strategy_integration
        enhanced_strategy_integration.enhanced_strategy = None

        strategy2 = enhanced_strategy_integration.get_enhanced_strategy()
        print("✅ Fresh strategy instance created")

        signal2 = await strategy2.generate_signal_for_pair('GBP_USD')
        if signal2:
            print("✅ API-style signal generation: SUCCESS")
            print(f"   Direction: {signal2['direction']}")
            print(f"   Confidence: {signal2['confidence_score']:.1%}")
            print(f"   Regime: {signal2['market_regime']}")
        else:
            print("❌ API-style signal generation: FAILED (filtered)")

    except Exception as e:
        print(f"❌ API-style call failed: {e}")
        return

    print("\n🎉 Fix verification complete!")
    print("If both tests show SUCCESS, the fix is working.")
    print("Restart the backend server to apply the fix to the API endpoints.")

if __name__ == "__main__":
    asyncio.run(test_api_vs_direct())