#!/usr/bin/env python3
"""
Quick test to verify threshold alignment fixes
"""
import asyncio
from enhanced_signal_generator import EnhancedSignalGenerator
import os
from dotenv import load_dotenv

load_dotenv()

async def test_thresholds():
    print("\n" + "="*70)
    print("TESTING ALIGNED THRESHOLDS")
    print("="*70)
    
    print("\nConfiguration:")
    print("  - min_votes_required: 1.5")
    print("  - min_strength: 25% (was 30%)")
    print("  - Expected: Signals with 1.5+ votes and 25%+ strength should pass")
    
    generator = EnhancedSignalGenerator()
    
    print("\n" + "-"*70)
    print("Testing signal generation for all 3 instruments...")
    print("-"*70)
    
    for instrument in ['GBP_USD', 'XAU_USD', 'USD_JPY']:
        print(f"\n{instrument}:")
        try:
            result = await generator.generate_signal(instrument)
            
            if result:
                if result['signal'] in ['BUY', 'SELL']:
                    print(f"  ✅ SIGNAL GENERATED: {result['signal']}")
                    print(f"     Entry: {result.get('entry', 'N/A')}")
                    print(f"     Confidence: {result.get('confidence_score', 'N/A'):.1f}%")
                    print(f"     Regime: {result.get('market_regime', 'N/A')}")
                elif result['signal'] == 'SKIP':
                    print(f"  ⏭️  SKIPPED: {result.get('reason', 'Unknown')}")
                    mtf = result.get('mtf_signal', {})
                    print(f"     Strength: {mtf.get('strength', 'N/A'):.1f}%")
                    print(f"     Buy votes: {mtf.get('buy_votes', 'N/A'):.2f}")
                    print(f"     Sell votes: {mtf.get('sell_votes', 'N/A'):.2f}")
            else:
                print(f"  ❌ No result returned")
                
        except Exception as e:
            print(f"  ❌ Error: {e}")
    
    print("\n" + "="*70)
    print("TEST COMPLETE")
    print("="*70 + "\n")

if __name__ == "__main__":
    asyncio.run(test_thresholds())
