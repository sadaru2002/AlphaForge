"""
AlphaForge Backtesting Engine with OANDA Historical Data
Tests the AlphaForge-enhanced strategy on real historical data
"""
import asyncio
import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import json
import os
import sys
from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsCandles
import logging
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Import our enhanced strategy
from enhanced_signal_generator import EnhancedSignalGenerator

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class OANDABacktestEngine:
    """
    Backtest AlphaForge strategy using OANDA historical data.
    """
    
    def __init__(self, api_key=None, initial_balance=10000, min_votes_required=2.5, min_strength=40.0):
        """
        Initialize backtest engine.
        
        Args:
            api_key: OANDA API key
            initial_balance: Starting account balance
            min_votes_required: Minimum indicator votes for signal (2.0-3.0)
            min_strength: Minimum signal strength percentage (30.0-50.0)
        """
        self.api_key = api_key or os.getenv("OANDA_API_KEY")
        self.api = API(access_token=self.api_key, environment="practice")
        self.initial_balance = initial_balance
        self.min_votes_required = min_votes_required
        self.min_strength = min_strength
        
        # Trading parameters
        self.balance = initial_balance
        self.equity = initial_balance
        self.trades = []
        self.open_position = None
        
        # Performance tracking
        self.total_trades = 0
        self.winning_trades = 0
        self.losing_trades = 0
        self.total_profit = 0
        self.total_loss = 0
        self.max_drawdown = 0
        self.peak_balance = initial_balance
        
        # Initialize signal generator with min_votes and min_strength settings
        self.signal_generator = EnhancedSignalGenerator(api_key)
        # Ensure engine settings match backtest config
        self.signal_generator.mtf_engine.min_votes_required = min_votes_required
        self.signal_generator.mtf_engine.min_strength = min_strength
        
    async def fetch_historical_data(self, instrument, start_date, end_date, granularity='M5'):
        """
        Fetch historical candle data from OANDA.
        
        Args:
            instrument: Trading pair (e.g., 'GBP_USD')
            start_date: Start date (datetime or string 'YYYY-MM-DD')
            end_date: End date (datetime or string 'YYYY-MM-DD')
            granularity: Timeframe (M5, M15, H1, etc.)
        
        Returns:
            DataFrame: Historical OHLCV data
        """
        logger.info(f"Fetching {instrument} data from {start_date} to {end_date}...")
        
        # Convert dates to datetime
        if isinstance(start_date, str):
            start_date = datetime.strptime(start_date, '%Y-%m-%d')
        if isinstance(end_date, str):
            end_date = datetime.strptime(end_date, '%Y-%m-%d')
        
        all_candles = []
        current_date = start_date
        
        # OANDA limits to 5000 candles per request
        max_candles = 5000
        
        while current_date < end_date:
            # Calculate candles needed for this chunk
            days_remaining = (end_date - current_date).days
            
            # Adjust count based on granularity
            if granularity == 'M5':
                candles_per_day = 288  # 24 * 60 / 5
            elif granularity == 'M15':
                candles_per_day = 96   # 24 * 60 / 15
            elif granularity == 'H1':
                candles_per_day = 24
            else:
                candles_per_day = 288  # Default
            
            count = min(max_candles, int(days_remaining * candles_per_day))
            
            params = {
                "granularity": granularity,
                "count": count,
                "from": current_date.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "price": "M"  # Midpoint pricing
            }
            
            try:
                request = InstrumentsCandles(instrument=instrument, params=params)
                
                # Run synchronous API call in executor
                loop = asyncio.get_event_loop()
                response = await loop.run_in_executor(
                    None,
                    lambda: self.api.request(request)
                )
                
                candles = response.get('candles', [])
                
                if not candles:
                    break
                
                all_candles.extend(candles)
                
                # Update current_date to last candle time
                last_time = candles[-1]['time'].replace('.000000000Z', '')
                current_date = datetime.strptime(last_time, '%Y-%m-%dT%H:%M:%S')
                current_date += timedelta(minutes=5)  # Move forward
                
                logger.info(f"Fetched {len(candles)} candles, total: {len(all_candles)}")
                
                # Sleep to avoid rate limits
                await asyncio.sleep(0.5)
                
            except Exception as e:
                logger.error(f"Error fetching data: {e}")
                break
        
        # Process candles into DataFrame
        df = self._process_candles(all_candles)
        logger.info(f"Total candles fetched: {len(df)}")
        
        return df
    
    def _process_candles(self, candles):
        """Convert OANDA candles to DataFrame."""
        data = []
        
        for candle in candles:
            if not candle.get('complete', False):
                continue
            
            time_str = candle['time'].replace('.000000000Z', '')
            timestamp = datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S')
            
            mid = candle.get('mid', candle.get('bid', candle.get('ask')))
            
            data.append({
                'timestamp': timestamp,
                'open': float(mid['o']),
                'high': float(mid['h']),
                'low': float(mid['l']),
                'close': float(mid['c']),
                'volume': int(candle['volume'])
            })
        
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
        
        return df
    
    async def run_backtest(self, instrument, start_date, end_date, risk_per_trade=0.02, focus_date=None):
        """
        Run backtest on historical data.
        
        Args:
            instrument: Trading pair
            start_date: Start date (for data loading)
            end_date: End date
            risk_per_trade: Risk percentage per trade (0.02 = 2%)
            focus_date: If set, only trade on this specific date (YYYY-MM-DD)
        
        Returns:
            dict: Backtest results
        """
        logger.info(f"\n{'='*80}")
        logger.info(f"Starting Backtest: {instrument}")
        logger.info(f"Data Period: {start_date} to {end_date}")
        if focus_date:
            logger.info(f"Focus Date: {focus_date} (only trading on this day)")
        logger.info(f"Initial Balance: ${self.initial_balance:,.2f}")
        logger.info(f"Risk per Trade: {risk_per_trade*100:.1f}%")
        logger.info(f"Min Votes: {self.min_votes_required} / 6.0")
        logger.info(f"{'='*80}\n")
        
        # Fetch historical data
        df = await self.fetch_historical_data(instrument, start_date, end_date, 'M5')
        
        if df.empty:
            logger.error("No data fetched!")
            return None
        
        # Prepare multi-timeframe data
        df_m15 = df.resample('15T').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        df_h1 = df.resample('1H').agg({
            'open': 'first',
            'high': 'max',
            'low': 'min',
            'close': 'last',
            'volume': 'sum'
        }).dropna()
        
        # Simulate trading
        logger.info("Running backtest simulation...")
        
        lookback = 500  # Candles needed for indicators
        signals_checked = 0
        signals_generated = 0
        signals_filtered = 0
        
        for i in range(lookback, len(df)):
            current_time = df.index[i]
            current_price = df['close'].iloc[i]
            
            # Skip if focus_date is set and this isn't the focus date
            if focus_date:
                focus_dt = datetime.strptime(focus_date, '%Y-%m-%d').date()
                if current_time.date() != focus_dt:
                    continue
            
            # Get data up to current point
            m5_data = df.iloc[:i+1].tail(500)
            m15_data = df_m15[df_m15.index <= current_time].tail(300)
            h1_data = df_h1[df_h1.index <= current_time].tail(200)
            
            # Prepare multi-timeframe data
            mtf_data = {
                'M5': m5_data,
                'M15': m15_data,
                'H1': h1_data
            }
            
            # Check for open position management
            if self.open_position:
                self._update_position(current_price, current_time)
                if self.open_position:  # Still open
                    continue
            
            # Generate signal
            # Generate signal using the ACTUAL signal generator logic
            # This ensures we test regime detection, cooldowns, and all filters exactly as live
            signal_result = await self.signal_generator.generate_signal(
                instrument,
                timestamp=current_time,
                provided_data=mtf_data
            )
            
            # If no signal or error, skip
            if not signal_result:
                continue
                
            # Track signal statistics
            if signal_result.get('signal') in ['BUY', 'SELL']:
                signals_generated += 1
                
                # Check if tradeable (passed all filters + cooldown)
                if not signal_result.get('tradeable', False):
                    signals_filtered += 1
                    if signals_filtered <= 5:  # Show first 5 filtered signals
                        logger.info(
                            f"Signal {signal_result['signal']} FILTERED at {current_time} | "
                            f"Reason: {signal_result.get('reason', 'Unknown')} | "
                            f"Strength: {signal_result.get('mtf_signal', {}).get('strength', 0):.1f}%"
                        )
                else:
                    # PASSED ALL CHECKS
                    # Extract metrics for trade management
                    mtf_sig = signal_result.get('mtf_signal', {})
                    
                    # Construct trade data structure expected by _open_trade
                    trade_data = {
                        'signal': signal_result['signal'],
                        'strength': mtf_sig.get('strength', 0),
                        'buy_votes': mtf_sig.get('buy_votes', 0),
                        'sell_votes': mtf_sig.get('sell_votes', 0),
                        'passed_filters': True,
                        'timeframe_signals': signal_result.get('timeframe_signals', {})
                    }
                    
                    self._open_trade(
                        signal_result['signal'],
                        current_price,
                        current_time,
                        risk_per_trade,
                        trade_data
                    )
        
        # Close any remaining position
        if self.open_position:
            self._close_trade(df['close'].iloc[-1], df.index[-1], "End of backtest")
        
        # Log signal statistics
        logger.info(f"\n{'='*80}")
        logger.info(f"SIGNAL STATISTICS")
        logger.info(f"{'='*80}")
        logger.info(f"Total candles checked: {signals_checked}")
        logger.info(f"Signals generated (BUY/SELL): {signals_generated}")
        logger.info(f"Signals filtered out: {signals_filtered}")
        logger.info(f"Signals accepted: {signals_generated - signals_filtered}")
        logger.info(f"{'='*80}\n")
        
        # Calculate results
        results = self._calculate_results(start_date, end_date)
        
        return results
    
    def _open_trade(self, direction, entry_price, entry_time, risk_per_trade, signal_data):
        """Open a new trade."""
        # Calculate position size based on risk
        atr = signal_data['timeframe_signals'].get('M5', {}).get('latest_data', {}).get('atr', entry_price * 0.001)
        
        # Stop loss distance
        if direction == 'BUY':
            stop_loss = entry_price - (atr * 1.5)
            take_profit = entry_price + (atr * 3.0)
        else:  # SELL
            stop_loss = entry_price + (atr * 1.5)
            take_profit = entry_price - (atr * 3.0)
        
        # Calculate position size
        risk_amount = self.balance * risk_per_trade
        stop_distance = abs(entry_price - stop_loss)
        position_size = risk_amount / stop_distance if stop_distance > 0 else 0
        
        if position_size <= 0:
            return
        
        self.open_position = {
            'direction': direction,
            'entry_price': entry_price,
            'entry_time': entry_time,
            'stop_loss': stop_loss,
            'take_profit': take_profit,
            'position_size': position_size,
            'risk_amount': risk_amount,
            'signal_strength': signal_data['strength'],
            'buy_votes': signal_data['buy_votes'],
            'sell_votes': signal_data['sell_votes']
        }
        
        logger.info(
            f"📈 OPENED {direction} @ {entry_price:.5f} | "
            f"SL: {stop_loss:.5f} | TP: {take_profit:.5f} | "
            f"Size: {position_size:.2f} | Strength: {signal_data['strength']:.1f}%"
        )
    
    def _update_position(self, current_price, current_time):
        """Update open position and check for exit."""
        if not self.open_position:
            return
        
        pos = self.open_position
        
        # Check stop loss
        if pos['direction'] == 'BUY':
            if current_price <= pos['stop_loss']:
                self._close_trade(pos['stop_loss'], current_time, "Stop Loss")
                return
            elif current_price >= pos['take_profit']:
                self._close_trade(pos['take_profit'], current_time, "Take Profit")
                return
        else:  # SELL
            if current_price >= pos['stop_loss']:
                self._close_trade(pos['stop_loss'], current_time, "Stop Loss")
                return
            elif current_price <= pos['take_profit']:
                self._close_trade(pos['take_profit'], current_time, "Take Profit")
                return
    
    def _close_trade(self, exit_price, exit_time, reason):
        """Close the open trade."""
        if not self.open_position:
            return
        
        pos = self.open_position
        
        # Calculate P&L
        if pos['direction'] == 'BUY':
            pnl = (exit_price - pos['entry_price']) * pos['position_size']
        else:  # SELL
            pnl = (pos['entry_price'] - exit_price) * pos['position_size']
        
        # Update balance
        self.balance += pnl
        self.equity = self.balance
        
        # Track peak and drawdown
        if self.balance > self.peak_balance:
            self.peak_balance = self.balance
        
        drawdown = (self.peak_balance - self.balance) / self.peak_balance
        if drawdown > self.max_drawdown:
            self.max_drawdown = drawdown
        
        # Update statistics
        self.total_trades += 1
        
        if pnl > 0:
            self.winning_trades += 1
            self.total_profit += pnl
            result_emoji = "✅"
        else:
            self.losing_trades += 1
            self.total_loss += abs(pnl)
            result_emoji = "❌"
        
        # Save trade
        trade_record = {
            'entry_time': pos['entry_time'],
            'exit_time': exit_time,
            'direction': pos['direction'],
            'entry_price': pos['entry_price'],
            'exit_price': exit_price,
            'position_size': pos['position_size'],
            'pnl': pnl,
            'pnl_pct': (pnl / self.initial_balance) * 100,
            'balance': self.balance,
            'reason': reason,
            'signal_strength': pos['signal_strength'],
            'buy_votes': pos['buy_votes'],
            'sell_votes': pos['sell_votes']
        }
        
        self.trades.append(trade_record)
        
        logger.info(
            f"{result_emoji} CLOSED {pos['direction']} @ {exit_price:.5f} | "
            f"P&L: ${pnl:+.2f} ({(pnl/pos['risk_amount'])*100:+.1f}%) | "
            f"Reason: {reason} | Balance: ${self.balance:,.2f}"
        )
        
        self.open_position = None
    
    def _calculate_results(self, start_date, end_date):
        """Calculate backtest performance metrics."""
        if not self.trades:
            logger.warning("No trades executed!")
            return None
        
        # Convert trades to DataFrame
        trades_df = pd.DataFrame(self.trades)
        
        # Calculate metrics
        win_rate = (self.winning_trades / self.total_trades) * 100 if self.total_trades > 0 else 0
        avg_win = self.total_profit / self.winning_trades if self.winning_trades > 0 else 0
        avg_loss = self.total_loss / self.losing_trades if self.losing_trades > 0 else 0
        profit_factor = self.total_profit / self.total_loss if self.total_loss > 0 else float('inf')
        
        net_profit = self.balance - self.initial_balance
        return_pct = (net_profit / self.initial_balance) * 100
        
        # Calculate expectancy
        expectancy = (win_rate/100 * avg_win) - ((100-win_rate)/100 * avg_loss)
        
        results = {
            'start_date': start_date,
            'end_date': end_date,
            'initial_balance': self.initial_balance,
            'final_balance': self.balance,
            'net_profit': net_profit,
            'return_pct': return_pct,
            'total_trades': self.total_trades,
            'winning_trades': self.winning_trades,
            'losing_trades': self.losing_trades,
            'win_rate': win_rate,
            'avg_win': avg_win,
            'avg_loss': avg_loss,
            'profit_factor': profit_factor,
            'max_drawdown': self.max_drawdown * 100,
            'expectancy': expectancy,
            'trades': trades_df.to_dict('records')
        }
        
        return results
    
    def print_results(self, results):
        """Print backtest results in a formatted way."""
        if not results:
            return
        
        print(f"\n{'='*80}")
        print(f"BACKTEST RESULTS")
        print(f"{'='*80}")
        print(f"Period: {results['start_date']} to {results['end_date']}")
        print(f"\n📊 PERFORMANCE SUMMARY")
        print(f"{'─'*80}")
        print(f"Initial Balance:     ${results['initial_balance']:>12,.2f}")
        print(f"Final Balance:       ${results['final_balance']:>12,.2f}")
        print(f"Net Profit:          ${results['net_profit']:>12,.2f}")
        print(f"Return:              {results['return_pct']:>12.2f}%")
        print(f"\n📈 TRADE STATISTICS")
        print(f"{'─'*80}")
        print(f"Total Trades:        {results['total_trades']:>12}")
        print(f"Winning Trades:      {results['winning_trades']:>12} ({results['win_rate']:.1f}%)")
        print(f"Losing Trades:       {results['losing_trades']:>12} ({100-results['win_rate']:.1f}%)")
        print(f"\n💰 PROFIT METRICS")
        print(f"{'─'*80}")
        print(f"Average Win:         ${results['avg_win']:>12,.2f}")
        print(f"Average Loss:        ${results['avg_loss']:>12,.2f}")
        print(f"Profit Factor:       {results['profit_factor']:>12.2f}")
        print(f"Expectancy:          ${results['expectancy']:>12,.2f}")
        print(f"\n📉 RISK METRICS")
        print(f"{'─'*80}")
        print(f"Max Drawdown:        {results['max_drawdown']:>12.2f}%")
        print(f"{'='*80}\n")
        
        # Show trade distribution
        if results['trades']:
            trades_df = pd.DataFrame(results['trades'])
            print(f"📊 TRADE DISTRIBUTION")
            print(f"{'─'*80}")
            print(f"Direction: {trades_df['direction'].value_counts().to_dict()}")
            print(f"Exit Reasons: {trades_df['reason'].value_counts().to_dict()}")
            print(f"{'='*80}\n")
    
    def save_results(self, results, filename='backtest_results.json'):
        """Save results to JSON file."""
        if not results:
            return
        
        # Convert datetime objects to strings
        results_copy = results.copy()
        results_copy['start_date'] = str(results_copy['start_date'])
        results_copy['end_date'] = str(results_copy['end_date'])
        
        # Convert trades DataFrame records
        for trade in results_copy['trades']:
            trade['entry_time'] = str(trade['entry_time'])
            trade['exit_time'] = str(trade['exit_time'])
        
        with open(filename, 'w') as f:
            json.dump(results_copy, f, indent=2)
        
        logger.info(f"Results saved to {filename}")


async def main():
    """Run backtest."""
    # Load configuration
    try:
        with open('backtest_config.json', 'r') as f:
            config = json.load(f)
            backtest_cfg = config['backtest_config']
    except:
        # Default configuration
        backtest_cfg = {
            'instrument': 'GBP_USD',
            'start_date': '2024-11-10',
            'end_date': '2024-11-11',
            'initial_balance': 10000,
            'risk_per_trade': 0.02,
            'min_votes_required': 2.5
        }
    
    # Configuration
    api_key = os.getenv("OANDA_API_KEY")
    
    if not api_key:
        print("❌ ERROR: OANDA_API_KEY not found in environment variables!")
        print("Please set your OANDA API key:")
        print("  export OANDA_API_KEY='your-api-key-here'  # Linux/Mac")
        print("  $env:OANDA_API_KEY='your-api-key-here'   # Windows PowerShell")
        return
    
    # Backtest parameters from config
    instrument = backtest_cfg.get('instrument', 'GBP_USD')
    start_date = backtest_cfg.get('start_date', '2024-11-01')
    end_date = backtest_cfg.get('end_date', '2024-11-11')
    initial_balance = backtest_cfg.get('initial_balance', 10000)
    risk_per_trade = backtest_cfg.get('risk_per_trade', 0.02)
    min_votes = backtest_cfg.get('min_votes_required', 2.5)
    min_strength = backtest_cfg.get('min_strength', 40.0)
    focus_date = backtest_cfg.get('focus_date', None)
    
    print(f"\n🚀 AlphaForge Backtest Engine")
    print(f"{'='*80}")
    print(f"Strategy: AlphaForge Enhanced (Indicator Voting System)")
    print(f"Instrument: {instrument}")
    print(f"Data Period: {start_date} to {end_date}")
    if focus_date:
        print(f"Focus Date: {focus_date} ⭐ (only trading on this day)")
    print(f"Initial Balance: ${initial_balance:,.2f}")
    print(f"Risk per Trade: {risk_per_trade*100:.1f}%")
    print(f"Min Votes Required: {min_votes} / 6.0 indicators")
    print(f"Min Strength: {min_strength}%")
    print(f"{'='*80}\n")
    
    # Run backtest
    engine = OANDABacktestEngine(api_key, initial_balance, min_votes, min_strength)
    
    results = await engine.run_backtest(
        instrument,
        start_date,
        end_date,
        risk_per_trade,
        focus_date
    )
    
    if results:
        # Print results
        engine.print_results(results)
        
        # Save results
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f'backtest_results_{instrument}_{timestamp}.json'
        engine.save_results(results, filename)
        
        print(f"\n✅ Backtest complete! Results saved to {filename}")
    else:
        print("\n❌ Backtest failed!")


if __name__ == "__main__":
    asyncio.run(main())

