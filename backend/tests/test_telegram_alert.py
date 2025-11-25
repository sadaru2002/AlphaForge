import asyncio
import os
from dotenv import load_dotenv
from notifications.telegram import TelegramNotifier

# Load environment variables
load_dotenv()

async def test_telegram():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    
    print(f"Token: {token[:5]}...{token[-5:]}")
    print(f"Chat ID: {chat_id}")
    
    if not token or not chat_id:
        print("❌ Missing credentials in .env")
        return

    notifier = TelegramNotifier(token, chat_id)
    
    print("\nSending test message...")
    success = await notifier.send_message(
        "🚀 <b>AlphaForge Telegram Setup Complete!</b>\n\n"
        "You will now receive instant alerts for:\n"
        "✅ New Trading Signals\n"
        "✅ Daily Summaries\n"
        "✅ System Alerts\n\n"
        "Happy Trading! 💰"
    )
    
    if success:
        print("✅ Test message sent successfully!")
    else:
        print("❌ Failed to send test message.")
    
    await notifier.close()

if __name__ == "__main__":
    asyncio.run(test_telegram())
