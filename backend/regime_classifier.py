import pandas as pd
import numpy as np
from typing import Dict, Literal
import logging

logger = logging.getLogger(__name__)

RegimeType = Literal['STRONG_TREND', 'WEAK_TREND', 'RANGING', 'VOLATILE_CHOP']

class RegimeClassifier:
    """
    Multi-timeframe regime classifier for identifying market conditions.
    
    Regime Types:
    - STRONG_TREND: ADX > 25, price clearly above/below EMAs
    - WEAK_TREND: ADX 18-25, moderate trend
    - RANGING: ADX < 18, sideways market
    - VOLATILE_CHOP: High ATR but low ADX
    """
    
    def __init__(self):
        self.adx_strong_threshold = 25
        self.adx_weak_threshold = 18
        self.atr_high_threshold = 0.008  # 0.8% volatility
        
    def classify_regime(self, mtf_data: Dict[str, pd.DataFrame]) -> Dict:
        """
        Classify market regime using multi-timeframe analysis.
        
        Args:
            mtf_data: Dictionary with 'M15', 'H1', 'H4' DataFrames
            
        Returns:
            {
                'regime': RegimeType,
                'trend_strength': float (0-100),
                'trend_direction': 'BULLISH' | 'BEARISH' | 'NEUTRAL',
                'confidence': float (0-1)
            }
        """
        try:
            # Primary analysis on H1 (our main timeframe)
            h1_df = mtf_data.get('H1')
            if h1_df is None or len(h1_df) < 50:
                return self._default_regime()
            
            # Calculate indicators
            h1_regime = self._analyze_timeframe(h1_df, 'H1')
            
            # Optional: Add H4 for confirmation if available
            h4_df = mtf_data.get('H4')
            if h4_df is not None and len(h4_df) >= 50:
                h4_regime = self._analyze_timeframe(h4_df, 'H4')
                # Weight: H1 70%, H4 30%
                h1_regime['trend_strength'] = (h1_regime['trend_strength'] * 0.7 + 
                                               h4_regime['trend_strength'] * 0.3)
            
            return h1_regime
            
        except Exception as e:
            logger.error(f"Error in regime classification: {e}")
            return self._default_regime()
    
    def _analyze_timeframe(self, df: pd.DataFrame, timeframe: str) -> Dict:
        """Analyze a single timeframe for regime."""
        # Calculate ADX if not present
        adx = self._calculate_adx(df)
        
        # Calculate EMAs
        ema_20 = df['close'].ewm(span=20, adjust=False).mean()
        ema_50 = df['close'].ewm(span=50, adjust=False).mean()
        
        # Calculate ATR
        atr = self._calculate_atr(df)
        atr_pct = atr.iloc[-1] / df['close'].iloc[-1] if len(atr) > 0 else 0
        
        # Current values
        current_price = df['close'].iloc[-1]
        current_adx = adx.iloc[-1] if len(adx) > 0 else 0
        current_ema20 = ema_20.iloc[-1]
        current_ema50 = ema_50.iloc[-1]
        
        # Determine trend direction
        if current_price > current_ema20 > current_ema50:
            trend_direction = 'BULLISH'
            price_ema_distance = (current_price - current_ema50) / current_ema50
        elif current_price < current_ema20 < current_ema50:
            trend_direction = 'BEARISH'
            price_ema_distance = (current_ema50 - current_price) / current_ema50
        else:
            trend_direction = 'NEUTRAL'
            price_ema_distance = 0
        
        # Calculate trend strength score (0-100)
        # Components:
        # 1. ADX (40 points max)
        # 2. EMA alignment (30 points max)
        # 3. Price distance from EMA (30 points max)
        
        adx_score = min(current_adx / 50 * 40, 40)  # Max 40 points
        
        ema_alignment = 1 if (ema_20.iloc[-1] > ema_50.iloc[-1] and trend_direction == 'BULLISH') or \
                              (ema_20.iloc[-1] < ema_50.iloc[-1] and trend_direction == 'BEARISH') else 0
        ema_score = ema_alignment * 30  # Max 30 points
        
        distance_score = min(abs(price_ema_distance) * 100 * 30, 30)  # Max 30 points
        
        trend_strength = adx_score + ema_score + distance_score
        
        # Determine regime type
        if current_adx > self.adx_strong_threshold and trend_direction != 'NEUTRAL' and price_ema_distance > 0.005:
            regime = 'STRONG_TREND'
            confidence = 0.8 + min(trend_strength / 100 * 0.2, 0.2)
        elif current_adx > self.adx_weak_threshold and trend_direction != 'NEUTRAL':
            regime = 'WEAK_TREND'
            confidence = 0.6 + min(trend_strength / 100 * 0.2, 0.2)
        elif atr_pct > self.atr_high_threshold and current_adx < self.adx_weak_threshold:
            regime = 'VOLATILE_CHOP'
            confidence = 0.5
        else:
            regime = 'RANGING'
            confidence = 0.4
        
        return {
            'regime': regime,
            'trend_strength': trend_strength,
            'trend_direction': trend_direction,
            'confidence': confidence,
            'adx': current_adx,
            'atr_pct': atr_pct,
            'price_ema_distance': price_ema_distance
        }
    
    def _calculate_adx(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ADX indicator."""
        high = df['high']
        low = df['low']
        close = df['close']
        
        # True Range
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        # Directional Movement
        up_move = high - high.shift()
        down_move = low.shift() - low
        
        plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0)
        minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0)
        
        # Smooth
        atr = tr.ewm(alpha=1/period, adjust=False).mean()
        plus_di = 100 * pd.Series(plus_dm).ewm(alpha=1/period, adjust=False).mean() / atr
        minus_di = 100 * pd.Series(minus_dm).ewm(alpha=1/period, adjust=False).mean() / atr
        
        # ADX
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        adx = dx.ewm(alpha=1/period, adjust=False).mean()
        
        return adx.fillna(0)
    
    def _calculate_atr(self, df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate ATR indicator."""
        high = df['high']
        low = df['low']
        close = df['close']
        
        tr1 = high - low
        tr2 = abs(high - close.shift())
        tr3 = abs(low - close.shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        
        atr = tr.ewm(alpha=1/period, adjust=False).mean()
        return atr.fillna(0)
    
    def _default_regime(self) -> Dict:
        """Return default regime when analysis fails."""
        return {
            'regime': 'RANGING',
            'trend_strength': 0,
            'trend_direction': 'NEUTRAL',
            'confidence': 0.0,
            'adx': 0,
            'atr_pct': 0,
            'price_ema_distance': 0
        }
    
    def should_trade(self, regime_info: Dict) -> bool:
        """
        Determine if trading is allowed based on regime.
        Only trade in STRONG_TREND regime.
        """
        return regime_info['regime'] == 'STRONG_TREND' and regime_info['confidence'] >= 0.7
