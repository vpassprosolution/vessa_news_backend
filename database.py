import psycopg2
from datetime import datetime, timedelta

# ✅ Replace with your actual Railway DB URL
DB_URL = "postgresql://postgres:vVMyqWjrqgVhEnwyFifTQxkDtPjQutGb@interchange.proxy.rlwy.net:30451/railway"

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

        # ✅ Use Malaysia date to delete correctly
        malaysia_date = (datetime.utcnow() + timedelta(hours=8)).date()
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
