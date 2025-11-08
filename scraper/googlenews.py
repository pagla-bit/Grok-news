# scraper/googlenews.py
import feedparser
import re

def get_google_news(ticker: str, limit=10):
    query = f"{ticker} stock"
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    news = []
    for entry in feed.entries[:limit]:
        title = entry.title
        if ticker.upper() in title.upper():
            news.append(title)
    return news[:limit]
