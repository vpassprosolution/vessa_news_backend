from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from database import connect_db
from datetime import date

app = FastAPI()

# ✅ Allow frontend access
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # You can limit this later to GitHub Pages domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/get_high_impact_news")
async def get_news():
    conn = connect_db()
    if not conn:
        return {"status": "error", "message": "DB connection failed"}

    try:
        cur = conn.cursor()
        cur.execute("""
            SELECT event_time, currency, event_name 
            FROM high_impact_news 
            WHERE date = CURRENT_DATE 
            ORDER BY event_time
        """)
        rows = cur.fetchall()
        cur.close()
        conn.close()

        news = [{"time": r[0], "currency": r[1], "event": r[2]} for r in rows]
        return {"status": "success", "data": news}

    except Exception as e:
        print("❌ Error fetching news:", e)
        return {"status": "error", "message": "Failed to fetch"}
