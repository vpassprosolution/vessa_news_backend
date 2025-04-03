import psycopg2
from datetime import date

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

        # Delete old news from today first
        cur.execute("DELETE FROM high_impact_news WHERE date = CURRENT_DATE")

        for news in news_list:
            cur.execute("""
                INSERT INTO high_impact_news (event_time, currency, event_name, importance)
                VALUES (%s, %s, %s, %s)
            """, (news["time"], news["currency"], news["event"], news["importance"]))

        conn.commit()
        cur.close()
        conn.close()
        print("✅ News saved to DB")
    except Exception as e:
        print("❌ Error saving news:", e)
