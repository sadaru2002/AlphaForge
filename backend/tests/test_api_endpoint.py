#!/usr/bin/env python3
"""
Test API endpoint
"""
import requests

print('🔍 Testing API Endpoint')
print('='*50)

try:
    # Test health
    response = requests.get('http://localhost:5000/health', timeout=5)
    print(f'Health check: {response.status_code}')

    if response.status_code == 200:
        # Test signal generation
        response = requests.post('http://localhost:5000/api/signals/enhanced/generate', timeout=30)
        print(f'Signal generation: {response.status_code}')

        if response.status_code == 200:
            data = response.json()
            print(f'Status: {data.get("status")}')
            print(f'Signals generated: {data.get("signals_generated", 0)}')

            if data.get('results'):
                for result in data['results']:
                    pair = result.get('pair', 'Unknown')
                    generated = result.get('generated', False)
                    reason = result.get('reason', 'Success')
                    print(f'  {pair}: {generated} - {reason}')
        else:
            print(f'Error: {response.text[:300]}')
    else:
        print('Backend server not responding')

except Exception as e:
    print(f'Error: {str(e)}')