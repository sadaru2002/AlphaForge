from .mt5_client import MT5Client
import pandas as pd
from typing import Dict, List, Optional
import logging
from datetime import datetime, timezone

logger = logging.getLogger(__name__)

class MultiTimeframeDataFetcher:
    """Fetch data across multiple timeframes for analysis"""
    
    def __init__(self, mt5_client: MT5Client):
        self.mt5 = mt5_client
    
    def fetch_all_data(self, symbol: str, timeframes: List[str] = None) -> Dict[str, pd.DataFrame]:
        """
        Fetch market data for all specified timeframes
        
        Args:
            symbol: Trading symbol
            timeframes: List of timeframes to fetch
            
        Returns:
            dict: {timeframe: DataFrame}
        """
        if timeframes is None:
            timeframes = ['M15', 'H1', 'H4', 'D1']
        
        data = {}
        
        for tf in timeframes:
            try:
                df = self.mt5.get_market_data(symbol, tf, bars=500)
                if df is not None and not df.empty:
                    data[tf] = df
                    logger.info(f"Successfully fetched {symbol} {tf}: {len(df)} bars")
                else:
                    logger.warning(f"Failed to fetch {symbol} {tf}")
            except Exception as e:
                logger.error(f"Error fetching {symbol} {tf}: {e}")
        
        logger.info(f"Fetched data for {symbol} across {len(data)} timeframes")
        return data
    
    def fetch_for_all_symbols(self, symbols: List[str], timeframes: List[str] = None) -> Dict[str, Dict[str, pd.DataFrame]]:
        """
        Fetch data for all symbols and all timeframes
        
        Args:
            symbols: List of trading symbols
            timeframes: List of timeframes to fetch
            
        Returns:
            dict: {symbol: {timeframe: DataFrame}}
        """
        all_data = {}
        
        for symbol in symbols:
            try:
                symbol_data = self.fetch_all_data(symbol, timeframes)
                if symbol_data:
                    all_data[symbol] = symbol_data
                    logger.info(f"Successfully fetched all data for {symbol}")
                else:
                    logger.warning(f"No data fetched for {symbol}")
            except Exception as e:
                logger.error(f"Error fetching data for {symbol}: {e}")
        
        return all_data
    
    def get_latest_candle(self, symbol: str, timeframe: str) -> Optional[Dict]:
        """Get the latest candle for a symbol"""
        try:
            df = self.mt5.get_market_data(symbol, timeframe, bars=1)
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                return {
                    'symbol': symbol,
                    'timeframe': timeframe,
                    'time': latest['time'],
                    'open': float(latest['open']),
                    'high': float(latest['high']),
                    'low': float(latest['low']),
                    'close': float(latest['close']),
                    'volume': int(latest['volume'])
                }
        except Exception as e:
            logger.error(f"Error getting latest candle for {symbol} {timeframe}: {e}")
        return None
    
    def validate_data_quality(self, df: pd.DataFrame, symbol: str, timeframe: str) -> bool:
        """
        Validate data quality
        
        Args:
            df: DataFrame to validate
            symbol: Symbol name
            timeframe: Timeframe
            
        Returns:
            bool: True if data is valid
        """
        if df is None or df.empty:
            logger.warning(f"No data for {symbol} {timeframe}")
            return False
        
        # Check for required columns
        required_columns = ['time', 'open', 'high', 'low', 'close', 'volume']
        missing_columns = [col for col in required_columns if col not in df.columns]
        if missing_columns:
            logger.warning(f"Missing columns for {symbol} {timeframe}: {missing_columns}")
            return False
        
        # Check for null values
        null_counts = df[required_columns].isnull().sum()
        if null_counts.any():
            logger.warning(f"Null values in {symbol} {timeframe}: {null_counts.to_dict()}")
            return False
        
        # Check for reasonable price values
        if (df['high'] < df['low']).any():
            logger.warning(f"Invalid OHLC data in {symbol} {timeframe}: high < low")
            return False
        
        if (df['high'] < df['open']).any() or (df['high'] < df['close']).any():
            logger.warning(f"Invalid OHLC data in {symbol} {timeframe}: high < open/close")
            return False
        
        if (df['low'] > df['open']).any() or (df['low'] > df['close']).any():
            logger.warning(f"Invalid OHLC data in {symbol} {timeframe}: low > open/close")
            return False
        
        # Check for reasonable volume
        if (df['volume'] < 0).any():
            logger.warning(f"Negative volume in {symbol} {timeframe}")
            return False
        
        logger.info(f"Data quality check passed for {symbol} {timeframe}")
        return True
    
    def get_data_summary(self, data: Dict[str, pd.DataFrame]) -> Dict[str, Dict]:
        """Get summary statistics for fetched data"""
        summary = {}
        
        for timeframe, df in data.items():
            if df is not None and not df.empty:
                latest = df.iloc[-1]
                summary[timeframe] = {
                    'bars_count': len(df),
                    'latest_time': latest['time'].strftime('%Y-%m-%d %H:%M:%S'),
                    'latest_close': float(latest['close']),
                    'price_range': {
                        'high': float(df['high'].max()),
                        'low': float(df['low'].min())
                    },
                    'volume_stats': {
                        'avg': float(df['volume'].mean()),
                        'max': int(df['volume'].max()),
                        'min': int(df['volume'].min())
                    }
                }
        
        return summary