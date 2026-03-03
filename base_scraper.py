import requests
import logging
from notifications import send_telegram_msg

class BaseScraper:
    def __init__(self, conn, cur, url, name):
        self.conn = conn
        self.cur = cur
        self.url = url
        self.name = name
        self.logger = logging.getLogger(self.name)

        self.headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
            "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
            "Connection": "keep-alive"
        }

    def fetch_html(self):
        self.logger.info(f"Send request to {self.url[:30]}...")
        try:
            response = requests.get(url=self.url, headers=self.headers, timeout=15)

            if response.status_code == 200:
                return response.text
            else:
                self.logger.error(f"Error! Status code: {response.status_code}")
                return None
        except Exception as e:
            self.logger.error(f"Request error: {e}")
            return None

    def save_to_db_and_notify(self, title, price, post_time, link):
        if not self.conn or not self.cur:
            return False
        try:
            self.cur.execute("""
                INSERT INTO listings (title, price, post_time, link)
                VALUES (%s, %s, %s, %s)
                ON CONFLICT (link) DO NOTHING
            """, (title, price, post_time, link))

            if self.cur.rowcount == 1:
                self.logger.info(f"NEW AD SAVED: {title} | {price}")
                msg = f"🚨 <b>{self.name}: New apartment found!</b>\n\n<b>Title:</b> {title}\n<b>Price:</b> {price}\n<b>Time:</b> {post_time}\n\n<a href='{link}'>Click here to visit ad!</a>"
                send_telegram_msg(msg)
                return True
        except Exception as e:
            self.logger.error(f"DB Error: {e}")
            self.conn.rollback()

        return False
