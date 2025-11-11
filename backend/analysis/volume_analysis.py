import pandas as pd
import numpy as np
from typing import Dict, Any, List
import logging

logger = logging.getLogger(__name__)

class VolumeAnalyzer:
    """Analyze volume profile and anomalies"""
    
    @staticmethod
    def analyze_volume(df: pd.DataFrame) -> Dict[str, Any]:
        """Comprehensive volume analysis"""
        try:
            latest = df.iloc[-1]
            volume_ma = df['volume'].rolling(window=20).mean().iloc[-1]
            
            # Volume spike detection
            volume_spike = latest['volume'] > (volume_ma * 1.5)
            volume_surge = latest['volume'] > (volume_ma * 2.0)
            
            # Volume trend analysis
            recent_volumes = df['volume'].tail(10)
            volume_increasing = recent_volumes.is_monotonic_increasing
            volume_decreasing = recent_volumes.is_monotonic_decreasing
            
            # Volume divergence analysis
            price_direction = 'UP' if df['close'].iloc[-1] > df['close'].iloc[-5] else 'DOWN'
            volume_direction = 'UP' if df['volume'].iloc[-1] > df['volume'].iloc[-5] else 'DOWN'
            volume_divergence = (price_direction == 'UP' and volume_direction == 'DOWN') or \
                              (price_direction == 'DOWN' and volume_direction == 'UP')
            
            # Volume profile analysis
            volume_profile = VolumeAnalyzer._analyze_volume_profile(df)
            
            # Volume at price levels
            volume_at_price = VolumeAnalyzer._analyze_volume_at_price(df)
            
            # Volume momentum
            volume_momentum = VolumeAnalyzer._calculate_volume_momentum(df)
            
            # Analysis summary
            analysis = VolumeAnalyzer._generate_volume_analysis(
                volume_spike, volume_surge, volume_divergence, 
                volume_increasing, volume_decreasing, volume_momentum
            )
            
            return {
                'volume_spike': volume_spike,
                'volume_surge': volume_surge,
                'volume_increasing': volume_increasing,
                'volume_decreasing': volume_decreasing,
                'volume_divergence': volume_divergence,
                'current_volume': int(latest['volume']),
                'volume_ma': int(volume_ma),
                'volume_ratio': round(latest['volume'] / volume_ma, 2),
                'price_direction': price_direction,
                'volume_direction': volume_direction,
                'volume_profile': volume_profile,
                'volume_at_price': volume_at_price,
                'volume_momentum': volume_momentum,
                'analysis': analysis
            }
            
        except Exception as e:
            logger.error(f"Error in volume analysis: {e}")
            return {
                'volume_spike': False,
                'volume_surge': False,
                'volume_increasing': False,
                'volume_decreasing': False,
                'volume_divergence': False,
                'current_volume': 0,
                'volume_ma': 0,
                'volume_ratio': 1.0,
                'price_direction': 'UNKNOWN',
                'volume_direction': 'UNKNOWN',
                'volume_profile': {},
                'volume_at_price': {},
                'volume_momentum': 0,
                'analysis': 'Error in volume analysis'
            }
    
    @staticmethod
    def _analyze_volume_profile(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume profile (simplified)"""
        try:
            # Calculate volume-weighted average price (VWAP)
            typical_price = (df['high'] + df['low'] + df['close']) / 3
            volume_price = typical_price * df['volume']
            vwap = volume_price.sum() / df['volume'].sum()
            
            # Volume distribution
            recent_data = df.tail(20)
            high_volume_candles = recent_data[recent_data['volume'] > recent_data['volume'].mean() * 1.2]
            
            # Volume clusters
            volume_clusters = VolumeAnalyzer._find_volume_clusters(recent_data)
            
            return {
                'vwap': round(vwap, 5),
                'high_volume_candles': len(high_volume_candles),
                'volume_clusters': volume_clusters,
                'avg_volume': int(recent_data['volume'].mean()),
                'max_volume': int(recent_data['volume'].max()),
                'min_volume': int(recent_data['volume'].min())
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume profile: {e}")
            return {}
    
    @staticmethod
    def _find_volume_clusters(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Find volume clusters (areas of high volume)"""
        try:
            clusters = []
            volume_threshold = df['volume'].mean() * 1.5
            
            high_volume_candles = df[df['volume'] > volume_threshold]
            
            for _, candle in high_volume_candles.iterrows():
                clusters.append({
                    'time': candle['time'],
                    'price_range': [candle['low'], candle['high']],
                    'volume': int(candle['volume']),
                    'strength': candle['volume'] / df['volume'].mean()
                })
            
            return sorted(clusters, key=lambda x: x['strength'], reverse=True)[:5]
            
        except Exception as e:
            logger.error(f"Error finding volume clusters: {e}")
            return []
    
    @staticmethod
    def _analyze_volume_at_price(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume at different price levels"""
        try:
            recent_data = df.tail(20)
            
            # Price levels
            price_high = recent_data['high'].max()
            price_low = recent_data['low'].min()
            price_range = price_high - price_low
            
            # Divide into thirds
            upper_third = price_high - (price_range * 0.33)
            lower_third = price_low + (price_range * 0.33)
            
            # Volume in each third
            upper_volume = recent_data[recent_data['close'] > upper_third]['volume'].sum()
            middle_volume = recent_data[
                (recent_data['close'] <= upper_third) & 
                (recent_data['close'] >= lower_third)
            ]['volume'].sum()
            lower_volume = recent_data[recent_data['close'] < lower_third]['volume'].sum()
            
            total_volume = upper_volume + middle_volume + lower_volume
            
            return {
                'upper_third_volume': int(upper_volume),
                'middle_third_volume': int(middle_volume),
                'lower_third_volume': int(lower_volume),
                'upper_volume_pct': round((upper_volume / total_volume) * 100, 1) if total_volume > 0 else 0,
                'middle_volume_pct': round((middle_volume / total_volume) * 100, 1) if total_volume > 0 else 0,
                'lower_volume_pct': round((lower_volume / total_volume) * 100, 1) if total_volume > 0 else 0,
                'price_high': round(price_high, 5),
                'price_low': round(price_low, 5)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume at price: {e}")
            return {}
    
    @staticmethod
    def _calculate_volume_momentum(df: pd.DataFrame) -> float:
        """Calculate volume momentum (rate of change)"""
        try:
            recent_volumes = df['volume'].tail(10)
            if len(recent_volumes) < 2:
                return 0.0
            
            # Calculate rate of change
            momentum = ((recent_volumes.iloc[-1] - recent_volumes.iloc[0]) / recent_volumes.iloc[0]) * 100
            return round(momentum, 2)
            
        except Exception as e:
            logger.error(f"Error calculating volume momentum: {e}")
            return 0.0
    
    @staticmethod
    def _generate_volume_analysis(volume_spike: bool, volume_surge: bool, 
                                volume_divergence: bool, volume_increasing: bool,
                                volume_decreasing: bool, volume_momentum: float) -> str:
        """Generate human-readable volume analysis"""
        
        if volume_surge:
            return "Volume surge detected - Strong institutional activity"
        elif volume_spike:
            return "Volume spike - Significant interest at current levels"
        elif volume_divergence:
            if volume_momentum < 0:
                return "Volume divergence - Price up but volume declining (weakness)"
            else:
                return "Volume divergence - Price down but volume increasing (strength)"
        elif volume_increasing:
            return "Volume increasing - Building momentum"
        elif volume_decreasing:
            return "Volume decreasing - Losing momentum"
        else:
            return "Normal volume levels - Standard market activity"
    
    @staticmethod
    def detect_volume_breakouts(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect volume breakouts"""
        try:
            breakouts = []
            volume_ma = df['volume'].rolling(window=20).mean()
            
            for i in range(20, len(df)):
                current_volume = df.iloc[i]['volume']
                avg_volume = volume_ma.iloc[i]
                
                # Volume breakout criteria
                if current_volume > avg_volume * 2.0:  # 2x average volume
                    price_change = abs(df.iloc[i]['close'] - df.iloc[i-1]['close'])
                    price_change_pct = (price_change / df.iloc[i-1]['close']) * 100
                    
                    if price_change_pct > 0.1:  # Significant price movement
                        breakouts.append({
                            'time': df.iloc[i]['time'],
                            'volume': int(current_volume),
                            'volume_ratio': round(current_volume / avg_volume, 2),
                            'price_change_pct': round(price_change_pct, 2),
                            'direction': 'UP' if df.iloc[i]['close'] > df.iloc[i-1]['close'] else 'DOWN',
                            'strength': round(current_volume / avg_volume * price_change_pct, 2)
                        })
            
            return sorted(breakouts, key=lambda x: x['strength'], reverse=True)[:5]
            
        except Exception as e:
            logger.error(f"Error detecting volume breakouts: {e}")
            return []
    
    @staticmethod
    def analyze_volume_trend(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze volume trend over time"""
        try:
            # Calculate volume moving averages
            df['volume_ma_5'] = df['volume'].rolling(window=5).mean()
            df['volume_ma_20'] = df['volume'].rolling(window=20).mean()
            
            latest = df.iloc[-1]
            
            # Volume trend
            volume_trend = 'INCREASING' if latest['volume_ma_5'] > latest['volume_ma_20'] else 'DECREASING'
            
            # Volume acceleration
            recent_5 = df['volume_ma_5'].tail(5)
            volume_acceleration = 'ACCELERATING' if recent_5.is_monotonic_increasing else 'DECELERATING'
            
            # Volume consistency
            volume_std = df['volume'].tail(20).std()
            volume_mean = df['volume'].tail(20).mean()
            volume_cv = volume_std / volume_mean if volume_mean > 0 else 0
            volume_consistency = 'CONSISTENT' if volume_cv < 0.5 else 'VOLATILE'
            
            return {
                'trend': volume_trend,
                'acceleration': volume_acceleration,
                'consistency': volume_consistency,
                'coefficient_of_variation': round(volume_cv, 3),
                'ma_5': int(latest['volume_ma_5']),
                'ma_20': int(latest['volume_ma_20']),
                'trend_strength': round((latest['volume_ma_5'] / latest['volume_ma_20'] - 1) * 100, 2)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing volume trend: {e}")
            return {}

