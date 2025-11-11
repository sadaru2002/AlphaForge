"""
Telegram Notifications
Send trading signals and alerts via Telegram
"""

import asyncio
import logging
from typing import List, Dict, Any, Optional
from datetime import datetime, timezone
import aiohttp

logger = logging.getLogger(__name__)

class TelegramNotifier:
    """Send notifications via Telegram"""
    
    def __init__(self, token: str, chat_id: str):
        """
        Initialize Telegram notifier
        
        Args:
            token: Telegram bot token
            chat_id: Telegram chat ID
        """
        self.token = token
        self.chat_id = chat_id
        self.base_url = f"https://api.telegram.org/bot{token}"
        self.session = None
    
    async def _get_session(self):
        """Get or create aiohttp session"""
        if self.session is None or self.session.closed:
            self.session = aiohttp.ClientSession()
        return self.session
    
    async def close(self):
        """Close the session"""
        if self.session and not self.session.closed:
            await self.session.close()
    
    async def send_message(self, message: str, parse_mode: str = "HTML") -> bool:
        """
        Send a message to Telegram
        
        Args:
            message: Message to send
            parse_mode: Message parse mode (HTML or Markdown)
            
        Returns:
            True if successful, False otherwise
        """
        try:
            session = await self._get_session()
            
            url = f"{self.base_url}/sendMessage"
            data = {
                "chat_id": self.chat_id,
                "text": message,
                "parse_mode": parse_mode
            }
            
            async with session.post(url, json=data) as response:
                if response.status == 200:
                    logger.info("Message sent successfully")
                    return True
                else:
                    error_text = await response.text()
                    logger.error(f"Failed to send message: {response.status} - {error_text}")
                    return False
                    
        except Exception as e:
            logger.error(f"Error sending Telegram message: {e}")
            return False
    
    async def send_signal_notification(self, signal: Dict[str, Any]) -> bool:
        """
        Send a trading signal notification
        
        Args:
            signal: Signal data
            
        Returns:
            True if successful, False otherwise
        """
        try:
            symbol = signal.get('metadata', {}).get('symbol', 'UNKNOWN')
            direction = signal.get('setup_details', {}).get('direction', 'UNKNOWN')
            confidence = signal.get('risk_management', {}).get('confidence_score', 0)
            grade = signal.get('risk_management', {}).get('setup_grade', 'D')
            
            trade_params = signal.get('trade_parameters', {})
            entry_price = trade_params.get('entry_price', 0)
            stop_loss = trade_params.get('stop_loss', 0)
            take_profit_1 = trade_params.get('take_profit_1', 0)
            rr_ratio = trade_params.get('take_profit_1_rr', 0)
            
            # Format message
            emoji = "🟢" if direction == "BUY" else "🔴" if direction == "SELL" else "⚪"
            
            message = f"""
{emoji} <b>NEW TRADING SIGNAL</b>

<b>Symbol:</b> {symbol}
<b>Direction:</b> {direction}
<b>Confidence:</b> {confidence}%
<b>Grade:</b> {grade}

<b>Entry Price:</b> {entry_price:.5f}
<b>Stop Loss:</b> {stop_loss:.5f}
<b>Take Profit:</b> {take_profit_1:.5f}
<b>R:R Ratio:</b> {rr_ratio:.2f}

<b>Time:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
            
            return await self.send_message(message.strip())
            
        except Exception as e:
            logger.error(f"Error sending signal notification: {e}")
            return False
    
    async def send_signal_notifications(self, signals: List[Dict[str, Any]]) -> int:
        """
        Send multiple signal notifications
        
        Args:
            signals: List of signals
            
        Returns:
            Number of successfully sent notifications
        """
        try:
            success_count = 0
            
            for signal in signals:
                if await self.send_signal_notification(signal):
                    success_count += 1
                    # Small delay between messages to avoid rate limiting
                    await asyncio.sleep(0.5)
            
            logger.info(f"Sent {success_count}/{len(signals)} signal notifications")
            return success_count
            
        except Exception as e:
            logger.error(f"Error sending signal notifications: {e}")
            return 0
    
    async def send_daily_summary(self, daily_stats: Dict[str, Any]) -> bool:
        """
        Send daily trading summary
        
        Args:
            daily_stats: Daily performance statistics
            
        Returns:
            True if successful, False otherwise
        """
        try:
            total_signals = daily_stats.get('total_signals', 0)
            wins = daily_stats.get('wins', 0)
            losses = daily_stats.get('losses', 0)
            win_rate = daily_stats.get('win_rate', 0)
            total_pnl = daily_stats.get('total_pnl', 0)
            
            # Determine emoji based on performance
            if total_pnl > 0:
                emoji = "📈"
            elif total_pnl < 0:
                emoji = "📉"
            else:
                emoji = "📊"
            
            message = f"""
{emoji} <b>DAILY TRADING SUMMARY</b>

<b>Total Signals:</b> {total_signals}
<b>Wins:</b> {wins}
<b>Losses:</b> {losses}
<b>Win Rate:</b> {win_rate:.1f}%
<b>P&L:</b> ${total_pnl:.2f}

<b>Date:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d')}
"""
            
            return await self.send_message(message.strip())
            
        except Exception as e:
            logger.error(f"Error sending daily summary: {e}")
            return False
    
    async def send_error_alert(self, error_message: str, component: str = "System") -> bool:
        """
        Send error alert
        
        Args:
            error_message: Error message
            component: Component that generated the error
            
        Returns:
            True if successful, False otherwise
        """
        try:
            message = f"""
🚨 <b>SYSTEM ERROR ALERT</b>

<b>Component:</b> {component}
<b>Error:</b> {error_message}
<b>Time:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
"""
            
            return await self.send_message(message.strip())
            
        except Exception as e:
            logger.error(f"Error sending error alert: {e}")
            return False
    
    async def send_startup_notification(self) -> bool:
        """Send system startup notification"""
        try:
            message = f"""
🚀 <b>TRADING SYSTEM STARTED</b>

<b>Status:</b> Online
<b>Time:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
<b>Version:</b> 1.0.0

System is now monitoring markets and generating signals.
"""
            
            return await self.send_message(message.strip())
            
        except Exception as e:
            logger.error(f"Error sending startup notification: {e}")
            return False
    
    async def send_shutdown_notification(self) -> bool:
        """Send system shutdown notification"""
        try:
            message = f"""
🛑 <b>TRADING SYSTEM SHUTDOWN</b>

<b>Status:</b> Offline
<b>Time:</b> {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}

System has been shut down.
"""
            
            return await self.send_message(message.strip())
            
        except Exception as e:
            logger.error(f"Error sending shutdown notification: {e}")
            return False
    
    async def test_connection(self) -> bool:
        """
        Test Telegram connection
        
        Returns:
            True if connection is working, False otherwise
        """
        try:
            message = "🔧 Telegram connection test - System is working!"
            return await self.send_message(message)
            
        except Exception as e:
            logger.error(f"Telegram connection test failed: {e}")
            return False
    
    def format_signal_message(self, signal: Dict[str, Any]) -> str:
        """
        Format a signal for display (without sending)
        
        Args:
            signal: Signal data
            
        Returns:
            Formatted message string
        """
        try:
            symbol = signal.get('metadata', {}).get('symbol', 'UNKNOWN')
            direction = signal.get('setup_details', {}).get('direction', 'UNKNOWN')
            confidence = signal.get('risk_management', {}).get('confidence_score', 0)
            grade = signal.get('risk_management', {}).get('setup_grade', 'D')
            
            trade_params = signal.get('trade_parameters', {})
            entry_price = trade_params.get('entry_price', 0)
            stop_loss = trade_params.get('stop_loss', 0)
            take_profit_1 = trade_params.get('take_profit_1', 0)
            rr_ratio = trade_params.get('take_profit_1_rr', 0)
            
            emoji = "🟢" if direction == "BUY" else "🔴" if direction == "SELL" else "⚪"
            
            return f"""
{emoji} NEW TRADING SIGNAL

Symbol: {symbol}
Direction: {direction}
Confidence: {confidence}%
Grade: {grade}

Entry Price: {entry_price:.5f}
Stop Loss: {stop_loss:.5f}
Take Profit: {take_profit_1:.5f}
R:R Ratio: {rr_ratio:.2f}

Time: {datetime.now(timezone.utc).strftime('%Y-%m-%d %H:%M:%S UTC')}
""".strip()
            
        except Exception as e:
            logger.error(f"Error formatting signal message: {e}")
            return f"Error formatting signal: {str(e)}"




