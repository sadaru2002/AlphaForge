"""
Trade Outcome Calculator - Determines win/loss and calculates P&L
"""
from datetime import datetime
from typing import Dict, Optional, Tuple
from .signal_models import TradeOutcome


class TradeCalculator:
    """
    Calculates trade outcomes, P&L, and performance metrics
    """
    
    @staticmethod
    def calculate_pips(entry_price: float, exit_price: float, direction: str) -> float:
        """
        Calculate pips gained/lost
        Args:
            entry_price: Entry price
            exit_price: Exit price
            direction: 'BUY' or 'SELL'
        Returns:
            Pips captured (positive for profit, negative for loss)
        """
        price_diff = exit_price - entry_price
        pips = price_diff * 10000  # Convert to pips (for forex)
        
        # For SELL trades, inverse the pips
        if direction == 'SELL':
            pips = -pips
        
        return round(pips, 1)
    
    @staticmethod
    def calculate_pnl(
        entry_price: float,
        exit_price: float,
        direction: str,
        position_size: float,
        pip_value: float = 10.0  # Standard lot pip value
    ) -> float:
        """
        Calculate profit/loss in dollars
        Args:
            entry_price: Entry price
            exit_price: Exit price
            direction: 'BUY' or 'SELL'
            position_size: Position size in lots
            pip_value: Value per pip (default $10 for standard lot)
        Returns:
            P&L in dollars
        """
        pips = TradeCalculator.calculate_pips(entry_price, exit_price, direction)
        pnl = pips * pip_value * position_size
        return round(pnl, 2)
    
    @staticmethod
    def determine_outcome(
        entry_price: float,
        exit_price: float,
        stop_loss: float,
        take_profit: float,
        direction: str,
        tolerance: float = 0.0001  # 1 pip tolerance
    ) -> Tuple[TradeOutcome, str]:
        """
        Determine if trade was a win, loss, or breakeven
        Args:
            entry_price: Entry price
            exit_price: Exit price
            stop_loss: Stop loss level
            take_profit: Take profit level
            direction: 'BUY' or 'SELL'
            tolerance: Price tolerance for determining exact hits
        Returns:
            Tuple of (TradeOutcome, reason_string)
        """
        # Check if hit stop loss
        if direction == 'BUY':
            if exit_price <= stop_loss + tolerance:
                return TradeOutcome.LOSS, f"Hit stop loss at {exit_price}"
            elif exit_price >= take_profit - tolerance:
                return TradeOutcome.WIN, f"Hit take profit at {exit_price}"
            elif abs(exit_price - entry_price) <= tolerance:
                return TradeOutcome.BREAKEVEN, f"Closed at breakeven {exit_price}"
            else:
                # Manual close
                if exit_price > entry_price:
                    return TradeOutcome.WIN, f"Manual close in profit at {exit_price}"
                else:
                    return TradeOutcome.LOSS, f"Manual close in loss at {exit_price}"
        
        else:  # SELL
            if exit_price >= stop_loss - tolerance:
                return TradeOutcome.LOSS, f"Hit stop loss at {exit_price}"
            elif exit_price <= take_profit + tolerance:
                return TradeOutcome.WIN, f"Hit take profit at {exit_price}"
            elif abs(exit_price - entry_price) <= tolerance:
                return TradeOutcome.BREAKEVEN, f"Closed at breakeven {exit_price}"
            else:
                # Manual close
                if exit_price < entry_price:
                    return TradeOutcome.WIN, f"Manual close in profit at {exit_price}"
                else:
                    return TradeOutcome.LOSS, f"Manual close in loss at {exit_price}"
    
    @staticmethod
    def calculate_risk_reward(
        entry_price: float,
        stop_loss: float,
        take_profit: float,
        direction: str
    ) -> float:
        """
        Calculate risk:reward ratio
        Returns:
            Risk reward ratio (e.g., 2.0 means 1:2)
        """
        if direction == 'BUY':
            risk = entry_price - stop_loss
            reward = take_profit - entry_price
        else:  # SELL
            risk = stop_loss - entry_price
            reward = entry_price - take_profit
        
        if risk <= 0:
            return 0
        
        rr_ratio = reward / risk
        return round(rr_ratio, 2)
    
    @staticmethod
    def calculate_position_size(
        account_balance: float,
        risk_percent: float,
        entry_price: float,
        stop_loss: float,
        pip_value: float = 10.0
    ) -> float:
        """
        Calculate optimal position size based on risk
        Args:
            account_balance: Account balance in dollars
            risk_percent: Percentage of account to risk (e.g., 1.0 for 1%)
            entry_price: Entry price
            stop_loss: Stop loss price
            pip_value: Value per pip
        Returns:
            Position size in lots
        """
        risk_amount = account_balance * (risk_percent / 100)
        pips_to_sl = abs(entry_price - stop_loss) * 10000
        
        if pips_to_sl == 0:
            return 0
        
        position_size = risk_amount / (pips_to_sl * pip_value)
        return round(position_size, 2)
    
    @staticmethod
    def calculate_mae_mfe(
        entry_price: float,
        highest_price: float,
        lowest_price: float,
        direction: str
    ) -> Tuple[float, float]:
        """
        Calculate Maximum Adverse Excursion and Maximum Favorable Excursion
        Args:
            entry_price: Entry price
            highest_price: Highest price during trade
            lowest_price: Lowest price during trade
            direction: 'BUY' or 'SELL'
        Returns:
            Tuple of (MAE in pips, MFE in pips)
        """
        if direction == 'BUY':
            mae = (entry_price - lowest_price) * 10000  # Worst drawdown
            mfe = (highest_price - entry_price) * 10000  # Best profit
        else:  # SELL
            mae = (highest_price - entry_price) * 10000  # Worst drawdown
            mfe = (entry_price - lowest_price) * 10000  # Best profit
        
        return round(mae, 1), round(mfe, 1)
    
    @staticmethod
    def calculate_trade_quality_score(
        actual_rr: float,
        planned_rr: float,
        duration_hours: float,
        slippage_pips: float,
        confidence_score: float
    ) -> Dict[str, any]:
        """
        Calculate a quality score for the trade execution
        Args:
            actual_rr: Actual risk:reward achieved
            planned_rr: Planned risk:reward
            duration_hours: How long trade was open
            slippage_pips: Entry slippage
            confidence_score: Original signal confidence
        Returns:
            Dictionary with quality metrics
        """
        # RR execution score (0-100)
        rr_execution = min(100, (actual_rr / planned_rr) * 100) if planned_rr > 0 else 0
        
        # Duration score (prefer trades that close within 24 hours)
        if duration_hours <= 24:
            duration_score = 100
        elif duration_hours <= 48:
            duration_score = 75
        elif duration_hours <= 72:
            duration_score = 50
        else:
            duration_score = 25
        
        # Slippage score (penalize high slippage)
        if slippage_pips <= 1:
            slippage_score = 100
        elif slippage_pips <= 2:
            slippage_score = 80
        elif slippage_pips <= 3:
            slippage_score = 60
        else:
            slippage_score = max(0, 100 - (slippage_pips * 10))
        
        # Overall quality score
        quality_score = (
            rr_execution * 0.4 +
            duration_score * 0.2 +
            slippage_score * 0.2 +
            confidence_score * 0.2
        )
        
        return {
            'overall_quality': round(quality_score, 1),
            'rr_execution': round(rr_execution, 1),
            'duration_score': round(duration_score, 1),
            'slippage_score': round(slippage_score, 1),
            'confidence_score': round(confidence_score, 1),
            'grade': TradeCalculator._get_grade(quality_score)
        }
    
    @staticmethod
    def _get_grade(score: float) -> str:
        """Convert quality score to letter grade"""
        if score >= 90:
            return 'A+'
        elif score >= 85:
            return 'A'
        elif score >= 80:
            return 'A-'
        elif score >= 75:
            return 'B+'
        elif score >= 70:
            return 'B'
        elif score >= 65:
            return 'B-'
        elif score >= 60:
            return 'C+'
        elif score >= 55:
            return 'C'
        elif score >= 50:
            return 'C-'
        else:
            return 'D'
    
    @staticmethod
    def analyze_trade(signal_data: Dict) -> Dict:
        """
        Comprehensive trade analysis
        Args:
            signal_data: Dictionary with signal and trade data
        Returns:
            Complete analysis dictionary
        """
        entry = signal_data.get('entry_price', signal_data.get('entry'))
        exit_price = signal_data.get('exit_price')
        stop_loss = signal_data.get('stop_loss')
        take_profit = signal_data.get('tp1')
        direction = signal_data.get('direction')
        position_size = signal_data.get('position_size', 0.1)
        
        if not all([entry, exit_price, stop_loss, take_profit, direction]):
            return {'error': 'Missing required data'}
        
        # Calculate pips and P&L
        pips = TradeCalculator.calculate_pips(entry, exit_price, direction)
        pnl = TradeCalculator.calculate_pnl(entry, exit_price, direction, position_size)
        
        # Determine outcome
        outcome, reason = TradeCalculator.determine_outcome(
            entry, exit_price, stop_loss, take_profit, direction
        )
        
        # Calculate R:R
        planned_rr = TradeCalculator.calculate_risk_reward(entry, stop_loss, take_profit, direction)
        
        # Calculate actual R:R achieved
        if direction == 'BUY':
            risk_pips = (entry - stop_loss) * 10000
            reward_pips = pips
        else:
            risk_pips = (stop_loss - entry) * 10000
            reward_pips = pips
        
        actual_rr = reward_pips / risk_pips if risk_pips > 0 else 0
        
        return {
            'outcome': outcome.value,
            'reason': reason,
            'pips_captured': pips,
            'pnl': pnl,
            'planned_rr': planned_rr,
            'actual_rr': round(actual_rr, 2),
            'rr_efficiency': round((actual_rr / planned_rr * 100), 1) if planned_rr > 0 else 0,
        }
