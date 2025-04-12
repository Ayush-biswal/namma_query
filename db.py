import json
import sqlite3

# 🔁 CHANGE THIS PATH to your JSON file output
json_file_path = "combined_stock_news_data.json"
database_file = "stock_news.db"

# Load the JSON data
with open(json_file_path, "r", encoding="utf-8") as f:
    data = json.load(f)

# Connect to SQLite
conn = sqlite3.connect(database_file)
cursor = conn.cursor()

# Create the tables
cursor.execute("""
CREATE TABLE IF NOT EXISTS stocks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    name TEXT,
    sector TEXT,
    date TEXT,
    open REAL,
    high REAL,
    low REAL,
    close REAL,
    volume INTEGER
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS news (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT,
    headline TEXT,
    summary TEXT,
    url TEXT,
    FOREIGN KEY (ticker) REFERENCES stocks(ticker)
)
""")

cursor.execute("DELETE FROM stocks")
cursor.execute("DELETE FROM news")

# Populate the database
for ticker, info in data.items():
    # Insert stock info
    cursor.execute("""
        INSERT INTO stocks (ticker, name, sector, date, open, high, low, close, volume)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
    """, (
        ticker,
        info.get("Name", ""),
        info.get("Sector", ""),
        info.get("Date", ""),
        info.get("Open", 0),
        info.get("High", 0),
        info.get("Low", 0),
        info.get("Close", 0),
        info.get("Volume", 0)
    ))

    # Insert related news
    for news in info.get("News", []):
        cursor.execute("""
            INSERT INTO news (ticker, headline, summary, url)
            VALUES (?, ?, ?, ?)
        """, (
            ticker,
            news.get("headline", ""),
            news.get("summary", ""),
            news.get("url", "")
        ))

# Commit and close
conn.commit()
conn.close()

print(f"✅ Done! Data saved to {database_file}")
