"""
Instrument-Specific Configuration for AlphaForge
Defines optimal SL/TP distances based on backtest results for each trading pair.
"""

class InstrumentConfig:
    """
    Instrument-specific trading parameters based on backtest performance.
    
    Each instrument has different volatility characteristics and pip values,
    requiring unique SL/TP distances for optimal performance.
    """
    
    # Configuration for each instrument
    CONFIGS = {
        'XAU_USD': {
            'name': 'Gold',
            'pip_value': 0.01,  # $0.01 = 1 pip for Gold
            'sl_pips': 45,       # $4.50 stop loss (45 pips)
            'tp_pips': 150,      # $15.00 take profit (150 pips) - OPTIMIZED for large moves
            'sl_dollars': 4.50,  # Direct dollar amount
            'tp_dollars': 15.00, # Direct dollar amount - INCREASED from $10.50
            'rr_ratio': 3.33,    # 15.00 / 4.50 = 3.33:1 (was 2.33:1)
            'description': 'High volatility - optimized for large moves. Backtest wins: $9.60-$13.17, targeting $15+',
            'atr_multiplier_sl': None,  # Use fixed pip distances instead
            'atr_multiplier_tp': None,
        },
        'GBP_USD': {
            'name': 'British Pound',
            'pip_value': 0.0001,  # 0.0001 = 1 pip for forex majors
            'sl_pips': 12,         # 12 pips stop loss
            'tp_pips': 25,         # 25 pips take profit
            'sl_dollars': 0.0012,  # In price terms
            'tp_dollars': 0.0025,  # In price terms
            'rr_ratio': 2.08,      # 25 / 12 = 2.08:1
            'description': 'M5 timeframe, smaller movements. Backtest wins: ~15.5-19.2 pips',
            'atr_multiplier_sl': None,
            'atr_multiplier_tp': None,
        },
        'USD_JPY': {
            'name': 'US Dollar / Japanese Yen',
            'pip_value': 0.01,    # 0.01 = 1 pip for JPY pairs
            'sl_pips': 17,         # 17 pips stop loss (0.17 in price)
            'tp_pips': 52,         # 52 pips take profit (0.52 in price)
            'sl_dollars': 0.17,    # In price terms
            'tp_dollars': 0.52,    # In price terms
            'rr_ratio': 3.06,      # 52 / 17 = 3.06:1
            'description': 'Strong trending behavior. Backtest wins: ~56-59 pips',
            'atr_multiplier_sl': None,
            'atr_multiplier_tp': None,
        }
    }
    
    @classmethod
    def get_config(cls, instrument):
        """Get configuration for a specific instrument."""
        return cls.CONFIGS.get(instrument, None)
    
    @classmethod
    def calculate_sltp(cls, instrument, entry_price, direction):
        """
        Calculate stop loss and take profit for an instrument.
        
        Args:
            instrument: Trading pair (e.g., 'GBP_USD')
            entry_price: Entry price
            direction: 'BUY' or 'SELL'
            
        Returns:
            dict with 'stop_loss', 'take_profit', 'sl_pips', 'tp_pips', 'rr_ratio'
        """
        config = cls.get_config(instrument)
        if not config:
            raise ValueError(f"No configuration found for {instrument}")
        
        # Use dollar-based distances directly
        sl_distance = config['sl_dollars']
        tp_distance = config['tp_dollars']
        
        if direction == 'BUY':
            stop_loss = entry_price - sl_distance
            take_profit = entry_price + tp_distance
        elif direction == 'SELL':
            stop_loss = entry_price + sl_distance
            take_profit = entry_price - tp_distance
        else:
            raise ValueError(f"Invalid direction: {direction}")
        
        return {
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'sl_pips': config['sl_pips'],
            'tp_pips': config['tp_pips'],
            'sl_distance': sl_distance,
            'tp_distance': tp_distance,
            'rr_ratio': config['rr_ratio'],
            'config_name': config['name']
        }
    
    @classmethod
    def get_all_instruments(cls):
        """Get list of all supported instruments."""
        return list(cls.CONFIGS.keys())
    
    @classmethod
    def print_configs(cls):
        """Print all instrument configurations."""
        print("\n" + "="*80)
        print("ALPHAFORGE INSTRUMENT CONFIGURATIONS")
        print("="*80)
        
        for instrument, config in cls.CONFIGS.items():
            print(f"\n{instrument} ({config['name']})")
            print(f"  Pip Value: {config['pip_value']}")
            print(f"  Stop Loss: {config['sl_pips']} pips (${config['sl_dollars']:.2f})")
            print(f"  Take Profit: {config['tp_pips']} pips (${config['tp_dollars']:.2f})")
            print(f"  Risk/Reward: 1:{config['rr_ratio']:.2f}")
            print(f"  Description: {config['description']}")


if __name__ == "__main__":
    # Test the configuration
    InstrumentConfig.print_configs()
    
    print("\n" + "="*80)
    print("EXAMPLE SL/TP CALCULATIONS")
    print("="*80)
    
    # Test calculations
    test_cases = [
        ('XAU_USD', 2450.00, 'BUY'),
        ('XAU_USD', 2450.00, 'SELL'),
        ('GBP_USD', 1.2700, 'BUY'),
        ('GBP_USD', 1.2700, 'SELL'),
        ('USD_JPY', 145.00, 'BUY'),
        ('USD_JPY', 145.00, 'SELL'),
    ]
    
    for instrument, entry, direction in test_cases:
        result = InstrumentConfig.calculate_sltp(instrument, entry, direction)
        print(f"\n{instrument} {direction} @ {entry}")
        print(f"  Stop Loss: {result['stop_loss']:.5f} ({result['sl_pips']} pips)")
        print(f"  Take Profit: {result['take_profit']:.5f} ({result['tp_pips']} pips)")
        print(f"  R:R Ratio: 1:{result['rr_ratio']:.2f}")
