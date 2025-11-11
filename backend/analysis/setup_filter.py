"""
Setup Pre-Filter System
Evaluates if a setup has high probability BEFORE sending to Gemini
This saves API calls and speeds up signal generation
"""

from typing import Dict, List, Any, Optional
import pandas as pd
from datetime import datetime, timezone


class SetupPreFilter:
    """
    Pre-filters trading setups to determine if they're worth analyzing with Gemini AI
    Only high-probability setups pass through to AI analysis
    """
    
    def __init__(self, min_confidence: int = 60):
        """
        Initialize the pre-filter
        
        Args:
            min_confidence: Minimum confidence score to pass (default 60%)
        """
        self.min_confidence = min_confidence
    
    def evaluate_setup(self, data_package: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate if a setup is high probability
        
        Args:
            data_package: Complete market analysis data
            
        Returns:
            dict: {
                'passes_filter': bool,
                'confidence_estimate': int (0-100),
                'reasons': list of strings,
                'setup_type': str or None
            }
        """
        
        confidence_score = 50  # Base score
        reasons = []
        setup_type = None
        
        # Extract data
        mtf_data = {
            'D1': data_package.get('d1', {}),
            'H4': data_package.get('h4', {}),
            'H1': data_package.get('h1', {}),
            'M15': data_package.get('m15', {}),
            'M5': data_package.get('m5', {}),
            'M1': data_package.get('m1', {})
        }
        
        indicators = data_package.get('indicators', {})
        order_blocks = data_package.get('order_blocks', [])
        fvgs = data_package.get('fvgs', [])
        market_structure = data_package.get('market_structure', {})
        premium_discount = data_package.get('premium_discount', {})
        session = data_package.get('session', {})
        current_price = data_package.get('current_price', 0)
        
        # ==================== TIMEFRAME ALIGNMENT ====================
        d1_trend = mtf_data['D1'].get('trend', 'UNKNOWN')
        h4_trend = mtf_data['H4'].get('trend', 'UNKNOWN')
        h1_trend = mtf_data['H1'].get('trend', 'UNKNOWN')
        m15_trend = mtf_data['M15'].get('trend', 'UNKNOWN')
        m5_trend = mtf_data['M5'].get('trend', 'UNKNOWN')
        
        # Check higher timeframe alignment (D1 + H4)
        if d1_trend == h4_trend and d1_trend in ['BULLISH', 'BEARISH']:
            confidence_score += 15
            reasons.append(f"D1 and H4 aligned ({d1_trend})")
        elif d1_trend != h4_trend:
            confidence_score -= 10
            reasons.append(f"D1 ({d1_trend}) conflicts with H4 ({h4_trend})")
        
        # Check lower timeframe alignment (H1 + M15)
        if h1_trend == m15_trend and h1_trend in ['BULLISH', 'BEARISH']:
            confidence_score += 10
            reasons.append(f"H1 and M15 aligned ({h1_trend})")
        
        # Perfect alignment across all major timeframes
        if d1_trend == h4_trend == h1_trend == m15_trend and d1_trend in ['BULLISH', 'BEARISH']:
            confidence_score += 10
            reasons.append("✅ Perfect multi-timeframe alignment!")
        
        # ==================== SESSION QUALITY ====================
        session_name = session.get('name', 'UNKNOWN')
        session_quality = session.get('quality', 'UNKNOWN')
        
        if session_name in ['LONDON_KILL_ZONE', 'NEW_YORK_KILL_ZONE']:
            confidence_score += 15
            reasons.append(f"In {session_name}")
        elif session_name in ['LONDON_OPEN', 'NEW_YORK_OPEN']:
            confidence_score += 10
            reasons.append(f"In {session_name}")
        else:
            confidence_score -= 15
            reasons.append(f"Outside Kill Zone ({session_name})")
        
        # ==================== SMC/ICT CONFLUENCE ====================
        
        # Order Blocks
        if order_blocks and len(order_blocks) > 0:
            strongest_ob = max(order_blocks, key=lambda x: x.get('strength', 0))
            ob_strength = strongest_ob.get('strength', 0)
            
            if ob_strength > 50:
                confidence_score += 12
                reasons.append(f"Strong Order Block detected (strength: {ob_strength:.0f})")
                setup_type = "Order Block Retest"
            elif ob_strength > 30:
                confidence_score += 7
                reasons.append(f"Moderate Order Block detected")
        else:
            confidence_score -= 5
            reasons.append("No Order Blocks detected")
        
        # Fair Value Gaps
        if fvgs and len(fvgs) > 0:
            unfilled_fvgs = [fvg for fvg in fvgs if fvg.get('status') in ['unfilled', 'partially_filled']]
            
            if unfilled_fvgs:
                confidence_score += 10
                reasons.append(f"{len(unfilled_fvgs)} unfilled FVG(s) present")
                if not setup_type:
                    setup_type = "FVG Fill"
        
        # Premium/Discount Zones
        pd_zone = premium_discount.get('zone', 'EQUILIBRIUM')
        pd_percentage = premium_discount.get('percentage', 50)
        
        # Check if price is in correct zone for the trend
        if d1_trend == 'BULLISH' and pd_zone == 'DISCOUNT':
            confidence_score += 10
            reasons.append("✅ Price in DISCOUNT zone (good for BUYS)")
        elif d1_trend == 'BEARISH' and pd_zone == 'PREMIUM':
            confidence_score += 10
            reasons.append("✅ Price in PREMIUM zone (good for SELLS)")
        elif pd_zone == 'EQUILIBRIUM':
            confidence_score -= 5
            reasons.append("Price in EQUILIBRIUM (wait for better zone)")
        else:
            confidence_score -= 8
            reasons.append(f"❌ Price in wrong zone ({pd_zone} for {d1_trend} trend)")
        
        # Market Structure
        structure_trend = market_structure.get('trend', 'UNKNOWN')
        if structure_trend in ['BULLISH', 'BEARISH']:
            confidence_score += 5
            reasons.append(f"Clear market structure ({structure_trend})")
        
        # ==================== TECHNICAL INDICATORS ====================
        
        rsi = indicators.get('rsi', 50)
        macd_histogram = indicators.get('macd_histogram', 0)
        adx = indicators.get('adx', 0)
        atr_pips = indicators.get('atr', 0) * 10000
        
        # RSI momentum
        if d1_trend == 'BULLISH' and rsi > 50:
            confidence_score += 5
            reasons.append(f"RSI confirms bullish momentum ({rsi:.0f})")
        elif d1_trend == 'BEARISH' and rsi < 50:
            confidence_score += 5
            reasons.append(f"RSI confirms bearish momentum ({rsi:.0f})")
        
        # MACD alignment
        if d1_trend == 'BULLISH' and macd_histogram > 0:
            confidence_score += 5
            reasons.append("MACD histogram positive")
        elif d1_trend == 'BEARISH' and macd_histogram < 0:
            confidence_score += 5
            reasons.append("MACD histogram negative")
        
        # Trend strength (ADX)
        if adx > 25:
            confidence_score += 8
            reasons.append(f"Strong trend (ADX: {adx:.0f})")
        elif adx < 15:
            confidence_score -= 8
            reasons.append(f"Weak/choppy trend (ADX: {adx:.0f})")
        
        # ==================== RISK MANAGEMENT ====================
        
        # Estimate stop loss size based on ATR
        estimated_sl_pips = atr_pips * 1.5
        
        if estimated_sl_pips > 15:
            confidence_score -= 15
            reasons.append(f"⚠️ Estimated SL ({estimated_sl_pips:.0f} pips) exceeds 15 pip limit")
        elif estimated_sl_pips <= 10:
            confidence_score += 5
            reasons.append(f"✅ Tight stop possible ({estimated_sl_pips:.0f} pips)")
        
        # ==================== VOLUME CONFIRMATION ====================
        
        volume_data = data_package.get('volume', {})
        volume_status = volume_data.get('status', 'UNKNOWN')
        
        if volume_status == 'ABOVE_AVERAGE':
            confidence_score += 8
            reasons.append("Volume confirming (above average)")
        elif volume_status == 'BELOW_AVERAGE':
            confidence_score -= 5
            reasons.append("Volume below average")
        
        # ==================== FINAL EVALUATION ====================
        
        # Cap confidence at 0-100
        confidence_score = max(0, min(100, confidence_score))
        
        # Determine if setup passes filter
        passes_filter = confidence_score >= self.min_confidence
        
        # Add overall assessment
        if passes_filter:
            reasons.append(f"✅ PASSES PRE-FILTER (confidence: {confidence_score}%)")
        else:
            reasons.append(f"❌ REJECTED (confidence: {confidence_score}% < {self.min_confidence}%)")
        
        return {
            'passes_filter': passes_filter,
            'confidence_estimate': confidence_score,
            'reasons': reasons,
            'setup_type': setup_type,
            'direction': self._determine_direction(d1_trend, h4_trend, m15_trend, m5_trend),
            'estimated_sl_pips': estimated_sl_pips
        }
    
    def _determine_direction(self, d1_trend: str, h4_trend: str, m15_trend: str, m5_trend: str) -> str:
        """
        Determine likely trade direction based on timeframe trends
        
        Returns:
            'BUY', 'SELL', or 'NO_TRADE'
        """
        
        # Higher timeframes dominate
        if d1_trend == 'BULLISH' and h4_trend in ['BULLISH', 'RANGING']:
            if m15_trend in ['BULLISH', 'RANGING'] or m5_trend == 'BULLISH':
                return 'BUY'
        
        elif d1_trend == 'BEARISH' and h4_trend in ['BEARISH', 'RANGING']:
            if m15_trend in ['BEARISH', 'RANGING'] or m5_trend == 'BEARISH':
                return 'SELL'
        
        return 'NO_TRADE'
    
    def should_analyze_with_gemini(self, data_package: Dict[str, Any]) -> bool:
        """
        Quick check if setup should be sent to Gemini AI
        
        Args:
            data_package: Market analysis data
            
        Returns:
            bool: True if worth analyzing with AI
        """
        result = self.evaluate_setup(data_package)
        return result['passes_filter']
    
    def get_filter_summary(self, data_package: Dict[str, Any]) -> str:
        """
        Get human-readable summary of filter evaluation
        
        Args:
            data_package: Market analysis data
            
        Returns:
            str: Formatted summary
        """
        result = self.evaluate_setup(data_package)
        
        lines = []
        lines.append("=" * 60)
        lines.append("SETUP PRE-FILTER EVALUATION")
        lines.append("=" * 60)
        lines.append(f"Confidence Estimate: {result['confidence_estimate']}%")
        lines.append(f"Passes Filter: {'✅ YES' if result['passes_filter'] else '❌ NO'}")
        lines.append(f"Setup Type: {result['setup_type'] or 'Unknown'}")
        lines.append(f"Direction: {result['direction']}")
        lines.append(f"Estimated SL: {result['estimated_sl_pips']:.0f} pips")
        lines.append("")
        lines.append("Reasons:")
        for i, reason in enumerate(result['reasons'], 1):
            lines.append(f"  {i}. {reason}")
        lines.append("=" * 60)
        
        return "\n".join(lines)


class SignalOptimizer:
    """
    Optimizes signal generation to target 10+ signals per trading day
    """
    
    def __init__(self):
        self.signals_today = 0
        self.last_signal_time = None
        self.target_daily_signals = 10
    
    def should_be_aggressive(self, current_time: datetime = None) -> bool:
        """
        Determine if system should be more aggressive in signal generation
        
        Returns:
            bool: True if should accept lower confidence setups
        """
        if current_time is None:
            current_time = datetime.now(timezone.utc)
        
        # Get current hour (UTC)
        hour = current_time.hour
        
        # London Kill Zone (07:00-10:00 UTC) - Be aggressive
        if 7 <= hour < 10:
            return True
        
        # NY Kill Zone (13:00-16:00 UTC) - Be aggressive
        if 13 <= hour < 16:
            return True
        
        # If we have < 5 signals and it's past 12:00 UTC, be more aggressive
        if self.signals_today < 5 and hour >= 12:
            return True
        
        return False
    
    def get_adjusted_min_confidence(self) -> int:
        """
        Get adjusted minimum confidence based on time and signals count
        
        Returns:
            int: Adjusted minimum confidence (60-70%)
        """
        if self.should_be_aggressive():
            return 60  # Accept 60%+ confidence during kill zones
        else:
            return 65  # Require 65%+ outside kill zones
    
    def record_signal(self):
        """Record that a signal was generated"""
        self.signals_today += 1
        self.last_signal_time = datetime.now(timezone.utc)
    
    def reset_daily_counter(self):
        """Reset signal counter (call at start of new trading day)"""
        self.signals_today = 0
        self.last_signal_time = None
    
    def get_progress_summary(self) -> str:
        """Get daily progress summary"""
        progress_pct = (self.signals_today / self.target_daily_signals) * 100
        return f"Signals today: {self.signals_today}/{self.target_daily_signals} ({progress_pct:.0f}%)"

