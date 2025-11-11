"""
Correlation Checker
Checks currency pair correlation to avoid overexposure
"""

from typing import Dict, List, Tuple, Any
import logging
import numpy as np
from datetime import datetime, timedelta

logger = logging.getLogger(__name__)

class CorrelationChecker:
    """Check currency pair correlation to avoid overexposure"""
    
    # Static correlation matrix (simplified - in production, calculate dynamically)
    CORRELATIONS = {
        ('GBPUSD', 'EURUSD'): 0.85,      # Highly correlated
        ('GBPUSD', 'USDJPY'): -0.70,     # Negatively correlated
        ('GBPUSD', 'XAUUSD'): 0.40,      # Weakly correlated
        ('EURUSD', 'USDJPY'): -0.75,     # Negatively correlated
        ('EURUSD', 'XAUUSD'): 0.35,      # Weakly correlated
        ('USDJPY', 'XAUUSD'): -0.60,     # Gold inverse to USD strength
        ('AUDUSD', 'NZDUSD'): 0.80,      # Highly correlated
        ('AUDUSD', 'XAUUSD'): 0.50,      # Moderately correlated
        ('USDCAD', 'USDJPY'): 0.30,      # Weakly correlated
        ('USDCHF', 'EURUSD'): -0.90,     # Highly negatively correlated
    }
    
    def __init__(self, max_correlation: float = 0.7, max_negative_correlation: float = -0.7):
        """
        Initialize correlation checker
        
        Args:
            max_correlation: Maximum allowed positive correlation
            max_negative_correlation: Maximum allowed negative correlation
        """
        self.max_correlation = max_correlation
        self.max_negative_correlation = max_negative_correlation
    
    def check_correlation(self, open_trades: List[Dict], new_signal: Dict) -> Tuple[bool, str]:
        """
        Check if new signal conflicts with open positions
        
        Args:
            open_trades: List of currently open trades
            new_signal: New signal to validate
            
        Returns:
            (is_safe, reason)
        """
        try:
            new_symbol = new_signal.get('symbol', '')
            new_direction = new_signal.get('direction', '')
            
            if not new_symbol or not new_direction:
                return False, "Invalid signal data"
            
            # Check if we already have a position on this symbol
            for trade in open_trades:
                trade_symbol = trade.get('symbol', '')
                trade_direction = trade.get('direction', '')
                
                if not trade_symbol or not trade_direction:
                    continue
                
                # Same symbol check
                if new_symbol == trade_symbol:
                    if new_direction == trade_direction:
                        return False, f"Already have {trade_direction} position on {trade_symbol}"
                    else:
                        return False, f"Conflicting direction: trying to {new_direction} while holding {trade_direction} on {trade_symbol}"
                
                # Correlation check
                correlation = self.get_correlation(new_symbol, trade_symbol)
                
                if correlation is None:
                    continue  # No correlation data available
                
                # High positive correlation + same direction = overexposure
                if correlation > self.max_correlation and new_direction == trade_direction:
                    return False, f"High positive correlation ({correlation:.2f}) with {trade_symbol} {trade_direction} trade"
                
                # High negative correlation + opposite direction = similar exposure
                if correlation < self.max_negative_correlation and new_direction != trade_direction:
                    return False, f"High negative correlation ({correlation:.2f}) creates similar exposure to {trade_symbol} {trade_direction} trade"
            
            return True, "No correlation conflicts"
            
        except Exception as e:
            logger.error(f"Error checking correlation: {e}")
            return False, f"Error checking correlation: {str(e)}"
    
    def get_correlation(self, symbol1: str, symbol2: str) -> float:
        """
        Get correlation between two symbols
        
        Args:
            symbol1: First symbol
            symbol2: Second symbol
            
        Returns:
            Correlation coefficient or None if not available
        """
        try:
            # Check both directions
            pair1 = (symbol1, symbol2)
            pair2 = (symbol2, symbol1)
            
            if pair1 in self.CORRELATIONS:
                return self.CORRELATIONS[pair1]
            elif pair2 in self.CORRELATIONS:
                return self.CORRELATIONS[pair2]
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error getting correlation: {e}")
            return None
    
    def calculate_portfolio_correlation(self, open_trades: List[Dict]) -> Dict[str, Any]:
        """
        Calculate overall portfolio correlation
        
        Args:
            open_trades: List of open trades
            
        Returns:
            Portfolio correlation analysis
        """
        try:
            if len(open_trades) < 2:
                return {
                    'average_correlation': 0.0,
                    'max_correlation': 0.0,
                    'correlation_pairs': [],
                    'risk_level': 'LOW',
                    'recommendation': 'SAFE'
                }
            
            correlations = []
            correlation_pairs = []
            
            # Calculate all pairwise correlations
            for i, trade1 in enumerate(open_trades):
                for j, trade2 in enumerate(open_trades[i+1:], i+1):
                    symbol1 = trade1.get('symbol', '')
                    symbol2 = trade2.get('symbol', '')
                    direction1 = trade1.get('direction', '')
                    direction2 = trade2.get('direction', '')
                    
                    if not all([symbol1, symbol2, direction1, direction2]):
                        continue
                    
                    correlation = self.get_correlation(symbol1, symbol2)
                    if correlation is not None:
                        # Adjust for direction
                        if direction1 != direction2:
                            correlation = -correlation
                        
                        correlations.append(abs(correlation))
                        correlation_pairs.append({
                            'pair': f"{symbol1}-{symbol2}",
                            'correlation': correlation,
                            'direction1': direction1,
                            'direction2': direction2
                        })
            
            if not correlations:
                return {
                    'average_correlation': 0.0,
                    'max_correlation': 0.0,
                    'correlation_pairs': [],
                    'risk_level': 'LOW',
                    'recommendation': 'SAFE'
                }
            
            # Calculate statistics
            avg_correlation = np.mean(correlations)
            max_correlation = np.max(correlations)
            
            # Determine risk level
            if max_correlation > 0.8:
                risk_level = 'HIGH'
                recommendation = 'REDUCE_EXPOSURE'
            elif max_correlation > 0.6:
                risk_level = 'MEDIUM'
                recommendation = 'MONITOR_CLOSELY'
            else:
                risk_level = 'LOW'
                recommendation = 'SAFE'
            
            return {
                'average_correlation': round(avg_correlation, 3),
                'max_correlation': round(max_correlation, 3),
                'correlation_pairs': correlation_pairs,
                'risk_level': risk_level,
                'recommendation': recommendation,
                'total_pairs': len(correlation_pairs)
            }
            
        except Exception as e:
            logger.error(f"Error calculating portfolio correlation: {e}")
            return {
                'average_correlation': 0.0,
                'max_correlation': 0.0,
                'correlation_pairs': [],
                'risk_level': 'UNKNOWN',
                'recommendation': 'ERROR'
            }
    
    def get_safe_symbols(self, open_trades: List[Dict], available_symbols: List[str]) -> List[str]:
        """
        Get symbols that are safe to trade based on current positions
        
        Args:
            open_trades: List of open trades
            available_symbols: List of available symbols
            
        Returns:
            List of safe symbols to trade
        """
        try:
            safe_symbols = []
            
            for symbol in available_symbols:
                is_safe = True
                
                for trade in open_trades:
                    trade_symbol = trade.get('symbol', '')
                    if not trade_symbol:
                        continue
                    
                    correlation = self.get_correlation(symbol, trade_symbol)
                    if correlation is None:
                        continue
                    
                    # Check if correlation is too high
                    if abs(correlation) > self.max_correlation:
                        is_safe = False
                        break
                
                if is_safe:
                    safe_symbols.append(symbol)
            
            return safe_symbols
            
        except Exception as e:
            logger.error(f"Error getting safe symbols: {e}")
            return available_symbols  # Return all symbols if error
    
    def analyze_correlation_risk(self, open_trades: List[Dict]) -> Dict[str, Any]:
        """
        Analyze correlation risk in current portfolio
        
        Args:
            open_trades: List of open trades
            
        Returns:
            Correlation risk analysis
        """
        try:
            if not open_trades:
                return {
                    'risk_score': 0,
                    'risk_level': 'LOW',
                    'recommendation': 'SAFE',
                    'details': 'No open trades'
                }
            
            portfolio_corr = self.calculate_portfolio_correlation(open_trades)
            
            # Calculate risk score (0-100)
            risk_score = int(portfolio_corr['max_correlation'] * 100)
            
            # Determine risk level
            if risk_score >= 80:
                risk_level = 'HIGH'
                recommendation = 'REDUCE_POSITIONS'
            elif risk_score >= 60:
                risk_level = 'MEDIUM'
                recommendation = 'MONITOR_CLOSELY'
            else:
                risk_level = 'LOW'
                recommendation = 'SAFE'
            
            # Get problematic pairs
            problematic_pairs = [
                pair for pair in portfolio_corr['correlation_pairs']
                if abs(pair['correlation']) > self.max_correlation
            ]
            
            return {
                'risk_score': risk_score,
                'risk_level': risk_level,
                'recommendation': recommendation,
                'max_correlation': portfolio_corr['max_correlation'],
                'average_correlation': portfolio_corr['average_correlation'],
                'problematic_pairs': problematic_pairs,
                'total_trades': len(open_trades),
                'correlation_pairs': len(portfolio_corr['correlation_pairs'])
            }
            
        except Exception as e:
            logger.error(f"Error analyzing correlation risk: {e}")
            return {
                'risk_score': 0,
                'risk_level': 'UNKNOWN',
                'recommendation': 'ERROR',
                'max_correlation': 0.0,
                'average_correlation': 0.0,
                'problematic_pairs': [],
                'total_trades': 0,
                'correlation_pairs': 0
            }
    
    def update_correlation_matrix(self, symbol1: str, symbol2: str, correlation: float):
        """
        Update correlation matrix with new data
        
        Args:
            symbol1: First symbol
            symbol2: Second symbol
            correlation: Correlation coefficient
        """
        try:
            pair = (symbol1, symbol2)
            self.CORRELATIONS[pair] = correlation
            logger.info(f"Updated correlation {symbol1}-{symbol2}: {correlation}")
            
        except Exception as e:
            logger.error(f"Error updating correlation matrix: {e}")
    
    def get_correlation_summary(self, open_trades: List[Dict]) -> str:
        """
        Get human-readable correlation summary
        
        Args:
            open_trades: List of open trades
            
        Returns:
            Correlation summary string
        """
        try:
            if not open_trades:
                return "No open trades - no correlation risk"
            
            analysis = self.analyze_correlation_risk(open_trades)
            
            if analysis['risk_level'] == 'LOW':
                return f"Low correlation risk ({analysis['risk_score']}%) - portfolio is well diversified"
            elif analysis['risk_level'] == 'MEDIUM':
                return f"Medium correlation risk ({analysis['risk_score']}%) - monitor positions closely"
            else:
                return f"High correlation risk ({analysis['risk_score']}%) - consider reducing positions"
                
        except Exception as e:
            logger.error(f"Error getting correlation summary: {e}")
            return f"Error analyzing correlation: {str(e)}"




