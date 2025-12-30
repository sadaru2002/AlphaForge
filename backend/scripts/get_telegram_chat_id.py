import requests
import time
import sys

TOKEN = "8472623982:AAGkT6g_dIJsRhqXyQ0Wo75dsCQMjFLG5tA"
URL = f"https://api.telegram.org/bot{TOKEN}/getUpdates"

print("="*60)
print("🤖 TELEGRAM CHAT ID RETRIEVER")
print("="*60)
print(f"\n1. Open your bot in Telegram: @AlphaForgeBot (or whatever name you gave it)")
print("2. Click 'Start' or send any message to the bot")
print("3. Waiting for your message...")

while True:
    try:
        response = requests.get(URL)
        data = response.json()
        
        if data.get("ok"):
            results = data.get("result", [])
            if results:
                # Get the latest message
                latest = results[-1]
                chat = latest.get("message", {}).get("chat", {})
                chat_id = chat.get("id")
                username = chat.get("username", "Unknown")
                first_name = chat.get("first_name", "Unknown")
                
                if chat_id:
                    print(f"\n✅ SUCCESS! Found Chat ID:")
                    print(f"--------------------------------------------------")
                    print(f"Chat ID:    {chat_id}")
                    print(f"User:       {first_name} (@{username})")
                    print(f"--------------------------------------------------")
                    print(f"\nCopy this Chat ID. We need it for the configuration.")
                    break
        
        time.sleep(2)
        print(".", end="", flush=True)
        
    except Exception as e:
        print(f"\n❌ Error: {e}")
        time.sleep(5)
