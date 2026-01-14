#!/usr/bin/env python3
"""
Signal Tracker - Automatically updates signal status based on price action.

Features:
1. Checks if Take Profit (TP) was hit -> Status = WON
2. Checks if Stop Loss (SL) was hit -> Status = LOST  
3. Expires signals after 4 hours if neither hit -> Status = EXPIRED

Runs every minute to check PENDING signals against current prices.
"""
import asyncio
import logging
import os
import sys
from datetime import datetime, timedelta
from oandapyV20 import API
from oandapyV20.endpoints.pricing import PricingInfo

# Add parent directory to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.connection import get_db
from database.signal_models import TradingSignal, SignalStatus

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("signal_tracker.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("SignalTracker")

# OANDA Configuration
OANDA_API_KEY = os.getenv("OANDA_API_KEY")
OANDA_ACCOUNT_ID = os.getenv("OANDA_ACCOUNT_ID")
OANDA_ENVIRONMENT = os.getenv("OANDA_ENVIRONMENT", "practice")

# Settings
EXPIRATION_HOURS = 4  # Expire signals after 4 hours if no TP/SL hit
CHECK_INTERVAL_SECONDS = 60  # Check every minute

# Symbol mapping (DB symbol -> OANDA instrument)
SYMBOL_TO_INSTRUMENT = {
    'GBP/USD': 'GBP_USD',
    'GOLD': 'XAU_USD',
    'USD/JPY': 'USD_JPY'
}


class SignalTracker:
    def __init__(self):
        self.api = API(access_token=OANDA_API_KEY, environment=OANDA_ENVIRONMENT)
        self.stats = {
            'won': 0,
            'lost': 0,
            'expired': 0,
            'checked': 0
        }
    
    def get_current_price(self, symbol: str) -> dict:
        """Fetch current bid/ask price from OANDA."""
        instrument = SYMBOL_TO_INSTRUMENT.get(symbol)
        if not instrument:
            logger.warning(f"Unknown symbol: {symbol}")
            return None
        
        try:
            params = {"instruments": instrument}
            r = PricingInfo(accountID=OANDA_ACCOUNT_ID, params=params)
            response = self.api.request(r)
            
            if response and 'prices' in response and len(response['prices']) > 0:
                price_data = response['prices'][0]
                return {
                    'bid': float(price_data['bids'][0]['price']),
                    'ask': float(price_data['asks'][0]['price']),
                    'mid': (float(price_data['bids'][0]['price']) + float(price_data['asks'][0]['price'])) / 2
                }
        except Exception as e:
            logger.error(f"Error fetching price for {symbol}: {e}")
        
        return None
    
    def check_signal_outcome(self, signal: TradingSignal, current_price: float) -> str:
        """
        Check if signal hit TP or SL.
        
        Returns:
            'WON' if TP hit
            'LOST' if SL hit
            'PENDING' if neither
        """
        entry = signal.entry
        tp = signal.tp1
        sl = signal.stop_loss
        direction = signal.direction.upper()
        
        if direction == 'BUY':
            # BUY: Win if price >= TP, Loss if price <= SL
            if current_price >= tp:
                return 'WON'
            elif current_price <= sl:
                return 'LOST'
        elif direction == 'SELL':
            # SELL: Win if price <= TP, Loss if price >= SL
            if current_price <= tp:
                return 'WON'
            elif current_price >= sl:
                return 'LOST'
        
        return 'PENDING'
    
    def check_expiration(self, signal: TradingSignal) -> bool:
        """Check if signal should be expired (older than 4 hours)."""
        if signal.timestamp:
            age = datetime.utcnow() - signal.timestamp
            return age.total_seconds() > (EXPIRATION_HOURS * 3600)
        return False
    
    def process_pending_signals(self):
        """Process all PENDING signals and update their status."""
        db = next(get_db())
        
        try:
            # Get all PENDING signals
            pending_signals = db.query(TradingSignal).filter(
                TradingSignal.status == SignalStatus.PENDING
            ).all()
            
            logger.info(f"📊 Checking {len(pending_signals)} PENDING signals...")
            
            for signal in pending_signals:
                self.stats['checked'] += 1
                
                # Get current price
                price_data = self.get_current_price(signal.symbol)
                if not price_data:
                    continue
                
                current_price = price_data['mid']
                
                # Check if TP or SL hit
                outcome = self.check_signal_outcome(signal, current_price)
                
                if outcome == 'WON':
                    signal.status = SignalStatus.WON
                    signal.exit_price = current_price
                    signal.exit_time = datetime.utcnow()
                    self.stats['won'] += 1
                    logger.info(f"🎉 SIGNAL WON: {signal.symbol} {signal.direction} (ID: {signal.id}) - TP hit at {current_price:.5f}")
                    
                    # Send Telegram notification
                    self._send_telegram_notification(signal, "WON", current_price)
                    
                elif outcome == 'LOST':
                    signal.status = SignalStatus.LOST
                    signal.exit_price = current_price
                    signal.exit_time = datetime.utcnow()
                    self.stats['lost'] += 1
                    logger.info(f"❌ SIGNAL LOST: {signal.symbol} {signal.direction} (ID: {signal.id}) - SL hit at {current_price:.5f}")
                    
                    # Send Telegram notification
                    self._send_telegram_notification(signal, "LOST", current_price)
                    
                elif self.check_expiration(signal):
                    signal.status = SignalStatus.EXPIRED
                    signal.exit_price = current_price
                    signal.exit_time = datetime.utcnow()
                    self.stats['expired'] += 1
                    logger.info(f"⏰ SIGNAL EXPIRED: {signal.symbol} {signal.direction} (ID: {signal.id}) - 4 hours elapsed")
                    
                    # Send Telegram notification
                    self._send_telegram_notification(signal, "EXPIRED", current_price)
                
                db.commit()
            
            logger.info(f"📈 Stats: Won={self.stats['won']}, Lost={self.stats['lost']}, Expired={self.stats['expired']}")
            
        except Exception as e:
            logger.error(f"Error processing signals: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _send_telegram_notification(self, signal: TradingSignal, outcome: str, exit_price: float):
        """Send Telegram notification about signal outcome."""
        try:
            import requests
            
            telegram_token = os.getenv("TELEGRAM_BOT_TOKEN")
            telegram_chat_id = os.getenv("TELEGRAM_CHAT_ID")
            
            if not telegram_token or not telegram_chat_id:
                return
            
            # Calculate P&L
            entry = signal.entry
            if signal.direction.upper() == 'BUY':
                pips = (exit_price - entry) * (10000 if 'JPY' not in signal.symbol else 100)
            else:
                pips = (entry - exit_price) * (10000 if 'JPY' not in signal.symbol else 100)
            
            # Format message based on outcome
            if outcome == 'WON':
                emoji = "🎉"
                title = "SIGNAL WON"
                color = "green"
            elif outcome == 'LOST':
                emoji = "❌"
                title = "SIGNAL LOST"
                color = "red"
            else:
                emoji = "⏰"
                title = "SIGNAL EXPIRED"
                color = "orange"
            
            msg = (
                f"{emoji} <b>{title}</b> {emoji}\n\n"
                f"📊 <b>{signal.symbol}</b>\n"
                f"📈 Direction: {signal.direction}\n"
                f"💰 Entry: {signal.entry:.5f}\n"
                f"🚪 Exit: {exit_price:.5f}\n"
                f"📊 P&L: {pips:+.1f} pips\n"
                f"⏰ Duration: {self._format_duration(signal.timestamp)}"
            )
            
            url = f"https://api.telegram.org/bot{telegram_token}/sendMessage"
            requests.post(url, data={
                "chat_id": telegram_chat_id,
                "text": msg,
                "parse_mode": "HTML"
            }, timeout=5)
            
        except Exception as e:
            logger.warning(f"Failed to send Telegram notification: {e}")
    
    def _format_duration(self, start_time):
        """Format duration since signal was created."""
        if not start_time:
            return "Unknown"
        
        delta = datetime.utcnow() - start_time
        hours = int(delta.total_seconds() // 3600)
        minutes = int((delta.total_seconds() % 3600) // 60)
        
        if hours > 0:
            return f"{hours}h {minutes}m"
        return f"{minutes}m"
    
    async def run(self):
        """Main loop - check signals every minute."""
        logger.info("🚀 Signal Tracker started")
        logger.info(f"⚙️  Settings: Expiration={EXPIRATION_HOURS}h, Check interval={CHECK_INTERVAL_SECONDS}s")
        
        while True:
            try:
                self.process_pending_signals()
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
            
            await asyncio.sleep(CHECK_INTERVAL_SECONDS)


if __name__ == "__main__":
    tracker = SignalTracker()
    asyncio.run(tracker.run())
