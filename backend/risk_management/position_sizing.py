"""
Position Sizing Calculator
Calculates appropriate position sizes based on risk parameters and account balance
"""

from typing import Dict, Any, Tuple
import logging

logger = logging.getLogger(__name__)

class PositionSizeCalculator:
    """Calculate proper position sizes based on risk parameters"""
    
    # Pip values per standard lot for different symbols
    PIP_VALUES = {
        'XAUUSD': 10.0,   # $10 per pip for 1 lot
        'GBPUSD': 10.0,   # $10 per pip
        'USDJPY': 9.09,   # ~$9 per pip (varies with JPY rate)
        'EURUSD': 10.0,   # $10 per pip
        'AUDUSD': 10.0,   # $10 per pip
        'USDCAD': 7.50,   # ~$7.50 per pip
        'NZDUSD': 10.0,   # $10 per pip
        'USDCHF': 9.50,   # ~$9.50 per pip
    }
    
    def __init__(self, max_risk_per_trade: float = 0.01, max_position_size: float = 0.1):
        """
        Initialize position size calculator
        
        Args:
            max_risk_per_trade: Maximum risk per trade as percentage of account (default 1%)
            max_position_size: Maximum position size as percentage of account (default 10%)
        """
        self.max_risk_per_trade = max_risk_per_trade
        self.max_position_size = max_position_size
    
    def calculate_lot_size(self, account_balance: float, risk_percentage: float, 
                          stop_loss_pips: float, symbol: str) -> Dict[str, Any]:
        """
        Calculate position size in lots
        
        Formula: Lot Size = (Account × Risk%) / (SL pips × Pip Value)
        
        Args:
            account_balance: Account equity
            risk_percentage: Risk per trade (e.g., 0.01 for 1%)
            stop_loss_pips: Stop loss distance in pips
            symbol: Trading symbol
            
        Returns:
            Dict with position size details
        """
        try:
            # Get pip value for symbol
            pip_value = self.PIP_VALUES.get(symbol, 10.0)
            
            # Calculate risk amount
            risk_amount = account_balance * risk_percentage
            
            # Calculate lot size
            lot_size = risk_amount / (stop_loss_pips * pip_value)
            
            # Round to 2 decimal places (0.01 lot minimum for most brokers)
            lot_size = round(lot_size, 2)
            
            # Apply minimum lot size
            if lot_size < 0.01:
                lot_size = 0.01
            
            # Validate position size
            is_valid, validation_message = self.validate_position_size(
                lot_size, symbol, account_balance
            )
            
            return {
                'lot_size': lot_size,
                'risk_amount': risk_amount,
                'risk_percentage': risk_percentage,
                'stop_loss_pips': stop_loss_pips,
                'pip_value': pip_value,
                'is_valid': is_valid,
                'validation_message': validation_message,
                'max_loss': lot_size * stop_loss_pips * pip_value
            }
            
        except Exception as e:
            logger.error(f"Error calculating lot size: {e}")
            return {
                'lot_size': 0.01,
                'risk_amount': 0,
                'risk_percentage': 0,
                'stop_loss_pips': 0,
                'pip_value': 10.0,
                'is_valid': False,
                'validation_message': f"Error: {str(e)}",
                'max_loss': 0
            }
    
    def validate_position_size(self, lot_size: float, symbol: str, 
                             account_balance: float) -> Tuple[bool, str]:
        """
        Validate if position size is reasonable
        
        Args:
            lot_size: Calculated lot size
            symbol: Trading symbol
            account_balance: Account balance
            
        Returns:
            (is_valid, message)
        """
        try:
            # Check minimum lot size
            if lot_size < 0.01:
                return False, "Position size below minimum (0.01 lots)"
            
            # Check maximum position size based on account balance
            max_lot_size = account_balance / 1000  # Max 1 lot per $1000
            if lot_size > max_lot_size:
                return False, f"Position size too large. Max: {max_lot_size:.2f} lots"
            
            # Check maximum position size percentage
            position_value = lot_size * 100000  # Standard lot value
            position_percentage = (position_value / account_balance) * 100
            
            if position_percentage > self.max_position_size * 100:
                return False, f"Position size exceeds {self.max_position_size*100}% of account"
            
            # Check if position size is reasonable for symbol
            pip_value = self.PIP_VALUES.get(symbol, 10.0)
            potential_loss_per_pip = lot_size * pip_value
            
            if potential_loss_per_pip > account_balance * 0.05:  # Max 5% per pip
                return False, "Position size too large - potential loss per pip exceeds 5% of account"
            
            return True, "Position size valid"
            
        except Exception as e:
            logger.error(f"Error validating position size: {e}")
            return False, f"Validation error: {str(e)}"
    
    def calculate_risk_reward_ratio(self, entry_price: float, stop_loss: float, 
                                  take_profit: float, symbol: str) -> Dict[str, Any]:
        """
        Calculate risk-reward ratio for a trade
        
        Args:
            entry_price: Entry price
            stop_loss: Stop loss price
            take_profit: Take profit price
            symbol: Trading symbol
            
        Returns:
            Dict with risk-reward details
        """
        try:
            # Calculate pip values
            pip_value = self.PIP_VALUES.get(symbol, 10.0)
            
            # Calculate distances in pips
            if 'JPY' in symbol:
                # For JPY pairs, pip is 0.01
                risk_pips = abs(entry_price - stop_loss) * 100
                reward_pips = abs(take_profit - entry_price) * 100
            else:
                # For other pairs, pip is 0.0001
                risk_pips = abs(entry_price - stop_loss) * 10000
                reward_pips = abs(take_profit - entry_price) * 10000
            
            # Calculate risk-reward ratio
            if risk_pips > 0:
                rr_ratio = reward_pips / risk_pips
            else:
                rr_ratio = 0
            
            # Calculate monetary values
            risk_amount = risk_pips * pip_value
            reward_amount = reward_pips * pip_value
            
            return {
                'risk_pips': round(risk_pips, 1),
                'reward_pips': round(reward_pips, 1),
                'risk_reward_ratio': round(rr_ratio, 2),
                'risk_amount': round(risk_amount, 2),
                'reward_amount': round(reward_amount, 2),
                'is_profitable': rr_ratio >= 1.0
            }
            
        except Exception as e:
            logger.error(f"Error calculating risk-reward ratio: {e}")
            return {
                'risk_pips': 0,
                'reward_pips': 0,
                'risk_reward_ratio': 0,
                'risk_amount': 0,
                'reward_amount': 0,
                'is_profitable': False
            }
    
    def calculate_max_position_size(self, account_balance: float, 
                                  available_margin: float) -> float:
        """
        Calculate maximum position size based on available margin
        
        Args:
            account_balance: Account balance
            available_margin: Available margin
            
        Returns:
            Maximum position size in lots
        """
        try:
            # Use 80% of available margin to be safe
            usable_margin = available_margin * 0.8
            
            # Calculate max position size (assuming 1:100 leverage)
            max_position_value = usable_margin * 100
            max_lots = max_position_value / 100000  # Standard lot value
            
            # Apply account balance limit
            balance_limit = account_balance / 1000  # Max 1 lot per $1000
            
            return min(max_lots, balance_limit)
            
        except Exception as e:
            logger.error(f"Error calculating max position size: {e}")
            return 0.01
    
    def adjust_position_for_volatility(self, base_lot_size: float, 
                                     current_atr: float, average_atr: float) -> float:
        """
        Adjust position size based on current volatility
        
        Args:
            base_lot_size: Base calculated lot size
            current_atr: Current ATR value
            average_atr: Average ATR value
            
        Returns:
            Adjusted lot size
        """
        try:
            if average_atr == 0:
                return base_lot_size
            
            # Calculate volatility ratio
            volatility_ratio = current_atr / average_atr
            
            # Adjust position size inversely to volatility
            if volatility_ratio > 1.5:  # High volatility
                adjustment_factor = 0.7
            elif volatility_ratio > 1.2:  # Above average volatility
                adjustment_factor = 0.8
            elif volatility_ratio < 0.7:  # Low volatility
                adjustment_factor = 1.2
            elif volatility_ratio < 0.5:  # Very low volatility
                adjustment_factor = 1.5
            else:  # Normal volatility
                adjustment_factor = 1.0
            
            adjusted_lot_size = base_lot_size * adjustment_factor
            
            # Ensure minimum lot size
            return max(adjusted_lot_size, 0.01)
            
        except Exception as e:
            logger.error(f"Error adjusting position for volatility: {e}")
            return base_lot_size
    
    def calculate_portfolio_risk(self, open_positions: list, account_balance: float) -> Dict[str, Any]:
        """
        Calculate overall portfolio risk
        
        Args:
            open_positions: List of open positions
            account_balance: Account balance
            
        Returns:
            Portfolio risk analysis
        """
        try:
            total_risk = 0
            total_exposure = 0
            position_count = len(open_positions)
            
            for position in open_positions:
                # Calculate position risk
                lot_size = position.get('lot_size', 0)
                stop_loss_pips = position.get('stop_loss_pips', 0)
                symbol = position.get('symbol', '')
                
                pip_value = self.PIP_VALUES.get(symbol, 10.0)
                position_risk = lot_size * stop_loss_pips * pip_value
                total_risk += position_risk
                
                # Calculate position exposure
                position_exposure = lot_size * 100000  # Standard lot value
                total_exposure += position_exposure
            
            # Calculate risk percentages
            risk_percentage = (total_risk / account_balance) * 100 if account_balance > 0 else 0
            exposure_percentage = (total_exposure / account_balance) * 100 if account_balance > 0 else 0
            
            return {
                'total_risk': round(total_risk, 2),
                'total_exposure': round(total_exposure, 2),
                'risk_percentage': round(risk_percentage, 2),
                'exposure_percentage': round(exposure_percentage, 2),
                'position_count': position_count,
                'avg_risk_per_position': round(total_risk / position_count, 2) if position_count > 0 else 0,
                'is_overexposed': exposure_percentage > 50,  # More than 50% of account
                'is_over_risked': risk_percentage > 10  # More than 10% risk
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio risk: {e}")
            return {
                'total_risk': 0,
                'total_exposure': 0,
                'risk_percentage': 0,
                'exposure_percentage': 0,
                'position_count': 0,
                'avg_risk_per_position': 0,
                'is_overexposed': False,
                'is_over_risked': False
            }




