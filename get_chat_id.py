import os
import requests
from dotenv import load_dotenv

load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

def get_chat_id():
    url = f"https://api.telegram.org/bot{TOKEN}/getUpdates"
    print(f"Checking for updates at: {url}")
    response = requests.get(url).json()
    
    if not response.get("ok"):
        print("Error connecting to Telegram API.")
        return

    results = response.get("result", [])
    if not results:
        print("\nNo messages found.")
        print("Please send a message to your bot (t.me/winautoobot) first, then run this script again.")
        return

    # Get the last message's chat ID
    last_msg = results[-1]
    chat_id = last_msg.get("message", {}).get("chat", {}).get("id")
    user_name = last_msg.get("message", {}).get("from", {}).get("first_name")

    if chat_id:
        print(f"\nSuccess! Found message from {user_name}.")
        print(f"Your TELEGRAM_CHAT_ID is: {chat_id}")
        print("\nUpdate your .env file with this ID.")
    else:
        print("Could not find a chat ID in the latest updates.")

if __name__ == "__main__":
    if not TOKEN:
        print("TELEGRAM_BOT_TOKEN not found in .env file.")
    else:
        get_chat_id()
