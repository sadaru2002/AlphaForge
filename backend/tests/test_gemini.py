"""Test Gemini AI Validator"""
from dotenv import load_dotenv
import os

# Load environment
load_dotenv()

print("="*60)
print("Testing Gemini AI Validator")
print("="*60)

# Check API key
gemini_key = os.getenv('GEMINI_API_KEY')
print(f"\n1. API Key Status:")
if gemini_key:
    print(f"   ✅ Found: {gemini_key[:20]}...")
else:
    print(f"   ❌ Not found in environment")

# Test validator initialization
print(f"\n2. Validator Initialization:")
try:
    from gemini.simple_validator import GeminiSignalValidator
    validator = GeminiSignalValidator()
    
    if validator.enabled:
        print(f"   ✅ Validator enabled")
        print(f"   Model: {validator.primary_model_name}")
    else:
        print(f"   ❌ Validator disabled")
except Exception as e:
    print(f"   ❌ Error: {e}")

# Test signal validation
if validator.enabled:
    print(f"\n3. Testing Signal Validation:")
    
    test_signal = {
        'symbol': 'EUR_USD',
        'type': 'BUY',
        'entry_price': 1.0850,
        'current_price': 1.0850,
        'stop_loss': 1.0800,
        'take_profit': 1.0950
    }
    
    test_analysis = {
        'rsi': 58,
        'adx': 28,
        'trend': 'BULLISH',
        'alma_signal': 'BULLISH_CROSSOVER',
        'volume_status': 'HIGH'
    }
    
    try:
        approved, result = validator.validate_signal(test_signal, test_analysis)
        
        print(f"   Signal Approved: {approved}")
        if result:
            print(f"   Confidence: {result.get('confidence')}%")
            print(f"   Optimized SL: {result.get('optimized_sl')}")
            print(f"   Optimized TP: {result.get('optimized_tp')}")
            print(f"   Risk/Reward: {result.get('risk_reward')}")
            print(f"   Reasoning: {result.get('reasoning')}")
    except Exception as e:
        print(f"   ❌ Validation error: {e}")

print("\n" + "="*60)
