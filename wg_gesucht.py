import re
import time
import os
from bs4 import BeautifulSoup
from base_scraper import BaseScraper


class WgGesuchtScraper(BaseScraper):

    def __init__(self, conn, cur):
        url = os.getenv("WG_GESUCHT_URL")
        if not url:
            print("[WG-Gesucht] WARNING: no URL found in .env")
            url = ""

        super().__init__(conn, cur, url, "WG-Gesucht")

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
            print("[WG-Gesucht] WARNING: 0 Ads found => possible captcha")
            return
        else:
            print(f"[WG-Gesucht] {len(items)} Ads found in HTML")

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

            post_time = time.strftime("%d.%m. %H:%M")
            div_time_tag = item.find("div", class_="col-xs-9")
            if div_time_tag:
                span_tag = div_time_tag.find(text=re.compile("Online:", re.IGNORECASE))
                if span_tag:
                    post_time = span_tag.text.replace("Online:", "").replace("Minuten", "Minutes").replace("Stunden",
                                                                                                           "Hours").strip() + " ago"

            if self.save_to_db_and_notify(title, price, post_time, link):
                new_items += 1

        if self.conn:
            self.conn.commit()

        print(f"[{self.name}] {new_items} new ads were added to db\n")
