"""
Optimized Gemini AI Signal Validator
Fast, efficient validation with caching and rate limiting
"""
import os
import json
import logging
import time
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple
from functools import lru_cache
import hashlib
import google.generativeai as genai
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class GeminiSignalValidator:
    """
    Optimized Gemini AI validator for trading signals
    Features:
    - Fast Gemini 2.5 Flash model
    - Smart caching (avoid redundant API calls)
    - Rate limiting (1 call/2 seconds)
    - Concise prompts (lower token usage)
    - Batch validation ready
    """
    
    def __init__(self):
        """Initialize optimized Gemini validator"""
        self.enabled = False
        self.model = None
        # Use stable 2.0-flash, fallback to 2.5-flash, upgrade to 2.5-pro on quota
        self.primary_model_name = "models/gemini-2.0-flash"  # Most stable & reliable
        self.flash_25_model_name = "models/gemini-2.5-flash"  # Faster, for quota issues
        self.pro_model_name = "models/gemini-2.5-pro"  # Highest quality (quota fallback)
        self.current_model_tier = "2.0-flash"  # Track which tier we're using
        
        # Rate limiting
        self.last_call_time = 0
        self.min_call_interval = 2.0  # seconds between calls
        
        # Response cache (avoid duplicate validations)
        self.cache = {}
        self.cache_ttl = 300  # 5 minutes cache TTL
        self.cache_hits = 0
        self.cache_misses = 0
        
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
                from google.generativeai.types import HarmCategory, HarmBlockThreshold
                
                self.model = genai.GenerativeModel(
                    self.primary_model_name,
                    generation_config={
                        "temperature": 0.3,  # Lower = more consistent
                        "top_p": 0.8,
                        "top_k": 20,
                        "max_output_tokens": 300,  # Limit response size
                    },
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
                logger.info(f"✅ Gemini validator initialized: {self.primary_model_name} (optimized)")
                self.enabled = True
            except Exception as e:
                logger.warning(f"⚠️ Primary 2.0-flash failed, trying 2.5-flash: {e}")
                self.model = genai.GenerativeModel(
                    self.flash_25_model_name,
                    generation_config={
                        "temperature": 0.3,
                        "top_p": 0.8,
                        "top_k": 20,
                        "max_output_tokens": 300,
                    },
                    safety_settings={
                        HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                        HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                    }
                )
                logger.info(f"✅ Gemini validator initialized: {self.flash_25_model_name} (fallback)")
                self.current_model_tier = "2.5-flash"
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
        Validate trading signal with Gemini AI (optimized with caching)
        
        Args:
            signal_data: Signal information (symbol, type, price, etc.)
            market_analysis: Technical analysis data
            confidence_threshold: Minimum confidence to approve (default 60%)
            
        Returns:
            Tuple of (approved: bool, gemini_response: Dict or None)
        """
        if not self.enabled:
            logger.warning("⚠️ Gemini disabled, auto-approving")
            return True, None
        
        # Generate cache key
        cache_key = self._generate_cache_key(signal_data, market_analysis)
        
        # Check cache first
        cached_result = self._get_cached_result(cache_key)
        if cached_result:
            self.cache_hits += 1
            logger.info(f"✨ Cache hit! ({self.cache_hits} hits / {self.cache_misses} misses)")
            confidence = cached_result.get('confidence', 0)
            approved = confidence >= confidence_threshold
            return approved, cached_result
        
        self.cache_misses += 1
            
        try:
            # Rate limiting
            self._apply_rate_limit()
            
            # Build concise validation prompt
            prompt = self._build_optimized_prompt(signal_data, market_analysis)
            
            # Call Gemini API
            logger.info(f"🤖 Validating with Gemini...")
            
            try:
                response = self.model.generate_content(prompt)
            except Exception as api_error:
                # Check if it's a quota/rate limit error
                error_msg = str(api_error).lower()
                if 'quota' in error_msg or 'rate' in error_msg or 'limit' in error_msg or '429' in error_msg:
                    logger.warning(f"⚠️ {self.current_model_tier} quota exceeded, upgrading to 2.5-pro...")
                    
                    # Try Pro model as fallback for quota issues
                    try:
                        from google.generativeai.types import HarmCategory, HarmBlockThreshold
                        
                        pro_model = genai.GenerativeModel(
                            self.pro_model_name,
                            generation_config={
                                "temperature": 0.3,
                                "top_p": 0.8,
                                "top_k": 20,
                                "max_output_tokens": 300,
                            },
                            safety_settings={
                                HarmCategory.HARM_CATEGORY_HATE_SPEECH: HarmBlockThreshold.BLOCK_NONE,
                                HarmCategory.HARM_CATEGORY_HARASSMENT: HarmBlockThreshold.BLOCK_NONE,
                                HarmCategory.HARM_CATEGORY_SEXUALLY_EXPLICIT: HarmBlockThreshold.BLOCK_NONE,
                                HarmCategory.HARM_CATEGORY_DANGEROUS_CONTENT: HarmBlockThreshold.BLOCK_NONE,
                            }
                        )
                        logger.info(f"✅ Switched to 2.5-pro (quota fallback)")
                        response = pro_model.generate_content(prompt)
                        self.model = pro_model  # Use Pro for rest of session
                        self.current_model_tier = "2.5-pro"
                    except Exception as pro_error:
                        logger.error(f"❌ Pro model also failed: {pro_error}")
                        return True, None
                else:
                    raise api_error
            
            # Check if response was blocked
            if not response.candidates or not response.candidates[0].content.parts:
                finish_reason = response.candidates[0].finish_reason if response.candidates else 'UNKNOWN'
                logger.warning(f"⚠️ Response blocked by safety filters (reason: {finish_reason})")
                logger.warning("Auto-approving - safety filters too strict")
                return True, None
            
            # Parse response
            gemini_data = self._parse_response(response.text)
            
            if not gemini_data:
                logger.warning("⚠️ Parse failed, auto-approving")
                return True, None
            
            # Cache the result
            self._cache_result(cache_key, gemini_data)
            
            # Check confidence threshold
            confidence = gemini_data.get('confidence', 0)
            approved = confidence >= confidence_threshold
            
            status = "✅ APPROVED" if approved else "❌ REJECTED"
            logger.info(f"{status} | Confidence: {confidence}% | Threshold: {confidence_threshold}%")
            
            return approved, gemini_data
            
        except Exception as e:
            logger.error(f"❌ Gemini error: {e}")
            return True, None  # Auto-approve on error
    
    def _build_optimized_prompt(self, signal_data: Dict, market_analysis: Dict) -> str:
        """Build concise, token-efficient prompt"""
        
        # Calculate potential RR
        entry = signal_data.get('entry_price', 0)
        sl = signal_data.get('stop_loss', 0)
        tp = signal_data.get('take_profit', 0)
        risk = abs(entry - sl)
        reward = abs(tp - entry)
        current_rr = round(reward / risk, 2) if risk > 0 else 0
        
        # Professional trading analysis prompt
        prompt = f"""As a technical analysis expert, evaluate this foreign exchange trading setup for educational purposes.

SETUP DETAILS:
Currency Pair: {signal_data.get('symbol')}
Direction: {signal_data.get('type')}
Entry Level: {entry}
Stop Loss: {sl}
Take Profit: {tp}
Risk-Reward: 1:{current_rr}
Timeframe: M5 (5-minute)

TECHNICAL INDICATORS:
RSI (14): {market_analysis.get('rsi', 'N/A')}
ADX (14): {market_analysis.get('adx', 'N/A')}
Market Trend: {market_analysis.get('trend', 'N/A')}
Volume Status: {market_analysis.get('volume_status', 'N/A')}

ANALYSIS REQUEST:
Assess this technical setup quality on a scale of 0-100 and provide optimal stop-loss and take-profit levels.

Respond in this exact JSON structure:
{{"confidence": 75, "approved": true, "optimized_sl": {sl}, "optimized_tp": {tp}, "risk_reward": {current_rr}, "reasoning": "Brief technical analysis"}}
"""
        return prompt
    
    def _generate_cache_key(self, signal_data: Dict, market_analysis: Dict) -> str:
        """Generate unique cache key for signal"""
        # Create hash from key signal parameters
        key_string = f"{signal_data.get('symbol')}_{signal_data.get('type')}_"
        key_string += f"{signal_data.get('entry_price')}_{signal_data.get('stop_loss')}_"
        key_string += f"{market_analysis.get('rsi')}_{market_analysis.get('adx')}"
        
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _get_cached_result(self, cache_key: str) -> Optional[Dict]:
        """Get cached validation result if not expired"""
        if cache_key in self.cache:
            cached_data, timestamp = self.cache[cache_key]
            age = (datetime.now() - timestamp).total_seconds()
            
            if age < self.cache_ttl:
                return cached_data
            else:
                # Expired, remove from cache
                del self.cache[cache_key]
        
        return None
    
    def _cache_result(self, cache_key: str, result: Dict):
        """Cache validation result"""
        self.cache[cache_key] = (result, datetime.now())
        
        # Clean old cache entries (keep max 100)
        if len(self.cache) > 100:
            oldest_key = min(self.cache.keys(), key=lambda k: self.cache[k][1])
            del self.cache[oldest_key]
    
    def _apply_rate_limit(self):
        """Apply rate limiting between API calls"""
        elapsed = time.time() - self.last_call_time
        
        if elapsed < self.min_call_interval:
            wait_time = self.min_call_interval - elapsed
            logger.debug(f"⏳ Rate limit: waiting {wait_time:.1f}s")
            time.sleep(wait_time)
        
        self.last_call_time = time.time()
    
    def get_stats(self) -> Dict:
        """Get validator statistics"""
        total = self.cache_hits + self.cache_misses
        hit_rate = (self.cache_hits / total * 100) if total > 0 else 0
        
        return {
            'enabled': self.enabled,
            'model_tier': self.current_model_tier,
            'cache_hits': self.cache_hits,
            'cache_misses': self.cache_misses,
            'hit_rate': f"{hit_rate:.1f}%",
            'cached_items': len(self.cache)
        }
    
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
    
    # Test signal validation twice (to test caching)
    print(f"\n{'='*60}")
    print(f"🧪 Gemini Validator Test (Optimized)")
    print(f"{'='*60}\n")
    
    print("📊 Test 1: Initial validation")
    approved1, result1 = validator.validate_signal(signal, analysis)
    print(f"✓ Approved: {approved1}")
    if result1:
        print(f"✓ Confidence: {result1.get('confidence')}%")
        print(f"✓ Reasoning: {result1.get('reasoning')}")
    
    print(f"\n📊 Test 2: Cached validation (should be instant)")
    approved2, result2 = validator.validate_signal(signal, analysis)
    print(f"✓ Approved: {approved2}")
    
    # Show stats
    stats = validator.get_stats()
    print(f"\n📈 Validator Stats:")
    print(f"✓ Cache Hit Rate: {stats['hit_rate']}")
    print(f"✓ Cached Items: {stats['cached_items']}")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    # Run test
    test_validator()
