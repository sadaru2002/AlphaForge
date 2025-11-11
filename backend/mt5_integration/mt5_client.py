try:
    import MetaTrader5 as mt5
    MT5_AVAILABLE = True
except ImportError:
    MT5_AVAILABLE = False
    # Mock MT5 for Linux/Mac compatibility
    class MockMT5:
        @staticmethod
        def initialize():
            return False
        @staticmethod
        def last_error():
            return (0, "MetaTrader5 is not available on this platform (Linux/Mac)")
    mt5 = MockMT5()

import pandas as pd
from datetime import datetime, timezone
import logging
from typing import Optional, Dict, Any, List
import platform

logger = logging.getLogger(__name__)

class MT5Client:
    """Handle all MT5 operations"""
    
    def __init__(self, login: int, password: str, server: str):
        self.login = login
        self.password = password
        self.server = server
        self.connected = False
    
    def connect(self) -> bool:
        """
        Initialize and login to MT5
        ✅ CRITICAL: This is your ONLY data source for signal generation
        """
        if not MT5_AVAILABLE:
            logger.warning("="*70)
            logger.warning("⚠️ MT5 NOT AVAILABLE")
            logger.warning("="*70)
            logger.warning(f"   Platform: {platform.system()}")
            logger.warning("   MetaTrader5 only works on Windows")
            logger.warning("   System will use OANDA as primary data source")
            logger.warning("="*70)
            return False
        
        try:
            logger.info("="*70)
            logger.info("🔌 MT5 CONNECTION ATTEMPT")
            logger.info("="*70)
            logger.info(f"   Server: {self.server}")
            logger.info(f"   Login: {self.login}")
            
            # Step 1: Initialize MT5
            if not mt5.initialize():
                error = mt5.last_error()
                logger.error(f"❌ MT5 initialization failed: {error}")
                logger.error("   Possible reasons:")
                logger.error("   1. MT5 terminal not running")
                logger.error("   2. MetaTrader5 library not installed")
                logger.error("   3. Terminal not responding")
                return False
            
            logger.info("✓ MT5 terminal initialized")
            
            # Step 2: Login to account
            authorized = mt5.login(
                login=self.login,
                password=self.password,
                server=self.server
            )
            
            if not authorized:
                error = mt5.last_error()
                logger.error(f"❌ MT5 login failed: {error}")
                logger.error("   Possible reasons:")
                logger.error("   1. Incorrect credentials")
                logger.error("   2. Server name wrong")
                logger.error("   3. No internet connection")
                mt5.shutdown()
                return False
            
            logger.info("✓ MT5 login successful")
            
            # Step 3: Get and display account info
            account_info = mt5.account_info()
            if account_info:
                logger.info(f"\n📊 Account Information:")
                logger.info(f"   Name: {account_info.name}")
                logger.info(f"   Login: {account_info.login}")
                logger.info(f"   Server: {account_info.server}")
                logger.info(f"   Balance: ${account_info.balance:,.2f}")
                logger.info(f"   Currency: {account_info.currency}")
                logger.info(f"   Leverage: 1:{account_info.leverage}")
            
            # Step 4: Verify data access
            if not self._verify_data_access():
                logger.error("❌ Data access verification failed")
                mt5.shutdown()
                return False
            
            self.connected = True
            logger.info("\n✅ MT5 CONNECTION ESTABLISHED")
            logger.info("   Status: READY FOR SIGNAL GENERATION")
            logger.info("="*70 + "\n")
            return True
            
        except Exception as e:
            logger.error(f"❌ MT5 connection error: {e}")
            return False
    
    def _verify_data_access(self) -> bool:
        """
        ✅ CRITICAL: Verify we're getting REAL data, not dummy data
        Tests data fetch for all trading symbols
        """
        logger.info("\n🔍 Verifying data access...")
        
        test_symbols = ['GBPUSD', 'USDJPY', 'XAUUSD']
        
        for symbol in test_symbols:
            try:
                # Try to fetch recent data
                rates = mt5.copy_rates_from_pos(symbol, mt5.TIMEFRAME_M15, 0, 10)
                
                if rates is None or len(rates) == 0:
                    logger.error(f"   ❌ {symbol}: No data available")
                    return False
                
                # Check data freshness
                latest_time = datetime.fromtimestamp(rates[-1]['time'], tz=timezone.utc)
                latest_price = rates[-1]['close']
                age_minutes = (datetime.now(timezone.utc) - latest_time).total_seconds() / 60
                
                if age_minutes > 60:
                    logger.warning(f"   ⚠️ {symbol}: Data is {age_minutes:.1f} minutes old")
                    return False
                else:
                    logger.info(f"   ✓ {symbol}: {latest_price:.5f} (age: {age_minutes:.1f} min)")
                    
            except Exception as e:
                logger.error(f"   ❌ {symbol}: Verification failed - {e}")
                return False
        
        logger.info("✓ Data access verified - ALL SYMBOLS OK\n")
        return True
    
    def disconnect(self):
        """Shutdown MT5 connection"""
        try:
            mt5.shutdown()
            self.connected = False
            logger.info("Disconnected from MT5")
        except Exception as e:
            logger.error(f"Error disconnecting from MT5: {e}")
    
    def get_market_data(self, symbol: str, timeframe_str: str, bars: int = 500) -> Optional[pd.DataFrame]:
        """
        Fetch OHLCV data for a symbol
        ✅ This is REAL MT5 data - THE ONLY SOURCE for signal generation
        
        Args:
            symbol: Trading symbol (XAUUSD, GBPUSD, etc.)
            timeframe_str: Timeframe string (M15, H1, H4, D1)
            bars: Number of bars to fetch
            
        Returns:
            DataFrame with OHLCV data or None if failed
        """
        if not self.connected:
            logger.warning(f"MT5 not connected, attempting to connect...")
            if not self.connect():
                logger.error("❌ Cannot fetch data - MT5 not connected")
                return None
        
        # Convert timeframe string to MT5 constant
        timeframe_map = {
            'M1': mt5.TIMEFRAME_M1,
            'M5': mt5.TIMEFRAME_M5,
            'M15': mt5.TIMEFRAME_M15,
            'M30': mt5.TIMEFRAME_M30,
            'H1': mt5.TIMEFRAME_H1,
            'H4': mt5.TIMEFRAME_H4,
            'D1': mt5.TIMEFRAME_D1
        }
        
        timeframe = timeframe_map.get(timeframe_str)
        if not timeframe:
            logger.error(f"Invalid timeframe: {timeframe_str}")
            return None
        
        try:
            # Fetch data from MT5
            logger.debug(f"📥 Fetching MT5 data: {symbol} {timeframe_str} ({bars} bars)...")
            rates = mt5.copy_rates_from_pos(symbol, timeframe, 0, bars)
            
            if rates is None or len(rates) == 0:
                error = mt5.last_error()
                logger.error(f"❌ Failed to fetch {symbol} {timeframe_str}: {error}")
                return None
            
            # Convert to DataFrame
            df = pd.DataFrame(rates)
            df['time'] = pd.to_datetime(df['time'], unit='s', utc=True)
            
            # Rename columns to match our convention
            df = df.rename(columns={'tick_volume': 'volume'})
            
            # ✅ CRITICAL: Validate data freshness
            latest_time = df.iloc[-1]['time']
            latest_price = df.iloc[-1]['close']
            age_minutes = (datetime.now(timezone.utc) - latest_time).total_seconds() / 60
            
            logger.info(f"✅ REAL MT5 DATA: {symbol} {timeframe_str}")
            logger.debug(f"   Bars fetched: {len(df)}")
            logger.debug(f"   Latest price: {latest_price:.5f}")
            logger.debug(f"   Latest time: {latest_time}")
            logger.debug(f"   Data age: {age_minutes:.1f} minutes")
            
            # Warn if data is old
            if age_minutes > 60:
                logger.warning(f"⚠️ Data is {age_minutes:.1f} minutes old (may be stale)")
            elif age_minutes > 5:
                logger.warning(f"⚠️ Data is {age_minutes:.1f} minutes old")
            
            return df
            
        except Exception as e:
            logger.error(f"❌ Error fetching market data for {symbol} {timeframe_str}: {e}")
            return None
    
    def get_current_price(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get current bid/ask price"""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            tick = mt5.symbol_info_tick(symbol)
            if tick is None:
                logger.error(f"Failed to get tick data for {symbol}")
                return None
            
            return {
                'symbol': symbol,
                'bid': tick.bid,
                'ask': tick.ask,
                'spread': (tick.ask - tick.bid) * 10000,  # in pips
                'time': datetime.fromtimestamp(tick.time, tz=timezone.utc)
            }
        except Exception as e:
            logger.error(f"Error getting current price for {symbol}: {e}")
            return None
    
    def get_account_info(self) -> Optional[Dict[str, Any]]:
        """Get account balance and equity"""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            info = mt5.account_info()
            if info is None:
                logger.error("Failed to get account info")
                return None
            
            return {
                'login': info.login,
                'balance': info.balance,
                'equity': info.equity,
                'profit': info.profit,
                'margin': info.margin,
                'margin_free': info.margin_free,
                'currency': info.currency,
                'leverage': info.leverage,
                'server': info.server
            }
        except Exception as e:
            logger.error(f"Error getting account info: {e}")
            return None
    
    def get_symbol_info(self, symbol: str) -> Optional[Dict[str, Any]]:
        """Get symbol information"""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            info = mt5.symbol_info(symbol)
            if info is None:
                logger.error(f"Symbol {symbol} not found")
                return None
            
            return {
                'symbol': symbol,
                'point': info.point,
                'digits': info.digits,
                'spread': info.spread,
                'trade_mode': info.trade_mode,
                'trade_stops_level': info.trade_stops_level,
                'trade_freeze_level': info.trade_freeze_level,
                'volume_min': info.volume_min,
                'volume_max': info.volume_max,
                'volume_step': info.volume_step,
                'margin_initial': info.margin_initial,
                'margin_maintenance': info.margin_maintenance
            }
        except Exception as e:
            logger.error(f"Error getting symbol info for {symbol}: {e}")
            return None
    
    def is_market_open(self, symbol: str) -> bool:
        """Check if market is open for trading"""
        if not self.connected:
            if not self.connect():
                return False
        
        try:
            info = mt5.symbol_info(symbol)
            if info is None:
                return False
            
            # Check if trading is allowed
            return info.trade_mode in [0, 1]  # 0 = long only, 1 = both directions
        except Exception as e:
            logger.error(f"Error checking market status for {symbol}: {e}")
            return False
    
    def get_server_time(self) -> Optional[datetime]:
        """Get server time"""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            time = mt5.symbol_info_tick("EURUSD")  # Use any symbol to get server time
            if time is None:
                return None
            return datetime.fromtimestamp(time.time, tz=timezone.utc)
        except Exception as e:
            logger.error(f"Error getting server time: {e}")
            return None