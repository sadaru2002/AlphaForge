#!/usr/bin/env python3
"""
Test API vs Direct signal generation
"""
import asyncio
from enhanced_strategy_integration import get_enhanced_strategy

async def test_api_vs_direct():
    print('🔍 Comparing API vs Direct Test')
    print('='*50)

    # Test using the same method as API endpoint
    strategy = get_enhanced_strategy()

    print('Testing GBP_USD with API method...')
    signal = await strategy.generate_signal_for_pair('GBP_USD')

    if signal:
        print('✅ API method: Signal generated')
        print('Direction:', signal.get('direction'))
        print('Confidence:', f"{signal.get('confidence_score', 0):.1%}")
        print('Regime:', signal.get('market_regime'))
    else:
        print('❌ API method: No signal')

    # Get statistics
    stats = strategy.get_statistics()
    print('Total signals:', stats['strategy']['total_signals'])
    print('Tradeable signals:', stats['strategy']['tradeable_signals'])
    print('Filter efficiency:', stats['strategy']['filter_efficiency'])

if __name__ == "__main__":
    asyncio.run(test_api_vs_direct())