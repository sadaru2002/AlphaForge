#!/usr/bin/env python3
"""
Test OANDA API and signal generation
"""
import os
import asyncio
from dotenv import load_dotenv
from enhanced_signal_generator import EnhancedSignalGenerator

load_dotenv()

async def test_system():
    print('🧪 AlphaForge System Test')
    print('='*50)

    try:
        # Test API key
        api_key = os.getenv('OANDA_API_KEY')
        if not api_key:
            print('❌ No OANDA API key found')
            return

        print('✅ API key found')

        # Test generator initialization
        generator = EnhancedSignalGenerator(oanda_api_key=api_key)
        print('✅ Generator initialized')

        # Test signal generation
        print('📊 Generating signal for GBP_USD...')
        signal = await generator.generate_signal('GBP_USD')

        if signal:
            print('✅ Signal generated!')
            print(f'Signal: {signal.get("signal", "N/A")}')
            print(f'Strength: {signal.get("strength", 0):.1f}%')
            print(f'Regime: {signal.get("regime", "N/A")}')
            print(f'Tradeable: {signal.get("tradeable", False)}')

            if signal.get('passed_filters', False):
                print('✅ Passed quality filters')
            else:
                print('❌ Failed quality filters')
                filters = signal.get('filter_results', {})
                print(f'Filter results: {filters}')
        else:
            print('❌ No signal generated')

    except Exception as e:
        print(f'❌ Error: {str(e)}')
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    asyncio.run(test_system())