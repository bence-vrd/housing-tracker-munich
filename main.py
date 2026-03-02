import requests
from bs4 import BeautifulSoup
import time
import random


# fetch data from given url
def fetch_house_data():
    url = "https://www.kleinanzeigen.de/s-auf-zeit-wg/muenchen/sortierung:neuste/anzeige:angebote/preis::1200/c199l6411r10"

    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/58.0.3029.110 Safari/537.36",
        "Accept-Language": "de-DE,de;q=0.9,en-US;q=0.8,en;q=0.7"
    }

    print(f"Send request to {url[:30]}...")

    response = requests.get(url=url, headers=headers)
    print(f"Status code: {response.status_code}")

    if response.status_code == 200:
        print("success! we are on the page")

        soup = BeautifulSoup(response.text, 'html.parser')

        print("Seiteninhalt:", soup.title.text.strip())

        # start extracting data
        print("\nsearch for housing...")
        items = soup.find_all("article", class_="aditem")

        print(f"found {len(items)} advertisements on this site\n")

        for item in items:
            title_tag = item.find("a", class_="ellipsis")

            if not title_tag:
                continue

            title = title_tag.text.strip()
            link = f"https://www.kleinanzeigen.de{title_tag['href']}" if title_tag.has_attr("href") else ""


            price_tag = item.find("p", class_="aditem-main--middle--price-shipping--price")
            price = price_tag.text.strip().replace("\n", " ") if price_tag else "no price found"

            time_tag = item.find("div", class_="aditem-main--top--right")
            post_time = time_tag.text.strip().replace("Heute,", "")

            print(f"Title: {title}")
            print(f"Price: {price}")
            print(f"Time: {post_time}")
            print("*" * 60)

    else:
        print("Failed to get on website")


if __name__ == "__main__":
    fetch_house_data()
