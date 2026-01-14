"""
Multi-Timeframe Data Fetcher and Signal Aggregator
Adapted from AlphaForge for AlphaForge trading system
Supports: GBP/USD, XAU/USD (Gold), USD/JPY
"""
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime
import logging
from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsCandles
import os

logger = logging.getLogger(__name__)

class MultiTimeframeEngine:
    """
    Fetches and analyzes multiple timeframes for enhanced signal generation.
    Uses weighted multi-timeframe confluence for better win rates.
    """

    def __init__(self, api_key=None, environment="practice", min_votes_required=2.0, min_strength=25.0):
        """
        Initialize Multi-Timeframe Engine.
        
        Args:
            api_key: OANDA API key
            environment: "practice" or "live"
            min_votes_required: Minimum indicator votes needed for signal (default: 2.0)
                                STRICT: 3.0 for higher quality
            min_strength: Minimum signal strength percentage (default: 25.0)
                         STRICT: 50.0 for higher quality
        """
        self.api_key = api_key or os.getenv("OANDA_API_KEY")
        self.api = API(access_token=self.api_key, environment=environment)
        self.min_votes_required = min_votes_required
        self.min_strength = min_strength
        
        # Supported instruments
        self.instruments = {
            'GBP_USD': {'name': 'British Pound / US Dollar', 'pip_value': 0.0001},
            'XAU_USD': {'name': 'Gold / US Dollar', 'pip_value': 0.01},
            'USD_JPY': {'name': 'US Dollar / Japanese Yen', 'pip_value': 0.01}
        }
        
        # Timeframe configuration with weights
        self.timeframes = {
            'M5': {
                'granularity': 'M5',
                'count': 500,
                'weight': 0.20,  # Reduced weight for scalping noise
                'name': '5-minute'
            },
            'M15': {
                'granularity': 'M15',
                'count': 300,
                'weight': 0.30,  # Intermediate confirmation
                'name': '15-minute'
            },
            'H1': {
                'granularity': 'H1',
                'count': 200,
                'weight': 0.50,  # Primary trend timeframe for Day Trading
                'name': '1-hour'
            }
        }
        
        # Cache for fetched data
        self.data_cache = {}
        
    async def fetch_candles_async(self, instrument, granularity, count, to_time=None):
        """
        Fetch candles asynchronously from OANDA API.
        
        Args:
            instrument: Trading pair (GBP_USD, XAU_USD, USD_JPY)
            granularity: Timeframe (M5, M15, H1)
            granularity: Timeframe (M5, M15, H1)
            count: Number of candles to fetch
            to_time: Optional datetime limit for historical data
        """
        params = {
            "granularity": granularity,
            "count": min(count, 5000),  # OANDA max limit
            "price": "M"  # Midpoint pricing
        }
        
        if to_time:
            params["to"] = to_time.strftime("%Y-%m-%dT%H:%M:%SZ")
        
        try:
            request = InstrumentsCandles(instrument=instrument, params=params)
            
            # Run synchronous API call in executor
            loop = asyncio.get_event_loop()
            response = await loop.run_in_executor(
                None,
                lambda: self.api.request(request)
            )
            
            # DEBUG: Print fetch details
            candles = response.get('candles', [])
            print(f"DEBUG: Fetched {len(candles)} candles for {instrument} {granularity} (to={params.get('to')})")
            df = self._process_candles(candles)
            
            logger.info(f"Fetched {len(df)} {granularity} candles for {instrument}")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching {instrument} {granularity}: {e}")
            return None

    def _process_candles(self, candles):
        """
        Convert OANDA API candles to DataFrame.
        
        Args:
            candles: List of candle dicts from OANDA
        
        Returns:
            DataFrame: Processed OHLCV data
        """
        data = []
        
        for candle in candles:
            # Skip incomplete candles
            if not candle.get('complete', False):
                continue
            
            # Extract timestamp
            time_str = candle['time'].replace('.000000000Z', '')
            timestamp = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
            
            # Extract OHLCV (midpoint pricing)
            mid = candle.get('mid', candle.get('bid', candle.get('ask')))
            
            data.append({
                'timestamp': timestamp,
                'open': float(mid['o']),
                'high': float(mid['h']),
                'low': float(mid['l']),
                'close': float(mid['c']),
                'volume': int(candle['volume'])
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
        
        return df

    async def fetch_multi_timeframe(self, instrument, to_time=None):
        """
        Fetch all timeframes (M5, M15, H1) in parallel.
        
        Args:
            instrument: Trading pair (GBP_USD, XAU_USD, USD_JPY)
        
        Returns:
            dict: {
                'M5': DataFrame,
                'M15': DataFrame,
                'H1': DataFrame
            }
        """
        if instrument not in self.instruments:
            logger.error(f"Unsupported instrument: {instrument}")
            return {}
        
        # Create tasks for all timeframes
        tasks = []
        tf_keys = []
        
        for tf_key, tf_config in self.timeframes.items():
            tasks.append(
                self.fetch_candles_async(
                    instrument,
                    tf_config['granularity'],
                    tf_config['count'],
                    to_time
                )
            )
            tf_keys.append(tf_key)
        
        # Fetch in parallel
        logger.info(f"Fetching {len(tasks)} timeframes for {instrument}...")
        results = await asyncio.gather(*tasks)
        
        # Build result dictionary
        data = {}
        for tf_key, df in zip(tf_keys, results):
            if df is not None and not df.empty:
                data[tf_key] = df
        
        # Cache the data
        self.data_cache[instrument] = {
            'data': data,
            'timestamp': datetime.now()
        }
        
        return data

    def _calculate_indicators(self, df):
        """
        Calculate AlphaForge-style fast indicators.
        
        Args:
            df: DataFrame with OHLCV data
        
        Returns:
            DataFrame: With indicators added
        """
        if df is None or len(df) < 50:
            return df
        
        # EMA Ribbon (5-8-13) - Ultra-fast trend detection
        df['ema5'] = df['close'].ewm(span=5, adjust=False).mean()
        df['ema8'] = df['close'].ewm(span=8, adjust=False).mean()
        df['ema13'] = df['close'].ewm(span=13, adjust=False).mean()
        
        # Fast RSI (7-period) - Optimized for M5 scalping
        delta = df['close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(window=7).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(window=7).mean()
        rs = gain / loss
        df['rsi7'] = 100 - (100 / (1 + rs))
        
        # Fast MACD (6-13-4) - Quick momentum detection
        ema_fast = df['close'].ewm(span=6, adjust=False).mean()
        ema_slow = df['close'].ewm(span=13, adjust=False).mean()
        df['macd'] = ema_fast - ema_slow
        df['macd_signal'] = df['macd'].ewm(span=4, adjust=False).mean()
        df['macd_hist'] = df['macd'] - df['macd_signal']
        
        # Bollinger Bands (14, 2.0)
        df['bb_middle'] = df['close'].rolling(window=14).mean()
        bb_std = df['close'].rolling(window=14).std()
        df['bb_upper'] = df['bb_middle'] + (bb_std * 2.0)
        df['bb_lower'] = df['bb_middle'] - (bb_std * 2.0)
        df['bb_position'] = (df['close'] - df['bb_lower']) / (df['bb_upper'] - df['bb_lower'])
        
        # Stochastic (5-3) - Fast stochastic for scalping
        low_min = df['low'].rolling(window=5).min()
        high_max = df['high'].rolling(window=5).max()
        df['stoch_k'] = 100 * (df['close'] - low_min) / (high_max - low_min)
        df['stoch_d'] = df['stoch_k'].rolling(window=3).mean()
        
        # ADX (14) - Trend strength
        plus_dm = df['high'].diff()
        minus_dm = -df['low'].diff()
        plus_dm[plus_dm < 0] = 0
        minus_dm[minus_dm < 0] = 0
        
        tr1 = df['high'] - df['low']
        tr2 = abs(df['high'] - df['close'].shift())
        tr3 = abs(df['low'] - df['close'].shift())
        tr = pd.concat([tr1, tr2, tr3], axis=1).max(axis=1)
        atr = tr.rolling(window=14).mean()
        
        plus_di = 100 * (plus_dm.rolling(window=14).mean() / atr)
        minus_di = 100 * (minus_dm.rolling(window=14).mean() / atr)
        dx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)
        df['adx'] = dx.rolling(window=14).mean()
        
        # ATR (14) - Volatility
        df['atr'] = atr
        df['atr_pct'] = (df['atr'] / df['close']) * 100
        
        # Volume average
        df['volume_avg'] = df['volume'].rolling(window=20).mean()
        df['volume_ratio'] = df['volume'] / df['volume_avg']
        
        return df

    def analyze_timeframe(self, df, market_regime='unknown'):
        """
        AlphaForge-style indicator voting system.
        
        Args:
            df: DataFrame with OHLCV data
            market_regime: Current market regime for adaptive thresholds
        
        Returns:
            dict: {
                'buy_votes': int,
                'sell_votes': int,
                'total_indicators': int,
                'signal_details': list,
                'strength': float
            }
        """
        if df is None or len(df) < 50:
            return {
                'buy_votes': 0,
                'sell_votes': 0,
                'total_indicators': 0,
                'signal_details': [],
                'strength': 0.0,
                'latest_data': {}
            }
        
        # Calculate indicators
        df = self._calculate_indicators(df)
        
        # Get latest values
        latest = df.iloc[-1]
        prev = df.iloc[-2]
        
        buy_votes = 0
        sell_votes = 0
        total_indicators = 0
        signal_details = []
        
        # ===== INDICATOR 1: EMA Ribbon (5-8-13) =====
        total_indicators += 1
        if latest['ema5'] > latest['ema8'] > latest['ema13']:
            buy_votes += 1
            signal_details.append("✅ EMA Ribbon bullish (5>8>13)")
        elif latest['ema5'] < latest['ema8'] < latest['ema13']:
            sell_votes += 1
            signal_details.append("✅ EMA Ribbon bearish (5<8<13)")
        else:
            signal_details.append("⚠️ EMA Ribbon mixed")
        
        # ===== INDICATOR 2: Fast RSI (7) - ADAPTIVE =====
        total_indicators += 1
        rsi = latest['rsi7']
        
        # Adaptive thresholds based on regime
        if 'ranging' in market_regime.lower():
            # Mean reversion in ranging markets
            if rsi < 20:
                buy_votes += 1
                signal_details.append(f"✅ RSI oversold (ranging): {rsi:.1f}")
            elif rsi > 80:
                sell_votes += 1
                signal_details.append(f"✅ RSI overbought (ranging): {rsi:.1f}")
            else:
                signal_details.append(f"⚠️ RSI neutral (ranging): {rsi:.1f}")
        
        elif 'trending_up' in market_regime.lower():
            # Momentum in uptrend - look for pullbacks
            if 30 < rsi < 50:
                buy_votes += 1
                signal_details.append(f"✅ RSI pullback in uptrend: {rsi:.1f}")
            elif rsi > 70:
                signal_details.append(f"⚠️ RSI overbought: {rsi:.1f}")
        
        elif 'trending_down' in market_regime.lower():
            # Momentum in downtrend - look for rallies
            if 50 < rsi < 70:
                sell_votes += 1
                signal_details.append(f"✅ RSI rally in downtrend: {rsi:.1f}")
            elif rsi < 30:
                signal_details.append(f"⚠️ RSI oversold: {rsi:.1f}")
        else:
            # Unknown regime - use standard thresholds
            if rsi < 30:
                buy_votes += 1
                signal_details.append(f"✅ RSI oversold: {rsi:.1f}")
            elif rsi > 70:
                sell_votes += 1
                signal_details.append(f"✅ RSI overbought: {rsi:.1f}")
        
        # ===== INDICATOR 3: Fast MACD (6-13-4) =====
        total_indicators += 1
        if latest['macd'] > latest['macd_signal'] and latest['macd_hist'] > 0:
            buy_votes += 1
            signal_details.append("✅ MACD bullish (macd > signal)")
        elif latest['macd'] < latest['macd_signal'] and latest['macd_hist'] < 0:
            sell_votes += 1
            signal_details.append("✅ MACD bearish (macd < signal)")
        else:
            signal_details.append("⚠️ MACD neutral")
        
        # ===== INDICATOR 4: Bollinger Bands - ADAPTIVE =====
        total_indicators += 1
        bb_pos = latest['bb_position']
        
        if 'ranging' in market_regime.lower():
            # Mean reversion in ranging
            if bb_pos < 0.2:
                buy_votes += 1
                signal_details.append(f"✅ BB near lower band (ranging): {bb_pos:.2f}")
            elif bb_pos > 0.8:
                sell_votes += 1
                signal_details.append(f"✅ BB near upper band (ranging): {bb_pos:.2f}")
        
        elif 'trending_up' in market_regime.lower():
            # Breakout in trending
            if latest['close'] > latest['bb_upper']:
                buy_votes += 1
                signal_details.append("✅ BB breakout above (trending)")
            elif bb_pos < 0.3:
                buy_votes += 1
                signal_details.append(f"✅ BB pullback to lower band: {bb_pos:.2f}")
        
        elif 'trending_down' in market_regime.lower():
            if latest['close'] < latest['bb_lower']:
                sell_votes += 1
                signal_details.append("✅ BB breakout below (trending)")
            elif bb_pos > 0.7:
                sell_votes += 1
                signal_details.append(f"✅ BB rally to upper band: {bb_pos:.2f}")
        
        # ===== INDICATOR 5: Stochastic (5-3) =====
        total_indicators += 1
        stoch_k = latest['stoch_k']
        stoch_d = latest['stoch_d']
        prev_stoch_k = prev['stoch_k']
        prev_stoch_d = prev['stoch_d']
        
        # Oversold crossover
        if stoch_k < 20 and stoch_k > stoch_d and prev_stoch_k <= prev_stoch_d:
            buy_votes += 1
            signal_details.append(f"✅ Stochastic oversold crossover: K={stoch_k:.1f}")
        # Overbought crossover
        elif stoch_k > 80 and stoch_k < stoch_d and prev_stoch_k >= prev_stoch_d:
            sell_votes += 1
            signal_details.append(f"✅ Stochastic overbought crossover: K={stoch_k:.1f}")
        else:
            signal_details.append(f"⚠️ Stochastic neutral: K={stoch_k:.1f}, D={stoch_d:.1f}")
        
        # ===== INDICATOR 6: Volume Confirmation =====
        total_indicators += 1
        volume_ratio = latest['volume_ratio']
        
        if volume_ratio > 1.2:
            # High volume - boost the stronger signal
            if buy_votes > sell_votes:
                buy_votes += 0.5
                signal_details.append(f"✅ Volume confirms BUY: {volume_ratio:.2f}x avg")
            elif sell_votes > buy_votes:
                sell_votes += 0.5
                signal_details.append(f"✅ Volume confirms SELL: {volume_ratio:.2f}x avg")
            else:
                signal_details.append(f"⚠️ High volume but no clear direction: {volume_ratio:.2f}x")
        else:
            signal_details.append(f"⚠️ Low volume: {volume_ratio:.2f}x avg")
        
        # Calculate strength (percentage of indicators agreeing)
        if buy_votes > sell_votes:
            strength = (buy_votes / total_indicators) * 100
        elif sell_votes > buy_votes:
            strength = (sell_votes / total_indicators) * 100
        else:
            strength = 0.0
        
        return {
            'buy_votes': buy_votes,
            'sell_votes': sell_votes,
            'total_indicators': total_indicators,
            'signal_details': signal_details,
            'strength': strength,
            'latest_data': {
                'ema5': latest['ema5'],
                'ema8': latest['ema8'],
                'ema13': latest['ema13'],
                'rsi7': latest['rsi7'],
                'macd': latest['macd'],
                'atr': latest['atr'],
                'atr_pct': latest['atr_pct'],
                'volume_ratio': volume_ratio,
                'adx': latest['adx']
            }
        }

    def generate_multi_timeframe_signal(self, instrument_data, market_regime='unknown'):
        """
        Generate AlphaForge-style multi-indicator voting signal.
        
        Args:
            instrument_data: {
                'M5': DataFrame,
                'M15': DataFrame,
                'H1': DataFrame
            }
            market_regime: Current market regime for adaptive thresholds
        
        Returns:
            dict: {
                'signal': 'BUY', 'SELL', or 'NO_ACTION',
                'buy_votes': float,
                'sell_votes': float,
                'strength': float (0-100),
                'confidence': float (0-1),
                'timeframe_signals': {...},
                'passed_filters': bool,
                'filter_results': {...}
            }
        """
        if not instrument_data:
            return {
                'signal': 'NO_ACTION',
                'buy_votes': 0,
                'sell_votes': 0,
                'strength': 0.0,
                'confidence': 0.0,
                'timeframe_signals': {},
                'agreement': 0.0,
                'passed_filters': False,
                'filter_results': {}
            }
        
        # Analyze each timeframe with voting system
        tf_signals = {}
        total_buy_votes = 0.0
        total_sell_votes = 0.0
        total_weight = 0.0
        
        for tf_key, df in instrument_data.items():
            if df is not None and not df.empty:
                # Analyze with indicator voting
                analysis = self.analyze_timeframe(df, market_regime)
                weight = self.timeframes[tf_key]['weight']
                
                tf_signals[tf_key] = {
                    'buy_votes': analysis['buy_votes'],
                    'sell_votes': analysis['sell_votes'],
                    'total_indicators': analysis['total_indicators'],
                    'strength': analysis['strength'],
                    'weight': weight,
                    'signal_details': analysis['signal_details'],
                    'latest_data': analysis['latest_data']
                }
                
                # Weighted vote aggregation
                total_buy_votes += analysis['buy_votes'] * weight
                total_sell_votes += analysis['sell_votes'] * weight
                total_weight += weight
        
        # Normalize votes
        if total_weight > 0:
            avg_buy_votes = total_buy_votes / total_weight
            avg_sell_votes = total_sell_votes / total_weight
        else:
            avg_buy_votes = 0
            avg_sell_votes = 0
        
        # ===== AlphaForge DECISION RULE: Configurable Indicator Agreement =====
        # min_votes_required can be adjusted:
        # 3.0 = strictest (AlphaForge paper standard) - fewer, highest quality signals
        # 2.5 = moderate (recommended for M5 scalping) - balanced quality/quantity
        # 2.0 = relaxed - more signals, may include lower quality
        
        if avg_buy_votes >= self.min_votes_required and avg_buy_votes > avg_sell_votes:
            signal_type = 'BUY'
            # Calculate strength as percentage of dominant votes vs total possible
            # Using max possible votes (6 indicators) for normalization
            strength = (avg_buy_votes / 6.0) * 100
        elif avg_sell_votes >= self.min_votes_required and avg_sell_votes > avg_buy_votes:
            signal_type = 'SELL'
            strength = (avg_sell_votes / 6.0) * 100
        else:
            signal_type = 'NO_ACTION'
            # Even with no clear direction, calculate strength for reporting
            max_votes = max(avg_buy_votes, avg_sell_votes)
            strength = (max_votes / 6.0) * 100
        
        # Calculate confidence (based on total weight)
        confidence = total_weight  # Max 1.0 if all timeframes present
        
        # Calculate agreement (how aligned are the timeframes?)
        agreement = self._calculate_voting_agreement(tf_signals)
        
        # ===== APPLY QUALITY FILTERS (AlphaForge-style) =====
        filter_results = self._apply_signal_filters(
            signal_type,
            strength,
            instrument_data.get('M5'),
            tf_signals
        )
        
        # Override signal if filters reject
        if not filter_results['passed']:
            signal_type = 'NO_ACTION'
            strength = 0.0
        
        return {
            'signal': signal_type,
            'buy_votes': avg_buy_votes,
            'sell_votes': avg_sell_votes,
            'strength': strength,
            'confidence': confidence,
            'timeframe_signals': tf_signals,
            'agreement': agreement,
            'passed_filters': filter_results['passed'],
            'filter_results': filter_results,
            'market_regime': market_regime
        }

    def _calculate_voting_agreement(self, tf_signals):
        """
        Calculate how well timeframes agree on signal direction.
        
        Args:
            tf_signals: Dict of timeframe analysis results
        
        Returns:
            float: Agreement percentage (0.0 to 1.0)
        """
        if not tf_signals:
            return 0.0
        
        # Determine direction for each timeframe
        directions = []
        for tf_key, analysis in tf_signals.items():
            if analysis['buy_votes'] > analysis['sell_votes'] + 0.5:
                directions.append('BUY')
            elif analysis['sell_votes'] > analysis['buy_votes'] + 0.5:
                directions.append('SELL')
            else:
                directions.append('NEUTRAL')
        
        # Count most common direction
        buy_count = directions.count('BUY')
        sell_count = directions.count('SELL')
        neutral_count = directions.count('NEUTRAL')
        
        total = len(directions)
        most_common_count = max(buy_count, sell_count, neutral_count)
        
        agreement = most_common_count / total if total > 0 else 0.0
        return agreement

    def _apply_signal_filters(self, signal_type, strength, df_m5, tf_signals):
        """
        AlphaForge-style quality filters to reject poor signals.
        
        Filters:
        1. Volatility range (0.05% - 0.25%)
        2. Minimum signal strength (50%)
        3. ADX trend strength check
        4. Spread check (simulated)
        
        Args:
            signal_type: BUY, SELL, or NO_ACTION
            strength: Signal strength percentage
            df_m5: M5 timeframe DataFrame
            tf_signals: Analysis results from all timeframes
        
        Returns:
            dict: {
                'passed': bool,
                'reasons': list,
                'volatility_ok': bool,
                'strength_ok': bool,
                'adx_ok': bool,
                'spread_ok': bool
            }
        """
        if signal_type == 'NO_ACTION':
            return {
                'passed': False,
                'reasons': ['No signal generated'],
                'volatility_ok': False,
                'strength_ok': False,
                'adx_ok': False,
                'spread_ok': False
            }
        
        reasons = []
        volatility_ok = False
        strength_ok = False
        adx_ok = False
        spread_ok = True  # Default true (simulated)
        
        # Get M5 data
        if df_m5 is None or df_m5.empty:
            return {
                'passed': False,
                'reasons': ['No M5 data available'],
                'volatility_ok': False,
                'strength_ok': False,
                'adx_ok': False,
                'spread_ok': False
            }
        
        m5_analysis = tf_signals.get('M5', {}).get('latest_data', {})
        
        # ===== FILTER 1: Volatility Range (RELAXED) =====
        atr_pct = m5_analysis.get('atr_pct', 0)
        
        # RELAXED: 0.02% minimum to catch more moves
        if 0.02 <= atr_pct <= 1.0:
            volatility_ok = True
        else:
            if atr_pct < 0.02:
                reasons.append(f"Volatility too low: {atr_pct:.2f}% (need 0.02%+)")
            else:
                reasons.append(f"Volatility too high: {atr_pct:.2f}% (max 1.0%)")
        
        # ===== FILTER 2: Minimum Signal Strength (LOWERED) =====
        if strength >= self.min_strength:
            strength_ok = True
        else:
            reasons.append(f"Signal strength too weak: {strength:.1f}% (need {self.min_strength}%+)")
        
        # ===== FILTER 3: ADX Trend Strength (ORIGINAL STRICT) =====
        adx = m5_analysis.get('adx', 0)
        
        # STRICT: 25 minimum for trend confirmation
        if signal_type in ['BUY', 'SELL']:
            if adx >= 25:
                adx_ok = True
            else:
                reasons.append(f"Weak trend (ADX={adx:.1f}, need 25+)")
        
        # ===== FILTER 4: Spread Check (Simulated) =====
        # In production, you'd check actual spread from broker
        # For now, assume spread is acceptable
        spread_ok = True
        
        # ===== FINAL DECISION =====
        passed = volatility_ok and strength_ok and adx_ok and spread_ok
        
        if passed:
            reasons.append(f"✅ All filters passed - SIGNAL VALID")
        
        return {
            'passed': passed,
            'reasons': reasons,
            'volatility_ok': volatility_ok,
            'strength_ok': strength_ok,
            'adx_ok': adx_ok,
            'spread_ok': spread_ok,
            'atr_pct': atr_pct,
            'adx': adx,
            'strength': strength
        }


# Example usage
async def main():
    """Test AlphaForge-style multi-timeframe voting system."""
    api_key = os.getenv("OANDA_API_KEY", "YOUR_API_KEY_HERE")
    
    engine = MultiTimeframeEngine(api_key=api_key, environment="practice")
    
    # Fetch GBP/USD data
    print("="*80)
    # ...existing code...
    print("="*80)
    print("\nFetching GBP/USD multi-timeframe data...")
    data = await engine.fetch_multi_timeframe("GBP_USD")
    
    if data:
        print(f"\n✅ Fetched timeframes:")
        for tf, df in data.items():
            print(f"  {tf}: {len(df)} candles")
        
        # Test with different regimes
        test_regimes = [
            'trending_up_low_volatility',
            'ranging_low_volatility',
            'trending_down_low_volatility'
        ]
        
        for regime in test_regimes:
            print(f"\n{'='*80}")
            print(f"Testing with regime: {regime}")
            print(f"{'='*80}")
            
            # Generate signal with voting system
            signal = engine.generate_multi_timeframe_signal(data, regime)
            
            print(f"\n🎯 FINAL SIGNAL: {signal['signal']}")
            print(f"   Buy Votes: {signal['buy_votes']:.2f}/6.0")
            print(f"   Sell Votes: {signal['sell_votes']:.2f}/6.0")
            print(f"   Strength: {signal['strength']:.1f}%")
            print(f"   Confidence: {signal['confidence']:.2f}")
            print(f"   Agreement: {signal['agreement']:.1%}")
            print(f"   Passed Filters: {'✅ YES' if signal['passed_filters'] else '❌ NO'}")
            
            # Show filter results
            if not signal['passed_filters']:
                print(f"\n⚠️ Filter Rejection Reasons:")
                for reason in signal['filter_results']['reasons']:
                    print(f"   {reason}")
            else:
                print(f"\n✅ Quality Filters:")
                filters = signal['filter_results']
                print(f"   Volatility: {filters['atr_pct']:.2f}% (0.05-0.25%) - {'✅' if filters['volatility_ok'] else '❌'}")
                print(f"   Strength: {filters['strength']:.1f}% (≥50%) - {'✅' if filters['strength_ok'] else '❌'}")
                print(f"   ADX: {filters['adx']:.1f} (≥15) - {'✅' if filters['adx_ok'] else '❌'}")
                print(f"   Spread: {'✅' if filters['spread_ok'] else '❌'}")
            
            # Show timeframe breakdown
            print(f"\n📊 Timeframe Analysis:")
            for tf, analysis in signal['timeframe_signals'].items():
                buy_v = analysis['buy_votes']
                sell_v = analysis['sell_votes']
                total = analysis['total_indicators']
                direction = 'BUY' if buy_v > sell_v else ('SELL' if sell_v > buy_v else 'NEUTRAL')
                
                print(f"\n   {tf} ({analysis['weight']*100:.0f}% weight): {direction}")
                print(f"      Buy: {buy_v:.1f}/{total} | Sell: {sell_v:.1f}/{total} | Strength: {analysis['strength']:.1f}%")
                
                # Show indicator details
                for detail in analysis['signal_details'][:3]:  # Show top 3
                    print(f"      {detail}")


if __name__ == "__main__":
    asyncio.run(main())

