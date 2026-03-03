import requests
from bs4 import BeautifulSoup
from notifications import send_telegram_msg

def fetch_kleinanzeigen(conn, cur):
    url = "https://www.kleinanzeigen.de/s-auf-zeit-wg/muenchen/sortierung:neuste/anzeige:angebote/preis::1100/c199l6411r10"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    print(f"[Kleinanzeigen] Send request to {url[:30]}...")

    try:
        response = requests.get(url=url, headers=headers, timeout=15)
    except Exception as e:
        print(f"[Kleinanzeigen] Error getting request: {e}")
        return

    print(f"[Kleinanzeigen] Status code: {response.status_code}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all("article", class_="aditem")

        if len(items) == 0:
            print("[Kleinanzeigen] WARNING: 0 Ads found => possible captcha")
            return
        else:
            print(f"[Kleinanzeigen] {len(items)} Ads found in HTML")
        new_items = 0

        for item in items:
            title_tag = item.find("a", class_="ellipsis")
            if not title_tag:
                continue

            title = title_tag.text.strip()
            link = f"https://www.kleinanzeigen.de{title_tag['href']}" if title_tag.has_attr("href") else ""

            price_tag = item.find("p", class_="aditem-main--middle--price-shipping--price")
            price = price_tag.text.strip().replace("\n", " ") if price_tag else "no price found"

            time_tag = item.find("div", class_="aditem-main--top--right")
            if not time_tag or not time_tag.text.strip():
                continue

            post_time = time_tag.text.strip().replace("Heute,", "").replace("Gestern, ", "")

            if conn and cur:
                try:
                    cur.execute("""
                        INSERT INTO listings (title, price, post_time, link)
                        VALUES (%s, %s, %s, %s)
                        ON CONFLICT (link) DO NOTHING                    
                    """, (title, price, post_time, link))

                    if cur.rowcount == 1:
                        new_items += 1
                        print(f"[Kleinanzeigen] NEW AD SAVED: {title} | {price}")

                        msg = f"🚨 <b>Kleinanzeigen: New apartment found!</b>\n\n<b>Title:</b> {title}\n<b>Price:</b> {price}\n<b>Time:</b> {post_time}\n\n<a href='{link}'>Click here to visit add!</a>"
                        send_telegram_msg(msg)

                except Exception as e:
                    print(f"Error saving to db: {e}")
                    conn.rollback()
        if conn:
            conn.commit()
        print(f"[Kleinanzeigen] {new_items} new ads were added to db\n")
        print("*" * 60)

    else:
        print(f"[Kleinanzeigen] Error! Status code: {response.status_code}")
