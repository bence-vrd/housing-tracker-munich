import psycopg2


# DB SETUP
def setup_database():
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
        return None, None
