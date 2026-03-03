import time
import schedule
import random
from flask import Flask
from threading import Thread
from database import setup_database
from kleinanzeigen import fetch_kleinanzeigen
from wg_gesucht import fetch_wg_gesucht


app = Flask('')

@app.route('/')
def home():
    return "Housing Bot is Running!"
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
