"""
Gemini Pro Chart Analyzer
Integrates all analysis components and generates comprehensive trading signals
Enhanced with deep historical data context for superior Gemini Pro analysis
"""

from .client import GeminiProClient
from .prompts import build_comprehensive_prompt, create_simplified_prompt
from ..analysis.technical import TechnicalAnalyzer
from ..analysis.patterns import SMCPatternDetector
from ..analysis.volume_analysis import VolumeAnalyzer
from ..analysis.multi_timeframe import MultiTimeframeAnalyzer
from ..analysis.setup_filter import SetupPreFilter, SignalOptimizer
from ..mt5_integration.data_fetcher import MultiTimeframeDataFetcher
from ..data.data_package_builder import DataPackageBuilder
from typing import Dict, Any, List, Optional
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class GeminiChartAnalyzer:
    """Main analyzer that combines all strategies and uses Gemini Pro for final analysis"""
    
    def __init__(self, gemini_client: GeminiProClient, data_fetcher: MultiTimeframeDataFetcher):
        self.gemini = gemini_client
        self.data_fetcher = data_fetcher
        self.technical_analyzer = TechnicalAnalyzer()
        self.pattern_detector = SMCPatternDetector()
        self.volume_analyzer = VolumeAnalyzer()
        self.mtf_analyzer = MultiTimeframeAnalyzer()
        self.setup_filter = SetupPreFilter(min_confidence=60)  # 60% minimum
        self.signal_optimizer = SignalOptimizer()
        
    def analyze_symbol(self, symbol: str, timeframes: List[str] = None) -> Optional[Dict[str, Any]]:
        """
        Complete analysis for a single symbol with deep historical context
        
        Args:
            symbol: Trading symbol to analyze
            timeframes: List of timeframes to analyze
            
        Returns:
            Complete analysis result or None if failed
        """
        try:
            logger.info(f"Starting comprehensive analysis for {symbol}")
            
            # Step 1: Fetch multi-timeframe data with EXTENDED HISTORY
            if timeframes is None:
                # Include M5 and M1 for precise entry timing
                timeframes = ['M1', 'M5', 'M15', 'H1', 'H4', 'D1']
            
            # Fetch with appropriate bars for each timeframe
            all_data = {}
            bars_config = {
                'M1': 500,   # 500 minutes ≈ 8 hours (recent price action)
                'M5': 500,   # 2500 minutes ≈ 42 hours (2 days)
                'M15': 1000, # 15000 minutes ≈ 10 days
                'H1': 500,   # 500 hours ≈ 20 days
                'H4': 500,   # 2000 hours ≈ 83 days
                'D1': 500    # 500 days ≈ 1.5 years
            }
            
            for tf in timeframes:
                bars = bars_config.get(tf, 500)
                df = self.data_fetcher.mt5.get_market_data(symbol, tf, bars=bars)
                if df is not None and not df.empty:
                    all_data[tf] = df
                    logger.info(f"Fetched {len(df)} bars for {symbol} {tf}")
            
            if not all_data or len(all_data) < 4:
                logger.error(f"Insufficient data for {symbol}")
                return None
            
            # Step 2: Calculate technical indicators for all timeframes
            for tf in all_data:
                all_data[tf] = self.technical_analyzer.add_all_indicators(all_data[tf])
                logger.debug(f"Added technical indicators to {tf}")
            
            # Step 3: Multi-timeframe analysis
            mtf_analysis = self.mtf_analyzer.analyze_trend_alignment(all_data)
            
            # Step 4: SMC/ICT pattern detection on M15
            order_blocks = self.pattern_detector.detect_order_blocks(all_data['M15'])
            fvgs = self.pattern_detector.detect_fair_value_gaps(all_data['M15'])
            market_structure = self.pattern_detector.analyze_market_structure(all_data['M15'])
            liquidity_sweeps = self.pattern_detector.detect_liquidity_sweeps(all_data['M15'])
            premium_discount = self.pattern_detector.calculate_premium_discount(all_data['M15'])
            ote_zones = self.pattern_detector.detect_optimal_trade_entry(all_data['M15'], order_blocks)
            
            # Step 5: Volume analysis
            volume_analysis = self.volume_analyzer.analyze_volume(all_data['M15'])
            
            # Step 6: Extract technical indicators for package
            technical_indicators = {
                "m15": self._extract_indicators(all_data['M15']),
                "h1": self._extract_indicators(all_data['H1']),
                "h4": self._extract_indicators(all_data['H4']),
                "d1": self._extract_indicators(all_data['D1']),
            }
            
            # Step 7: Build COMPREHENSIVE data package with deep history
            data_package = DataPackageBuilder.build_complete_package(
                symbol=symbol,
                all_data=all_data,
                mtf_analysis=mtf_analysis,
                order_blocks=order_blocks,
                fvgs=fvgs,
                market_structure=market_structure,
                liquidity_sweeps=liquidity_sweeps,
                premium_discount=premium_discount,
                ote_zones=ote_zones,
                volume_analysis=volume_analysis,
                technical_indicators=technical_indicators
            )
            
            logger.info(f"Built comprehensive data package for {symbol} with deep historical context")
            
            # Step 7.5: PRE-FILTER - Check if setup is high probability
            logger.info("Running setup pre-filter...")
            filter_result = self.setup_filter.evaluate_setup(data_package)
            
            if not filter_result['passes_filter']:
                logger.info(f"❌ Setup rejected by pre-filter (confidence: {filter_result['confidence_estimate']}%)")
                logger.info(f"Reasons: {', '.join(filter_result['reasons'][:3])}")
                
                return {
                    'setup_detected': False,
                    'market_assessment': {
                        'overall_condition': 'LOW_PROBABILITY',
                        'tradeable': False,
                        'bias': 'NEUTRAL',
                        'key_observation': f"Pre-filter rejected: {filter_result['reasons'][0]}"
                    },
                    'setup_details': {
                        'direction': 'NO_TRADE',
                        'primary_setup': None
                    },
                    'filter_result': filter_result,
                    'skipped_gemini': True  # Indicates we didn't waste API call
                }
            
            logger.info(f"✅ Setup passes pre-filter (confidence: {filter_result['confidence_estimate']}%)")
            logger.info(f"Setup type: {filter_result['setup_type']}, Direction: {filter_result['direction']}")
            
            # Adjust minimum confidence based on session/time
            adjusted_min_confidence = self.signal_optimizer.get_adjusted_min_confidence()
            logger.info(f"Adjusted min confidence: {adjusted_min_confidence}%")
            
            # Step 8: Generate Gemini Pro analysis with enriched context
            prompt = build_comprehensive_prompt(symbol, data_package)
            analysis = self.gemini.analyze_chart(prompt)
            
            if not analysis:
                logger.error(f"Failed to get Gemini analysis for {symbol}")
                return None
            
            # If Gemini detected a setup, record it
            if analysis.get('setup_detected'):
                self.signal_optimizer.record_signal()
                logger.info(f"📊 {self.signal_optimizer.get_progress_summary()}")
            
            # Step 9: Add metadata
            analysis['metadata'] = {
                'symbol': symbol,
                'analysis_time': datetime.now(timezone.utc).isoformat(),
                'timeframes_analyzed': timeframes,
                'data_quality': self._assess_data_quality(all_data),
                'pattern_count': {
                    'order_blocks': len(order_blocks),
                    'fvgs': len(fvgs),
                    'liquidity_sweeps': len(liquidity_sweeps),
                    'ote_zones': len(ote_zones)
                }
            }
            
            logger.info(f"Analysis complete for {symbol}")
            return analysis
            
        except Exception as e:
            logger.error(f"Error analyzing {symbol}: {e}")
            return None
    
    def _build_data_package(self, symbol: str, all_data: Dict, mtf_analysis: Dict,
                          order_blocks: List, fvgs: List, market_structure: Dict,
                          liquidity_sweeps: List, premium_discount: Dict,
                          ote_zones: List, volume_analysis: Dict) -> Dict[str, Any]:
        """Build comprehensive data package for Gemini prompt"""
        
        current_time = datetime.now(timezone.utc)
        current_price = all_data['M15'].iloc[-1]['close']
        
        # Get session info
        session = self._get_session_info(current_time)
        
        # Get daily bias
        daily_bias = mtf_analysis.get('daily_bias', 'NEUTRAL')
        
        # Get trend alignment
        trend_alignment = mtf_analysis.get('alignment', {}).get('description', 'Unknown')
        
        # Format recent candles
        recent_candles = self._format_recent_candles(all_data['M15'])
        
        # Get indicators from M15
        indicators = self._extract_indicators(all_data['M15'])
        
        # Get fundamental context
        fundamental_context = self._get_fundamental_context(symbol, current_time)
        
        # Format liquidity description
        liquidity_description = self._format_liquidity_description(liquidity_sweeps)
        
        return {
            'symbol': symbol,
            'execution_timeframe': 'M15',
            'timestamp': current_time.strftime('%Y-%m-%d %H:%M UTC'),
            'current_price': round(current_price, 5),
            'session': session,
            'daily_bias': daily_bias,
            
            # Timeframe data
            'd1': {
                'trend': all_data['D1'].iloc[-1].get('trend', 'UNKNOWN'),
                'ema_50': round(all_data['D1'].iloc[-1]['ema_50'], 5),
                'ema_200': round(all_data['D1'].iloc[-1]['ema_200'], 5),
                'observation': f"D1 shows {all_data['D1'].iloc[-1].get('trend', 'UNKNOWN')} structure"
            },
            'h4': {
                'trend': all_data['H4'].iloc[-1].get('trend', 'UNKNOWN'),
                'ema_50': round(all_data['H4'].iloc[-1]['ema_50'], 5),
                'structure': market_structure.get('trend', 'UNKNOWN'),
                'swing_high': round(all_data['H4']['high'].tail(20).max(), 5),
                'swing_low': round(all_data['H4']['low'].tail(20).min(), 5)
            },
            'h1': {
                'trend': all_data['H1'].iloc[-1].get('trend', 'UNKNOWN'),
                'ema_20': round(all_data['H1'].iloc[-1]['ema_21'], 5),
                'ema_50': round(all_data['H1'].iloc[-1]['ema_50'], 5),
                'momentum': 'BULLISH' if all_data['H1'].iloc[-1]['rsi'] > 50 else 'BEARISH'
            },
            'm15': {
                'trend': all_data['M15'].iloc[-1].get('trend', 'UNKNOWN'),
                'ema_9': round(all_data['M15'].iloc[-1]['ema_9'], 5),
                'ema_21': round(all_data['M15'].iloc[-1]['ema_21'], 5),
                'price_action': self._describe_price_action(all_data['M15'])
            },
            'm5': {
                'trend': all_data.get('M5', all_data['M15']).iloc[-1].get('trend', 'UNKNOWN') if 'M5' in all_data else 'UNKNOWN',
                'ema_9': round(all_data['M5'].iloc[-1]['ema_9'], 5) if 'M5' in all_data else 0,
                'ema_21': round(all_data['M5'].iloc[-1]['ema_21'], 5) if 'M5' in all_data else 0,
                'price_action': self._describe_price_action(all_data['M5']) if 'M5' in all_data else 'No data',
                'rsi': round(all_data['M5'].iloc[-1].get('rsi', 50), 2) if 'M5' in all_data else 50
            },
            'm1': {
                'trend': all_data.get('M1', all_data['M15']).iloc[-1].get('trend', 'UNKNOWN') if 'M1' in all_data else 'UNKNOWN',
                'ema_9': round(all_data['M1'].iloc[-1]['ema_9'], 5) if 'M1' in all_data else 0,
                'recent_candles': self._format_m1_candles(all_data['M1']) if 'M1' in all_data else 'No data',
                'momentum': 'BULLISH' if ('M1' in all_data and all_data['M1'].iloc[-1].get('rsi', 50) > 50) else 'BEARISH'
            },
            
            'trend_alignment': trend_alignment,
            'order_blocks': order_blocks,
            'fvgs': fvgs,
            'market_structure': market_structure,
            'liquidity_description': liquidity_description,
            'premium_discount': premium_discount,
            'indicators': indicators,
            'volume': volume_analysis,
            'recent_candles': recent_candles,
            'fundamental_context': fundamental_context
        }
    
    def _get_session_info(self, current_time: datetime) -> Dict[str, str]:
        """Get current trading session information"""
        hour = current_time.hour
        
        if 7 <= hour < 10:
            return {'name': 'LONDON_KILL_ZONE', 'quality': 'EXCELLENT'}
        elif 13 <= hour < 16:
            return {'name': 'NEW_YORK_KILL_ZONE', 'quality': 'EXCELLENT'}
        elif 0 <= hour < 3:
            return {'name': 'ASIAN_KILL_ZONE', 'quality': 'MODERATE'}
        else:
            return {'name': 'OFF_HOURS', 'quality': 'POOR'}
    
    def _format_recent_candles(self, df) -> List[Dict]:
        """Format recent candles for display"""
        candles = []
        for _, row in df.tail(10).iterrows():
            pattern = 'BULLISH' if row['close'] > row['open'] else 'BEARISH'
            candles.append({
                'time': row['time'].strftime('%H:%M'),
                'open': round(row['open'], 5),
                'high': round(row['high'], 5),
                'low': round(row['low'], 5),
                'close': round(row['close'], 5),
                'pattern': pattern
            })
        return candles
    
    def _extract_indicators(self, df) -> Dict[str, Any]:
        """Extract all indicators from DataFrame"""
        latest = df.iloc[-1]
        
        rsi = round(latest['rsi'], 1)
        if rsi > 70:
            rsi_status = 'OVERBOUGHT'
        elif rsi < 30:
            rsi_status = 'OVERSOLD'
        else:
            rsi_status = 'NEUTRAL'
        
        return {
            'rsi': rsi,
            'rsi_status': rsi_status,
            'macd': round(latest['macd'], 2),
            'macd_signal': round(latest['macd_signal'], 2),
            'macd_histogram': round(latest['macd_diff'], 2),
            'stoch_k': round(latest['stoch_k'], 1),
            'stoch_d': round(latest['stoch_d'], 1),
            'stoch_status': 'OVERBOUGHT' if latest['stoch_k'] > 80 else 'OVERSOLD' if latest['stoch_k'] < 20 else 'NEUTRAL',
            'adx': round(latest['adx'], 1),
            'trend_strength': 'STRONG' if latest['adx'] > 25 else 'WEAK',
            'ema_alignment': 'BULLISH' if latest['ema_9'] > latest['ema_21'] > latest['ema_50'] else 'BEARISH' if latest['ema_9'] < latest['ema_21'] < latest['ema_50'] else 'MIXED',
            'atr': round(latest['atr'], 5),
            'volatility_level': 'HIGH' if latest['atr'] > df['atr'].mean() * 1.5 else 'LOW' if latest['atr'] < df['atr'].mean() * 0.5 else 'NORMAL',
            'bb_upper': round(latest['bb_upper'], 5),
            'bb_middle': round(latest['bb_middle'], 5),
            'bb_lower': round(latest['bb_lower'], 5),
            'bb_width': round(latest['bb_width'], 4),
            'bb_status': 'SQUEEZE' if latest['bb_width'] < 0.02 else 'EXPANDING'
        }
    
    def _describe_price_action(self, df) -> str:
        """Describe recent price action"""
        last_5 = df.tail(5)
        bullish_count = sum(1 for _, row in last_5.iterrows() if row['close'] > row['open'])
        
        if bullish_count >= 4:
            return 'Strong bullish momentum (4-5 green candles)'
        elif bullish_count >= 3:
            return 'Moderate bullish pressure'
        elif bullish_count <= 1:
            return 'Strong bearish momentum (4-5 red candles)'
        elif bullish_count <= 2:
            return 'Moderate bearish pressure'
        else:
            return 'Choppy price action'
    
    def _format_m1_candles(self, df) -> str:
        """Format recent M1 candles for ultra-precise timing"""
        if df is None or df.empty:
            return 'No M1 data'
        
        last_5 = df.tail(5)
        candles_text = []
        
        for _, row in last_5.iterrows():
            candle_type = 'BULL' if row['close'] > row['open'] else 'BEAR'
            candle_size = abs(row['close'] - row['open']) * 10000  # pips
            candles_text.append(f"{candle_type} {candle_size:.1f}p")
        
        return ' | '.join(candles_text)
    
    def _get_fundamental_context(self, symbol: str, current_time: datetime) -> str:
        """Get fundamental context (simplified)"""
        # In production, integrate with economic calendar API
        return f"No major news events scheduled for next 4 hours. Standard {symbol} trading conditions."
    
    def _format_liquidity_description(self, liquidity_sweeps: List) -> str:
        """Format liquidity sweeps description"""
        if not liquidity_sweeps:
            return "No recent liquidity sweeps detected"
        
        description = "Recent liquidity sweeps:\n"
        for i, sweep in enumerate(liquidity_sweeps[:3], 1):
            description += f"{i}. {sweep['type']} at {sweep.get('sweep_high', sweep.get('sweep_low', 'N/A')):.5f}\n"
        
        return description
    
    def _assess_data_quality(self, all_data: Dict) -> str:
        """Assess the quality of fetched data"""
        try:
            total_bars = sum(len(df) for df in all_data.values() if df is not None)
            expected_bars = len(all_data) * 500  # Expected bars per timeframe
            
            quality_ratio = total_bars / expected_bars if expected_bars > 0 else 0
            
            if quality_ratio >= 0.9:
                return 'EXCELLENT'
            elif quality_ratio >= 0.7:
                return 'GOOD'
            elif quality_ratio >= 0.5:
                return 'FAIR'
            else:
                return 'POOR'
                
        except Exception as e:
            logger.error(f"Error assessing data quality: {e}")
            return 'UNKNOWN'
    
    def quick_analysis(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Quick analysis for rapid signal generation"""
        try:
            # Fetch only M15 data for quick analysis
            data = self.data_fetcher.fetch_all_data(symbol, ['M15'])
            
            if not data or 'M15' not in data:
                return None
            
            # Add basic indicators
            data['M15'] = self.technical_analyzer.add_all_indicators(data['M15'])
            
            # Get basic info
            latest = data['M15'].iloc[-1]
            current_price = latest['close']
            trend = self.technical_analyzer.identify_trend(data['M15'])
            session = self._get_session_info(datetime.now(timezone.utc))
            confidence = 50  # Default confidence
            
            # Create simplified prompt
            prompt = create_simplified_prompt(symbol, current_price, trend, session['name'], confidence)
            
            # Get quick analysis
            analysis = self.gemini.analyze_chart(prompt)
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error in quick analysis for {symbol}: {e}")
            return None


