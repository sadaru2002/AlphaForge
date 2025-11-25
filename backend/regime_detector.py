"""
Market Regime Detector using Gaussian Mixture Model
Adapted from AlphaForge for AlphaForge trading system
"""
import pandas as pd
import numpy as np
import logging
from enum import Enum
from sklearn.mixture import GaussianMixture
from sklearn.preprocessing import StandardScaler
import warnings
warnings.filterwarnings('ignore')

logger = logging.getLogger(__name__)

class MarketRegime(Enum):
    """Market regime states for trading decisions."""
    TRENDING_UP_HIGH_VOL = "trending_up_high_volatility"
    TRENDING_UP_LOW_VOL = "trending_up_low_volatility"
    TRENDING_DOWN_HIGH_VOL = "trending_down_high_volatility"
    TRENDING_DOWN_LOW_VOL = "trending_down_low_volatility"
    RANGING_HIGH_VOL = "ranging_high_volatility"
    RANGING_LOW_VOL = "ranging_low_volatility"
    TRANSITIONAL = "transitional"
    UNKNOWN = "unknown"

class MarketRegimeDetector:
    """
    Advanced market regime detection using Gaussian Mixture Model.
    Detects market conditions to filter out unfavorable trading environments.
    """

    def __init__(self):
        """Initialize the regime detector with GMM."""
        self.gmm = GaussianMixture(
            n_components=4, 
            covariance_type='full', 
            random_state=42,
            max_iter=100
        )
        self.scaler = StandardScaler()
        self.regime_history = []
        self.is_fitted = False
        
        # Volatility thresholds (for GBP/USD, XAU/USD, USD/JPY)
        self.volatility_thresholds = {
            'GBP_USD': {'high': 0.0015, 'low': 0.0008},
            'XAU_USD': {'high': 0.015, 'low': 0.008},  # Gold is more volatile
            'USD_JPY': {'high': 0.008, 'low': 0.004}
        }
        
        # ADX thresholds
        self.trending_adx = 25
        self.ranging_adx = 20

    def detect_regime(self, df, instrument='GBP_USD'):
        """
        Detect current market regime using Gaussian Mixture Model.
        
        Args:
            df: DataFrame with OHLCV and technical indicators
            instrument: Trading pair (GBP_USD, XAU_USD, USD_JPY)
        
        Returns:
            MarketRegime: Current market condition
        """
        if df is None or len(df) < 50:
            logger.warning("Insufficient data for regime detection")
            return MarketRegime.UNKNOWN

        try:
            # Calculate regime features
            features = self._calculate_regime_features(df)

            if features is None or len(features) < 20:
                logger.warning("Could not calculate regime features")
                return MarketRegime.UNKNOWN

            # Fit GMM if not already fitted
            if not self.is_fitted and len(features) >= 100:
                try:
                    scaled_features = self.scaler.fit_transform(features)
                    self.gmm.fit(scaled_features)
                    self.is_fitted = True
                    logger.info("GMM model fitted successfully")
                except Exception as e:
                    logger.error(f"Error fitting GMM: {e}")
                    return self._rule_based_regime_detection(features.iloc[-1], instrument)

            # Predict regime
            if self.is_fitted:
                try:
                    scaled_features = self.scaler.transform(features[-1:])
                    regime = self.gmm.predict(scaled_features)[0]
                    probabilities = self.gmm.predict_proba(scaled_features)[0]
                    
                    # Map GMM cluster to market condition
                    regime_state = self._map_regime_to_condition(
                        regime, 
                        features.iloc[-1], 
                        probabilities,
                        instrument
                    )
                    
                    # Track regime history
                    self.regime_history.append({
                        'regime': regime_state,
                        'confidence': max(probabilities),
                        'timestamp': df.index[-1] if hasattr(df.index[-1], 'strftime') else None
                    })
                    
                    # Keep only last 100 regimes
                    if len(self.regime_history) > 100:
                        self.regime_history = self.regime_history[-100:]
                    
                    return regime_state
                    
                except Exception as e:
                    logger.error(f"Error predicting regime: {e}")
                    return self._rule_based_regime_detection(features.iloc[-1], instrument)
            else:
                # Fallback to rule-based detection
                return self._rule_based_regime_detection(features.iloc[-1], instrument)

        except Exception as e:
            logger.error(f"Error in regime detection: {str(e)}")
            return MarketRegime.UNKNOWN

    def _calculate_regime_features(self, df):
        """
        Calculate features for regime detection.
        
        Returns:
            DataFrame with regime classification features
        """
        try:
            features = pd.DataFrame(index=df.index)

            # Price-based features
            features['returns'] = df['close'].pct_change()
            features['returns_std'] = features['returns'].rolling(20).std()
            features['returns_skew'] = features['returns'].rolling(20).skew()
            features['returns_kurt'] = features['returns'].rolling(20).kurt()

            # Trend features
            if 'adx' in df.columns:
                features['adx'] = df['adx']
                features['trend_strength'] = df['adx'] / 50  # Normalized
            else:
                features['adx'] = 20
                features['trend_strength'] = 0.4

            # Volatility features
            if 'atr' in df.columns:
                features['atr'] = df['atr']
                features['atr_pct'] = df['atr'] / df['close']
                features['volatility'] = features['atr_pct']
                features['volatility_ma'] = features['volatility'].rolling(20).mean()
            else:
                # Calculate ATR if not present
                high_low = df['high'] - df['low']
                high_close = abs(df['high'] - df['close'].shift())
                low_close = abs(df['low'] - df['close'].shift())
                true_range = pd.concat([high_low, high_close, low_close], axis=1).max(axis=1)
                atr = true_range.rolling(14).mean()
                features['atr'] = atr
                features['atr_pct'] = atr / df['close']
                features['volatility'] = features['atr_pct']
                features['volatility_ma'] = features['volatility'].rolling(20).mean()

            # Volume features (if available)
            if 'volume' in df.columns:
                features['volume_ratio'] = df['volume'] / df['volume'].rolling(20).mean()
            else:
                features['volume_ratio'] = 1.0

            # RSI features (if available)
            if 'rsi' in df.columns:
                features['rsi'] = df['rsi']
                features['rsi_normalized'] = (df['rsi'] - 50) / 50  # -1 to 1
            else:
                features['rsi'] = 50
                features['rsi_normalized'] = 0

            # Remove NaN values
            features = features.dropna()

            return features if len(features) > 0 else None

        except Exception as e:
            logger.error(f"Error calculating regime features: {str(e)}")
            return None

    def _map_regime_to_condition(self, regime, features, probabilities, instrument):
        """
        Map GMM regime to market condition with confidence check.
        
        Args:
            regime: GMM cluster (0-3)
            features: Current feature values
            probabilities: Prediction probabilities
            instrument: Trading pair
        
        Returns:
            MarketRegime: Classified market condition
        """
        confidence = max(probabilities)

        # Low confidence = transitional market
        if confidence < 0.6:
            return MarketRegime.TRANSITIONAL

        # Get volatility threshold for instrument
        vol_thresholds = self.volatility_thresholds.get(
            instrument, 
            self.volatility_thresholds['GBP_USD']
        )
        
        # Determine volatility level
        volatility = features.get('volatility', 0.001)
        is_high_vol = volatility > vol_thresholds['high']

        # Determine trend direction and strength
        adx = features.get('adx', 20)
        returns = features.get('returns', 0)

        # Map GMM clusters to market conditions
        # Note: These mappings are calibrated through backtesting
        if regime == 0:  # Trending up cluster
            if is_high_vol:
                return MarketRegime.TRENDING_UP_HIGH_VOL
            else:
                return MarketRegime.TRENDING_UP_LOW_VOL
                
        elif regime == 1:  # Trending down cluster
            if is_high_vol:
                return MarketRegime.TRENDING_DOWN_HIGH_VOL
            else:
                return MarketRegime.TRENDING_DOWN_LOW_VOL
                
        elif regime == 2:  # Ranging cluster
            if is_high_vol:
                return MarketRegime.RANGING_HIGH_VOL
            else:
                return MarketRegime.RANGING_LOW_VOL
                
        else:  # Transitional cluster
            return MarketRegime.TRANSITIONAL

    def _rule_based_regime_detection(self, features, instrument):
        """
        Fallback rule-based regime detection when GMM is not fitted.
        
        Args:
            features: Current feature values
            instrument: Trading pair
        
        Returns:
            MarketRegime: Classified market condition
        """
        # Get values
        adx = features.get('adx', 20)
        volatility = features.get('volatility', 0.001)
        returns = features.get('returns', 0)

        # Get volatility threshold
        vol_thresholds = self.volatility_thresholds.get(
            instrument,
            self.volatility_thresholds['GBP_USD']
        )
        
        is_high_vol = volatility > vol_thresholds['high']

        # Rule-based classification
        if adx > self.trending_adx:
            # Strong trend
            if returns > 0:
                return MarketRegime.TRENDING_UP_HIGH_VOL if is_high_vol else MarketRegime.TRENDING_UP_LOW_VOL
            else:
                return MarketRegime.TRENDING_DOWN_HIGH_VOL if is_high_vol else MarketRegime.TRENDING_DOWN_LOW_VOL
                
        elif adx < self.ranging_adx:
            # Ranging market
            return MarketRegime.RANGING_HIGH_VOL if is_high_vol else MarketRegime.RANGING_LOW_VOL
            
        else:
            # Transitional
            return MarketRegime.TRANSITIONAL

    def should_trade(self, regime):
        """
        Determine if trading is recommended for current regime.
        
        Args:
            regime: MarketRegime
        
        Returns:
            bool: True if should trade, False otherwise
        """
        # Skip trading in these unfavorable conditions (LOWERED - removed TRANSITIONAL)
        unfavorable_regimes = {
            MarketRegime.RANGING_HIGH_VOL,  # Choppy, no clear direction
            MarketRegime.UNKNOWN             # Cannot determine
        }
        
        return regime not in unfavorable_regimes

    def get_position_multiplier(self, regime):
        """
        Get position size multiplier based on regime.
        
        Args:
            regime: MarketRegime
        
        Returns:
            float: Position size multiplier (0.5 to 1.5)
        """
        multipliers = {
            MarketRegime.TRENDING_UP_LOW_VOL: 1.2,      # Ideal for long
            MarketRegime.TRENDING_DOWN_LOW_VOL: 1.2,    # Ideal for short
            MarketRegime.TRENDING_UP_HIGH_VOL: 0.9,     # Reduce size in volatility
            MarketRegime.TRENDING_DOWN_HIGH_VOL: 0.9,   # Reduce size in volatility
            MarketRegime.RANGING_LOW_VOL: 0.8,          # Small size in ranging
            MarketRegime.RANGING_HIGH_VOL: 0.5,         # Very small in choppy
            MarketRegime.TRANSITIONAL: 0.6,             # Cautious in transition
            MarketRegime.UNKNOWN: 0.5                   # Minimal in unknown
        }
        
        return multipliers.get(regime, 1.0)

    def get_regime_info(self):
        """
        Get current regime statistics.
        
        Returns:
            dict: Regime history statistics
        """
        if not self.regime_history:
            return {
                'current_regime': None,
                'confidence': 0,
                'regime_count': 0
            }
        
        # Get regime distribution
        regime_counts = {}
        for item in self.regime_history[-20:]:  # Last 20 regimes
            regime = item['regime'].value
            regime_counts[regime] = regime_counts.get(regime, 0) + 1
        
        return {
            'current_regime': self.regime_history[-1]['regime'].value,
            'confidence': self.regime_history[-1]['confidence'],
            'regime_count': len(self.regime_history),
            'recent_distribution': regime_counts
        }


# Example usage
if __name__ == "__main__":
    import sys
    sys.path.append('..')
    
    # Test with sample data
    detector = MarketRegimeDetector()
    
    # Create sample DataFrame
    dates = pd.date_range(start='2025-01-01', periods=200, freq='5T')
    sample_data = pd.DataFrame({
        'close': np.random.randn(200).cumsum() + 1.2700,
        'high': np.random.randn(200).cumsum() + 1.2710,
        'low': np.random.randn(200).cumsum() + 1.2690,
        'volume': np.random.randint(100, 1000, 200),
        'adx': np.random.uniform(15, 35, 200),
        'rsi': np.random.uniform(30, 70, 200)
    }, index=dates)
    
    # Detect regime
    regime = detector.detect_regime(sample_data, instrument='GBP_USD')
    print(f"Detected Regime: {regime.value}")
    print(f"Should Trade: {detector.should_trade(regime)}")
    print(f"Position Multiplier: {detector.get_position_multiplier(regime)}")
