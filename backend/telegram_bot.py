import asyncio
import logging
import os
import sys
import time
from datetime import datetime
import aiohttp
from dotenv import load_dotenv

# Add parent directory to path to import backend modules
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from multi_timeframe_engine import MultiTimeframeEngine
from regime_detector import MarketRegimeDetector, MarketRegime

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler("telegram_bot.log"),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger("TelegramBot")

# Load environment variables
load_dotenv()

class AlphaForgeBot:
    def __init__(self):
        self.token = os.getenv("TELEGRAM_BOT_TOKEN")
        self.base_url = f"https://api.telegram.org/bot{self.token}"
        self.offset = 0
        self.running = True
        
        # Initialize Analysis Engines
        self.mtf_engine = MultiTimeframeEngine(environment="practice")
        self.regime_detector = MarketRegimeDetector()
        
        logger.info("🤖 AlphaForge Bot Initialized")

    async def get_updates(self):
        """Long poll for new messages"""
        timeout = 30
        url = f"{self.base_url}/getUpdates?offset={self.offset}&timeout={timeout}"
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        return data.get("result", [])
                    else:
                        logger.error(f"Error getting updates: {response.status}")
                        return []
        except Exception as e:
            logger.error(f"Connection error: {e}")
            await asyncio.sleep(5)
            return []

    async def send_message(self, chat_id, text, parse_mode="HTML"):
        """Send message to user"""
        url = f"{self.base_url}/sendMessage"
        payload = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": parse_mode
        }
        
        try:
            async with aiohttp.ClientSession() as session:
                async with session.post(url, json=payload) as response:
                    return response.status == 200
        except Exception as e:
            logger.error(f"Error sending message: {e}")
            return False

    async def handle_market_command(self, chat_id):
        """Analyze market and send report"""
        await self.send_message(chat_id, "🔍 <b>Scanning markets...</b>\n<i>This may take a few seconds.</i>")
        
        instruments = ['GBP_USD', 'XAU_USD', 'USD_JPY']
        report = "📊 <b>MARKET SNAPSHOT</b>\n\n"
        
        for instrument in instruments:
            try:
                # Fetch Data
                data = await self.mtf_engine.fetch_multi_timeframe(instrument)
                m5_data = data.get('M5')
                
                if m5_data is not None and not m5_data.empty:
                    # Calculate Indicators explicitly
                    m5_data = self.mtf_engine._calculate_indicators(m5_data)
                    
                    # Detect Regime
                    regime = self.regime_detector.detect_regime(m5_data, instrument)
                    latest_price = m5_data['close'].iloc[-1]
                    
                    # Get Indicators
                    adx = m5_data['adx'].iloc[-1] if 'adx' in m5_data.columns else 0
                    rsi = m5_data['rsi7'].iloc[-1] if 'rsi7' in m5_data.columns else 0
                    
                    # Format Regime String
                    regime_str = regime.value.replace('_', ' ').title()
                    
                    # Icons
                    if "Trending Up" in regime_str:
                        icon = "🟢"
                    elif "Trending Down" in regime_str:
                        icon = "🔴"
                    else:
                        icon = "⚪"
                        
                    # Instrument Icon
                    inst_icon = "🇬🇧" if "GBP" in instrument else "🥇" if "XAU" in instrument else "🇯🇵"
                    
                    report += f"{inst_icon} <b>{instrument.replace('_', '/')}</b>\n"
                    report += f"• Price: {latest_price:.5f}\n"
                    report += f"• Regime: {regime_str} {icon}\n"
                    report += f"• ADX: {adx:.1f} ({'Strong' if adx > 25 else 'Weak'})\n"
                    report += f"• RSI: {rsi:.1f}\n\n"
                else:
                    report += f"⚠️ <b>{instrument}</b>: No data available\n\n"
                    
            except Exception as e:
                logger.error(f"Error analyzing {instrument}: {e}")
                report += f"⚠️ <b>{instrument}</b>: Error analyzing\n\n"
        
        report += f"<i>Updated: {datetime.now().strftime('%H:%M UTC')}</i>"
        await self.send_message(chat_id, report)

    async def handle_status_command(self, chat_id):
        """Check system status"""
        status_msg = "🛠 <b>SYSTEM STATUS</b>\n\n"
        
        # 1. Backend Check
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get("http://localhost:5000/health") as resp:
                    if resp.status == 200:
                        status_msg += "✅ <b>Backend API:</b> Online\n"
                    else:
                        status_msg += "❌ <b>Backend API:</b> Error\n"
        except:
            status_msg += "❌ <b>Backend API:</b> Offline\n"
            
        # 2. Database Check (File existence)
        db_path = "trading_signals.db"
        if os.path.exists(db_path):
            size_kb = os.path.getsize(db_path) / 1024
            status_msg += f"✅ <b>Database:</b> Active ({size_kb:.1f} KB)\n"
        else:
            status_msg += "❌ <b>Database:</b> Missing\n"
            
        # 3. Scheduler Check (Process check - simplified)
        # In a real app we'd check the PID or a heartbeat file
        status_msg += "✅ <b>Bot Service:</b> Running\n"
        
        status_msg += f"\n<i>Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S UTC')}</i>"
        
        await self.send_message(chat_id, status_msg)

    async def handle_help_command(self, chat_id):
        """Send help message"""
        help_text = """
🤖 <b>AlphaForge Bot Commands</b>

/market - Get real-time market analysis
/status - Check system health
/help - Show this message

<i>Signals are sent automatically when generated.</i>
"""
        await self.send_message(chat_id, help_text)

    async def process_update(self, update):
        """Process a single Telegram update"""
        message = update.get("message", {})
        chat_id = message.get("chat", {}).get("id")
        text = message.get("text", "")
        
        if not text or not chat_id:
            return

        logger.info(f"Received command: {text} from {chat_id}")
        
        if text.startswith("/market"):
            await self.handle_market_command(chat_id)
        elif text.startswith("/status"):
            await self.handle_status_command(chat_id)
        elif text.startswith("/help") or text.startswith("/start"):
            await self.handle_help_command(chat_id)
        else:
            # Ignore other messages or send help
            pass

    async def run(self):
        """Main bot loop"""
        logger.info("🚀 Bot started polling...")
        print("🤖 AlphaForge Bot is running! Press Ctrl+C to stop.")
        
        # Send startup message to admin
        admin_id = os.getenv("TELEGRAM_CHAT_ID")
        if admin_id:
            await self.send_message(admin_id, "🤖 <b>Bot Online</b>\nListening for commands...")
        
        while self.running:
            updates = await self.get_updates()
            
            for update in updates:
                update_id = update.get("update_id")
                self.offset = update_id + 1
                await self.process_update(update)
            
            # Small sleep to prevent CPU spinning if requests fail fast
            if not updates:
                await asyncio.sleep(1)

if __name__ == "__main__":
    bot = AlphaForgeBot()
    try:
        asyncio.run(bot.run())
    except KeyboardInterrupt:
        print("\n🛑 Bot stopped.")
