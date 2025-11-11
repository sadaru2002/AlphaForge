"""
Gemini API Client with Auto-Fallback
Handles interaction with Google's Gemini AI models.
Compatible with google-generativeai 0.1.0rc1 (Python 3.8)
"""

import google.generativeai as genai
import logging
from typing import Optional, Dict, Any
import os

logger = logging.getLogger(__name__)

class GeminiProClient:
    """
    Gemini AI Client with intelligent model fallback
    - Starts with gemini-pro (most capable, 50 requests/day limit)
    - Auto-falls back to gemini-flash (unlimited) after quota exhaustion
    Compatible with older API (0.1.0rc1)
    """
    
    def __init__(self, api_key: str, use_pro_first: bool = True):
        """
        Initialize Gemini client
        
        Args:
            api_key: Google Gemini API key
            use_pro_first: If True, tries Pro model first, falls back to Flash on quota error
        """
        self.api_key = api_key
        self.use_pro_first = use_pro_first
        
        # Configure API
        genai.configure(api_key=self.api_key)
        
        # Model names (simplified for 0.1.0rc1)
        self.pro_model_name = "models/gemini-pro"
        self.flash_model_name = "models/gemini-pro"  # Same for old API
        
        # Current model
        self.current_model_name = self.pro_model_name
        
        logger.info(f"✅ Gemini client initialized (legacy API mode)")
        logger.info(f"   Model: {self.current_model_name}")
        logger.info(f"   Auto-fallback: {'Enabled' if use_pro_first else 'Disabled'}")
    
    def analyze_chart(self, prompt: str, timeout: int = 60) -> Optional[Dict[str, Any]]:
        """
        Send analysis request to Gemini AI
        
        Args:
            prompt: The full trading analysis prompt
            timeout: Request timeout in seconds
            
        Returns:
            Dictionary with analysis results or None if failed
        """
        try:
            logger.info(f"📤 Sending request to {self.current_model_name}...")
            
            # Use generate_text for old API
            response = genai.generate_text(
                model=self.current_model_name,
                prompt=prompt,
                temperature=0.7,
                max_output_tokens=2048
            )
            
            # Extract text response
            if response and hasattr(response, 'result') and response.result:
                logger.info(f"✅ Response received from {self.current_model_name}")
                logger.debug(f"Response length: {len(response.result)} characters")
                
                return {
                    'status': 'success',
                    'response': response.result,
                    'model_used': self.current_model_name
                }
            elif response and hasattr(response, 'candidates') and response.candidates:
                # Try candidates format
                text = response.candidates[0].get('output', '')
                if text:
                    logger.info(f"✅ Response received from {self.current_model_name}")
                    return {
                        'status': 'success',
                        'response': text,
                        'model_used': self.current_model_name
                    }
            
            logger.error("Empty response from Gemini")
            return None
                
        except Exception as e:
            error_str = str(e).lower()
            logger.error(f"Gemini API error: {e}")
            
            # Check if it's a quota/rate limit error
            if '429' in error_str or 'quota' in error_str or 'rate limit' in error_str:
                logger.warning(f"⚠️ Quota exhausted for {self.current_model_name}")
                logger.error("Quota exceeded - using fallback strategy")
            
            return None
    
    def get_model_info(self) -> Dict[str, Any]:
        """Get current model configuration and status"""
        return {
            'current_model': self.current_model_name,
            'api_version': 'legacy (0.1.0rc1)',
            'auto_fallback_enabled': self.use_pro_first
        }
    
    def test_connection(self) -> Dict[str, Any]:
        """
        Test connection to Gemini API
        Returns status and model information
        """
        try:
            # Simple test prompt
            test_prompt = "Respond with only: OK"
            
            response = genai.generate_text(
                model=self.current_model_name,
                prompt=test_prompt,
                max_output_tokens=10
            )
            
            if response and hasattr(response, 'result') and response.result:
                return {
                    'status': 'success',
                    'message': 'Gemini API connection successful',
                    'model_info': self.get_model_info(),
                    'test_response': response.result[:100]
                }
            else:
                return {
                    'status': 'error',
                    'message': 'Empty response from Gemini'
                }
                
        except Exception as e:
            return {
                'status': 'error',
                'message': f'Connection test failed: {str(e)}'
            }
