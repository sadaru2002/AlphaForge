#!/usr/bin/env python3
"""
Test the API endpoint to verify the signal generation fix works
"""
import requests
import time

def test_api_endpoint():
    """Test the enhanced signal generation API endpoint"""
    print("🧪 Testing API Endpoint Fix")
    print("="*40)

    # Test the enhanced generate endpoint
    url = "http://localhost:5000/api/signals/enhanced/generate"

    try:
        print("📡 Calling /api/signals/enhanced/generate...")
        response = requests.post(url, timeout=30)

        print(f"Status Code: {response.status_code}")

        if response.status_code == 200:
            data = response.json()
            print("✅ API Response:")
            print(f"   Status: {data.get('status', 'unknown')}")
            print(f"   Signals Generated: {data.get('signals_generated', 0)}")

            if data.get('signals_generated', 0) > 0:
                print("🎉 SUCCESS: Signals are now being generated!")
                for result in data.get('results', []):
                    if result.get('generated', False):
                        print(f"   ✅ {result['pair']}: {result['direction']} signal")
            else:
                print("❌ No signals generated")
                for result in data.get('results', []):
                    print(f"   ❌ {result['pair']}: {result.get('reason', 'unknown')}")

        else:
            print(f"❌ API Error: {response.status_code}")
            print(f"Response: {response.text}")

    except requests.exceptions.ConnectionError:
        print("❌ Connection Error: Backend server not running")
        print("Please start the backend server first:")
        print("cd backend && python app.py")
    except Exception as e:
        print(f"❌ Test failed: {e}")

if __name__ == "__main__":
    test_api_endpoint()