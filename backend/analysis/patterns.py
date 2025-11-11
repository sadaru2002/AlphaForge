import pandas as pd
import numpy as np
from typing import List, Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class SMCPatternDetector:
    """Detect Smart Money Concepts patterns"""
    
    @staticmethod
    def detect_order_blocks(df: pd.DataFrame, lookback: int = 20) -> List[Dict[str, Any]]:
        """Detect Order Blocks"""
        try:
            order_blocks = []
            
            for i in range(lookback, len(df) - 3):
                current = df.iloc[i]
                next_candles = df.iloc[i+1:i+4]
                
                # Bullish Order Block
                if all(next_candles['close'] > next_candles['open']):
                    if next_candles.iloc[-1]['close'] > current['high']:
                        strength = (next_candles.iloc[-1]['close'] - current['low']) * 10000
                        order_blocks.append({
                            'type': 'BULLISH_OB',
                            'low': float(current['low']),
                            'high': float(current['high']),
                            'time': current['time'],
                            'strength': strength,
                            'index': i
                        })
                
                # Bearish Order Block
                if all(next_candles['close'] < next_candles['open']):
                    if next_candles.iloc[-1]['close'] < current['low']:
                        strength = (current['high'] - next_candles.iloc[-1]['close']) * 10000
                        order_blocks.append({
                            'type': 'BEARISH_OB',
                            'low': float(current['low']),
                            'high': float(current['high']),
                            'time': current['time'],
                            'strength': strength,
                            'index': i
                        })
            
            # Sort by strength and return top 5
            return sorted(order_blocks, key=lambda x: x['strength'], reverse=True)[:5]
            
        except Exception as e:
            logger.error(f"Error detecting order blocks: {e}")
            return []
    
    @staticmethod
    def detect_fair_value_gaps(df: pd.DataFrame) -> List[Dict[str, Any]]:
        """Detect Fair Value Gaps"""
        try:
            fvgs = []
            
            for i in range(len(df) - 2):
                c1 = df.iloc[i]
                c2 = df.iloc[i + 1]
                c3 = df.iloc[i + 2]
                
                # Bullish FVG
                if c1['high'] < c3['low']:
                    gap_size = (c3['low'] - c1['high']) * 10000
                    if gap_size >= 5:  # Minimum 5 pips
                        fvgs.append({
                            'type': 'BULLISH_FVG',
                            'gap_low': float(c1['high']),
                            'gap_high': float(c3['low']),
                            'size_pips': gap_size,
                            'time': c3['time'],
                            'index': i + 2
                        })
                
                # Bearish FVG
                if c1['low'] > c3['high']:
                    gap_size = (c1['low'] - c3['high']) * 10000
                    if gap_size >= 5:  # Minimum 5 pips
                        fvgs.append({
                            'type': 'BEARISH_FVG',
                            'gap_low': float(c3['high']),
                            'gap_high': float(c1['low']),
                            'size_pips': gap_size,
                            'time': c3['time'],
                            'index': i + 2
                        })
            
            # Return most recent 5 FVGs
            return fvgs[-5:] if fvgs else []
            
        except Exception as e:
            logger.error(f"Error detecting fair value gaps: {e}")
            return []
    
    @staticmethod
    def analyze_market_structure(df: pd.DataFrame) -> Dict[str, Any]:
        """Analyze market structure for CHoCH and BOS"""
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
                    swing_highs.append({
                        'price': float(df.iloc[i]['high']),
                        'time': df.iloc[i]['time'],
                        'index': i
                    })
                
                # Swing Low
                if (df.iloc[i]['low'] < df.iloc[i-1]['low'] and 
                    df.iloc[i]['low'] < df.iloc[i-2]['low'] and
                    df.iloc[i]['low'] < df.iloc[i+1]['low'] and 
                    df.iloc[i]['low'] < df.iloc[i+2]['low']):
                    swing_lows.append({
                        'price': float(df.iloc[i]['low']),
                        'time': df.iloc[i]['time'],
                        'index': i
                    })
            
            # Determine trend
            trend = 'UNDEFINED'
            structure_description = "Market structure undefined"
            
            if len(swing_highs) >= 2 and len(swing_lows) >= 2:
                latest_high = swing_highs[-1]['price']
                prev_high = swing_highs[-2]['price']
                latest_low = swing_lows[-1]['price']
                prev_low = swing_lows[-2]['price']
                
                if latest_high > prev_high and latest_low > prev_low:
                    trend = 'BULLISH'
                    structure_description = "Higher highs and higher lows - Bullish structure"
                elif latest_high < prev_high and latest_low < prev_low:
                    trend = 'BEARISH'
                    structure_description = "Lower highs and lower lows - Bearish structure"
                else:
                    trend = 'RANGING'
                    structure_description = "Mixed structure - Ranging market"
            
            return {
                'trend': trend,
                'swing_highs': swing_highs[-3:],  # Last 3 swing highs
                'swing_lows': swing_lows[-3:],    # Last 3 swing lows
                'structure_description': structure_description,
                'total_swing_highs': len(swing_highs),
                'total_swing_lows': len(swing_lows)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing market structure: {e}")
            return {
                'trend': 'UNKNOWN',
                'swing_highs': [],
                'swing_lows': [],
                'structure_description': 'Error analyzing structure',
                'total_swing_highs': 0,
                'total_swing_lows': 0
            }
    
    @staticmethod
    def detect_liquidity_sweeps(df: pd.DataFrame, lookback: int = 20) -> List[Dict[str, Any]]:
        """Detect liquidity sweeps (stop hunts)"""
        try:
            liquidity_sweeps = []
            
            for i in range(lookback, len(df) - 1):
                current = df.iloc[i]
                next_candle = df.iloc[i + 1]
                
                # Check for liquidity sweep above previous high
                if i >= 2:
                    prev_high = df.iloc[i-2:i]['high'].max()
                    if (current['high'] > prev_high and 
                        next_candle['close'] < prev_high):
                        liquidity_sweeps.append({
                            'type': 'BEARISH_LIQUIDITY_SWEEP',
                            'sweep_high': float(current['high']),
                            'liquidity_level': float(prev_high),
                            'time': current['time'],
                            'index': i
                        })
                
                # Check for liquidity sweep below previous low
                if i >= 2:
                    prev_low = df.iloc[i-2:i]['low'].min()
                    if (current['low'] < prev_low and 
                        next_candle['close'] > prev_low):
                        liquidity_sweeps.append({
                            'type': 'BULLISH_LIQUIDITY_SWEEP',
                            'sweep_low': float(current['low']),
                            'liquidity_level': float(prev_low),
                            'time': current['time'],
                            'index': i
                        })
            
            return liquidity_sweeps[-5:] if liquidity_sweeps else []
            
        except Exception as e:
            logger.error(f"Error detecting liquidity sweeps: {e}")
            return []
    
    @staticmethod
    def detect_breaker_blocks(df: pd.DataFrame, order_blocks: List[Dict]) -> List[Dict[str, Any]]:
        """Detect breaker blocks (failed order blocks)"""
        try:
            breaker_blocks = []
            
            for ob in order_blocks:
                ob_index = ob['index']
                ob_type = ob['type']
                
                # Check if order block was broken
                if ob_index + 5 < len(df):
                    subsequent_candles = df.iloc[ob_index + 1:ob_index + 6]
                    
                    if ob_type == 'BULLISH_OB':
                        # Check if price broke below the order block
                        if any(candle['low'] < ob['low'] for _, candle in subsequent_candles.iterrows()):
                            breaker_blocks.append({
                                'type': 'BEARISH_BREAKER',
                                'original_ob': ob,
                                'broken_at': subsequent_candles.iloc[0]['time'],
                                'strength': ob['strength'] * 0.5  # Reduced strength
                            })
                    
                    elif ob_type == 'BEARISH_OB':
                        # Check if price broke above the order block
                        if any(candle['high'] > ob['high'] for _, candle in subsequent_candles.iterrows()):
                            breaker_blocks.append({
                                'type': 'BULLISH_BREAKER',
                                'original_ob': ob,
                                'broken_at': subsequent_candles.iloc[0]['time'],
                                'strength': ob['strength'] * 0.5  # Reduced strength
                            })
            
            return breaker_blocks
            
        except Exception as e:
            logger.error(f"Error detecting breaker blocks: {e}")
            return []
    
    @staticmethod
    def calculate_premium_discount(df: pd.DataFrame, lookback: int = 50) -> Dict[str, Any]:
        """Calculate premium/discount zones using Fibonacci levels"""
        try:
            recent_data = df.tail(lookback)
            range_high = recent_data['high'].max()
            range_low = recent_data['low'].min()
            current_price = df.iloc[-1]['close']
            
            # Calculate position in range
            range_size = range_high - range_low
            position = ((current_price - range_low) / range_size) * 100
            
            # Define zones
            if position > 61.8:
                zone = 'PREMIUM'
                description = 'Price in premium zone - SELL setups preferred'
            elif position < 38.2:
                zone = 'DISCOUNT'
                description = 'Price in discount zone - BUY setups preferred'
            else:
                zone = 'EQUILIBRIUM'
                description = 'Price at equilibrium - Wait for better positioning'
            
            # Calculate Fibonacci levels
            fib_levels = {
                '0%': range_low,
                '23.6%': range_low + (range_size * 0.236),
                '38.2%': range_low + (range_size * 0.382),
                '50%': range_low + (range_size * 0.5),
                '61.8%': range_low + (range_size * 0.618),
                '78.6%': range_low + (range_size * 0.786),
                '100%': range_high
            }
            
            return {
                'zone': zone,
                'percentage': round(position, 1),
                'range_high': round(range_high, 5),
                'range_low': round(range_low, 5),
                'current_price': round(current_price, 5),
                'description': description,
                'fib_levels': fib_levels
            }
            
        except Exception as e:
            logger.error(f"Error calculating premium/discount: {e}")
            return {
                'zone': 'UNKNOWN',
                'percentage': 50.0,
                'range_high': 0.0,
                'range_low': 0.0,
                'current_price': 0.0,
                'description': 'Error calculating zones',
                'fib_levels': {}
            }
    
    @staticmethod
    def detect_optimal_trade_entry(df: pd.DataFrame, order_blocks: List[Dict]) -> List[Dict[str, Any]]:
        """Detect Optimal Trade Entry (OTE) zones using Fibonacci retracements"""
        try:
            ote_zones = []
            
            for ob in order_blocks:
                if ob['type'] == 'BULLISH_OB':
                    # For bullish OB, look for pullback to 61.8%-78.6% retracement
                    ob_high = ob['high']
                    ob_low = ob['low']
                    ob_range = ob_high - ob_low
                    
                    # Calculate OTE levels
                    ote_618 = ob_high - (ob_range * 0.618)
                    ote_786 = ob_high - (ob_range * 0.786)
                    
                    ote_zones.append({
                        'type': 'BULLISH_OTE',
                        'order_block': ob,
                        'ote_high': round(ote_618, 5),
                        'ote_low': round(ote_786, 5),
                        'strength': ob['strength']
                    })
                
                elif ob['type'] == 'BEARISH_OB':
                    # For bearish OB, look for pullback to 61.8%-78.6% retracement
                    ob_high = ob['high']
                    ob_low = ob['low']
                    ob_range = ob_high - ob_low
                    
                    # Calculate OTE levels
                    ote_618 = ob_low + (ob_range * 0.618)
                    ote_786 = ob_low + (ob_range * 0.786)
                    
                    ote_zones.append({
                        'type': 'BEARISH_OTE',
                        'order_block': ob,
                        'ote_high': round(ote_786, 5),
                        'ote_low': round(ote_618, 5),
                        'strength': ob['strength']
                    })
            
            return sorted(ote_zones, key=lambda x: x['strength'], reverse=True)[:3]
            
        except Exception as e:
            logger.error(f"Error detecting OTE zones: {e}")
            return []
    
    @staticmethod
    def detect_patterns(df: pd.DataFrame) -> Dict[str, Any]:
        """Main method to detect all SMC patterns"""
        try:
            # Detect all pattern types
            order_blocks = SMCPatternDetector.detect_order_blocks(df)
            fvgs = SMCPatternDetector.detect_fair_value_gaps(df)
            market_structure = SMCPatternDetector.analyze_market_structure(df)
            liquidity_sweeps = SMCPatternDetector.detect_liquidity_sweeps(df)
            breaker_blocks = SMCPatternDetector.detect_breaker_blocks(df, order_blocks)
            premium_discount = SMCPatternDetector.calculate_premium_discount(df)
            ote_zones = SMCPatternDetector.detect_optimal_trade_entry(df, order_blocks)
            
            return {
                'order_blocks': order_blocks,
                'fair_value_gaps': fvgs,
                'market_structure': market_structure,
                'liquidity_sweeps': liquidity_sweeps,
                'breaker_blocks': breaker_blocks,
                'premium_discount': premium_discount,
                'optimal_trade_entries': ote_zones,
                'total_patterns': len(order_blocks) + len(fvgs) + len(liquidity_sweeps) + len(breaker_blocks) + len(ote_zones)
            }
            
        except Exception as e:
            logger.error(f"Error detecting patterns: {e}")
            return {
                'order_blocks': [],
                'fair_value_gaps': [],
                'market_structure': {'trend': 'UNKNOWN'},
                'liquidity_sweeps': [],
                'breaker_blocks': [],
                'premium_discount': {'zone': 'UNKNOWN'},
                'optimal_trade_entries': [],
                'total_patterns': 0
            }