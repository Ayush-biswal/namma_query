from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import yfinance as yf
import sqlite3
from textblob import TextBlob
import google.generativeai as genai
import requests
from fastapi.responses import JSONResponse

# ===== API KEYS =====
genai.configure(api_key="AIzaSyBUOaiuWHurJgxrrQh7qMNYrHLMuuTKUOU")  # Replace with your Gemini API key
FINNHUB_API_KEY = "cvstalhr01qhup0suj80cvstalhr01qhup0suj8g"  # Replace with your Finnhub API key

# ===== FastAPI SETUP =====
app = FastAPI()

# CORS setup
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ===== DATABASE & MODELS =====
DB_PATH = "stock_news.db"

class UserInput(BaseModel):
    user_input: str

tickers = {
    "apple": "AAPL", "microsoft": "MSFT", "google": "GOOGL", "alphabet": "GOOGL",
    "amazon": "AMZN", "tesla": "TSLA", "nvidia": "NVDA", "meta": "META",
    "facebook": "META", "berkshire hathaway": "BRK-B", "unitedhealth": "UNH",
    "exxon mobil": "XOM", "johnson & johnson": "JNJ", "jpmorgan": "JPM",
    "visa": "V", "procter & gamble": "PG", "mastercard": "MA", "home depot": "HD",
    "chevron": "CVX", "merck": "MRK", "abbvie": "ABBV", "eli lilly": "LLY",
    "pepsi": "PEP", "coca cola": "KO", "bank of america": "BAC", "broadcom": "AVGO",
    "adobe": "ADBE", "costco": "COST", "walmart": "WMT", "disney": "DIS",
    "thermo fisher": "TMO", "intel": "INTC", "salesforce": "CRM", "pfizer": "PFE",
    "cisco": "CSCO", "netflix": "NFLX", "abbott": "ABT", "accenture": "ACN",
    "danaher": "DHR", "mcdonald's": "MCD", "wells fargo": "WFC", "texas instruments": "TXN",
    "lockheed martin": "LMT", "oracle": "ORCL", "starbucks": "SBUX"
}

# ===== HELPER FUNCTIONS =====

def get_sentiment(text: str):
    polarity = TextBlob(text).sentiment.polarity
    if polarity > 0:
        return "positive"
    elif polarity < 0:
        return "negative"
    else:
        return "neutral"

def get_ticker_from_name(company_name):

    name = company_name.lower().strip()

    if name in tickers:
        return tickers[name]

    # Try fetching from Finnhub
    url = f"https://finnhub.io/api/v1/search?q={company_name}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if data.get("count", 0) > 0:
        for item in data["result"]:
            if item["symbol"].isupper() and item.get("type") == "Common Stock":
                return item["symbol"]
        return data["result"][0]["symbol"]
    return None

def get_stock_price_finnhub(symbol: str):
    url = f"https://finnhub.io/api/v1/quote?symbol={symbol}&token={FINNHUB_API_KEY}"
    response = requests.get(url)
    data = response.json()

    if "c" in data and data["c"] != 0:
        return f"📈 The current stock price of {symbol} is *${data['c']}*."
    else:
        return f"❌ Could not fetch stock price for '{symbol}'."

def generate_content(input_text: str):
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")  # use gemini-pro or other available models
        response = model.generate_content(input_text)
        return response.text
    except Exception as e:
        return f"Error from Gemini: {str(e)}"

# ===== FASTAPI ENDPOINTS =====

@app.get("/stock/{symbol}")
def get_stock_data(symbol: str):
    symbol = symbol.upper()
    ticker = yf.Ticker(symbol)
    hist = ticker.history(period="1mo")

    if hist.empty:
        return {
            "dates": [],
            "close_prices": [],
            "news": []
        }

    dates = hist.index.strftime('%b %d').tolist()
    close_prices = hist["Close"].tolist()

    # Fetch news from SQLite
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT headline, summary, url FROM news WHERE ticker = ?", (symbol,))
    rows = cursor.fetchall()
    conn.close()

    news = [
        {
            "headline": row[0],
            "summary": row[1],
            "url": row[2],
            "sentiment": get_sentiment(row[1])
        }
        for row in rows
    ]

    return {
        "dates": dates,
        "close_prices": close_prices,
        "news": news
    }

@app.post("/chat")

async def chat(user_input: UserInput):
    input_text = user_input.user_input.lower()

    # Try to extract company name and fetch price
    if "stock" in input_text or "price" in input_text:
        company_name = (
            input_text.replace("stock price of", "")
                      .replace("price of", "")
                      .replace("stock", "")
                      .strip()
        )
        symbol = get_ticker_from_name(company_name)
        if symbol:      
            return {"response": get_stock_price_finnhub(symbol)}
        else:
            gemini_response = generate_content(user_input.user_input + "exclude time and date from the output")
            return{"response":gemini_response}

    # Otherwise use Gemini
    gemini_response = generate_content(user_input.user_input)
    return {"response": gemini_response}

import re
def extract_company_name(text):
    # Lowercase everything and remove common phrases
    text = text.lower()
    text = re.sub(r"(what'?s|what is)?\s?(the)?\s?(current)?\s?(stock)?\s?(price)?\s?(of)?", "", text)
    text = re.sub(r"[^\w\s]", "", text)  # Remove punctuation
    return text.strip()



