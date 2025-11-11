"""
Simple Gemini AI Signal Validator
Validates trading signals and optimizes SL/TP levels
"""
import os
import json
import logging
from datetime import datetime
from typing import Dict, Optional, Tuple
import google.generativeai as genai

logger = logging.getLogger(__name__)


class GeminiSignalValidator:
    """
    Lightweight Gemini AI validator for trading signals
    Uses Gemini 2.0 Flash for fast, cost-effective validation
    """
    
    def __init__(self):
        """Initialize Gemini validator"""
        self.enabled = False
        self.model = None
        # Use newer Gemini 2.5 Flash model per request; fall back to 2.0 Flash (exp) if needed
        self.primary_model_name = "gemini-2.5-flash"
        self.fallback_model_name = "gemini-2.0-flash-exp"
        
        try:
            # Get API key from environment
            api_key = os.getenv('GEMINI_API_KEY') or os.getenv('GOOGLE_API_KEY')
            
            if not api_key:
                logger.warning("⚠️ No Gemini API key found in environment")
                return
                
            # Configure Gemini
            genai.configure(api_key=api_key)
            
            # Try primary model first
            try:
                self.model = genai.GenerativeModel(self.primary_model_name)
                logger.info(f"✅ Gemini validator initialized with {self.primary_model_name}")
                self.enabled = True
            except Exception as e:
                logger.warning(f"⚠️ Primary model {self.primary_model_name} failed, trying fallback: {e}")
                # Fallback to Gemini 1.5 Flash
                self.model = genai.GenerativeModel(self.fallback_model_name)
                logger.info(f"✅ Gemini validator initialized with {self.fallback_model_name} (fallback)")
                self.enabled = True
                
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini: {e}")
            self.enabled = False
    
    def validate_signal(
        self,
        signal_data: Dict,
        market_analysis: Dict,
        confidence_threshold: float = 0.60
    ) -> Tuple[bool, Optional[Dict]]:
        """
        Validate trading signal with Gemini AI
        
        Args:
            signal_data: Signal information (symbol, type, price, etc.)
            market_analysis: Technical analysis data
            confidence_threshold: Minimum confidence to approve (default 60%)
            
        Returns:
            Tuple of (approved: bool, gemini_response: Dict or None)
        """
        if not self.enabled:
            logger.warning("⚠️ Gemini not available, auto-approving signal")
            return True, None
            
        try:
            # Build validation prompt
            prompt = self._build_validation_prompt(signal_data, market_analysis)
            
            # Call Gemini API
            logger.info(f"🤖 Sending signal to Gemini for validation...")
            response = self.model.generate_content(prompt)
            
            # Parse response
            gemini_data = self._parse_response(response.text)
            
            if not gemini_data:
                logger.warning("⚠️ Failed to parse Gemini response, auto-approving")
                return True, None
            
            # Check confidence threshold
            confidence = gemini_data.get('confidence', 0)
            approved = confidence >= confidence_threshold
            
            if approved:
                logger.info(f"✅ Gemini APPROVED signal (confidence: {confidence}%)")
            else:
                logger.warning(f"❌ Gemini REJECTED signal (confidence: {confidence}% < {confidence_threshold}%)")
            
            return approved, gemini_data
            
        except Exception as e:
            logger.error(f"❌ Gemini validation error: {e}")
            # On error, auto-approve to not block trading
            return True, None
    
    def _build_validation_prompt(self, signal_data: Dict, market_analysis: Dict) -> str:
        """Build prompt for Gemini validation"""
        
        prompt = f"""You are an expert forex trading analyst. Analyze this trading signal and provide your assessment.

**SIGNAL DETAILS:**
- Symbol: {signal_data.get('symbol')}
- Type: {signal_data.get('type')}
- Entry Price: {signal_data.get('entry_price')}
- Current Price: {signal_data.get('current_price')}
- Stop Loss: {signal_data.get('stop_loss')}
- Take Profit: {signal_data.get('take_profit')}

**TECHNICAL ANALYSIS:**
- RSI: {market_analysis.get('rsi', 'N/A')}
- ADX: {market_analysis.get('adx', 'N/A')}
- Trend: {market_analysis.get('trend', 'N/A')}
- ALMA Crossover: {market_analysis.get('alma_signal', 'N/A')}
- Volume: {market_analysis.get('volume_status', 'N/A')}

**YOUR TASK:**
1. Assess signal quality (0-100%)
2. Suggest optimized Stop Loss and Take Profit levels
3. Provide brief reasoning

**RESPONSE FORMAT (JSON only):**
{{
    "confidence": <number 0-100>,
    "approved": <true/false>,
    "optimized_sl": <number>,
    "optimized_tp": <number>,
    "risk_reward": <number>,
    "reasoning": "<brief explanation>"
}}

Respond with ONLY the JSON object, no markdown formatting.
"""
        return prompt
    
    def _parse_response(self, response_text: str) -> Optional[Dict]:
        """Parse Gemini JSON response"""
        try:
            # Remove markdown code blocks if present
            text = response_text.strip()
            if text.startswith('```'):
                # Extract JSON from code block
                lines = text.split('\n')
                json_lines = []
                in_code = False
                for line in lines:
                    if line.startswith('```'):
                        in_code = not in_code
                        continue
                    if in_code or (not line.startswith('```')):
                        json_lines.append(line)
                text = '\n'.join(json_lines)
            
            # Parse JSON
            data = json.loads(text)
            
            # Validate required fields
            required = ['confidence', 'approved', 'optimized_sl', 'optimized_tp']
            if not all(field in data for field in required):
                logger.warning(f"⚠️ Gemini response missing required fields: {data}")
                return None
            
            return data
            
        except json.JSONDecodeError as e:
            logger.error(f"❌ Failed to parse Gemini JSON: {e}")
            logger.debug(f"Response text: {response_text}")
            return None
        except Exception as e:
            logger.error(f"❌ Error parsing Gemini response: {e}")
            return None


# Quick test function
def test_validator():
    """Test the Gemini validator"""
    validator = GeminiSignalValidator()
    
    if not validator.enabled:
        print("❌ Validator not enabled (check API key)")
        return
    
    # Test signal
    signal = {
        'symbol': 'GBP_USD',
        'type': 'BUY',
        'entry_price': 1.2650,
        'current_price': 1.2650,
        'stop_loss': 1.2600,
        'take_profit': 1.2750
    }
    
    analysis = {
        'rsi': 55,
        'adx': 25,
        'trend': 'BULLISH',
        'alma_signal': 'BULLISH_CROSSOVER',
        'volume_status': 'HIGH'
    }
    
    approved, result = validator.validate_signal(signal, analysis)
    
    print(f"\n{'='*60}")
    print(f"✅ Gemini Validator Test")
    print(f"{'='*60}")
    print(f"Approved: {approved}")
    if result:
        print(f"Confidence: {result.get('confidence')}%")
        print(f"Optimized SL: {result.get('optimized_sl')}")
        print(f"Optimized TP: {result.get('optimized_tp')}")
        print(f"Risk/Reward: {result.get('risk_reward')}")
        print(f"Reasoning: {result.get('reasoning')}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Run test
    test_validator()
