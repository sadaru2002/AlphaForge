"""
Signal Validator
Validates signals before execution to ensure quality and safety
"""

from typing import Dict, Any, List, Tuple, Optional
import logging
from datetime import datetime, timezone
from ..config import settings

logger = logging.getLogger(__name__)

class SignalValidator:
    """Validate signals before execution"""
    
    def __init__(self, min_confidence: int = 70, min_rr_ratio: float = 2.0, 
                 max_daily_signals: int = 10):
        """
        Initialize signal validator
        
        Args:
            min_confidence: Minimum confidence score required
            min_rr_ratio: Minimum risk-reward ratio required
            max_daily_signals: Maximum signals per day
        """
        self.min_confidence = min_confidence
        self.min_rr_ratio = min_rr_ratio
        self.max_daily_signals = max_daily_signals
    
    def validate_signal(self, signal: Dict[str, Any], daily_stats: Dict[str, Any] = None) -> Tuple[bool, str, Dict[str, Any]]:
        """
        Comprehensive signal validation
        
        Args:
            signal: Signal to validate
            daily_stats: Daily performance statistics
            
        Returns:
            (is_valid, reason, validation_details)
        """
        try:
            validation_details = {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'checks_passed': 0,
                'checks_failed': 0,
                'warnings': [],
                'errors': []
            }
            
            # Basic structure validation
            is_valid, reason = self._validate_structure(signal)
            if not is_valid:
                validation_details['errors'].append(reason)
                validation_details['checks_failed'] += 1
                return False, reason, validation_details
            validation_details['checks_passed'] += 1
            
            # Confidence validation
            is_valid, reason = self._validate_confidence(signal)
            if not is_valid:
                validation_details['errors'].append(reason)
                validation_details['checks_failed'] += 1
                return False, reason, validation_details
            validation_details['checks_passed'] += 1
            
            # Risk-reward validation
            is_valid, reason = self._validate_risk_reward(signal)
            if not is_valid:
                validation_details['errors'].append(reason)
                validation_details['checks_failed'] += 1
                return False, reason, validation_details
            validation_details['checks_passed'] += 1
            
            # Setup quality validation
            is_valid, reason = self._validate_setup_quality(signal)
            if not is_valid:
                validation_details['warnings'].append(reason)
                validation_details['checks_failed'] += 1
                # Don't fail for setup quality, just warn
            else:
                validation_details['checks_passed'] += 1
            
            # Market conditions validation
            is_valid, reason = self._validate_market_conditions(signal)
            if not is_valid:
                validation_details['warnings'].append(reason)
                validation_details['checks_failed'] += 1
                # Don't fail for market conditions, just warn
            else:
                validation_details['checks_passed'] += 1
            
            # Daily limits validation
            is_valid, reason = self._validate_daily_limits(daily_stats)
            if not is_valid:
                validation_details['errors'].append(reason)
                validation_details['checks_failed'] += 1
                return False, reason, validation_details
            validation_details['checks_passed'] += 1
            
            # Price validation
            is_valid, reason = self._validate_prices(signal)
            if not is_valid:
                validation_details['errors'].append(reason)
                validation_details['checks_failed'] += 1
                return False, reason, validation_details
            validation_details['checks_passed'] += 1
            
            # Calculate overall score
            total_checks = validation_details['checks_passed'] + validation_details['checks_failed']
            validation_score = (validation_details['checks_passed'] / total_checks) * 100 if total_checks > 0 else 0
            validation_details['validation_score'] = round(validation_score, 1)
            
            if validation_details['checks_failed'] == 0:
                return True, "All validations passed", validation_details
            elif validation_details['errors']:
                return False, f"Validation failed: {validation_details['errors'][0]}", validation_details
            else:
                return True, f"Validation passed with {len(validation_details['warnings'])} warnings", validation_details
                
        except Exception as e:
            logger.error(f"Error validating signal: {e}")
            return False, f"Validation error: {str(e)}", {
                'timestamp': datetime.now(timezone.utc).isoformat(),
                'checks_passed': 0,
                'checks_failed': 1,
                'warnings': [],
                'errors': [f"Validation error: {str(e)}"],
                'validation_score': 0
            }
    
    def _validate_structure(self, signal: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate signal structure"""
        try:
            required_fields = [
                'setup_details',
                'trade_parameters',
                'risk_management',
                'market_assessment'
            ]
            
            for field in required_fields:
                if field not in signal:
                    return False, f"Missing required field: {field}"
            
            # Check setup_details
            setup_details = signal.get('setup_details', {})
            if 'direction' not in setup_details:
                return False, "Missing direction in setup_details"
            
            # Check trade_parameters
            trade_params = signal.get('trade_parameters', {})
            required_params = ['entry_price', 'stop_loss', 'take_profit_1']
            for param in required_params:
                if param not in trade_params or trade_params[param] is None:
                    return False, f"Missing required trade parameter: {param}"
            
            return True, "Structure valid"
            
        except Exception as e:
            return False, f"Structure validation error: {str(e)}"
    
    def _validate_confidence(self, signal: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate confidence score"""
        try:
            confidence = signal.get('risk_management', {}).get('confidence_score', 0)
            
            if confidence < self.min_confidence:
                return False, f"Confidence too low: {confidence}% (min: {self.min_confidence}%)"
            
            if confidence > 100:
                return False, f"Confidence too high: {confidence}% (max: 100%)"
            
            return True, f"Confidence valid: {confidence}%"
            
        except Exception as e:
            return False, f"Confidence validation error: {str(e)}"
    
    def _validate_risk_reward(self, signal: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate risk-reward ratio"""
        try:
            trade_params = signal.get('trade_parameters', {})
            entry_price = trade_params.get('entry_price', 0)
            stop_loss = trade_params.get('stop_loss', 0)
            take_profit_1 = trade_params.get('take_profit_1', 0)
            
            if not all([entry_price, stop_loss, take_profit_1]):
                return False, "Missing price data for R:R calculation"
            
            # Calculate risk and reward
            risk = abs(entry_price - stop_loss)
            reward = abs(take_profit_1 - entry_price)
            
            if risk == 0:
                return False, "Risk is zero - invalid setup"
            
            rr_ratio = reward / risk
            
            if rr_ratio < self.min_rr_ratio:
                return False, f"R:R ratio too low: {rr_ratio:.2f} (min: {self.min_rr_ratio})"
            
            return True, f"R:R ratio valid: {rr_ratio:.2f}"
            
        except Exception as e:
            return False, f"R:R validation error: {str(e)}"
    
    def _validate_setup_quality(self, signal: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate setup quality"""
        try:
            setup_details = signal.get('setup_details', {})
            grade = signal.get('risk_management', {}).get('setup_grade', 'D')
            
            # Check setup grade
            if grade not in ['A+', 'A', 'B', 'C', 'D']:
                return False, f"Invalid setup grade: {grade}"
            
            # Check confluence
            confluence = signal.get('confluence_analysis', {})
            total_confluence = confluence.get('total_confluence', 0)
            
            if total_confluence < 50:
                return False, f"Low confluence: {total_confluence}%"
            
            # Check confirmations
            confirmations = setup_details.get('confirmations_present', [])
            if len(confirmations) < 3:
                return False, f"Too few confirmations: {len(confirmations)}"
            
            return True, f"Setup quality valid: Grade {grade}, Confluence {total_confluence}%"
            
        except Exception as e:
            return False, f"Setup quality validation error: {str(e)}"
    
    def _validate_market_conditions(self, signal: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate market conditions"""
        try:
            market_assessment = signal.get('market_assessment', {})
            time_factors = signal.get('time_factors', {})
            
            # Check if market is tradeable
            if not market_assessment.get('tradeable', True):
                return False, "Market not tradeable"
            
            # Check session quality
            session_quality = time_factors.get('session_quality', 'POOR')
            if session_quality == 'POOR':
                return False, "Poor session quality"
            
            # Check if in kill zone
            in_kill_zone = time_factors.get('in_kill_zone', False)
            if not in_kill_zone:
                return False, "Not in kill zone"
            
            return True, f"Market conditions valid: {session_quality} session"
            
        except Exception as e:
            return False, f"Market conditions validation error: {str(e)}"
    
    def _validate_daily_limits(self, daily_stats: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate daily limits"""
        try:
            if not daily_stats:
                return True, "No daily stats - limits not applicable"
            
            total_signals = daily_stats.get('total_signals', 0)
            if total_signals >= self.max_daily_signals:
                return False, f"Daily signal limit reached: {total_signals}/{self.max_daily_signals}"
            
            return True, f"Daily limits valid: {total_signals}/{self.max_daily_signals} signals"
            
        except Exception as e:
            return False, f"Daily limits validation error: {str(e)}"
    
    def _validate_prices(self, signal: Dict[str, Any]) -> Tuple[bool, str]:
        """Validate price data"""
        try:
            trade_params = signal.get('trade_parameters', {})
            entry_price = trade_params.get('entry_price', 0)
            stop_loss = trade_params.get('stop_loss', 0)
            take_profit_1 = trade_params.get('take_profit_1', 0)
            
            # Check for valid prices
            if not all([entry_price > 0, stop_loss > 0, take_profit_1 > 0]):
                return False, "Invalid price data (zero or negative)"
            
            # Check price relationships
            direction = signal.get('setup_details', {}).get('direction', '')
            
            if direction == 'BUY':
                if stop_loss >= entry_price:
                    return False, "Invalid BUY setup: stop loss >= entry price"
                if take_profit_1 <= entry_price:
                    return False, "Invalid BUY setup: take profit <= entry price"
            
            elif direction == 'SELL':
                if stop_loss <= entry_price:
                    return False, "Invalid SELL setup: stop loss <= entry price"
                if take_profit_1 >= entry_price:
                    return False, "Invalid SELL setup: take profit >= entry price"
            
            return True, "Price data valid"
            
        except Exception as e:
            return False, f"Price validation error: {str(e)}"
    
    def validate_batch(self, signals: List[Dict[str, Any]], daily_stats: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Validate a batch of signals
        
        Args:
            signals: List of signals to validate
            daily_stats: Daily performance statistics
            
        Returns:
            Batch validation results
        """
        try:
            results = {
                'total_signals': len(signals),
                'valid_signals': 0,
                'invalid_signals': 0,
                'warnings': 0,
                'validation_details': []
            }
            
            for i, signal in enumerate(signals):
                is_valid, reason, details = self.validate_signal(signal, daily_stats)
                
                if is_valid:
                    results['valid_signals'] += 1
                else:
                    results['invalid_signals'] += 1
                
                if details.get('warnings'):
                    results['warnings'] += len(details['warnings'])
                
                results['validation_details'].append({
                    'signal_index': i,
                    'symbol': signal.get('metadata', {}).get('symbol', 'UNKNOWN'),
                    'is_valid': is_valid,
                    'reason': reason,
                    'validation_score': details.get('validation_score', 0)
                })
            
            results['validation_rate'] = (results['valid_signals'] / results['total_signals'] * 100) if results['total_signals'] > 0 else 0
            
            return results
            
        except Exception as e:
            logger.error(f"Error validating batch: {e}")
            return {
                'total_signals': 0,
                'valid_signals': 0,
                'invalid_signals': 0,
                'warnings': 0,
                'validation_details': [],
                'validation_rate': 0,
                'error': str(e)
            }
    
    def get_validation_summary(self, validation_results: Dict[str, Any]) -> str:
        """
        Get human-readable validation summary
        
        Args:
            validation_results: Results from validate_batch
            
        Returns:
            Summary string
        """
        try:
            total = validation_results['total_signals']
            valid = validation_results['valid_signals']
            invalid = validation_results['invalid_signals']
            warnings = validation_results['warnings']
            rate = validation_results['validation_rate']
            
            summary = f"Validation Summary: {valid}/{total} signals valid ({rate:.1f}%)"
            
            if invalid > 0:
                summary += f", {invalid} invalid"
            
            if warnings > 0:
                summary += f", {warnings} warnings"
            
            return summary
            
        except Exception as e:
            logger.error(f"Error generating validation summary: {e}")
            return f"Error generating summary: {str(e)}"




