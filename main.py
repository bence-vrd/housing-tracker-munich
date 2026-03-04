import time
import schedule
import random
import logging
from flask import Flask, render_template_string
from threading import Thread
from database import setup_database
from kleinanzeigen import KleinanzeigenScraper
from wg_gesucht import WgGesuchtScraper


# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - [%(name)s] - %(levelname)s - %(message)s',
    datefmt='%d.%m.%Y %H:%M:%S'
)
logger = logging.getLogger("Main")


app = Flask(__name__)


HTML_TEMPLATE = """
<!DOCTYPE html>
<html>
<head>
    <title>Housing Tracker Munich</title>
    <style>
            body { font-family: Arial, sans-serif; margin: 40px; }
            table { border-collapse: collapse; width: 100%; }
            th, td { border: 1px solid #ddd; padding: 8px; text-align: left; }
            th { background-color: #f2f2f2; }
            a { color: #0066cc; text-decoration: none; }
    </style>
</head>
<body>
    <h2>Last 10 found Ads</h2>
    <table>
        <tr>
            <th>Title</th>
            <th>Price</th>
            <th>Time</th>
            <th>Link</th>
            <th>Website</th>
        </tr>
        {% for listing in listings %}
        <tr>
            <td>{{ listing[1] }}</td> <td>{{ listing[2] }}</td> <td>{{ listing[3] }}</td> <td><a href="{{ listing[4] }}" target="_blank">Link</a></td> <td>
                {% if 'wg-gesucht.de' in listing[4] %}
                    WG-Gesucht
                {% elif 'kleinanzeigen.de' in listing[4] %}
                    Kleinanzeigen
                {% else %}
                    Unbekannt
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </table>
</body>
</html>
 """

@app.route('/')
def home():
    conn, cur = setup_database()
    if conn and cur:
        cur.execute("SELECT * FROM listings ORDER BY post_time DESC, created_at DESC LIMIT 10")
        recent_listings = cur.fetchall()

        cur.close()
        conn.close()
    else:
        recent_listings = []

    return render_template_string(HTML_TEMPLATE, listings=recent_listings)


def run_web_server():
    log = logging.getLogger('werkzeug')
    log.setLevel(logging.ERROR)
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run_web_server)
    t.start()


def job():
    logger.info("Start automatically searching ---")
    db_conn, db_cur = setup_database()

    if db_conn:
        wggesucht_scraper = WgGesuchtScraper(db_conn, db_cur)
        wggesucht_scraper.run()

        time.sleep(random.uniform(5, 10))

        kleinanzeigen_scraper = KleinanzeigenScraper(db_conn, db_cur)
        kleinanzeigen_scraper.run()

        logger.info("Fetching done")

        db_cur.close()
        db_conn.close()
    else:
        logger.error("Couldn't connect to db")


if __name__ == "__main__":
    logger.info("Housing bot started!")
    logger.info("The bot now searches every 10 minute for new housings! (Press Ctrl+C to stop)")

    keep_alive()

    # Wait 15 seconds for db booting up
    time.sleep(15)

    job()
    schedule.every(10).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(3)
