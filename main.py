import time
import schedule
import random
from flask import Flask, render_template_string
from threading import Thread
from database import setup_database
from kleinanzeigen import fetch_kleinanzeigen
from wg_gesucht import fetch_wg_gesucht


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
            <th>Posted</th>
            <th>Link</th>
        </tr>
        {% for listing in listings %}
        <tr>
            <td>{{ listing[1] }}</td> <td>{{ listing[2] }}</td> <td>{{ listing[3] }}</td> <td><a href="{{ listing[4] }}" target="_blank">Link</a></td> </tr>
        {% endfor %}
    </table>
</body>
</html>
 """

@app.route('/')
def home():
    conn, cur = setup_database()
    if conn and cur:
        cur.execute("SELECT * FROM listings ORDER BY id DESC LIMIT 10")
        recent_listings = cur.fetchall()
        cur.close()
        conn.close()
    else:
        recent_listings = []

    return render_template_string(HTML_TEMPLATE, listings=recent_listings)


def run_web_server():
    app.run(host='0.0.0.0', port=8080)


def keep_alive():
    t = Thread(target=run_web_server)
    t.start()


def job():
    print(f"\n---[{time.strftime('%d.%m.%Y %H:%M:%S')}] Start automatically searching ---")

    db_conn, db_cur = setup_database()

    if db_conn:
        fetch_kleinanzeigen(db_conn, db_cur)

        time.sleep(random.uniform(5, 10))
        fetch_wg_gesucht(db_conn, db_cur)

        print("Fetching done")

        db_cur.close()
        db_conn.close()
    else:
        print("Error: couldn't connect to db")


if __name__ == "__main__":
    print("Housing bot started!")
    print("The bot now searches every 10 minute for new housings! (Press Ctrl+C to stop)")

    keep_alive()

    job()
    schedule.every(10).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(3)
