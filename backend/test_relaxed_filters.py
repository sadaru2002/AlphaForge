"""
Quick test to verify the relaxed filter thresholds work correctly.
Run this to check if GBP/USD and XAU/USD can now generate signals.
"""
import asyncio
import os
import sys

# Add backend to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from enhanced_signal_generator import EnhancedSignalGenerator

async def test_signal_generation():
    """Test signal generation for all pairs with relaxed filters."""
    print("=" * 80)
    print("AlphaForge Signal Generation Test - Relaxed Filters")
    print("=" * 80)
    print("\nNew Filter Settings:")
    print("  - ADX minimum: 15 (was 20)")
    print("  - min_votes_required: 1.0 (was 2.0)")
    print("  - min_strength: 10% (was 25%)")
    print("  - Signal strength threshold: 10% (was 15%)")
    print("  - Regime: Only blocks UNKNOWN (previously blocked RANGING_HIGH_VOL)")
    print("=" * 80)
    
    api_key = os.getenv("OANDA_API_KEY")
    if not api_key:
        print("\nERROR: OANDA_API_KEY environment variable not set")
        return
    
    generator = EnhancedSignalGenerator(oanda_api_key=api_key)
    
    for instrument in ['GBP_USD', 'XAU_USD', 'USD_JPY']:
        print(f"\n{'='*60}")
        print(f"Testing {instrument}...")
        print(f"{'='*60}")
        
        try:
            signal = await generator.generate_signal(instrument)
            
            if signal:
                print(f"\nSignal: {signal['signal']}")
                print(f"Tradeable: {signal.get('tradeable', False)}")
                print(f"Regime: {signal.get('regime', 'N/A')}")
                
                if signal.get('tradeable'):
                    print(f"  Strength: {signal.get('strength', 0):.1f}%")
                    print(f"  Buy Votes: {signal.get('buy_votes', 0):.1f}")
                    print(f"  Sell Votes: {signal.get('sell_votes', 0):.1f}")
                    print(f"  Entry: {signal.get('entry_price', 0):.5f}")
                    print(f"  SL: {signal.get('stop_loss', 0):.5f}")
                    print(f"  TP: {signal.get('take_profit', 0):.5f}")
                else:
                    print(f"  Reason: {signal.get('reason', 'N/A')}")
                    
                    # Show filter results if available
                    filter_results = signal.get('filter_results', {})
                    if filter_results:
                        print(f"  Filter reasons: {filter_results.get('reasons', [])}")
            else:
                print("  ERROR: No signal returned")
                
        except Exception as e:
            print(f"  ERROR: {e}")
    
    print("\n" + "=" * 80)
    print("Test Complete")
    print("=" * 80)

if __name__ == "__main__":
    asyncio.run(test_signal_generation())
