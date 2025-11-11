import pandas as pd
import numpy as np
from typing import Dict, Any, List, Tuple
import logging

logger = logging.getLogger(__name__)

class MultiTimeframeAnalyzer:
    """Analyze multiple timeframes for trend alignment and bias"""
    
    @staticmethod
    def analyze_trend_alignment(data: Dict[str, pd.DataFrame]) -> Dict[str, Any]:
        """
        Analyze trend alignment across all timeframes
        
        Args:
            data: Dict with timeframe as key and DataFrame as value
            
        Returns:
            Dict with trend analysis results
        """
        try:
            timeframe_analysis = {}
            
            # Analyze each timeframe
            for tf, df in data.items():
                if df is not None and not df.empty:
                    timeframe_analysis[tf] = MultiTimeframeAnalyzer._analyze_single_timeframe(df, tf)
            
            # Determine overall alignment
            alignment_result = MultiTimeframeAnalyzer._determine_alignment(timeframe_analysis)
            
            # Calculate daily bias
            daily_bias = MultiTimeframeAnalyzer._calculate_daily_bias(timeframe_analysis)
            
            # Get session analysis
            session_analysis = MultiTimeframeAnalyzer._analyze_trading_session()
            
            return {
                'timeframe_analysis': timeframe_analysis,
                'alignment': alignment_result,
                'daily_bias': daily_bias,
                'session_analysis': session_analysis,
                'overall_strength': MultiTimeframeAnalyzer._calculate_overall_strength(timeframe_analysis)
            }
            
        except Exception as e:
            logger.error(f"Error in multi-timeframe analysis: {e}")
            return {}
    
    @staticmethod
    def _analyze_single_timeframe(df: pd.DataFrame, timeframe: str) -> Dict[str, Any]:
        """Analyze a single timeframe"""
        try:
            latest = df.iloc[-1]
            
            # Basic trend analysis
            trend = MultiTimeframeAnalyzer._determine_trend(df)
            
            # EMA analysis
            ema_analysis = MultiTimeframeAnalyzer._analyze_ema_alignment(df)
            
            # Momentum analysis
            momentum = MultiTimeframeAnalyzer._analyze_momentum(df)
            
            # Structure analysis
            structure = MultiTimeframeAnalyzer._analyze_structure(df)
            
            # Volatility analysis
            volatility = MultiTimeframeAnalyzer._analyze_volatility(df)
            
            return {
                'timeframe': timeframe,
                'trend': trend,
                'ema_analysis': ema_analysis,
                'momentum': momentum,
                'structure': structure,
                'volatility': volatility,
                'current_price': float(latest['close']),
                'timestamp': latest['time']
            }
            
        except Exception as e:
            logger.error(f"Error analyzing timeframe {timeframe}: {e}")
            return {}
    
    @staticmethod
    def _determine_trend(df: pd.DataFrame) -> str:
        """Determine trend for a timeframe"""
        try:
            latest = df.iloc[-1]
            
            # EMA trend
            ema_9 = latest['ema_9']
            ema_21 = latest['ema_21']
            ema_50 = latest['ema_50']
            ema_200 = latest['ema_200']
            current_price = latest['close']
            
            # Strong bullish: All EMAs aligned and price above all
            if (ema_9 > ema_21 > ema_50 > ema_200 and current_price > ema_9):
                return 'STRONG_BULLISH'
            
            # Strong bearish: All EMAs aligned and price below all
            elif (ema_9 < ema_21 < ema_50 < ema_200 and current_price < ema_9):
                return 'STRONG_BEARISH'
            
            # Moderate bullish: Price above 50 EMA
            elif current_price > ema_50 and ema_9 > ema_21:
                return 'BULLISH'
            
            # Moderate bearish: Price below 50 EMA
            elif current_price < ema_50 and ema_9 < ema_21:
                return 'BEARISH'
            
            # Ranging
            else:
                return 'RANGING'
                
        except Exception as e:
            logger.error(f"Error determining trend: {e}")
            return 'UNKNOWN'
    
    @staticmethod
    def _analyze_ema_alignment(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze EMA alignment"""
        try:
            latest = df.iloc[-1]
            
            ema_9 = latest['ema_9']
            ema_21 = latest['ema_21']
            ema_50 = latest['ema_50']
            ema_200 = latest['ema_200']
            current_price = latest['close']
            
            # Check alignment
            bullish_alignment = ema_9 > ema_21 > ema_50 > ema_200
            bearish_alignment = ema_9 < ema_21 < ema_50 < ema_200
            
            # Check price position
            price_above_all = current_price > max(ema_9, ema_21, ema_50, ema_200)
            price_below_all = current_price < min(ema_9, ema_21, ema_50, ema_200)
            
            # Calculate distances
            distance_to_ema9 = abs(current_price - ema_9) / current_price * 100
            distance_to_ema50 = abs(current_price - ema_50) / current_price * 100
            
            return {
                'bullish_alignment': bullish_alignment,
                'bearish_alignment': bearish_alignment,
                'price_above_all': price_above_all,
                'price_below_all': price_below_all,
                'distance_to_ema9': round(distance_to_ema9, 2),
                'distance_to_ema50': round(distance_to_ema50, 2),
                'alignment_strength': 'STRONG' if (bullish_alignment or bearish_alignment) else 'WEAK'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing EMA alignment: {e}")
            return {}
    
    @staticmethod
    def _analyze_momentum(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze momentum indicators"""
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
            
            # ADX analysis
            adx = latest['adx']
            trend_strength = 'STRONG' if adx > 25 else 'WEAK'
            
            # Stochastic analysis
            stoch_k = latest['stoch_k']
            stoch_d = latest['stoch_d']
            stoch_bullish = stoch_k > stoch_d and stoch_k > 20
            
            # Overall momentum
            bullish_signals = sum([macd_bullish, stoch_bullish, rsi > 50])
            momentum_direction = 'BULLISH' if bullish_signals >= 2 else 'BEARISH' if bullish_signals <= 1 else 'NEUTRAL'
            
            return {
                'rsi': {'value': rsi, 'status': rsi_status},
                'macd': {'value': macd, 'signal': macd_signal, 'histogram': macd_histogram, 'bullish': macd_bullish},
                'adx': {'value': adx, 'strength': trend_strength},
                'stochastic': {'k': stoch_k, 'd': stoch_d, 'bullish': stoch_bullish},
                'momentum_direction': momentum_direction,
                'bullish_signals': bullish_signals
            }
            
        except Exception as e:
            logger.error(f"Error analyzing momentum: {e}")
            return {}
    
    @staticmethod
    def _analyze_structure(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market structure"""
        try:
            # Find swing highs and lows
            swing_highs = []
            swing_lows = []
            
            for i in range(2, len(df) - 2):
                # Swing High
                if (df.iloc[i]['high'] > df.iloc[i-1]['high'] and 
                    df.iloc[i]['high'] > df.iloc[i-2]['high'] and
                    df.iloc[i]['high'] > df.iloc[i+1]['high'] and 
                    df.iloc[i]['high'] > df.iloc[i+2]['high']):
                    swing_highs.append(df.iloc[i]['high'])
                
                # Swing Low
                if (df.iloc[i]['low'] < df.iloc[i-1]['low'] and 
                    df.iloc[i]['low'] < df.iloc[i-2]['low'] and
                    df.iloc[i]['low'] < df.iloc[i+1]['low'] and 
                    df.iloc[i]['low'] < df.iloc[i+2]['low']):
                    swing_lows.append(df.iloc[i]['low'])
            
            # Determine structure
            structure = 'UNDEFINED'
            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                if swing_highs[-1] > swing_highs[-2] and swing_lows[-1] > swing_lows[-2]:
                    structure = 'BULLISH'
                elif swing_highs[-1] < swing_highs[-2] and swing_lows[-1] < swing_lows[-2]:
                    structure = 'BEARISH'
                else:
                    structure = 'RANGING'
            
            return {
                'structure': structure,
                'swing_highs': swing_highs[-3:],
                'swing_lows': swing_lows[-3:],
                'structure_quality': 'CLEAR' if structure != 'UNDEFINED' else 'UNCLEAR'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing structure: {e}")
            return {}
    
    @staticmethod
    def _analyze_volatility(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volatility"""
        try:
            latest = df.iloc[-1]
            
            # ATR analysis
            atr = latest['atr']
            atr_ma = df['atr'].rolling(window=20).mean().iloc[-1]
            volatility_ratio = atr / atr_ma if atr_ma > 0 else 1
            
            # Bollinger Bands analysis
            bb_width = latest['bb_width']
            bb_squeeze = bb_width < 0.02
            
            # Price position in BB
            bb_position = (latest['close'] - latest['bb_lower']) / (latest['bb_upper'] - latest['bb_lower'])
            
            volatility_level = 'HIGH' if volatility_ratio > 1.5 else 'LOW' if volatility_ratio < 0.5 else 'NORMAL'
            
            return {
                'atr': atr,
                'volatility_ratio': round(volatility_ratio, 2),
                'volatility_level': volatility_level,
                'bb_squeeze': bb_squeeze,
                'bb_position': round(bb_position, 2)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volatility: {e}")
            return {}
    
    @staticmethod
    def _determine_alignment(timeframe_analysis: Dict[str, Any]) -> Dict[str, Any]:
        """Determine overall trend alignment"""
        try:
            trends = []
            for tf, analysis in timeframe_analysis.items():
                if 'trend' in analysis:
                    trends.append((tf, analysis['trend']))
            
            if not trends:
                return {'status': 'UNKNOWN', 'description': 'No trend data available'}
            
            # Check for alignment
            bullish_count = sum(1 for _, trend in trends if 'BULLISH' in trend)
            bearish_count = sum(1 for _, trend in trends if 'BEARISH' in trend)
            total_count = len(trends)
            
            if bullish_count == total_count:
                return {
                    'status': 'FULLY_ALIGNED_BULLISH',
                    'description': 'All timeframes bullish',
                    'strength': 'STRONG'
                }
            elif bearish_count == total_count:
                return {
                    'status': 'FULLY_ALIGNED_BEARISH',
                    'description': 'All timeframes bearish',
                    'strength': 'STRONG'
                }
            elif bullish_count > bearish_count:
                return {
                    'status': 'MOSTLY_BULLISH',
                    'description': f'{bullish_count}/{total_count} timeframes bullish',
                    'strength': 'MODERATE'
                }
            elif bearish_count > bullish_count:
                return {
                    'status': 'MOSTLY_BEARISH',
                    'description': f'{bearish_count}/{total_count} timeframes bearish',
                    'strength': 'MODERATE'
                }
            else:
                return {
                    'status': 'MIXED',
                    'description': 'Mixed timeframe signals',
                    'strength': 'WEAK'
                }
                
        except Exception as e:
            logger.error(f"Error determining alignment: {e}")
            return {'status': 'ERROR', 'description': 'Error analyzing alignment'}
    
    @staticmethod
    def _calculate_daily_bias(timeframe_analysis: Dict[str, Any]) -> str:
        """Calculate daily bias based on higher timeframes"""
        try:
            # Prioritize higher timeframes
            priority_order = ['D1', 'H4', 'H1', 'M15']
            
            for tf in priority_order:
                if tf in timeframe_analysis and 'trend' in timeframe_analysis[tf]:
                    trend = timeframe_analysis[tf]['trend']
                    if 'BULLISH' in trend:
                        return 'BULLISH'
                    elif 'BEARISH' in trend:
                        return 'BEARISH'
            
            return 'NEUTRAL'
            
        except Exception as e:
            logger.error(f"Error calculating daily bias: {e}")
            return 'UNKNOWN'
    
    @staticmethod
    def _analyze_trading_session() -> Dict[str, Any]:
        """Analyze current trading session"""
        try:
            from datetime import datetime, timezone
            
            now = datetime.now(timezone.utc)
            hour = now.hour
            
            # Define sessions (UTC)
            sessions = {
                'ASIAN': (0, 8),
                'LONDON': (7, 16),
                'NEW_YORK': (13, 22),
                'OVERLAP': (13, 16)  # London-NY overlap
            }
            
            current_session = 'CLOSED'
            session_quality = 'POOR'
            
            for session_name, (start, end) in sessions.items():
                if start <= hour < end:
                    current_session = session_name
                    if session_name in ['LONDON', 'NEW_YORK', 'OVERLAP']:
                        session_quality = 'EXCELLENT'
                    elif session_name == 'ASIAN':
                        session_quality = 'MODERATE'
                    break
            
            # Check if in kill zones
            in_kill_zone = current_session in ['LONDON', 'NEW_YORK', 'OVERLAP']
            
            return {
                'current_session': current_session,
                'session_quality': session_quality,
                'in_kill_zone': in_kill_zone,
                'hour_utc': hour,
                'recommended_action': 'TRADE' if in_kill_zone else 'WAIT'
            }
            
        except Exception as e:
            logger.error(f"Error analyzing trading session: {e}")
            return {}
    
    @staticmethod
    def _calculate_overall_strength(timeframe_analysis: Dict[str, Any]) -> str:
        """Calculate overall market strength"""
        try:
            strength_scores = []
            
            for tf, analysis in timeframe_analysis.items():
                score = 0
                
                # Trend strength
                if 'trend' in analysis:
                    trend = analysis['trend']
                    if 'STRONG' in trend:
                        score += 3
                    elif 'BULLISH' in trend or 'BEARISH' in trend:
                        score += 2
                    else:
                        score += 1
                
                # EMA alignment
                if 'ema_analysis' in analysis and 'alignment_strength' in analysis['ema_analysis']:
                    if analysis['ema_analysis']['alignment_strength'] == 'STRONG':
                        score += 2
                    else:
                        score += 1
                
                # Momentum
                if 'momentum' in analysis and 'momentum_direction' in analysis['momentum']:
                    if analysis['momentum']['momentum_direction'] != 'NEUTRAL':
                        score += 1
                
                strength_scores.append(score)
            
            if not strength_scores:
                return 'UNKNOWN'
            
            avg_score = sum(strength_scores) / len(strength_scores)
            
            if avg_score >= 4:
                return 'VERY_STRONG'
            elif avg_score >= 3:
                return 'STRONG'
            elif avg_score >= 2:
                return 'MODERATE'
            else:
                return 'WEAK'
                
        except Exception as e:
            logger.error(f"Error calculating overall strength: {e}")
            return 'UNKNOWN'




