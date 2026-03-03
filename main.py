import time
import schedule

from database import setup_database
from kleinanzeigen import fetch_kleinanzeigen_data
from wg_gesucht import fetch_wg_gesucht


def job():
    print(f"\n---[{time.strftime('%d.%m.%Y %H:%M:%S')}] Start automatically searching ---")

    db_conn, db_cur = setup_database()

    if db_conn:
        fetch_kleinanzeigen_data(db_conn, db_cur)
        fetch_wg_gesucht(db_conn, db_cur)

        print("Fetching done")

        db_cur.close()
        db_conn.close()
    else:
        print("Error: couldnt connect to db")


if __name__ == "__main__":
    print("Housing bot started!")
    print("The bot now searches every 15 minute for new housings! (Press Ctrl+C to stop)")

    job()
    schedule.every(15).minutes.do(job)

    while True:
        schedule.run_pending()
        time.sleep(5)
