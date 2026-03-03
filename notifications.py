import os
import requests
import logging
from dotenv import load_dotenv

load_dotenv()
logger = logging.getLogger("Telegram")

TELEGRAM_TOKEN = os.getenv("TELEGRAM_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")




def send_telegram_msg(text):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram token or chat id not in .env file")
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": text,
        "parse_mode": "HTML"
    }

    try:
        response = requests.post(url=url, data=payload)

        if response.status_code != 200:
            logger.error(f"Error sending to telegram: {response.text}")
    except Exception as e:
        logger.error(f"Telegram Exception: {e}")


