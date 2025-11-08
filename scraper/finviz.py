# scraper/finviz.py
import asyncio
from playwright.async_api import async_playwright
import re

async def get_finviz_news(ticker: str, limit=10):
    url = f"https://finviz.com/quote.ashx?t={ticker}"
    news = []
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        page = await browser.new_page()
        await page.goto(url, wait_until="networkidle")
        await page.wait_for_selector("table#news-table", timeout=10000)

        rows = await page.query_selector_all("table#news-table tr")
        for row in rows[:limit]:
            link_elem = await row.query_selector("a.news-link")
            if not link_elem: continue
            title = await link_elem.text_content()
            href = await link_elem.get_attribute("href")
            news.append(title.strip())
        await browser.close()
    return news[:limit]
