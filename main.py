import requests
from bs4 import BeautifulSoup
import time
import random
import psycopg2



## DB SETUP
def setup_databse():
    print("Connect with databse...")
    try:
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="housing_tracker",
            user="myuser",
            password="mypassword"
        )
        cur = conn.cursor()

        cur.execute("""
            CREATE TABLE IF NOT EXISTS listings (
            id SERIAL PRIMARY KEY,
            title VARCHAR(255),
            price VARCHAR(63),
            post_time VARCHAR(63),
            link TEXT UNIQUE
            )
        """)
        conn.commit()
        print("Database ready\n")
        return conn, cur
    except Exception as e:
        print(f"Database exception: {e}")
        return  None, None


# fetch data from given url
def fetch_house_data(conn, cur):
    url = "https://www.kleinanzeigen.de/s-auf-zeit-wg/muenchen/sortierung:neuste/anzeige:angebote/preis::1200/c199l6411r10"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/122.0.0.0 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    print(f"Send request to {url[:30]}...")

    response = requests.get(url=url, headers=headers)
    print(f"Status code: {response.status_code}")

    if response.status_code == 200:
        soup = BeautifulSoup(response.text, 'html.parser')
        items = soup.find_all("article", class_="aditem")

        print(f"DEBUG: found {len(items)} ads in HTML")
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
                        print(f"NEW AD SAVED: {title} | {price}")
                except Exception as e:
                    print(f"Error saving to db: {e}")
                    conn.rollback()
        if conn:
            conn.commit()
        print(f"\nFinished! {new_items} new ads were added to db")
        print("*" * 60)

    else:
        print("Failed to get on website")


if __name__ == "__main__":
    db_conn, db_cur = setup_databse()

    if db_conn:
        fetch_house_data(db_conn, db_cur)

        db_cur.close()
        db_conn.close()

