"""
Kelly Criterion Position Sizing
Adapted from AlphaForge for AlphaForge trading system
"""
import numpy as np
import logging
from collections import deque

logger = logging.getLogger(__name__)

class KellyCriterion:
    """
    Kelly Criterion implementation for optimal position sizing.
    Dynamically adjusts position size based on recent performance.
    """

    def __init__(self, lookback_trades=50, kelly_fraction=0.25):
        """
        Initialize Kelly Criterion calculator.
        
        Args:
            lookback_trades: Number of recent trades to analyze
            kelly_fraction: Fraction of Kelly to use (0.25 = 25% Kelly for safety)
        """
        self.lookback_trades = lookback_trades
        self.kelly_fraction = kelly_fraction
        self.trade_results = deque(maxlen=lookback_trades)
        
        # Default risk until enough trade data
        self.default_risk = 0.02  # 2%
        self.min_risk = 0.005     # 0.5%
        self.max_risk = 0.03      # 3%

    def add_trade_result(self, profit_loss, risk_amount):
        """
        Add a completed trade result for Kelly calculation.
        
        Args:
            profit_loss: P&L in account currency (positive = win, negative = loss)
            risk_amount: Amount risked on the trade
        """
        win = 1 if profit_loss > 0 else 0
        win_amount = abs(profit_loss) if profit_loss > 0 else 0
        loss_amount = abs(profit_loss) if profit_loss < 0 else risk_amount

        self.trade_results.append({
            'win': win,
            'profit': profit_loss,
            'win_amount': win_amount,
            'loss_amount': loss_amount,
            'risk': risk_amount
        })
        
        logger.debug(f"Trade added - Win: {win}, P/L: {profit_loss:.2f}, Risk: {risk_amount:.2f}")

    def calculate_optimal_fraction(self):
        """
        Calculate optimal betting fraction using Kelly Criterion.
        
        Formula: f = (p * b - q) / b
        where:
            p = win probability
            b = win/loss ratio
            q = loss probability (1 - p)
            f = optimal fraction to bet
        
        Returns:
            float: Optimal position size as fraction of account (0.005 to 0.03)
        """
        # Need minimum trades for reliable calculation
        if len(self.trade_results) < 20:
            logger.debug(f"Only {len(self.trade_results)} trades, using default risk")
            return self.default_risk

        # Calculate win rate
        wins = sum(t['win'] for t in self.trade_results)
        total = len(self.trade_results)

        # Edge cases
        if wins == 0:
            # All losses - reduce risk dramatically
            logger.warning("No winning trades in lookback period, reducing risk")
            return self.min_risk
        
        if wins == total:
            # All wins - still be conservative
            logger.info("100% win rate in lookback, using max risk")
            return self.max_risk

        # Calculate probabilities
        p = wins / total  # Win probability
        q = 1 - p         # Loss probability

        # Calculate average win/loss amounts
        winning_trades = [t for t in self.trade_results if t['win']]
        losing_trades = [t for t in self.trade_results if not t['win']]
        
        avg_win = np.mean([t['win_amount'] for t in winning_trades]) if winning_trades else 0
        avg_loss = np.mean([t['loss_amount'] for t in losing_trades]) if losing_trades else 1
        
        # Avoid division by zero
        if avg_loss == 0:
            logger.warning("Average loss is 0, using default risk")
            return self.default_risk

        # Win/loss ratio
        b = avg_win / avg_loss

        # Kelly formula: f = (p * b - q) / b
        kelly_full = (p * b - q) / b

        # Apply safety fraction (typically 25% of full Kelly)
        kelly_safe = kelly_full * self.kelly_fraction

        # Bound between min and max risk
        kelly_optimal = max(self.min_risk, min(self.max_risk, kelly_safe))

        logger.info(
            f"Kelly Calculation - WR: {p:.2%}, Avg W/L: {b:.2f}, "
            f"Full Kelly: {kelly_full:.2%}, Safe Kelly: {kelly_optimal:.2%}"
        )

        return kelly_optimal

    def get_position_size(self, account_balance, stop_loss_distance, instrument='GBP_USD'):
        """
        Calculate position size based on Kelly Criterion.
        
        Args:
            account_balance: Current account balance
            stop_loss_distance: Distance to stop loss in pips
            instrument: Trading pair (for pip value calculation)
        
        Returns:
            int: Position size in units
        """
        # Get optimal risk fraction
        risk_fraction = self.calculate_optimal_fraction()
        
        # Calculate risk amount
        risk_amount = account_balance * risk_fraction
        
        # Calculate pip value based on instrument
        pip_values = {
            'GBP_USD': 0.0001,
            'XAU_USD': 0.01,    # Gold
            'USD_JPY': 0.01
        }
        pip_value = pip_values.get(instrument, 0.0001)
        
        # Calculate position size
        # Position size = Risk amount / (Stop loss distance × Pip value)
        position_size = risk_amount / (stop_loss_distance * pip_value)
        
        logger.info(
            f"Position Sizing - Balance: ${account_balance:.2f}, "
            f"Risk: {risk_fraction:.2%} (${risk_amount:.2f}), "
            f"SL: {stop_loss_distance} pips, Size: {int(position_size)} units"
        )
        
        return int(position_size)

    def get_statistics(self):
        """
        Get Kelly Criterion statistics.
        
        Returns:
            dict: Performance statistics
        """
        if len(self.trade_results) == 0:
            return {
                'trade_count': 0,
                'win_rate': 0,
                'avg_win': 0,
                'avg_loss': 0,
                'win_loss_ratio': 0,
                'kelly_fraction': self.default_risk
            }

        wins = sum(t['win'] for t in self.trade_results)
        total = len(self.trade_results)
        win_rate = wins / total if total > 0 else 0

        winning_trades = [t for t in self.trade_results if t['win']]
        losing_trades = [t for t in self.trade_results if not t['win']]

        avg_win = np.mean([t['profit'] for t in winning_trades]) if winning_trades else 0
        avg_loss = abs(np.mean([t['profit'] for t in losing_trades])) if losing_trades else 0
        
        win_loss_ratio = avg_win / avg_loss if avg_loss > 0 else 0

        return {
            'trade_count': total,
            'win_count': wins,
            'loss_count': total - wins,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'win_loss_ratio': win_loss_ratio,
            'kelly_fraction': self.calculate_optimal_fraction(),
            'total_profit': sum(t['profit'] for t in self.trade_results)
        }


# Example usage
if __name__ == "__main__":
    # Test Kelly Criterion
    kelly = KellyCriterion(lookback_trades=50, kelly_fraction=0.25)
    
    # Simulate 30 trades
    np.random.seed(42)
    for i in range(30):
        # Simulate 45% win rate
        is_win = np.random.random() < 0.45
        
        if is_win:
            # Win 2R (2:1 risk/reward)
            profit_loss = 200
            risk = 100
        else:
            # Lose 1R
            profit_loss = -100
            risk = 100
        
        kelly.add_trade_result(profit_loss, risk)
        
        if i >= 19:  # After 20 trades
            optimal_risk = kelly.calculate_optimal_fraction()
            print(f"Trade {i+1}: Optimal risk = {optimal_risk:.2%}")
    
    # Get statistics
    stats = kelly.get_statistics()
    print("\nKelly Statistics:")
    print(f"  Win Rate: {stats['win_rate']:.2%}")
    print(f"  Avg Win: ${stats['avg_win']:.2f}")
    print(f"  Avg Loss: ${stats['avg_loss']:.2f}")
    print(f"  Win/Loss Ratio: {stats['win_loss_ratio']:.2f}")
    print(f"  Recommended Risk: {stats['kelly_fraction']:.2%}")
    
    # Calculate position size for GBP/USD
    position = kelly.get_position_size(
        account_balance=10000,
        stop_loss_distance=50,  # 50 pips
        instrument='GBP_USD'
    )
    print(f"\nPosition Size (GBP/USD, 50 pip SL): {position} units")
