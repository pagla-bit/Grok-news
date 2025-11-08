# scraper/yfinance.py
import requests
from bs4 import BeautifulSoup

def get_yfinance_news(ticker: str, limit=10):
    url = f"https://finance.yahoo.com/quote/{ticker}/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    try:
        resp = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(resp.text, "lxml")
        items = soup.find_all("h3", class_="Mb(5px)")
        news = [item.get_text() for item in items[:limit]]
        return news
    except:
        return []
