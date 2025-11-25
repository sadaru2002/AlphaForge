import pandas as pd
import os
from datetime import datetime, timedelta
import logging
from oandapyV20 import API
from oandapyV20.endpoints.instruments import InstrumentsCandles
import asyncio

logger = logging.getLogger(__name__)

class DataManager:
    """
    Manages historical data fetching and caching to avoid repeated API calls.
    Supports saving/loading to Parquet (efficient) or CSV.
    """
    
    def __init__(self, api_key, cache_dir='data_cache'):
        self.api_key = api_key
        self.api = API(access_token=self.api_key, environment="practice")
        self.cache_dir = cache_dir
        
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)
            
    def get_data(self, instrument, start_date, end_date, granularity='M5', force_update=False):
        """
        Get data from cache or fetch from API if missing/outdated.
        """
        filename = f"{instrument}_{granularity}_{start_date}_{end_date}.parquet"
        filepath = os.path.join(self.cache_dir, filename)
        
        if not force_update and os.path.exists(filepath):
            logger.info(f"Loading cached data from {filepath}")
            try:
                df = pd.read_parquet(filepath)
                return df
            except Exception as e:
                logger.warning(f"Failed to read cache: {e}. Fetching fresh data.")
        
        # Fetch fresh data
        df = self._fetch_from_api(instrument, start_date, end_date, granularity)
        
        if not df.empty:
            # Save to cache
            try:
                df.to_parquet(filepath)
                logger.info(f"Saved data to cache: {filepath}")
            except Exception as e:
                logger.error(f"Failed to cache data: {e}")
                
        return df
    
    def _fetch_from_api(self, instrument, start_date, end_date, granularity):
        """Fetch data from OANDA API (synchronous wrapper)."""
        # This is a blocking call, but for data fetching scripts it's acceptable
        # or we can run it in an executor if needed.
        # Reusing logic from BacktestEngine but making it synchronous for simplicity in this utility
        
        logger.info(f"Fetching {instrument} {granularity} from {start_date} to {end_date}...")
        
        dt_start = datetime.strptime(start_date, '%Y-%m-%d')
        dt_end = datetime.strptime(end_date, '%Y-%m-%d')
        
        all_candles = []
        current = dt_start
        
        while current < dt_end:
            # OANDA limit
            count = 5000
            
            params = {
                "granularity": granularity,
                "count": count,
                "from": current.strftime('%Y-%m-%dT%H:%M:%SZ'),
                "price": "M"
            }
            
            try:
                r = InstrumentsCandles(instrument=instrument, params=params)
                self.api.request(r)
                candles = r.response.get('candles', [])
                
                if not candles:
                    break
                    
                all_candles.extend(candles)
                
                # Update current time
                last_time = candles[-1]['time'].replace('.000000000Z', '')
                current = datetime.strptime(last_time, '%Y-%m-%dT%H:%M:%S') + timedelta(minutes=5)
                
            except Exception as e:
                logger.error(f"API Error: {e}")
                break
                
        return self._process_candles(all_candles)

    def _process_candles(self, candles):
        """Convert OANDA candles to DataFrame."""
        data = []
        for candle in candles:
            if not candle.get('complete', False):
                continue
                
            time_str = candle['time'].replace('.000000000Z', '')
            
            mid = candle.get('mid', {})
            data.append({
                'timestamp': datetime.strptime(time_str, '%Y-%m-%dT%H:%M:%S'),
                'open': float(mid.get('o', 0)),
                'high': float(mid.get('h', 0)),
                'low': float(mid.get('l', 0)),
                'close': float(mid.get('c', 0)),
                'volume': int(candle.get('volume', 0))
            })
            
        df = pd.DataFrame(data)
        if not df.empty:
            df.set_index('timestamp', inplace=True)
            df.sort_index(inplace=True)
            
            # Ensure no duplicates
            df = df[~df.index.duplicated(keep='first')]
            
        return df
