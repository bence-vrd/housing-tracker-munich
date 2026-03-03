import re
import time
import os
from datetime import datetime, timedelta
from bs4 import BeautifulSoup
from base_scraper import BaseScraper


class WgGesuchtScraper(BaseScraper):

    def __init__(self, conn, cur):
        url = os.getenv("WG_GESUCHT_URL")

        super().__init__(conn, cur, url, "WG-Gesucht")

        if not url:
            self.logger.warning("No URL found in .env")

    def run(self):
        if not self.url:
            return

        html = self.fetch_html()
        if not html:
            return

        soup = BeautifulSoup(html, 'lxml')
        premium_ad = soup.find("div", class_="premium_user_extra_list")
        if premium_ad:
            premium_ad.decompose()

        items = soup.find_all("div", class_="wgg_card offer_list_item")

        if len(items) == 0:
            self.logger.warning("0 Ads found => possible captcha")
            return
        else:
            self.logger.info(f"{len(items)} Ads found in HTML")

        new_items = 0

        for item in items:
            h2_tag = item.find("h2", class_="truncate_title noprint")
            title = ""
            link = ""

            if h2_tag:
                a_tag = h2_tag.find("a")
                if a_tag:
                    title = a_tag.text.strip()
                    link = f"https://www.wg-gesucht.de{a_tag['href']}"

            div_price_tag = item.find("div", class_="col-xs-3")
            price = "N/A"
            if div_price_tag:
                b_tag = div_price_tag.find("b")
                if b_tag:
                    price = b_tag.text.strip()

            if not link or not title:
                continue

            now = datetime.now()
            post_time = now.strftime('%H:%M')

            div_time_tag = item.find("div", class_="col-xs-9")
            if div_time_tag:
                span_tag = div_time_tag.find(string=re.compile("Online:", re.IGNORECASE))
                if span_tag:
                    raw_text = span_tag.text.replace("Online:", "").strip()

                    try:
                        val = int(re.search(r'\d+', raw_text).group())

                        if "Minute" in raw_text:
                            calc_time = now - timedelta(minutes=val)
                        elif "Stunde" in raw_text:
                            calc_time = now - timedelta(hours=val)
                        elif "Sekunde" in raw_text:
                            calc_time = now - timedelta(seconds=val)
                        elif "Tag" in raw_text:
                            calc_time = now - timedelta(days=val)
                        else:
                            calc_time = now

                        post_time = calc_time.strftime("%H:%M")
                    except Exception as e:
                        self.logger.error(f"Time parsing error for {raw_text}")

            if self.save_to_db_and_notify(title, price, post_time, link):
                new_items += 1

        if self.conn:
            self.conn.commit()

        self.logger.info(f"{new_items} new ads were added to db\n" + "*" * 60)
