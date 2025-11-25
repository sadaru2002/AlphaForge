"""
Enhanced AlphaForge Signal Generator with AlphaForge Integration
Supports: GBP/USD, XAU/USD (Gold), USD/JPY
Features: Regime Detection, Kelly Criterion, Multi-Timeframe Analysis
"""
import pandas as pd
import numpy as np
import asyncio
import logging
from datetime import datetime, timedelta
import sys
import os

# Import AlphaForge-inspired modules
from regime_detector import MarketRegimeDetector, MarketRegime
from kelly_criterion import KellyCriterion
from multi_timeframe_engine import MultiTimeframeEngine
from regime_classifier import RegimeClassifier  # NEW: Upgraded regime detection
from instrument_config import InstrumentConfig  # NEW: Instrument-specific SL/TP

logger = logging.getLogger(__name__)

class EnhancedSignalGenerator:
    """
    Enhanced signal generator combining AlphaForge and AlphaForge strategies.
    - Multi-timeframe confluence (M5, M15, H1)
    - Gaussian Mixture Model regime detection
    - Kelly Criterion position sizing
    - Gemini AI validation (existing AlphaForge feature)
    """

    def __init__(self, oanda_api_key=None):
        """Initialize enhanced signal generator."""
        # Core components
        self.regime_detector = MarketRegimeDetector()
        self.kelly_criterion = KellyCriterion(lookback_trades=50, kelly_fraction=0.25)
        
        # UPGRADED: Stricter parameters for 50%+ win rate
        self.mtf_engine = MultiTimeframeEngine(
            api_key=oanda_api_key, 
            min_votes_required=2.5,  # UPGRADED: 1.5 → 2.5
            min_strength=35.0        # UPGRADED: 25.0 → 35.0
        )
        
        # NEW: Advanced regime classifier for STRONG_TREND filtering
        self.regime_classifier = RegimeClassifier()
        
        # Supported instruments
        self.instruments = ['GBP_USD', 'XAU_USD', 'USD_JPY']
        
        # Signal history
        self.signal_history = {instrument: [] for instrument in self.instruments}
        
        # Trading session configuration (GMT)
        self.trading_sessions = {
            'LONDON': {'start': 8, 'end': 16, 'weight': 1.2},
            'NEW_YORK': {'start': 13, 'end': 21, 'weight': 1.2},
            'TOKYO': {'start': 0, 'end': 8, 'weight': 0.8},
            'SYDNEY': {'start': 22, 'end': 6, 'weight': 0.8}
        }
        
        # Minimum signal thresholds (Kept at relaxed levels)
        self.min_confidence = 0.4
        self.min_agreement = 0.5
        
    async def generate_signal(self, instrument='GBP_USD', timestamp=None, provided_data=None):
        """
        Generate trading signal with full AlphaForge enhancement.
        
        Args:
            instrument: GBP_USD, XAU_USD, or USD_JPY
        
        Returns:
            dict: Complete signal with regime, MTF analysis, position sizing
        """
        if instrument not in self.instruments:
            logger.error(f"Unsupported instrument: {instrument}")
            return None
        
        try:
            # Step 1: Fetch multi-timeframe data
            if provided_data:
                # Use injected data for backtesting
                mtf_data = provided_data
            else:
                # Fetch live data
                logger.info(f"Fetching multi-timeframe data for {instrument}...")
                mtf_data = await self.mtf_engine.fetch_multi_timeframe(instrument, to_time=timestamp)
            
            if not mtf_data or 'M5' not in mtf_data:
                logger.error(f"Failed to fetch data for {instrument}")
                return None
            
            # Step 1.5: Check cooldown (4 hours)
            # "Day Trading" focus - avoid spamming signals in same trend
            last_signals = self.signal_history.get(instrument, [])
            if last_signals:
                last_sig = last_signals[-1]
                last_time = datetime.fromisoformat(last_sig['timestamp'])
                
                # Use provided timestamp or current time for comparison
                current_time = timestamp or datetime.now()
                
                # If last signal was tradeable and less than 4 hours ago
                if last_sig.get('tradeable', False) and (current_time - last_time) < timedelta(hours=4) and (current_time - last_time).total_seconds() > 0:
                    logger.info(f"Cooldown active for {instrument} (Last signal: {last_time.strftime('%H:%M')})")
                    return {
                        'instrument': instrument,
                        'signal': 'SKIP',
                        'reason': 'Cooldown active (4h)',
                        'tradeable': False,
                        'timestamp': current_time.isoformat()
                    }
            
            # Step 2: Detect market regime (using M5 data)
            df_m5 = mtf_data['M5']
            regime = self.regime_detector.detect_regime(df_m5, instrument)
            
            logger.info(f"Market regime for {instrument}: {regime.value}")
            
            # Step 3: Check if regime is tradeable
            should_trade = self.regime_detector.should_trade(regime)
            
            if not should_trade:
                logger.warning(f"Unfavorable regime: {regime.value} - Skipping trade")
                return {
                    'instrument': instrument,
                    'signal': 'SKIP',
                    'regime': regime.value,
                    'reason': 'Unfavorable market regime',
                    'tradeable': False,
                    'timestamp': (timestamp or datetime.now()).isoformat()
                }
            
            # Step 4: Generate multi-timeframe signal WITH REGIME
            mtf_signal = self.mtf_engine.generate_multi_timeframe_signal(
                mtf_data, 
                regime.value  # Pass regime for adaptive thresholds
            )
            
            logger.info(
                f"MTF Signal: {mtf_signal['signal']} "
                f"(buy_votes: {mtf_signal['buy_votes']:.1f}, "
                f"sell_votes: {mtf_signal['sell_votes']:.1f}, "
                f"strength: {mtf_signal['strength']:.1f}%, "
                f"passed_filters: {mtf_signal['passed_filters']})"
            )
            
            # Precompute price context for both accepted and rejected cases
            tf_signals = mtf_signal.get('timeframe_signals', {})
            m5_data = tf_signals.get('M5', {}).get('latest_data', {})
            atr = m5_data.get('atr', df_m5['close'].iloc[-1] * 0.001)
            current_price = df_m5['close'].iloc[-1]

            # Infer suggested direction from votes when needed
            suggested_direction = (
                'BUY' if mtf_signal.get('buy_votes', 0) > mtf_signal.get('sell_votes', 0)
                else ('SELL' if mtf_signal.get('sell_votes', 0) > mtf_signal.get('buy_votes', 0) else 'NEUTRAL')
            )

            # Compute hypothetical levels even for rejected signals (for debugging/reporting)
            # Use INSTRUMENT-SPECIFIC SL/TP from backtest results
            try:
                proposed_levels = InstrumentConfig.calculate_sltp(
                    instrument, 
                    current_price, 
                    suggested_direction if suggested_direction in ['BUY', 'SELL'] else 'BUY'
                )
                proposed_sl = proposed_levels['stop_loss']
                proposed_tp = proposed_levels['take_profit']
            except:
                # Fallback to current price if direction is invalid
                proposed_sl = current_price
                proposed_tp = current_price

            # Step 5: Check if filters passed (AlphaForge quality control)
            if not mtf_signal['passed_filters']:
                filter_reasons = mtf_signal['filter_results'].get('reasons', [])
                logger.warning(f"Signal rejected by quality filters: {filter_reasons}")
            # Step 6: Check signal strength (align with engine's threshold)
            if mtf_signal['strength'] < 25:  # Lowered to 25%
                logger.warning(f"Low strength: {mtf_signal['strength']:.1f}%")
                return {
                    'instrument': instrument,
                    'signal': 'SKIP',
                    'regime': regime.value,
                    'reason': 'Signal strength below 25%',
                    'mtf_signal': mtf_signal,
                    'tradeable': False,
                    # Price context for rejected signals
                    'last_price': current_price,
                    'suggested_direction': suggested_direction,
                    'proposed_entry': current_price,
                    'proposed_stop_loss': proposed_sl,
                    'proposed_take_profit': proposed_tp,
                    'timestamp': (timestamp or datetime.now()).isoformat()
                }
            
            if mtf_signal['agreement'] < self.min_agreement:
                logger.warning(f"Low agreement: {mtf_signal['agreement']:.1%}")
                return {
                    'instrument': instrument,
                    'signal': 'SKIP',
                    'regime': regime.value,
                    'reason': 'Poor timeframe agreement',
                    'mtf_signal': mtf_signal,
                    'tradeable': False,
                    'timestamp': (timestamp or datetime.now()).isoformat()
                }
            
            # Step 7: Calculate position sizing parameters
            position_multiplier = self.regime_detector.get_position_multiplier(regime)
            kelly_fraction = self.kelly_criterion.calculate_optimal_fraction()
            
            # Combine regime and Kelly sizing
            recommended_risk = kelly_fraction * position_multiplier
            
            # Step 8: Get session weight
            current_hour = datetime.utcnow().hour
            session_weight = self._get_session_weight(current_hour)
            
            # Step 9: Calculate final signal strength (already calculated by voting system)
            final_strength = mtf_signal['strength']
            
            # Step 10: Determine entry/exit levels (INSTRUMENT-SPECIFIC)
            # NEW: Using backtest-optimized distances for each instrument
            # XAU/USD: $4.50 SL / $10.50 TP (45/105 pips)
            # GBP/USD: 12 pips SL / 25 pips TP
            # USD/JPY: 17 pips SL / 52 pips TP
            
            sltp_levels = InstrumentConfig.calculate_sltp(
                instrument, 
                current_price, 
                mtf_signal['signal']
            )
            
            stop_loss = sltp_levels['stop_loss']
            take_profit = sltp_levels['take_profit']
            actual_rr_ratio = sltp_levels['rr_ratio']
            
            # Step 11: Build complete signal
            complete_signal = {
                'instrument': instrument,
                'signal': mtf_signal['signal'],
                'strength': final_strength,
                'buy_votes': mtf_signal['buy_votes'],
                'sell_votes': mtf_signal['sell_votes'],
                'confidence': mtf_signal['confidence'],
                'agreement': mtf_signal['agreement'],
                
                # Market regime
                'regime': regime.value,
                'regime_tradeable': should_trade,
                'position_multiplier': position_multiplier,
                
                # Multi-timeframe analysis
                'timeframe_signals': mtf_signal['timeframe_signals'],
                
                # AlphaForge Quality Filters
                'passed_filters': mtf_signal['passed_filters'],
                'filter_results': mtf_signal['filter_results'],
                
                # Position sizing
                'kelly_fraction': kelly_fraction,
                'recommended_risk': recommended_risk,
                
                # Entry/Exit levels
                'entry_price': current_price,
                'stop_loss': stop_loss,
                'take_profit': take_profit,
                'atr': atr,
                'risk_reward_ratio': actual_rr_ratio,
                'sl_pips': sltp_levels['sl_pips'],
                'tp_pips': sltp_levels['tp_pips'],
                
                # Session info
                'session_weight': session_weight,
                'trading_hour': current_hour,
                
                # Metadata
                'tradeable': True,
                'tradeable': True,
                'timestamp': (timestamp or datetime.now()).isoformat(),
                'candles_analyzed': {
                    tf: len(df) for tf, df in mtf_data.items()
                }
            }
            
            # Store in history
            self.signal_history[instrument].append(complete_signal)
            if len(self.signal_history[instrument]) > 100:
                self.signal_history[instrument] = self.signal_history[instrument][-100:]
            
            logger.info(f"Generated complete signal for {instrument}: {mtf_signal['signal']}")
            
            return complete_signal
            
        except Exception as e:
            logger.error(f"Error generating signal for {instrument}: {e}")
            return None
    
    def _get_session_weight(self, hour_gmt):
        """Get trading session weight based on GMT hour."""
        for session, config in self.trading_sessions.items():
            if config['start'] <= hour_gmt < config['end']:
                return config['weight']
        return 0.8  # Off-hours weight
    
    def update_trade_result(self, instrument, profit_loss, risk_amount):
        """
        Update Kelly Criterion with trade result.
        
        Args:
            instrument: Trading pair
            profit_loss: P&L in account currency
            risk_amount: Amount risked
        """
        self.kelly_criterion.add_trade_result(profit_loss, risk_amount)
        logger.info(
            f"Trade result added for {instrument}: "
            f"P/L=${profit_loss:.2f}, Risk=${risk_amount:.2f}"
        )
    
    def get_statistics(self):
        """Get performance statistics."""
        kelly_stats = self.kelly_criterion.get_statistics()
        regime_info = self.regime_detector.get_regime_info()
        
        return {
            'kelly_stats': kelly_stats,
            'regime_info': regime_info,
            'signal_counts': {
                instrument: len(history)
                for instrument, history in self.signal_history.items()
            }
        }


# Example usage
async def main():
    """Test enhanced signal generator."""
    api_key = os.getenv("OANDA_API_KEY", "YOUR_API_KEY_HERE")
    
    generator = EnhancedSignalGenerator(oanda_api_key=api_key)
    
    # Generate signals for all 3 pairs
    for instrument in ['GBP_USD', 'XAU_USD', 'USD_JPY']:
        print(f"\n{'='*60}")
        print(f"Generating signal for {instrument}...")
        print(f"{'='*60}")
        
        signal = await generator.generate_signal(instrument)
        
        if signal:
            print(f"\nSignal: {signal['signal']}")
            print(f"Strength: {signal.get('strength', 0):.1f}%")
            print(f"Buy Votes: {signal.get('buy_votes', 0):.1f}/6.0")
            print(f"Sell Votes: {signal.get('sell_votes', 0):.1f}/6.0")
            print(f"Confidence: {signal['confidence']:.2f}")
            print(f"Agreement: {signal['agreement']:.1%}")
            print(f"Regime: {signal['regime']}")
            print(f"Tradeable: {signal['tradeable']}")
            print(f"Passed Filters: {'✅ YES' if signal.get('passed_filters', False) else '❌ NO'}")
            
            if signal['tradeable']:
                print(f"\nEntry: {signal['entry_price']:.5f}")
                print(f"Stop Loss: {signal['stop_loss']:.5f}")
                print(f"Take Profit: {signal['take_profit']:.5f}")
                print(f"Recommended Risk: {signal['recommended_risk']:.2%}")
                
                if signal.get('filter_results'):
                    filters = signal['filter_results']
                    print(f"\nQuality Filters:")
                    print(f"  Volatility: {filters.get('atr_pct', 0):.2f}% - {'✅' if filters.get('volatility_ok') else '❌'}")
                    print(f"  ADX: {filters.get('adx', 0):.1f} - {'✅' if filters.get('adx_ok') else '❌'}")
            else:
                print(f"Reason: {signal.get('reason', 'N/A')}")
    
    # Get statistics
    print(f"\n{'='*60}")
    print("Performance Statistics")
    print(f"{'='*60}")
    stats = generator.get_statistics()
    print(f"\nKelly Stats:")
    print(f"  Win Rate: {stats['kelly_stats']['win_rate']:.2%}")
    print(f"  Recommended Risk: {stats['kelly_stats']['kelly_fraction']:.2%}")


if __name__ == "__main__":
    asyncio.run(main())

