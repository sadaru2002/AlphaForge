import asyncio
import os
import sys
sys.path.append('/app/backend')
from notifications.telegram import TelegramNotifier

async def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    chat_id = os.getenv("TELEGRAM_CHAT_ID")
    print(f"Token: {token}")
    print(f"Chat ID: {chat_id}")
    
    if not token or not chat_id:
        print("Error: Missing credentials")
        return

    notifier = TelegramNotifier(token, chat_id)
    print("Sending message...")
    try:
        success = await notifier.send_message("Test message from CLI")
        print(f"Send result: {success}")
    except Exception as e:
        print(f"Exception: {e}")

if __name__ == "__main__":
    asyncio.run(main())
