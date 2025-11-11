"""
Signal Generator
Main signal generation pipeline that integrates all components
"""

from ..mt5_integration.mt5_client import MT5Client
from ..mt5_integration.data_fetcher import MultiTimeframeDataFetcher
from ..analysis.technical import TechnicalAnalyzer
from ..analysis.patterns import SMCPatternDetector
from ..analysis.volume_analysis import VolumeAnalyzer
from ..analysis.multi_timeframe import MultiTimeframeAnalyzer
from ..gemini.client import GeminiProClient
from ..gemini.analyzer import GeminiChartAnalyzer
from ..risk_management.position_sizing import PositionSizeCalculator
from ..risk_management.daily_limits import DailyLossLimiter
from ..risk_management.correlation import CorrelationChecker
from ..database.crud_safe import create_signal, get_today_signals, log_info, log_warning, log_error
from ..config import settings
from typing import Dict, Any, List, Optional, Tuple
import logging
from datetime import datetime, timezone
import asyncio

logger = logging.getLogger(__name__)

class SignalGenerator:
    """Complete signal generation pipeline"""
    
    def __init__(self, db_session):
        self.db = db_session
        self.mt5 = MT5Client(
            settings.MT5_LOGIN,
            settings.MT5_PASSWORD,
            settings.MT5_SERVER
        )
        self.data_fetcher = MultiTimeframeDataFetcher(self.mt5)
        self.gemini_client = GeminiProClient(settings.GEMINI_API_KEY)
        self.gemini_analyzer = GeminiChartAnalyzer(self.gemini_client, self.data_fetcher)
        self.position_calculator = PositionSizeCalculator(
            max_risk_per_trade=settings.RISK_PER_TRADE
        )
        self.daily_limiter = DailyLossLimiter(
            max_daily_loss_pct=settings.MAX_DAILY_RISK,
            max_trades_per_day=settings.MAX_SIGNALS_PER_DAY
        )
        self.correlation_checker = CorrelationChecker()
        
    async def generate_signal(self, symbol: str) -> Optional[Dict[str, Any]]:
        """
        Complete signal generation for one symbol
        ✅ Uses MT5 DATA ONLY - No OANDA data
        
        Args:
            symbol: Trading symbol to analyze
            
        Returns:
            Signal with all details or None
        """
        try:
            logger.info(f"═══ Starting analysis for {symbol} ═══")
            
            # ✅ CRITICAL: Verify MT5 connection before proceeding
            if not self.mt5.connected:
                logger.error("❌ CANNOT GENERATE SIGNAL - MT5 NOT CONNECTED")
                logger.error("   Attempting reconnection...")
                if not self.mt5.connect():
                    logger.error("   Reconnection failed")
                    return None
                logger.info("   ✅ MT5 reconnected successfully")
            
            logger.info(f"✅ Using MT5 data source for {symbol}")
            
            # Step 1: Check if trading is allowed today
            account_info = self.mt5.get_account_info()
            if not account_info:
                logger.error("❌ Failed to get MT5 account info")
                return None
            
            daily_stats = get_today_signals(self.db)
            can_trade, reason = self.daily_limiter.can_trade(account_info['balance'])
            
            if not can_trade:
                logger.warning(f"Trading not allowed: {reason}")
                return {
                    'symbol': symbol,
                    'signal_type': 'NO_TRADE',
                    'reason': reason,
                    'timestamp': datetime.now(timezone.utc).isoformat()
                }
            
            # Step 2: Get comprehensive analysis from Gemini
            logger.info("Getting comprehensive analysis from Gemini Pro...")
            analysis = self.gemini_analyzer.analyze_symbol(symbol)
            
            if not analysis:
                logger.error(f"Failed to get Gemini analysis for {symbol}")
                return None
            
            # Step 3: Validate signal
            logger.info("Validating signal...")
            is_valid, validation_reason = self._validate_signal(analysis, symbol)
            
            if not is_valid:
                logger.warning(f"Signal rejected: {validation_reason}")
                analysis['setup_details']['direction'] = 'NO_TRADE'
                analysis['rejection_reason'] = validation_reason
            
            # Step 4: Calculate position size if valid
            if is_valid and analysis['setup_details']['direction'] != 'NO_TRADE':
                stop_loss_pips = analysis['trade_parameters']['stop_loss_pips']
                position_info = self.position_calculator.calculate_lot_size(
                    account_info['balance'],
                    settings.RISK_PER_TRADE,
                    stop_loss_pips,
                    symbol
                )
                
                analysis['trade_parameters']['position_size'] = position_info['lot_size']
                analysis['trade_parameters']['risk_amount'] = position_info['risk_amount']
                analysis['trade_parameters']['max_loss'] = position_info['max_loss']
            
            # Step 5: Add metadata
            analysis['metadata'] = {
                'symbol': symbol,
                'generated_at': datetime.now(timezone.utc).isoformat(),
                'account_balance': account_info['balance'],
                'validation_passed': is_valid,
                'validation_reason': validation_reason if not is_valid else None
            }
            
            # Step 6: Log signal
            self._log_signal(analysis, symbol)
            
            if is_valid and analysis['setup_details']['direction'] != 'NO_TRADE':
                logger.info(f"✅ VALID SIGNAL: {symbol} {analysis['setup_details']['direction']} "
                          f"at {analysis['trade_parameters']['entry_price']}")
            else:
                logger.info(f"❌ NO TRADE: {symbol} - {validation_reason}")
            
            return analysis
            
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {e}")
            log_error(self.db, "SignalGenerator", f"Error generating signal for {symbol}: {str(e)}")
            return None
    
    def _validate_signal(self, analysis: Dict[str, Any], symbol: str) -> Tuple[bool, str]:
        """Validate signal quality and risk parameters"""
        try:
            # Check if setup detected
            if not analysis.get('setup_detected', False):
                return False, "No valid setup detected"
            
            # Check confidence score
            confidence = analysis.get('risk_management', {}).get('confidence_score', 0)
            if confidence < settings.MIN_CONFIDENCE:
                return False, f"Confidence too low: {confidence}% (min: {settings.MIN_CONFIDENCE}%)"
            
            # Check risk:reward ratio
            rr_ratio = analysis.get('trade_parameters', {}).get('take_profit_1_rr', 0)
            if rr_ratio < settings.MIN_RR_RATIO:
                return False, f"R:R too low: {rr_ratio} (min: {settings.MIN_RR_RATIO})"
            
            # Check if should trade
            if not analysis.get('risk_management', {}).get('should_trade', False):
                return False, "Gemini recommends NO_TRADE"
            
            # Check setup grade
            grade = analysis.get('risk_management', {}).get('setup_grade', 'D')
            if grade not in ['A+', 'A']:
                return False, f"Setup grade too low: {grade}"
            
            # Check correlation with open trades
            open_trades = self._get_open_trades()
            new_signal = {
                'symbol': symbol,
                'direction': analysis.get('setup_details', {}).get('direction', '')
            }
            
            is_safe, corr_reason = self.correlation_checker.check_correlation(open_trades, new_signal)
            if not is_safe:
                return False, f"Correlation conflict: {corr_reason}"
            
            # Check if we already have too many signals today
            today_signals = get_today_signals(self.db)
            if len(today_signals) >= settings.MAX_SIGNALS_PER_DAY:
                return False, f"Max signals per day reached: {len(today_signals)}"
            
            return True, "All validations passed"
            
        except Exception as e:
            logger.error(f"Error validating signal: {e}")
            return False, f"Validation error: {str(e)}"
    
    def _get_open_trades(self) -> List[Dict[str, Any]]:
        """Get currently open trades"""
        try:
            # This would typically query the database for open trades
            # For now, return empty list
            return []
        except Exception as e:
            logger.error(f"Error getting open trades: {e}")
            return []
    
    def _log_signal(self, analysis: Dict[str, Any], symbol: str):
        """Log signal to database"""
        try:
            signal_data = {
                'symbol': symbol,
                'timeframe': 'M15',
                'signal_type': analysis.get('setup_details', {}).get('direction', 'NO_TRADE'),
                'entry_price': analysis.get('trade_parameters', {}).get('entry_price'),
                'stop_loss': analysis.get('trade_parameters', {}).get('stop_loss'),
                'take_profit_1': analysis.get('trade_parameters', {}).get('take_profit_1'),
                'take_profit_2': analysis.get('trade_parameters', {}).get('take_profit_2'),
                'risk_reward_1': analysis.get('trade_parameters', {}).get('take_profit_1_rr'),
                'risk_reward_2': analysis.get('trade_parameters', {}).get('take_profit_2_rr'),
                'position_size': analysis.get('trade_parameters', {}).get('position_size'),
                'confidence_score': analysis.get('risk_management', {}).get('confidence_score'),
                'setup_type': analysis.get('setup_details', {}).get('primary_setup'),
                'strategy_used': analysis.get('setup_details', {}).get('strategy_combination'),
                'daily_bias': analysis.get('market_assessment', {}).get('bias'),
                'session': analysis.get('time_factors', {}).get('session_quality'),
                'market_structure': analysis.get('market_assessment', {}).get('overall_condition'),
                'gemini_reasoning': analysis.get('comprehensive_reasoning'),
                'confirmations': analysis.get('setup_details', {}).get('confirmations_present'),
                'risks': analysis.get('risk_management', {}).get('key_risks'),
                'was_traded': False
            }
            
            create_signal(self.db, **signal_data)
            log_info(self.db, "SignalGenerator", f"Created signal for {symbol}")
            
        except Exception as e:
            logger.error(f"Error logging signal: {e}")
            log_error(self.db, "SignalGenerator", f"Error logging signal for {symbol}: {str(e)}")
    
    async def generate_all_signals(self) -> List[Dict[str, Any]]:
        """
        Generate signals for all configured symbols
        
        Returns:
            List of all generated signals
        """
        try:
            logger.info("Starting signal generation for all symbols")
            signals = []
            
            for symbol in settings.symbols_list:
                try:
                    signal = await self.generate_signal(symbol)
                    if signal:
                        signals.append(signal)
                except Exception as e:
                    logger.error(f"Error generating signal for {symbol}: {e}")
                    continue
            
            logger.info(f"Generated {len(signals)} signals total")
            return signals
            
        except Exception as e:
            logger.error(f"Error generating all signals: {e}")
            return []
    
    def get_signal_summary(self, signals: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Get summary of generated signals
        
        Args:
            signals: List of generated signals
            
        Returns:
            Signal summary
        """
        try:
            total_signals = len(signals)
            valid_signals = [s for s in signals if s.get('setup_details', {}).get('direction') != 'NO_TRADE']
            buy_signals = [s for s in valid_signals if s.get('setup_details', {}).get('direction') == 'BUY']
            sell_signals = [s for s in valid_signals if s.get('setup_details', {}).get('direction') == 'SELL']
            
            avg_confidence = 0
            if valid_signals:
                confidences = [s.get('risk_management', {}).get('confidence_score', 0) for s in valid_signals]
                avg_confidence = sum(confidences) / len(confidences)
            
            return {
                'total_signals': total_signals,
                'valid_signals': len(valid_signals),
                'buy_signals': len(buy_signals),
                'sell_signals': len(sell_signals),
                'no_trade_signals': total_signals - len(valid_signals),
                'average_confidence': round(avg_confidence, 1),
                'symbols_analyzed': len(set(s.get('metadata', {}).get('symbol') for s in signals)),
                'generation_time': datetime.now(timezone.utc).isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error generating signal summary: {e}")
            return {
                'total_signals': 0,
                'valid_signals': 0,
                'buy_signals': 0,
                'sell_signals': 0,
                'no_trade_signals': 0,
                'average_confidence': 0,
                'symbols_analyzed': 0,
                'generation_time': datetime.now(timezone.utc).isoformat()
            }

