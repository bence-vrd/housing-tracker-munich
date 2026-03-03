import psycopg2
import os
from dotenv import load_dotenv

load_dotenv()


# DB SETUP
def setup_database():
    db_url = os.getenv("DATABASE_URL")

    if not db_url:
        print("Error: DATABASE_URL not in .env")
        return None, None

    print("Connect with databse...")
    try:
        conn = psycopg2.connect(db_url)
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
        print("Cloud database ready\n")
        return conn, cur

    except Exception as e:
        print(f"Database exception: {e}")
        return None, None
