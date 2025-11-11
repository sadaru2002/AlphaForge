"""
Daily Loss Limiter
Enforces daily loss limits and trading restrictions
"""

from datetime import date, datetime, timedelta
from typing import Dict, Any, Tuple, List
import logging

logger = logging.getLogger(__name__)

class DailyLossLimiter:
    """Enforce daily loss limits and trading restrictions"""
    
    def __init__(self, max_daily_loss_pct: float = 0.03, max_trades_per_day: int = 10,
                 max_consecutive_losses: int = 3, circuit_breaker_loss_pct: float = 0.05):
        """
        Initialize daily loss limiter
        
        Args:
            max_daily_loss_pct: Maximum daily loss as percentage of account (default 3%)
            max_trades_per_day: Maximum number of trades per day (default 10)
            max_consecutive_losses: Maximum consecutive losses before stopping (default 3)
            circuit_breaker_loss_pct: Circuit breaker loss percentage (default 5%)
        """
        self.max_daily_loss_pct = max_daily_loss_pct
        self.max_trades_per_day = max_trades_per_day
        self.max_consecutive_losses = max_consecutive_losses
        self.circuit_breaker_loss_pct = circuit_breaker_loss_pct
    
    def can_trade(self, account_balance: float, daily_stats: Dict[str, Any] = None) -> Tuple[bool, str]:
        """
        Check if trading is allowed today
        
        Args:
            account_balance: Current account balance
            daily_stats: Daily performance statistics
            
        Returns:
            (can_trade, reason)
        """
        try:
            today = date.today()
            
            if not daily_stats:
                return True, "No daily stats available - trading allowed"
            
            # Check daily loss limit
            daily_pnl = daily_stats.get('total_pnl', 0)
            if daily_pnl < 0:
                daily_loss_pct = abs(daily_pnl) / account_balance
                if daily_loss_pct >= self.max_daily_loss_pct:
                    return False, f"Daily loss limit reached: {daily_loss_pct*100:.1f}% (max: {self.max_daily_loss_pct*100}%)"
            
            # Check circuit breaker
            if daily_loss_pct >= self.circuit_breaker_loss_pct:
                return False, f"Circuit breaker activated: {daily_loss_pct*100:.1f}% loss (max: {self.circuit_breaker_loss_pct*100}%)"
            
            # Check max trades limit
            total_signals = daily_stats.get('total_signals', 0)
            if total_signals >= self.max_trades_per_day:
                return False, f"Max trades per day reached: {total_signals} (max: {self.max_trades_per_day})"
            
            # Check consecutive losses
            consecutive_losses = daily_stats.get('consecutive_losses', 0)
            if consecutive_losses >= self.max_consecutive_losses:
                return False, f"Max consecutive losses reached: {consecutive_losses} (max: {self.max_consecutive_losses})"
            
            # Check if we're in a drawdown period
            if self._is_in_drawdown(daily_stats):
                return False, "Account in drawdown - trading suspended"
            
            return True, "Trading allowed"
            
        except Exception as e:
            logger.error(f"Error checking trading permission: {e}")
            return False, f"Error checking trading permission: {str(e)}"
    
    def _is_in_drawdown(self, daily_stats: Dict[str, Any]) -> bool:
        """Check if account is in a significant drawdown"""
        try:
            max_drawdown = daily_stats.get('max_drawdown', 0)
            return max_drawdown >= 0.15  # 15% drawdown threshold
            
        except Exception as e:
            logger.error(f"Error checking drawdown: {e}")
            return False
    
    def calculate_risk_adjustment(self, account_balance: float, 
                                daily_stats: Dict[str, Any]) -> float:
        """
        Calculate risk adjustment factor based on daily performance
        
        Args:
            account_balance: Current account balance
            daily_stats: Daily performance statistics
            
        Returns:
            Risk adjustment factor (0.0 to 1.0)
        """
        try:
            if not daily_stats:
                return 1.0
            
            daily_pnl = daily_stats.get('total_pnl', 0)
            win_rate = daily_stats.get('win_rate', 0)
            consecutive_losses = daily_stats.get('consecutive_losses', 0)
            
            # Start with full risk
            risk_factor = 1.0
            
            # Reduce risk if losing money today
            if daily_pnl < 0:
                loss_pct = abs(daily_pnl) / account_balance
                if loss_pct > 0.01:  # More than 1% loss
                    risk_factor *= 0.5
                if loss_pct > 0.02:  # More than 2% loss
                    risk_factor *= 0.3
            
            # Reduce risk if win rate is low
            if win_rate < 0.5:  # Less than 50% win rate
                risk_factor *= 0.7
            if win_rate < 0.3:  # Less than 30% win rate
                risk_factor *= 0.4
            
            # Reduce risk for consecutive losses
            if consecutive_losses >= 2:
                risk_factor *= 0.6
            if consecutive_losses >= 3:
                risk_factor *= 0.3
            
            # Ensure minimum risk factor
            return max(risk_factor, 0.1)
            
        except Exception as e:
            logger.error(f"Error calculating risk adjustment: {e}")
            return 0.5  # Conservative default
    
    def get_daily_summary(self, daily_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get daily trading summary
        
        Args:
            daily_stats: Daily performance statistics
            
        Returns:
            Daily summary
        """
        try:
            if not daily_stats:
                return {
                    'status': 'NO_DATA',
                    'message': 'No daily statistics available',
                    'recommendation': 'TRADE_NORMALLY'
                }
            
            total_signals = daily_stats.get('total_signals', 0)
            signals_traded = daily_stats.get('signals_traded', 0)
            wins = daily_stats.get('wins', 0)
            losses = daily_stats.get('losses', 0)
            win_rate = daily_stats.get('win_rate', 0)
            total_pnl = daily_stats.get('total_pnl', 0)
            consecutive_losses = daily_stats.get('consecutive_losses', 0)
            
            # Determine status
            if total_pnl < 0 and abs(total_pnl) > 1000:  # Significant loss
                status = 'LOSSES'
                recommendation = 'REDUCE_RISK'
            elif consecutive_losses >= 3:
                status = 'STREAK'
                recommendation = 'PAUSE_TRADING'
            elif win_rate < 0.3:
                status = 'POOR_PERFORMANCE'
                recommendation = 'REDUCE_RISK'
            elif total_pnl > 0 and win_rate > 0.6:
                status = 'PROFITABLE'
                recommendation = 'TRADE_NORMALLY'
            else:
                status = 'NEUTRAL'
                recommendation = 'TRADE_CAUTIOUSLY'
            
            return {
                'status': status,
                'total_signals': total_signals,
                'signals_traded': signals_traded,
                'wins': wins,
                'losses': losses,
                'win_rate': win_rate,
                'total_pnl': total_pnl,
                'consecutive_losses': consecutive_losses,
                'recommendation': recommendation,
                'message': self._get_status_message(status, total_pnl, win_rate, consecutive_losses)
            }
            
        except Exception as e:
            logger.error(f"Error getting daily summary: {e}")
            return {
                'status': 'ERROR',
                'message': f'Error generating summary: {str(e)}',
                'recommendation': 'PAUSE_TRADING'
            }
    
    def _get_status_message(self, status: str, total_pnl: float, 
                          win_rate: float, consecutive_losses: int) -> str:
        """Get human-readable status message"""
        if status == 'LOSSES':
            return f"Significant losses today: ${total_pnl:.2f}. Consider reducing position sizes."
        elif status == 'STREAK':
            return f"Consecutive losses: {consecutive_losses}. Take a break from trading."
        elif status == 'POOR_PERFORMANCE':
            return f"Low win rate: {win_rate:.1%}. Review trading strategy."
        elif status == 'PROFITABLE':
            return f"Good performance: ${total_pnl:.2f} profit, {win_rate:.1%} win rate."
        else:
            return "Normal trading conditions."
    
    def should_reduce_risk(self, account_balance: float, 
                          daily_stats: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Determine if risk should be reduced
        
        Args:
            account_balance: Current account balance
            daily_stats: Daily performance statistics
            
        Returns:
            (should_reduce, reason)
        """
        try:
            if not daily_stats:
                return False, "No daily stats available"
            
            daily_pnl = daily_stats.get('total_pnl', 0)
            win_rate = daily_stats.get('win_rate', 0)
            consecutive_losses = daily_stats.get('consecutive_losses', 0)
            
            # Check for significant loss
            if daily_pnl < 0:
                loss_pct = abs(daily_pnl) / account_balance
                if loss_pct > 0.02:  # More than 2% loss
                    return True, f"Significant daily loss: {loss_pct*100:.1f}%"
            
            # Check for poor win rate
            if win_rate < 0.3 and daily_stats.get('total_signals', 0) >= 5:
                return True, f"Poor win rate: {win_rate:.1%}"
            
            # Check for consecutive losses
            if consecutive_losses >= 2:
                return True, f"Consecutive losses: {consecutive_losses}"
            
            return False, "Risk levels acceptable"
            
        except Exception as e:
            logger.error(f"Error checking risk reduction: {e}")
            return True, f"Error checking risk: {str(e)}"
    
    def get_trading_recommendation(self, account_balance: float, 
                                 daily_stats: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get comprehensive trading recommendation
        
        Args:
            account_balance: Current account balance
            daily_stats: Daily performance statistics
            
        Returns:
            Trading recommendation
        """
        try:
            can_trade, trade_reason = self.can_trade(account_balance, daily_stats)
            risk_adjustment = self.calculate_risk_adjustment(account_balance, daily_stats)
            should_reduce, reduce_reason = self.should_reduce_risk(account_balance, daily_stats)
            daily_summary = self.get_daily_summary(daily_stats)
            
            # Calculate recommended risk per trade
            base_risk = 0.01  # 1% base risk
            recommended_risk = base_risk * risk_adjustment
            
            return {
                'can_trade': can_trade,
                'trade_reason': trade_reason,
                'risk_adjustment_factor': risk_adjustment,
                'recommended_risk_per_trade': recommended_risk,
                'should_reduce_risk': should_reduce,
                'reduce_reason': reduce_reason,
                'daily_summary': daily_summary,
                'max_position_size': self._calculate_max_position_size(account_balance, recommended_risk),
                'trading_advice': self._get_trading_advice(can_trade, should_reduce, daily_summary['status'])
            }
            
        except Exception as e:
            logger.error(f"Error getting trading recommendation: {e}")
            return {
                'can_trade': False,
                'trade_reason': f"Error: {str(e)}",
                'risk_adjustment_factor': 0.1,
                'recommended_risk_per_trade': 0.001,
                'should_reduce_risk': True,
                'reduce_reason': f"Error: {str(e)}",
                'daily_summary': {'status': 'ERROR', 'message': str(e)},
                'max_position_size': 0.01,
                'trading_advice': 'PAUSE_TRADING'
            }
    
    def _calculate_max_position_size(self, account_balance: float, risk_per_trade: float) -> float:
        """Calculate maximum recommended position size"""
        try:
            # Conservative calculation: max 2% of account per trade
            max_risk = min(risk_per_trade, 0.02)
            max_position_value = account_balance * max_risk
            
            # Convert to lots (assuming $10 per pip for standard lot)
            max_lots = max_position_value / 1000  # Conservative estimate
            
            return max(max_lots, 0.01)  # Minimum 0.01 lots
            
        except Exception as e:
            logger.error(f"Error calculating max position size: {e}")
            return 0.01
    
    def _get_trading_advice(self, can_trade: bool, should_reduce: bool, status: str) -> str:
        """Get trading advice based on current conditions"""
        if not can_trade:
            return "PAUSE_TRADING"
        elif should_reduce:
            return "REDUCE_RISK"
        elif status == 'PROFITABLE':
            return "TRADE_NORMALLY"
        elif status == 'NEUTRAL':
            return "TRADE_CAUTIOUSLY"
        else:
            return "TRADE_CAREFULLY"




