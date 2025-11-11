"""
OANDA Live Price Feed Integration
Fetches real-time prices for frontend and live monitoring
"""

import requests
import logging
from typing import Dict, Optional, List
from datetime import datetime, timezone
import asyncio
import json

logger = logging.getLogger(__name__)


class OANDAClient:
    """Handle OANDA API operations for live price feeds"""
    
    def __init__(self, api_key: str, account_id: str, base_url: str = "https://api-fxpractice.oanda.com/v3"):
        self.api_key = api_key
        self.account_id = account_id
        self.base_url = base_url
        self.headers = {
            "Authorization": f"Bearer {api_key}",
            "AcceptDatetimeFormat": "UNIX",
            "Content-Type": "application/json"
        }
        self.connected = False
        
    def connect(self) -> bool:
        """Verify OANDA connection"""
        try:
            response = requests.get(
                f"{self.base_url}/accounts/{self.account_id}",
                headers=self.headers,
                timeout=10
            )
            if response.status_code == 200:
                account_data = response.json()
                logger.info(f"Connected to OANDA: Account {self.account_id}")
                logger.info(f"Balance: {account_data['account']['balance']}")
                self.connected = True
                return True
            else:
                logger.error(f"OANDA connection failed: {response.status_code} - {response.text}")
                return False
        except Exception as e:
            logger.error(f"OANDA connection error: {e}")
            return False
    
    def get_live_prices(self, symbols: List[str]) -> Dict[str, Dict]:
        """
        Get current live prices for multiple symbols
        
        Args:
            symbols: List of instrument names (e.g., ['XAU_USD', 'GBP_USD', 'USD_JPY'])
            
        Returns:
            Dict with current prices for each symbol
        """
        if not self.connected:
            if not self.connect():
                return {}
        
        try:
            # OANDA uses different format (XAU_USD instead of XAUUSD)
            oanda_instruments = ",".join(symbols)
            
            response = requests.get(
                f"{self.base_url}/accounts/{self.account_id}/pricing",
                headers=self.headers,
                params={"instruments": oanda_instruments},
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                prices = {}
                
                for price_data in data.get('prices', []):
                    instrument = price_data['instrument']
                    prices[instrument] = {
                        'bid': float(price_data['bids'][0]['price']) if price_data['bids'] else None,
                        'ask': float(price_data['asks'][0]['price']) if price_data['asks'] else None,
                        'time': price_data['time'],
                        'bid_volume': float(price_data['bids'][0]['liquidity']) if price_data['bids'] else 0,
                        'ask_volume': float(price_data['asks'][0]['liquidity']) if price_data['asks'] else 0,
                    }
                
                logger.debug(f"Fetched live prices for {len(prices)} instruments")
                return prices
            else:
                logger.error(f"Failed to fetch prices: {response.status_code}")
                return {}
                
        except Exception as e:
            logger.error(f"Error fetching live prices: {e}")
            return {}
    
    def get_single_price(self, symbol: str) -> Optional[Dict]:
        """
        Get current price for a single symbol
        
        Args:
            symbol: OANDA instrument name (e.g., 'XAU_USD')
            
        Returns:
            Price data or None if failed
        """
        prices = self.get_live_prices([symbol])
        return prices.get(symbol) if prices else None
    
    def get_historical_data(self, symbol: str, granularity: str = "M15", count: int = 300) -> Optional[Dict]:
        """
        Get historical candle data from OANDA
        
        Args:
            symbol: OANDA instrument name
            granularity: Candle granularity (M15, H1, H4, D)
            count: Number of candles to fetch
            
        Returns:
            Candle data or None if failed
        """
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            response = requests.get(
                f"{self.base_url}/instruments/{symbol}/candles",
                headers=self.headers,
                params={
                    "granularity": granularity,
                    "count": count,
                    "price": "MBA"  # Mid, Bid, Ask
                },
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                logger.info(f"Fetched {len(data['candles'])} candles for {symbol} {granularity}")
                return data
            else:
                logger.error(f"Failed to fetch historical data: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching historical data: {e}")
            return None
    
    def get_account_summary(self) -> Optional[Dict]:
        """Get account summary with balance, positions, etc."""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            response = requests.get(
                f"{self.base_url}/accounts/{self.account_id}",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Failed to fetch account summary: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching account summary: {e}")
            return None
    
    def get_open_positions(self) -> Optional[List[Dict]]:
        """Get all open positions"""
        account = self.get_account_summary()
        if account:
            return account.get('account', {}).get('positions', [])
        return None
    
    def get_open_trades(self) -> Optional[List[Dict]]:
        """Get all open trades"""
        if not self.connected:
            if not self.connect():
                return None
        
        try:
            response = requests.get(
                f"{self.base_url}/accounts/{self.account_id}/openTrades",
                headers=self.headers,
                timeout=10
            )
            
            if response.status_code == 200:
                data = response.json()
                return data.get('trades', [])
            else:
                logger.error(f"Failed to fetch open trades: {response.status_code}")
                return None
                
        except Exception as e:
            logger.error(f"Error fetching open trades: {e}")
            return None


class OANDAPriceStreamer:
    """Async streaming of live prices from OANDA"""
    
    def __init__(self, client: OANDAClient):
        self.client = client
        self.stream_url = "https://stream-fxpractice.oanda.com/v3"
        self.is_streaming = False
        self.callbacks = []
    
    def add_callback(self, callback):
        """Add callback function to be called when new price data arrives"""
        self.callbacks.append(callback)
    
    async def stream_prices(self, symbols: List[str]):
        """
        Stream live prices for multiple symbols
        
        Args:
            symbols: List of OANDA instrument names
        """
        if not self.client.connected:
            if not self.client.connect():
                logger.error("Cannot stream prices - not connected to OANDA")
                return
        
        self.is_streaming = True
        
        try:
            instruments_str = ",".join(symbols)
            
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    f"{self.stream_url}/accounts/{self.client.account_id}/pricing/stream",
                    headers=self.client.headers,
                    params={"instruments": instruments_str},
                    timeout=aiohttp.ClientTimeout(total=None)
                ) as response:
                    
                    if response.status != 200:
                        logger.error(f"Stream connection failed: {response.status}")
                        self.is_streaming = False
                        return
                    
                    async for line in response.content:
                        if not self.is_streaming:
                            break
                        
                        try:
                            data = json.loads(line.decode('utf-8'))
                            
                            # Call all registered callbacks
                            for callback in self.callbacks:
                                await callback(data)
                                
                        except json.JSONDecodeError:
                            continue
                        except Exception as e:
                            logger.error(f"Error processing stream data: {e}")
        
        except Exception as e:
            logger.error(f"Stream error: {e}")
        finally:
            self.is_streaming = False
    
    def stop_streaming(self):
        """Stop the price stream"""
        self.is_streaming = False
        logger.info("Price stream stopped")


# Symbol mapping between MT5 and OANDA
SYMBOL_MAPPING = {
    'XAUUSD': 'XAU_USD',
    'GBPUSD': 'GBP_USD',
    'USDJPY': 'USD_JPY',
    'EURUSD': 'EUR_USD',
}

def mt5_to_oanda(symbol: str) -> str:
    """Convert MT5 symbol to OANDA format"""
    return SYMBOL_MAPPING.get(symbol, symbol.replace('USD', '_USD'))

def oanda_to_mt5(symbol: str) -> str:
    """Convert OANDA symbol to MT5 format"""
    reverse_map = {v: k for k, v in SYMBOL_MAPPING.items()}
    return reverse_map.get(symbol, symbol.replace('_USD', 'USD'))
