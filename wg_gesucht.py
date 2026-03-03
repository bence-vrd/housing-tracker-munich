import re
import time
import requests
from bs4 import BeautifulSoup
from notifications import send_telegram_msg


def fetch_wg_gesucht(conn, cur):
    url = "https://www.wg-gesucht.de/wg-zimmer-und-1-zimmer-wohnungen-und-wohnungen-und-haeuser-in-Muenchen.90.0+1+2+3.1.0.html?offer_filter=1&city_id=90&sort_order=0&noDeact=1&categories%5B%5D=0&categories%5B%5D=1&categories%5B%5D=2&categories%5B%5D=3&rMax=900"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Connection": "keep-alive"
    }

    print(f"[WG-Gesucht] Send request to {url[:30]}...")

    try:
        response = requests.get(url=url, headers=headers, timeout=15)
    except Exception as e:
        print(f"[WG-Gesucht] Error getting request: {e}")
        return

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'lxml')
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
                    post_time = span_tag.text.replace("Online:", "").replace("Minuten", "Minutes").replace("Stunden", "Hours").strip() + " ago"

            if conn and cur:
                try:
                    cur.execute("""
                        INSERT INTO listings (title, price, post_time, link)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (link) DO NOTHING
                    """, (title, price, post_time, link))

                    if cur.rowcount == 1:
                        new_items += 1
                        print(f"[WG-Gesucht] NEW AD SAVED: {title} | {price}")

                        msg = f"🚨 <b>WG-Gesucht: New apartment found!</b>\n\n<b>Title:</b> {title}\n<b>Price:</b> {price}\n<b>Time:</b> {post_time}\n\n<a href='{link}'>Click here to visit add!</a>"
                        send_telegram_msg(msg)
                except Exception as e:
                    print(f"[WG-Gesucht] DB Error: {e}")
                    conn.rollback()

        if conn:
            conn.commit()
        print(f"[WG-Gesucht] {new_items} new ads were added to db\n")

    else:
        print(f"[WG-Gesucht] Error: Status code: {response.status_code}")




