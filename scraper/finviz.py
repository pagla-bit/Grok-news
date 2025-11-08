# scraper/finviz.py
import asyncio
from playwright.async_api import async_playwright

async def get_finviz_news(ticker: str, limit: int = 10) -> list[str]:
    """Return up to *limit* news titles from Finviz (async)."""
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    news: list[str] = []

    try:
        async with async_playwright() as p:
            browser = await p.chromium.launch(headless=True)
            page = await browser.new_page()
            await page.goto(url, wait_until="networkidle", timeout=15000)

            # Wait for the news table (it may be empty)
            await page.wait_for_selector("table#news-table", timeout=8000)

            rows = await page.query_selector_all("table#news-table tr")
            for row in rows[:limit]:
                link = await row.query_selector("a.news-link")
                if link:
                    title = await link.text_content()
                    if title:
                        news.append(title.strip())
            await browser.close()
    except Exception:
        # Any error → return empty list (cached later)
        pass

    return news[:limit]
