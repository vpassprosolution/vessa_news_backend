import psycopg2
import os
from datetime import datetime, timedelta

# ✅ Securely get DB URL from Railway variable
DB_URL = os.environ.get("DB_URL")

def connect_db():
    try:
        conn = psycopg2.connect(DB_URL)
        return conn
    except Exception as e:
        print("❌ Database connection failed:", e)
        return None

def save_news_to_db(news_list):
    conn = connect_db()
    if not conn:
        return

    try:
        cur = conn.cursor()

        # ✅ Use Malaysia date (UTC+8)
        malaysia_date = (datetime.utcnow() + timedelta(hours=8)).date()

        # ✅ Delete today's old data before inserting new one
        cur.execute("DELETE FROM high_impact_news WHERE date = %s", (malaysia_date,))

        for news in news_list:
            cur.execute("""
                INSERT INTO high_impact_news (event_time, currency, event_name, importance, date)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                news["time"],
                news["currency"],
                news["event"],
                news["importance"],
                malaysia_date
            ))

        conn.commit()
        cur.close()
        conn.close()
        print("✅ News saved to DB")
    except Exception as e:
        print("❌ Error saving news:", e)
