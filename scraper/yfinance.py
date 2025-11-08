# scraper/yfinance.py
import requests
from bs4 import BeautifulSoup

def get_yfinance_news(ticker: str, limit: int = 10) -> list[str]:
    """Return up to *limit* news headlines from Yahoo Finance."""
    url = f"https://finance.yahoo.com/quote/{ticker}/news"
    headers = {"User-Agent": "Mozilla/5.0"}
    news: list[str] = []

    try:
        resp = requests.get(url, headers=headers, timeout=12)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "lxml")
        items = soup.find_all("h3", class_="Mb(5px)")[:limit]
        for h in items:
            txt = h.get_text(strip=True)
            if txt:
                news.append(txt)
    except Exception:
        pass

    return news[:limit]
