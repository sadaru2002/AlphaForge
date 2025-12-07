"""
Enhanced Signal Generator Integration for AlphaForge
Integrates AlphaForge best components: Regime Detection, Kelly Criterion, Multi-Timeframe
Replaces old alphaforge_strategy.py with enhanced version
"""
import asyncio
import os
from datetime import datetime
import logging
from typing import Dict, Optional
from dotenv import load_dotenv
from enhanced_signal_generator import EnhancedSignalGenerator
from regime_detector import MarketRegimeDetector, MarketRegime
from kelly_criterion import KellyCriterion
from multi_timeframe_engine import MultiTimeframeEngine

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)

class AlphaForgeEnhancedStrategy:
    """
    Enhanced AlphaForge Trading Strategy
    Combines AlphaForge regime detection + Kelly sizing + Multi-TF with Gemini AI validation
    """
    
    def __init__(self):
        """Initialize enhanced strategy components"""
        # Get OANDA API key
        self.oanda_api_key = os.getenv("OANDA_API_KEY")
        
        # Initialize AlphaForge components
        self.signal_generator = EnhancedSignalGenerator(oanda_api_key=self.oanda_api_key)
        self.regime_detector = MarketRegimeDetector()
        self.kelly = KellyCriterion(lookback_trades=50, kelly_fraction=0.25)
        self.mtf_engine = MultiTimeframeEngine(api_key=self.oanda_api_key)
        
        # Supported instruments
        self.instruments = ['GBP_USD', 'XAU_USD', 'USD_JPY']
        
        # Performance tracking
        self.stats = {
            'total_signals': 0,
            'regime_filtered': 0,
            'confidence_filtered': 0,
            'agreement_filtered': 0,
            'tradeable_signals': 0,
            'by_regime': {}
        }
    
    async def generate_signal_for_pair(self, pair: str) -> Optional[Dict]:
        """
        Generate enhanced signal for a trading pair.
        
        Args:
            pair: GBP_USD, XAU_USD, or USD_JPY
        
        Returns:
            Complete signal dict or None
        """
        try:
            logger.info(f"Generating enhanced signal for {pair}...")
            
            # Generate signal using AlphaForge integration
            signal = await self.signal_generator.generate_signal(pair)
            
            # Update statistics
            self.stats['total_signals'] += 1
            
            if signal is None:
                logger.warning(f"Failed to generate signal for {pair}")
                return None
            
            # Track regime distribution
            regime = signal.get('regime', 'UNKNOWN')
            self.stats['by_regime'][regime] = self.stats['by_regime'].get(regime, 0) + 1
            
            # Check if signal is tradeable
            if not signal.get('tradeable', False):
                reason = signal.get('reason', 'Unknown')
                logger.info(f"Signal filtered: {reason}")
                
                if 'regime' in reason.lower():
                    self.stats['regime_filtered'] += 1
                elif 'confidence' in reason.lower():
                    self.stats['confidence_filtered'] += 1
                elif 'agreement' in reason.lower():
                    self.stats['agreement_filtered'] += 1
                
                return None
            
            # Signal passed all filters
            self.stats['tradeable_signals'] += 1
            
            # Convert to AlphaForge format for database/frontend
            alphaforge_signal = self._convert_to_alphaforge_format(signal)
            
            logger.info(
                f"✅ Enhanced signal generated for {pair}: {signal['signal']} "
                f"(score: {signal.get('score', 0):.3f}, confidence: {signal.get('confidence', 0):.3f})"
            )
            
            return alphaforge_signal
            
        except Exception as e:
            logger.error(f"Error generating signal for {pair}: {e}")
            return None
    
    def _convert_to_alphaforge_format(self, signal: Dict) -> Dict:
        """
        Convert enhanced signal format to AlphaForge database format.
        
        Args:
            signal: Enhanced signal dict from AlphaForge generator
        
        Returns:
            AlphaForge-compatible signal dict
        """
        # Map instrument names
        symbol_map = {
            'GBP_USD': 'GBP/USD',
            'XAU_USD': 'GOLD',
            'USD_JPY': 'USD/JPY'
        }
        
        # Calculate risk/reward metrics
        entry = signal.get('entry_price', 0)
        sl = signal.get('stop_loss', 0)
        tp = signal.get('take_profit', 0)
        
        sl_distance = abs(entry - sl)
        tp_distance = abs(tp - entry)
        risk_reward = tp_distance / sl_distance if sl_distance > 0 else 2.0
        
        # Get regime info
        regime = signal.get('regime', 'UNKNOWN')
        regime_config = {
            'trending_up_low_volatility': {'color': '#10B981', 'tradeable': True},
            'trending_down_low_volatility': {'color': '#EF4444', 'tradeable': True},
            'trending_up_high_volatility': {'color': '#34D399', 'tradeable': True},
            'trending_down_high_volatility': {'color': '#F87171', 'tradeable': True},
            'ranging_low_volatility': {'color': '#FBBF24', 'tradeable': True},
            'ranging_high_volatility': {'color': '#F59E0B', 'tradeable': False},
            'transitional': {'color': '#6B7280', 'tradeable': False},
            'unknown': {'color': '#9CA3AF', 'tradeable': False}
        }
        
        regime_info = regime_config.get(regime, regime_config['unknown'])
        
        return {
            # Basic info
            'symbol': symbol_map.get(signal['instrument'], signal['instrument']),
            'pair': signal['instrument'],
            'direction': signal['signal'],
            'timeframe': 'M5',
            
            # Price levels
            'entry': entry,
            'stop_loss': sl,
            'take_profit': tp,
            'tp1': tp,
            'tp2': tp + (tp_distance * 0.5) if signal['signal'] == 'BUY' else tp - (tp_distance * 0.5),
            'tp3': None,
            
            # Signal quality
            'confidence_score': signal.get('confidence', 0.0),
            'score': signal.get('score', 0.0),
            'agreement': signal.get('agreement', 0.0),
            
            # Multi-timeframe data
            'timeframe_signals': signal.get('timeframe_signals', {}),
            'mtf_m5': signal['timeframe_signals'].get('M5', {}).get('score', 0),
            'mtf_m15': signal['timeframe_signals'].get('M15', {}).get('score', 0),
            'mtf_h1': signal['timeframe_signals'].get('H1', {}).get('score', 0),
            
            # Regime detection
            'market_regime': regime,
            'regime_tradeable': regime_info['tradeable'],
            'regime_color': regime_info['color'],
            'position_multiplier': signal.get('position_multiplier', 1.0),
            
            # Position sizing
            'kelly_fraction': signal.get('kelly_fraction', 0.02),
            'recommended_risk': signal.get('recommended_risk', 0.02),
            'risk_reward_ratio': risk_reward,
            
            # Technical data
            'atr': signal.get('atr', 0),
            'session_weight': signal.get('session_weight', 1.0),
            'trading_hour': signal.get('trading_hour', 0),
            
            # Reasoning (for Gemini AI validation)
            'reasoning': self._generate_reasoning(signal),
            
            # Metadata
            'timestamp': signal.get('timestamp', datetime.now().isoformat()),
            'candles_analyzed': signal.get('candles_analyzed', {}),
            'strategy_version': 'AlphaForge Enhanced v2.0 (AlphaForge Integration)',
            
            # Status
            'status': 'PENDING',
            'tradeable': True,
            'gemini_validated': False
        }
    
    def _generate_reasoning(self, signal: Dict) -> str:
        """Generate reasoning text for Gemini AI validation"""
        regime = signal.get('regime', 'unknown').replace('_', ' ').title()
        direction = signal['signal']
        score = signal.get('score', 0)
        confidence = signal.get('confidence', 0)
        agreement = signal.get('agreement', 0)
        
        # Multi-timeframe breakdown
        tf_signals = signal.get('timeframe_signals', {})
        tf_text = []
        for tf, data in tf_signals.items():
            tf_score = data.get('score', 0)
            tf_dir = 'BUY' if tf_score > 0.2 else ('SELL' if tf_score < -0.2 else 'NEUTRAL')
            tf_text.append(f"{tf}: {tf_dir} ({tf_score:.3f})")
        
        reasoning = f"""
Enhanced AlphaForge Signal - {signal['instrument']}

Direction: {direction}
Signal Score: {score:.3f}
Confidence: {confidence:.1%}
Timeframe Agreement: {agreement:.1%}

Market Regime: {regime}
Position Multiplier: {signal.get('position_multiplier', 1.0):.2f}
Recommended Risk: {signal.get('recommended_risk', 0.02):.2%}

Multi-Timeframe Analysis:
{chr(10).join(tf_text)}

Entry: {signal.get('entry_price', 0):.5f}
Stop Loss: {signal.get('stop_loss', 0):.5f}
Take Profit: {signal.get('take_profit', 0):.5f}
Risk/Reward: 1:{signal.get('risk_reward_ratio', 2.0):.1f}

ATR: {signal.get('atr', 0):.5f}
Session Weight: {signal.get('session_weight', 1.0):.2f}
Trading Hour: {signal.get('trading_hour', 0)} GMT

This signal passed:
✓ Regime detection (favorable market condition)
✓ Multi-timeframe confluence (60%+ confidence)
✓ Timeframe agreement (67%+ alignment)
✓ Session quality check
✓ ATR-based dynamic SL/TP
✓ Kelly Criterion position sizing
""".strip()
        
        return reasoning
    
    def update_trade_result(self, pair: str, profit_loss: float, risk: float):
        """Update Kelly Criterion with trade result"""
        self.signal_generator.update_trade_result(pair, profit_loss, risk)
        logger.info(f"Trade result updated for {pair}: P/L ${profit_loss:.2f}")
    
    def get_statistics(self) -> Dict:
        """Get strategy statistics"""
        # Get Kelly stats
        kelly_stats = self.kelly.get_statistics()
        
        # Get regime stats
        regime_info = self.regime_detector.get_regime_info()
        
        # Calculate filter efficiency
        total = self.stats['total_signals']
        tradeable = self.stats['tradeable_signals']
        efficiency = (tradeable / total * 100) if total > 0 else 0
        
        return {
            'strategy': {
                'name': 'AlphaForge Enhanced (AlphaForge Integration)',
                'version': '2.0',
                'total_signals': total,
                'tradeable_signals': tradeable,
                'filter_efficiency': f"{efficiency:.1f}%",
                'regime_filtered': self.stats['regime_filtered'],
                'confidence_filtered': self.stats['confidence_filtered'],
                'agreement_filtered': self.stats['agreement_filtered']
            },
            'kelly_criterion': {
                'win_rate': kelly_stats.get('win_rate', 0),
                'avg_win': kelly_stats.get('avg_win', 0),
                'avg_loss': kelly_stats.get('avg_loss', 0),
                'win_loss_ratio': kelly_stats.get('win_loss_ratio', 0),
                'recommended_risk': kelly_stats.get('kelly_fraction', 0.02),
                'trade_count': kelly_stats.get('trade_count', 0)
            },
            'regime_detection': {
                'current_regime': regime_info.get('current_regime', None),
                'confidence': regime_info.get('confidence', 0),
                'regime_distribution': self.stats['by_regime']
            }
        }


# Global instance
enhanced_strategy = None

def get_enhanced_strategy() -> AlphaForgeEnhancedStrategy:
    """Get or create enhanced strategy instance"""
    global enhanced_strategy
    if enhanced_strategy is None:
        enhanced_strategy = AlphaForgeEnhancedStrategy()
    return enhanced_strategy


# Example usage
async def test_enhanced_strategy():
    """Test the enhanced strategy"""
    strategy = get_enhanced_strategy()
    
    # Generate signals for all 3 pairs
    for pair in ['GBP_USD', 'XAU_USD', 'USD_JPY']:
        print(f"\n{'='*60}")
        print(f"Testing {pair}")
        print(f"{'='*60}")
        
        signal = await strategy.generate_signal_for_pair(pair)
        
        if signal:
            print(f"✅ Signal generated!")
            print(f"Direction: {signal['direction']}")
            print(f"Entry: {signal['entry']:.5f}")
            print(f"Stop Loss: {signal['stop_loss']:.5f}")
            print(f"Take Profit: {signal['take_profit']:.5f}")
            print(f"Confidence: {signal['confidence_score']:.1%}")
            print(f"Regime: {signal['market_regime']}")
            print(f"Recommended Risk: {signal['recommended_risk']:.2%}")
        else:
            print(f"❌ No tradeable signal (filtered)")
    
    # Print statistics
    print(f"\n{'='*60}")
    print("Strategy Statistics")
    print(f"{'='*60}")
    stats = strategy.get_statistics()
    print(f"Total Signals: {stats['strategy']['total_signals']}")
    print(f"Tradeable: {stats['strategy']['tradeable_signals']}")
    print(f"Filter Efficiency: {stats['strategy']['filter_efficiency']}")


if __name__ == "__main__":
    asyncio.run(test_enhanced_strategy())

