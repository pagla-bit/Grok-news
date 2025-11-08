# scraper/googlenews.py
import feedparser

def get_google_news(ticker: str, limit: int = 10) -> list[str]:
    """Return up to *limit* titles from Google News RSS."""
    query = f"{ticker} stock"
    url = f"https://news.google.com/rss/search?q={query}&hl=en-US&gl=US&ceid=US:en"
    feed = feedparser.parse(url)
    news: list[str] = []

    for entry in feed.entries[:limit]:
        title = entry.get("title", "").strip()
        if title and ticker.upper() in title.upper():
            news.append(title)

    return news[:limit]
