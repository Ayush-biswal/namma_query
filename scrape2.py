import yfinance as yf
import requests
from bs4 import BeautifulSoup
import json
import time
import random
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed

# Top 100 US stock tickers (you can update these as needed)
tickers = [
    "AAPL", "MSFT", "GOOGL", "AMZN", "TSLA", "NVDA", "META", "BRK-B", "UNH", "XOM",
    "JNJ", "JPM", "V", "PG", "MA", "HD", "CVX", "MRK", "ABBV", "LLY",
    "PEP", "KO", "BAC", "AVGO", "ADBE", "COST", "WMT", "DIS", "TMO", "INTC",
    "CRM", "PFE", "CSCO", "NFLX", "ABT", "ACN", "DHR", "MCD", "WFC", "TXN",
    "LIN", "AMD", "BMY", "NEE", "VZ", "UPS", "NKE", "UNP", "LOW", "INTU",
    "RTX", "ORCL", "MS", "PM", "MDT", "HON", "SCHW", "QCOM", "IBM", "SBUX",
    "GE", "ISRG", "T", "AMGN", "BLK", "CAT", "DE", "GS", "NOW", "SPGI",
    "AMAT", "ELV", "ZTS", "SYK", "LMT", "BKNG", "TJX", "PLD", "MDLZ", "ADI",
    "MO", "MMC", "ADP", "VRTX", "CB", "CI", "CL", "PANW", "GILD", "CDNS",
    "PGR", "REGN", "FISV", "APD", "EW", "AON", "CSX", "TGT", "FDX", "AZO"
]

def scrape_yahoo_finance_news(symbol):
    user_agents = [
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36",
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/14.1.1 Safari/605.1.15",
        "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/92.0.4515.107 Safari/537.36"
    ]
    
    headers = {
        "User-Agent": random.choice(user_agents),
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,/;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://finance.yahoo.com/",
        "DNT": "1",
        "Connection": "keep-alive",
        "Upgrade-Insecure-Requests": "1",
        "Cache-Control": "max-age=0"
    }

    url = f"https://finance.yahoo.com/quote/{symbol}/news?p={symbol}"

    try:
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()

        soup = BeautifulSoup(response.text, 'html.parser')
        articles = []

        news_list = soup.select('li.js-stream-content')

        if not news_list:
            all_li_tags = soup.find_all('li')
            news_list = [li for li in all_li_tags if li.find('h3') and li.find('p')]

        for item in news_list:
            headline_tag = item.find('h3')
            summary_tag = item.find('p')
            link_tag = item.find('a', href=True)

            if headline_tag:
                title = headline_tag.get_text().strip()
                link = ""

                if link_tag and 'href' in link_tag.attrs:
                    link = link_tag['href']
                elif headline_tag.find('a', href=True):
                    link = headline_tag.find('a', href=True)['href']

                if link and not link.startswith("http"):
                    link = "https://finance.yahoo.com" + link

                summary = summary_tag.get_text().strip() if summary_tag else ""

                if title and link:
                    articles.append({
                        "headline": title,
                        "summary": summary,
                        "url": link
                    })

            if len(articles) >= 5:
                break

        return articles[:5]

    except Exception as e:
        print(f"❌ Error scraping news for {symbol}: {str(e)}")
        return []

def process_single_stock(symbol):
    try:
        today = datetime.today().strftime('%Y-%m-%d')
        stock = yf.Ticker(symbol)
        hist = stock.history(period="1d")

        if hist.empty:
            return symbol, None, f"⚠ No stock data for {symbol}"

        row = hist.iloc[0]
        news = scrape_yahoo_finance_news(symbol)

        stock_info = {
            "Name": stock.info.get("shortName", "Unknown"),
            "Sector": stock.info.get("sector", "Unknown"),
            "Date": today,
            "Open": round(row["Open"], 2),
            "High": round(row["High"], 2),
            "Low": round(row["Low"], 2),
            "Close": round(row["Close"], 2),
            "Volume": int(row["Volume"]),
            "News": news
        }

        output = f"""
📊 {symbol} - {stock_info['Name']}
Sector: {stock_info['Sector']}
Date: {stock_info['Date']}
Open: {stock_info['Open']} | High: {stock_info['High']} | Low: {stock_info['Low']} | Close: {stock_info['Close']}
Volume: {stock_info['Volume']}

📰 Latest News:
""" + "\n".join([f"→ {a['headline']}\nSummary: {a['summary']}\nURL: {a['url']}" for a in news]) + "\n" + "-"*60

        return symbol, stock_info, output

    except Exception as e:
        return symbol, None, f"❌ Error processing {symbol}: {str(e)}"

def get_stock_data_with_news(ticker_list):
    result = {}

    with ThreadPoolExecutor(max_workers=10) as executor:  # Increase max_workers if needed
        futures = {executor.submit(process_single_stock, ticker): ticker for ticker in ticker_list}
        for future in as_completed(futures):
            symbol, stock_data, message = future.result()
            if stock_data:
                result[symbol] = stock_data
            print(message)

    return result

# Run the script
data = get_stock_data_with_news(tickers)

# Save to JSON
with open("combined_stock_news_data.json", "w") as f:
    json.dump(data, f, indent=4)

print("\n✅ All data saved to combined_stock_news_data.json")
