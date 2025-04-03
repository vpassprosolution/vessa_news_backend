import httpx
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
from database import connect_db

URL = "https://www.investing.com/economic-calendar/"

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 (KHTML, like Gecko) "
                  "Chrome/120.0.0.0 Safari/537.36",
    "Accept-Language": "en-US,en;q=0.9"
}

def scrape_high_impact_news():
    malaysia_now = datetime.utcnow() + timedelta(hours=8)
    malaysia_date = malaysia_now.date()
    print(f"📅 Scraping high-impact news for: {malaysia_now.strftime('%A, %b %d (%Y)')} (MYT)")

    try:
        response = httpx.get(URL, headers=HEADERS, timeout=30)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, "html.parser")

        rows = soup.select("tr.js-event-item")
        news_items = []

        for row in rows:
            bulls = row.select(".grayFullBullishIcon")
            if len(bulls) < 3:
                continue  # Only high impact

            time = row.select_one(".time")
            currency = row.select_one(".flagCur")
            event = row.select_one(".event")

            if not (time and currency and event):
                continue

            news_items.append({
                "event_time": time.get_text(strip=True),
                "currency": currency.get_text(strip=True),
                "event_name": event.get_text(strip=True),
                "importance": "High",
                "date": malaysia_date
            })

        print(f"✅ Found {len(news_items)} high-impact news.")

        if not news_items:
            print("❌ No high-impact news found.")
            return

        # ✅ Save to DB
        conn = connect_db()
        cur = conn.cursor()

        # ✅ DELETE based on MYT DATE, not UTC
        cur.execute("DELETE FROM high_impact_news WHERE date = %s", (malaysia_date,))

        for item in news_items:
            cur.execute("""
                INSERT INTO high_impact_news (event_time, currency, event_name, importance, date)
                VALUES (%s, %s, %s, %s, %s)
            """, (
                item["event_time"],
                item["currency"],
                item["event_name"],
                item["importance"],
                item["date"]
            ))

        conn.commit()
        cur.close()
        conn.close()
        print("✅ Data saved to database.")

    except Exception as e:
        print("❌ Error scraping:", e)

if __name__ == "__main__":
    scrape_high_impact_news()
