"""
AlphaForge Trading Strategy - Oanda API Implementation
Converted from Pine Script v5 to Python
Supports: XAUUSD, GBPUSD, USDJPY on 5-minute timeframe
Multi-filter technical analysis with ALMA/TEMA/HullMA base
"""

import pandas as pd
import numpy as np
from oandapyV20 import API
import oandapyV20.endpoints.instruments as instruments
import oandapyV20.endpoints.orders as orders
import oandapyV20.endpoints.positions as positions
import oandapyV20.endpoints.accounts as accounts
from datetime import datetime, timedelta
import time
import pandas_ta as ta
from typing import Tuple, Optional
import logging
import pytz

# Setup logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class OandaConfig:
    """Oanda API Configuration"""
    def __init__(self, access_token: str, account_id: str, environment: str = "practice"):
        self.access_token = access_token
        self.account_id = account_id
        self.environment = environment  # "practice" or "live"
        

class StrategyConfig:
    """Strategy Parameters - Import from strategy_variables.py"""
    def __init__(self):
        # Import configuration from strategy_variables
        try:
            import strategy_variables as sv
            
            # Main Strategy Parameters
            self.TIMEFRAME = sv.TIMEFRAME
            self.USE_ALTERNATE_SIGNALS = sv.USE_ALTERNATE_SIGNALS
            self.ALTERNATE_MULTIPLIER = sv.ALTERNATE_MULTIPLIER
            self.BASIS_TYPE = sv.BASIS_TYPE
            self.BASIS_LENGTH = sv.BASIS_LENGTH
            self.OFFSET_SIGMA = sv.OFFSET_SIGMA
            self.OFFSET_ALMA = sv.OFFSET_ALMA
            self.DELAY_OFFSET = sv.DELAY_OFFSET
            
            # RSI Parameters
            self.RSI_PERIOD = sv.RSI_PERIOD
            self.RSI_OVERBOUGHT = sv.RSI_OVERBOUGHT
            self.RSI_OVERSOLD = sv.RSI_OVERSOLD
            
            # Filter Parameters
            self.ENABLE_ATR_FILTER_1 = sv.ENABLE_ATR_FILTER_1
            self.ENABLE_ATR_FILTER_2 = sv.ENABLE_ATR_FILTER_2
            self.ENABLE_VOLUME_FILTER = sv.ENABLE_VOLUME_FILTER
            self.ENABLE_RSI_EMA_FILTER = sv.ENABLE_RSI_EMA_FILTER
            self.ENABLE_EMA_FILTER = sv.ENABLE_EMA_FILTER
            self.EMA_LENGTH = sv.EMA_LENGTH
            self.ENABLE_ADX_FILTER = sv.ENABLE_ADX_FILTER
            self.ADX_SMOOTHING = sv.ADX_SMOOTHING
            self.ADX_DI_LENGTH = sv.ADX_DI_LENGTH
            self.ADX_THRESHOLD = sv.ADX_THRESHOLD
            self.ENABLE_RSI_FILTER = sv.ENABLE_RSI_FILTER
            self.ENABLE_BB_FILTER = sv.ENABLE_BB_FILTER
            
            # Volume multiplier
            self.VOLUME_MULTIPLIER = getattr(sv, 'VOLUME_MULTIPLIER', 1.5)
            
            # Risk Management
            self.INITIAL_CAPITAL = sv.INITIAL_CAPITAL
            self.POSITION_SIZE_PCT = sv.POSITION_SIZE_PCT
            self.STOP_LOSS_POINTS = sv.STOP_LOSS_POINTS
            self.TAKE_PROFIT_POINTS = sv.TAKE_PROFIT_POINTS
            self.COMMISSION_PCT = sv.COMMISSION_PCT
            
            # DEMA ATR Parameters
            self.USE_HA_CANDLES = sv.USE_HA_CANDLES
            self.DEMA_PERIOD = sv.DEMA_PERIOD
            self.ATR_PERIOD = sv.ATR_PERIOD
            self.ATR_FACTOR = sv.ATR_FACTOR
            
            # ALMA Ribbon Parameters
            self.USE_MOVING_AVERAGES = sv.USE_MOVING_AVERAGES
            self.ALMA_MAIN_LENGTH = sv.ALMA_MAIN_LENGTH
            
            # Lookback for historical data
            self.LOOKBACK_BARS = sv.LOOKBACK_BARS
            
        except ImportError:
            # Fallback to default values if strategy_variables not found
            logger.warning("Could not import strategy_variables, using defaults")
            self._set_defaults()
    
    def _set_defaults(self):
        """Set default values if strategy_variables import fails"""
        self.TIMEFRAME = "M5"
        self.USE_ALTERNATE_SIGNALS = True
        self.ALTERNATE_MULTIPLIER = 18
        self.BASIS_TYPE = "ALMA"
        self.BASIS_LENGTH = 2
        self.OFFSET_SIGMA = 5
        self.OFFSET_ALMA = 0.85
        self.DELAY_OFFSET = 0
        self.RSI_PERIOD = 14
        self.RSI_OVERBOUGHT = 70
        self.RSI_OVERSOLD = 30
        self.ENABLE_ATR_FILTER_1 = False
        self.ENABLE_ATR_FILTER_2 = False
        self.ENABLE_VOLUME_FILTER = False
        self.ENABLE_RSI_EMA_FILTER = False
        self.ENABLE_EMA_FILTER = False
        self.EMA_LENGTH = 200
        self.ENABLE_ADX_FILTER = False
        self.ADX_SMOOTHING = 14
        self.ADX_DI_LENGTH = 14
        self.ADX_THRESHOLD = 25
        self.ENABLE_RSI_FILTER = False
        self.ENABLE_BB_FILTER = False
        self.INITIAL_CAPITAL = 5000
        self.POSITION_SIZE_PCT = 50
        self.STOP_LOSS_POINTS = 0
        self.TAKE_PROFIT_POINTS = 0
        self.COMMISSION_PCT = 0.02
        self.USE_HA_CANDLES = True
        self.DEMA_PERIOD = 7
        self.ATR_PERIOD = 14
        self.ATR_FACTOR = 1.7
        self.USE_MOVING_AVERAGES = False
        self.ALMA_MAIN_LENGTH = 423
        self.LOOKBACK_BARS = 500


class DataHandler:
    """Handles all data fetching and processing from Oanda"""
    
    def __init__(self, config: OandaConfig):
        self.client = API(access_token=config.access_token, environment=config.environment)
        self.account_id = config.account_id
        
    def fetch_historical_data(self, instrument: str, granularity: str = "M5", count: int = 500) -> pd.DataFrame:
        """Fetch historical OHLCV data from Oanda"""
        try:
            params = {
                "count": count,
                "granularity": granularity,
                "price": "MBA"  # Mid, Bid, Ask
            }
            
            r = instruments.InstrumentsCandles(instrument=instrument, params=params)
            self.client.request(r)
            
            # New York timezone (UTC-4)
            ny_tz = pytz.timezone('America/New_York')
            
            data = []
            for candle in r.response['candles']:
                if candle['complete']:
                    # Convert UTC time to NY time
                    utc_time = pd.to_datetime(candle['time'])
                    ny_time = utc_time.tz_convert(ny_tz)
                    
                    data.append({
                        'time': ny_time,
                        'open': float(candle['mid']['o']),
                        'high': float(candle['mid']['h']),
                        'low': float(candle['mid']['l']),
                        'close': float(candle['mid']['c']),
                        'volume': int(candle['volume'])
                    })
            
            df = pd.DataFrame(data)
            df.set_index('time', inplace=True)
            
            logger.info(f"Fetched {len(df)} bars for {instrument} (Times in NY UTC-4)")
            return df
            
        except Exception as e:
            logger.error(f"Error fetching data for {instrument}: {e}")
            return pd.DataFrame()
    
    def get_latest_candle(self, instrument: str, granularity: str = "M5") -> Optional[pd.Series]:
        """Get the most recent completed candle"""
        df = self.fetch_historical_data(instrument, granularity, count=1)
        return df.iloc[-1] if not df.empty else None


class TechnicalIndicators:
    """All technical indicator calculations"""
    
    @staticmethod
    def calculate_heikinashi(df: pd.DataFrame) -> pd.DataFrame:
        """Calculate Heikin Ashi candles"""
        ha_df = df.copy()
        
        ha_df['ha_close'] = (df['open'] + df['high'] + df['low'] + df['close']) / 4
        ha_df['ha_open'] = 0.0
        
        for i in range(len(df)):
            if i == 0:
                ha_df.loc[ha_df.index[i], 'ha_open'] = (df['open'].iloc[i] + df['close'].iloc[i]) / 2
            else:
                ha_df.loc[ha_df.index[i], 'ha_open'] = (ha_df['ha_open'].iloc[i-1] + ha_df['ha_close'].iloc[i-1]) / 2
        
        ha_df['ha_high'] = ha_df[['high', 'ha_open', 'ha_close']].max(axis=1)
        ha_df['ha_low'] = ha_df[['low', 'ha_open', 'ha_close']].min(axis=1)
        
        return ha_df
    
    @staticmethod
    def calculate_alma(series: pd.Series, length: int = 9, offset: float = 0.85, sigma: float = 6) -> pd.Series:
        """Calculate Arnaud Legoux Moving Average"""
        m = offset * (length - 1)
        s = length / sigma
        
        alma = pd.Series(index=series.index, dtype=float)
        wtd_sum = 0.0
        cum_wt = 0.0
        
        for i in range(length):
            wt = np.exp(-((i - m) ** 2) / (2 * s * s))
            wtd_sum += wt
        
        for i in range(length - 1, len(series)):
            cum_wt = 0.0
            cum_val = 0.0
            for j in range(length):
                wt = np.exp(-((j - m) ** 2) / (2 * s * s))
                cum_val += series.iloc[i - length + 1 + j] * wt
                cum_wt += wt
            alma.iloc[i] = cum_val / cum_wt
        
        return alma
    
    @staticmethod
    def calculate_tema(series: pd.Series, length: int) -> pd.Series:
        """Calculate Triple Exponential Moving Average"""
        ema1 = series.ewm(span=length, adjust=False).mean()
        ema2 = ema1.ewm(span=length, adjust=False).mean()
        ema3 = ema2.ewm(span=length, adjust=False).mean()
        tema = 3 * ema1 - 3 * ema2 + ema3
        return tema
    
    @staticmethod
    def calculate_hull_ma(series: pd.Series, length: int) -> pd.Series:
        """Calculate Hull Moving Average"""
        half_length = int(length / 2)
        sqrt_length = int(np.sqrt(length))
        
        wma_half = series.rolling(window=half_length).apply(
            lambda x: np.sum(x * np.arange(1, half_length + 1)) / np.sum(np.arange(1, half_length + 1)), raw=True
        )
        wma_full = series.rolling(window=length).apply(
            lambda x: np.sum(x * np.arange(1, length + 1)) / np.sum(np.arange(1, length + 1)), raw=True
        )
        
        raw_hma = 2 * wma_half - wma_full
        hull_ma = raw_hma.rolling(window=sqrt_length).apply(
            lambda x: np.sum(x * np.arange(1, sqrt_length + 1)) / np.sum(np.arange(1, sqrt_length + 1)), raw=True
        )
        
        return hull_ma
    
    @staticmethod
    def calculate_variant_ma(df: pd.DataFrame, ma_type: str, source_col: str, length: int, 
                            offset_sigma: int, offset_alma: float) -> pd.Series:
        """Calculate moving average based on type"""
        series = df[source_col]
        
        if ma_type == 'ALMA':
            return TechnicalIndicators.calculate_alma(series, length, offset_alma, offset_sigma)
        elif ma_type == 'TEMA':
            return TechnicalIndicators.calculate_tema(series, length)
        elif ma_type == 'HullMA':
            return TechnicalIndicators.calculate_hull_ma(series, length)
        else:
            return series.rolling(window=length).mean()  # Default SMA
    
    @staticmethod
    def calculate_rsi(series: pd.Series, period: int = 14) -> pd.Series:
        """Calculate RSI"""
        return ta.rsi(series, length=period)
    
    @staticmethod
    def calculate_atr(df: pd.DataFrame, period: int = 14) -> pd.Series:
        """Calculate Average True Range"""
        return ta.atr(df['high'], df['low'], df['close'], length=period)
    
    @staticmethod
    def calculate_adx(df: pd.DataFrame, length: int = 14) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate ADX, +DI, -DI"""
        adx_df = ta.adx(df['high'], df['low'], df['close'], length=length)
        return adx_df[f'ADX_{length}'], adx_df[f'DMP_{length}'], adx_df[f'DMN_{length}']
    
    @staticmethod
    def calculate_bollinger_bands(series: pd.Series, length: int = 20, std: float = 2.0) -> Tuple[pd.Series, pd.Series, pd.Series]:
        """Calculate Bollinger Bands"""
        bb = ta.bbands(series, length=length, std=std)
        
        # pandas_ta returns different column names depending on version
        # Try different naming conventions
        try:
            middle = bb[f'BBM_{length}_{std}']
            upper = bb[f'BBU_{length}_{std}']
            lower = bb[f'BBL_{length}_{std}']
        except KeyError:
            try:
                middle = bb[f'BBM_{length}_{int(std)}']
                upper = bb[f'BBU_{length}_{int(std)}']
                lower = bb[f'BBL_{length}_{int(std)}']
            except KeyError:
                # Fallback to manual calculation
                middle = series.rolling(window=length).mean()
                rolling_std = series.rolling(window=length).std()
                upper = middle + (rolling_std * std)
                lower = middle - (rolling_std * std)
        
        return middle, upper, lower


class StrategyEngine:
    """Main strategy logic"""
    
    def __init__(self, config: StrategyConfig):
        self.config = config
        
    def add_indicators(self, df: pd.DataFrame) -> pd.DataFrame:
        """Add all technical indicators to dataframe"""
        
        # Heikin Ashi if enabled
        if self.config.USE_HA_CANDLES:
            ha_df = TechnicalIndicators.calculate_heikinashi(df)
            df['ha_close'] = ha_df['ha_close']
            df['ha_open'] = ha_df['ha_open']
            source_close = 'ha_close'
            source_open = 'ha_open'
        else:
            source_close = 'close'
            source_open = 'open'
        
        # Main MA series (with delay offset)
        if self.config.DELAY_OFFSET > 0:
            df['close_delayed'] = df[source_close].shift(self.config.DELAY_OFFSET)
            df['open_delayed'] = df[source_open].shift(self.config.DELAY_OFFSET)
            ma_close_source = 'close_delayed'
            ma_open_source = 'open_delayed'
        else:
            ma_close_source = source_close
            ma_open_source = source_open
        
        # Calculate close and open series
        df['close_series'] = TechnicalIndicators.calculate_variant_ma(
            df, self.config.BASIS_TYPE, ma_close_source, 
            self.config.BASIS_LENGTH, self.config.OFFSET_SIGMA, self.config.OFFSET_ALMA
        )
        
        df['open_series'] = TechnicalIndicators.calculate_variant_ma(
            df, self.config.BASIS_TYPE, ma_open_source,
            self.config.BASIS_LENGTH, self.config.OFFSET_SIGMA, self.config.OFFSET_ALMA
        )
        
        # Apply alternate timeframe resolution if enabled
        if self.config.USE_ALTERNATE_SIGNALS:
            resample_minutes = 5 * self.config.ALTERNATE_MULTIPLIER
            df_resampled = df[['close_series', 'open_series']].resample(f'{resample_minutes}min').last()
            df_resampled = df_resampled.ffill()
            df['close_series_alt'] = df_resampled['close_series'].reindex(df.index, method='ffill')
            df['open_series_alt'] = df_resampled['open_series'].reindex(df.index, method='ffill')
        else:
            df['close_series_alt'] = df['close_series']
            df['open_series_alt'] = df['open_series']
        
        # RSI
        df['rsi'] = TechnicalIndicators.calculate_rsi(df['close'], self.config.RSI_PERIOD)
        df['rsi_ema'] = df['rsi'].ewm(span=20, adjust=False).mean()
        df['rsi_ob'] = (df['rsi'] > 60) & (df['rsi'] > df['rsi_ema'])
        df['rsi_os'] = (df['rsi'] < 40) & (df['rsi'] < df['rsi_ema'])
        
        # EMA 20
        df['ema_20'] = df['close'].ewm(span=20, adjust=False).mean()
        df['ema_bull'] = df['close'] > df['ema_20']
        
        # ATR
        df['atr'] = TechnicalIndicators.calculate_atr(df, 14)
        
        # EMA 200
        df['ema_200'] = df['close'].ewm(span=200, adjust=False).mean()
        
        # ADX
        df['adx'], df['di_plus'], df['di_minus'] = TechnicalIndicators.calculate_adx(df, 14)
        
        # Volume
        df['volume_sma'] = df['volume'].rolling(window=14).mean()
        
        return df
    
    def apply_filters(self, df: pd.DataFrame) -> pd.DataFrame:
        """Apply all enabled filters"""
        
        # Initialize all filters as True (no filtering)
        df['atr_cond_bull'] = True
        df['atr_cond_bear'] = True
        df['atr_cond_2'] = True
        df['volume_filter'] = True
        df['rsi_ema_filter_bull'] = True
        df['rsi_ema_filter_bear'] = True
        df['ema_filter_bull'] = True
        df['ema_filter_bear'] = True
        df['adx_filter'] = True
        df['rsi_filter_long'] = True
        df['rsi_filter_short'] = True
        df['bb_filter_long'] = True
        df['bb_filter_short'] = True
        
        # Apply volume filter if enabled
        if self.config.ENABLE_VOLUME_FILTER:
            df['volume_threshold'] = df['volume_sma'] * self.config.VOLUME_MULTIPLIER
            df['volume_filter'] = df['volume'] > df['volume_threshold']
        
        return df
    
    def generate_signals(self, df: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals"""
        
        # Crossover signals using alternate timeframe series
        df['cross_long'] = (df['close_series_alt'] > df['open_series_alt']) & \
                          (df['close_series_alt'].shift(1) <= df['open_series_alt'].shift(1))
        
        df['cross_short'] = (df['close_series_alt'] < df['open_series_alt']) & \
                           (df['close_series_alt'].shift(1) >= df['open_series_alt'].shift(1))
        
        # Long entry trigger
        df['long_trigger'] = (
            df['cross_long'] &
            df['rsi_filter_long'] &
            df['bb_filter_long'] &
            df['ema_filter_bull'] &
            df['atr_cond_2'] &
            df['atr_cond_bull'] &
            df['volume_filter'] &
            df['rsi_ema_filter_bull'] &
            df['adx_filter']
        )
        
        # Short entry trigger
        df['short_trigger'] = (
            df['cross_short'] &
            df['rsi_filter_short'] &
            df['bb_filter_short'] &
            df['ema_filter_bear'] &
            df['atr_cond_2'] &
            df['atr_cond_bear'] &
            df['volume_filter'] &
            df['rsi_ema_filter_bear'] &
            df['adx_filter']
        )
        
        return df
