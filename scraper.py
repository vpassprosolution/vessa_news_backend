import requests
from bs4 import BeautifulSoup
from datetime import datetime
from database import connect_db

URL = "https://www.investing.com/economic-calendar/"

HEADERS = {
    "User-Agent": "Mozilla/5.0",
    "Accept-Language": "en-US,en;q=0.9"
}

def scrape_high_impact_news():
    today = datetime.today().strftime("%b %d, %Y")
    print(f"📅 Scraping news for {today}")

    try:
        response = requests.get(URL, headers=HEADERS)
        soup = BeautifulSoup(response.content, "html.parser")

        rows = soup.select("tr.js-event-item")

        news_items = []

        for row in rows:
            importance = row.get("data-importance", "")
            date_attr = row.get("data-event-datetime", "")

            if importance != "3":
                continue  # Only high-impact

            if not date_attr:
                continue

            event_date = datetime.utcfromtimestamp(int(date_attr)).date()
            if event_date != datetime.today().date():
                continue  # Skip old/future dates

            time = row.select_one(".first.left.time") or row.select_one(".first.left.noTime")
            currency = row.select_one(".left.flagCur.noWrap span")
            event_name = row.select_one(".event")

            if time and currency and event_name:
                news_items.append({
                    "event_time": time.text.strip(),
                    "currency": currency.text.strip(),
                    "event_name": event_name.text.strip(),
                    "importance": "High"
                })

        print(f"✅ Found {len(news_items)} high-impact news.")

        if news_items:
            conn = connect_db()
            cur = conn.cursor()

            # 🧹 Delete previous records
            cur.execute("DELETE FROM high_impact_news WHERE date = CURRENT_DATE")

            for item in news_items:
                cur.execute("""
                    INSERT INTO high_impact_news (event_time, currency, event_name, importance)
                    VALUES (%s, %s, %s, %s)
                """, (item["event_time"], item["currency"], item["event_name"], item["importance"]))

            conn.commit()
            cur.close()
            conn.close()

            print("✅ Data saved to database.")

    except Exception as e:
        print("❌ Error during scraping:", e)

if __name__ == "__main__":
    scrape_high_impact_news()
