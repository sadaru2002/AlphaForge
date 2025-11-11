import pandas as pd
import numpy as np
from ta.trend import EMAIndicator, MACD, ADXIndicator
from ta.momentum import RSIIndicator, StochasticOscillator
from ta.volatility import BollingerBands, AverageTrueRange
from ta.volume import OnBalanceVolumeIndicator, VolumeWeightedAveragePrice
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class TechnicalAnalyzer:
    """Calculate all technical indicators"""
    
    @staticmethod
    def calculate_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate all technical indicators (alias for add_all_indicators)
        Kept for backward compatibility
        """
        return TechnicalAnalyzer.add_all_indicators(df)
    
    @staticmethod
    def add_all_indicators(df: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicators to DataFrame"""
        try:
            # EMAs
            for period in [9, 21, 50, 200]:
                df[f'ema_{period}'] = EMAIndicator(df['close'], window=period).ema_indicator()
            
            # RSI
            df['rsi'] = RSIIndicator(df['close'], window=14).rsi()
            
            # MACD
            macd = MACD(df['close'])
            df['macd'] = macd.macd()
            df['macd_signal'] = macd.macd_signal()
            df['macd_diff'] = macd.macd_diff()
            
            # Bollinger Bands
            bb = BollingerBands(df['close'], window=20, window_dev=2)
            df['bb_upper'] = bb.bollinger_hband()
            df['bb_middle'] = bb.bollinger_mavg()
            df['bb_lower'] = bb.bollinger_lband()
            df['bb_width'] = (df['bb_upper'] - df['bb_lower']) / df['bb_middle']
            
            # ATR
            df['atr'] = AverageTrueRange(df['high'], df['low'], df['close'], window=14).average_true_range()
            
            # ADX (Trend Strength)
            adx = ADXIndicator(df['high'], df['low'], df['close'], window=14)
            df['adx'] = adx.adx()
            
            # Stochastic
            stoch = StochasticOscillator(df['high'], df['low'], df['close'])
            df['stoch_k'] = stoch.stoch()
            df['stoch_d'] = stoch.stoch_signal()
            
            # Volume MA
            df['volume_ma'] = df['volume'].rolling(window=20).mean()
            
            # Williams %R
            df['williams_r'] = TechnicalAnalyzer._calculate_williams_r(df)
            
            # CCI (Commodity Channel Index)
            df['cci'] = TechnicalAnalyzer._calculate_cci(df)
            
            logger.info("Technical indicators calculated successfully")
            return df
            
        except Exception as e:
            logger.error(f"Error calculating technical indicators: {e}")
            return df
    
    @staticmethod
    def _calculate_williams_r(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Williams %R"""
        high_max = df['high'].rolling(window=period).max()
        low_min = df['low'].rolling(window=period).min()
        return -100 * (high_max - df['close']) / (high_max - low_min)
    
    @staticmethod
    def _calculate_cci(df: pd.DataFrame, period: int = 20) -> pd.Series:
        """Calculate Commodity Channel Index"""
        typical_price = (df['high'] + df['low'] + df['close']) / 3
        sma = typical_price.rolling(window=period).mean()
        mad = typical_price.rolling(window=period).apply(lambda x: np.mean(np.abs(x - x.mean())))
        return (typical_price - sma) / (0.015 * mad)
    
    @staticmethod
    def identify_trend(df: pd.DataFrame) -> str:
        """Determine current trend"""
        try:
            latest = df.iloc[-1]
            
            # EMA alignment
            ema_bullish = (latest['ema_9'] > latest['ema_21'] > latest['ema_50'])
            ema_bearish = (latest['ema_9'] < latest['ema_21'] < latest['ema_50'])
            
            # ADX strength
            strong_trend = latest['adx'] > 25
            
            # Price vs EMAs
            price_above_ema = latest['close'] > latest['ema_50']
            price_below_ema = latest['close'] < latest['ema_50']
            
            if ema_bullish and strong_trend and price_above_ema:
                return 'STRONG_BULLISH'
            elif ema_bullish and price_above_ema:
                return 'BULLISH'
            elif ema_bearish and strong_trend and price_below_ema:
                return 'STRONG_BEARISH'
            elif ema_bearish and price_below_ema:
                return 'BEARISH'
            else:
                return 'RANGING'
                
        except Exception as e:
            logger.error(f"Error identifying trend: {e}")
            return 'UNKNOWN'
    
    @staticmethod
    def get_support_resistance(df: pd.DataFrame, lookback: int = 50) -> Dict[str, List[float]]:
        """Identify key support and resistance levels"""
        try:
            recent_data = df.tail(lookback)
            
            # Find swing highs and lows
            highs = recent_data['high'].rolling(window=5, center=True).max() == recent_data['high']
            lows = recent_data['low'].rolling(window=5, center=True).min() == recent_data['low']
            
            swing_highs = recent_data[highs]['high'].tolist()
            swing_lows = recent_data[lows]['low'].tolist()
            
            # Get most significant levels (clusters)
            resistance_levels = TechnicalAnalyzer._cluster_levels(swing_highs, tolerance=0.001)
            support_levels = TechnicalAnalyzer._cluster_levels(swing_lows, tolerance=0.001)
            
            return {
                'resistance': sorted(resistance_levels, reverse=True)[:5],
                'support': sorted(support_levels)[:5]
            }
            
        except Exception as e:
            logger.error(f"Error calculating support/resistance: {e}")
            return {'resistance': [], 'support': []}
    
    @staticmethod
    def _cluster_levels(levels: List[float], tolerance: float = 0.001) -> List[float]:
        """Cluster nearby levels together"""
        if not levels:
            return []
        
        levels = sorted(levels)
        clusters = []
        current_cluster = [levels[0]]
        
        for level in levels[1:]:
            if abs(level - current_cluster[-1]) <= tolerance:
                current_cluster.append(level)
            else:
                clusters.append(np.mean(current_cluster))
                current_cluster = [level]
        
        clusters.append(np.mean(current_cluster))
        return clusters
    
    @staticmethod
    def detect_divergence(df: pd.DataFrame, indicator: str = 'rsi', lookback: int = 20) -> Dict[str, Any]:
        """Detect price-indicator divergence"""
        try:
            recent_data = df.tail(lookback)
            
            # Find peaks and troughs in price
            price_peaks = recent_data['high'].rolling(window=3, center=True).max() == recent_data['high']
            price_troughs = recent_data['low'].rolling(window=3, center=True).min() == recent_data['low']
            
            # Find peaks and troughs in indicator
            indicator_peaks = recent_data[indicator].rolling(window=3, center=True).max() == recent_data[indicator]
            indicator_troughs = recent_data[indicator].rolling(window=3, center=True).min() == recent_data[indicator]
            
            # Get recent peaks/troughs
            price_peak_values = recent_data[price_peaks]['high'].values
            price_trough_values = recent_data[price_troughs]['low'].values
            indicator_peak_values = recent_data[indicator_peaks][indicator].values
            indicator_trough_values = recent_data[indicator_troughs][indicator].values
            
            # Check for divergence (simplified)
            bullish_divergence = False
            bearish_divergence = False
            
            if len(price_trough_values) >= 2 and len(indicator_trough_values) >= 2:
                # Price making lower lows, indicator making higher lows
                if (price_trough_values[-1] < price_trough_values[-2] and 
                    indicator_trough_values[-1] > indicator_trough_values[-2]):
                    bullish_divergence = True
            
            if len(price_peak_values) >= 2 and len(indicator_peak_values) >= 2:
                # Price making higher highs, indicator making lower highs
                if (price_peak_values[-1] > price_peak_values[-2] and 
                    indicator_peak_values[-1] < indicator_peak_values[-2]):
                    bearish_divergence = True
            
            return {
                'bullish_divergence': bullish_divergence,
                'bearish_divergence': bearish_divergence,
                'indicator': indicator
            }
            
        except Exception as e:
            logger.error(f"Error detecting divergence: {e}")
            return {'bullish_divergence': False, 'bearish_divergence': False, 'indicator': indicator}
    
    @staticmethod
    def get_momentum_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive momentum analysis"""
        try:
            latest = df.iloc[-1]
            
            # RSI analysis
            rsi = latest['rsi']
            rsi_status = 'OVERBOUGHT' if rsi > 70 else 'OVERSOLD' if rsi < 30 else 'NEUTRAL'
            
            # MACD analysis
            macd = latest['macd']
            macd_signal = latest['macd_signal']
            macd_histogram = latest['macd_diff']
            macd_bullish = macd > macd_signal and macd_histogram > 0
            macd_bearish = macd < macd_signal and macd_histogram < 0
            
            # Stochastic analysis
            stoch_k = latest['stoch_k']
            stoch_d = latest['stoch_d']
            stoch_status = 'OVERBOUGHT' if stoch_k > 80 else 'OVERSOLD' if stoch_k < 20 else 'NEUTRAL'
            stoch_bullish = stoch_k > stoch_d and stoch_k > 20
            stoch_bearish = stoch_k < stoch_d and stoch_k < 80
            
            # Williams %R analysis
            williams_r = latest['williams_r']
            williams_status = 'OVERBOUGHT' if williams_r > -20 else 'OVERSOLD' if williams_r < -80 else 'NEUTRAL'
            
            # Overall momentum score
            bullish_signals = sum([macd_bullish, stoch_bullish, rsi > 50, williams_r > -50])
            bearish_signals = sum([macd_bearish, stoch_bearish, rsi < 50, williams_r < -50])
            
            momentum_score = bullish_signals - bearish_signals
            momentum_direction = 'BULLISH' if momentum_score > 0 else 'BEARISH' if momentum_score < 0 else 'NEUTRAL'
            
            return {
                'rsi': {'value': rsi, 'status': rsi_status},
                'macd': {'value': macd, 'signal': macd_signal, 'histogram': macd_histogram, 'bullish': macd_bullish},
                'stochastic': {'k': stoch_k, 'd': stoch_d, 'status': stoch_status, 'bullish': stoch_bullish},
                'williams_r': {'value': williams_r, 'status': williams_status},
                'momentum_score': momentum_score,
                'momentum_direction': momentum_direction,
                'bullish_signals': bullish_signals,
                'bearish_signals': bearish_signals
            }
            
        except Exception as e:
            logger.error(f"Error in momentum analysis: {e}")
            return {}
    
    @staticmethod
    def get_volatility_analysis(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market volatility"""
        try:
            latest = df.iloc[-1]
            
            # ATR analysis
            atr = latest['atr']
            atr_ma = df['atr'].rolling(window=20).mean().iloc[-1]
            volatility_ratio = atr / atr_ma if atr_ma > 0 else 1
            
            volatility_level = 'HIGH' if volatility_ratio > 1.5 else 'LOW' if volatility_ratio < 0.5 else 'NORMAL'
            
            # Bollinger Bands analysis
            bb_width = latest['bb_width']
            bb_squeeze = bb_width < 0.02  # Very tight bands
            
            # Price position in BB
            bb_position = (latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower'])
            bb_status = 'UPPER' if bb_position > 0.8 else 'LOWER' if bb_position < 0.2 else 'MIDDLE'
            
            return {
                'atr': atr,
                'atr_ratio': volatility_ratio,
                'volatility_level': volatility_level,
                'bb_width': bb_width,
                'bb_squeeze': bb_squeeze,
                'bb_position': bb_position,
                'bb_status': bb_status
            }
            
        except Exception as e:
            logger.error(f"Error in volatility analysis: {e}")
            return {}