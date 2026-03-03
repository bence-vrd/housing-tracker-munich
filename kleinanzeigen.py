import os
from bs4 import BeautifulSoup
from base_scraper import BaseScraper


class KleinanzeigenScraper(BaseScraper):

    def __init__(self, conn, cur):
        url = os.getenv("KLEINANZEIGEN_URL")
        if not url:
            print("[Kleinanzeigen] WARNING: No URL found in .env")
            url = ""
        super().__init__(conn, cur, url, "Kleinanzeigen")

    def run(self):
        if not self.url:
            return

        html = self.fetch_html()
        if not html:
            return

        soup = BeautifulSoup(html, 'lxml')
        items = soup.find_all("article", class_="aditem")

        if len(items) == 0:
            print(f"[{self.name}] WARNING: 0 Ads found => possible captcha")
            return
        else:
            print(f"[{self.name}] {len(items)} Ads found in HTML")
        new_items = 0

        for item in items:
            title_tag = item.find("a", class_="ellipsis")
            if not title_tag:
                continue

            title = title_tag.text.strip()
            link = f"https://www.kleinanzeigen.de{title_tag['href']}" if title_tag.has_attr("href") else ""

            price_tag = item.find("p", class_="aditem-main--middle--price-shipping--price")
            if price_tag:
                price = " ".join(price_tag.text.split())
            else:
                price = "N\A"

            time_tag = item.find("div", class_="aditem-main--top--right")
            if not time_tag or not time_tag.text.strip():
                continue

            post_time = time_tag.text.strip().replace("Heute,", "").replace("Gestern, ", "")

            if self.save_to_db_and_notify(title, price, post_time, link):
                new_items += 1

        if self.conn:
            self.conn.commit()

        print(f"[{self.name}] {new_items} new ads were added to db\n")
        print("*" * 60)
