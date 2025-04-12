## 📘 `README.md` – *Namma Query Search: Stock Movement + AI Reasoning Dashboard*

### 🔎 Overview

**Namma Query Search** is an AI-powered stock dashboard that explains **why a company's stock went up or down** — using real-time market data, news scraping, and intelligent summarization.

It includes:
- 📉 Daily stock price movements
- 📰 Web-scraped news from Yahoo Finance
- 💬 AI-generated explanations using Google Gemini
- 🧠 Chatbot for user queries
- 📊 Frontend dashboard to visualize prices + news sentiment

---

### 🚀 Features

- 🔍 Search by stock ticker (e.g., `AAPL`, `TSLA`, `GOOGL`)
- 📈 Line chart for last 30 days' stock prices
- 🧾 Sentiment-tagged news summaries
- 💬 Chat assistant (powered by Gemini + FastAPI)
- 🗃 SQLite backend for efficient query + persistence

---

### 🗂️ Project Structure

```
📁 project-root/
│
├── scrape2.py         # Scrapes stock + news data and saves to JSON
├── db.py              # Converts JSON into SQLite (stock_news.db)
├── app.py             # FastAPI backend for API and chatbot
├── fe.html            # HTML frontend for stock dashboard + chat UI
├── combined_stock_news_data.json  # Output from scraping (created)
├── stock_news.db      # SQLite DB (created after running db.py)
```

---

### ⚙️ How to Run

#### 1️⃣ Scrape Stock + News
```bash
python scrape2.py
```

✅ This fetches news + price data for top 100 US stocks  
📁 Saves to: `combined_stock_news_data.json`

---

#### 2️⃣ Load into SQLite
```bash
python db.py
```

✅ Creates: `stock_news.db`  
📋 Populates `stocks` and `news` tables

---

#### 3️⃣ Run FastAPI Backend
```bash
uvicorn app:app --reload
```

🚀 Runs backend at `http://127.0.0.1:8000`

---

#### 4️⃣ Open Frontend
- Open `fe.html` in your browser
- Search for any stock (e.g. `TSLA`, `AAPL`, `GOOGL`)
- View chart, sentiment, and AI-explained news

---

### 🧠 Tech Stack

| Part        | Tech Used                        |
|-------------|----------------------------------|
| Backend     | Python, FastAPI, SQLite, yFinance |
| Scraping    | BeautifulSoup, Yahoo Finance     |
| NLP         | Google Gemini (via API)          |
| Sentiment   | TextBlob                         |
| Frontend    | HTML, JavaScript, Chart.js       |

---

### 📌 Notes
- Make sure to replace **your Gemini and Finnhub API keys** in `app.py`.
- You can update `tickers` in `scrape2.py` to target custom stocks.
- For fully offline demo, you can skip APIs and just show existing scraped data.

---
