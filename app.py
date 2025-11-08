# app.py  (only the changed part – replace the whole file or just this snippet)

# ------------------------------------------------------------------
# CACHE FUNCTION
# ------------------------------------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)          # 1-hour cache
def get_sentiment_cached(ticker: str, source: str):
    news_func = {
        "finviz": get_finviz_news,
        "google": get_google_news,
        "yfinance": get_yfinance_news,
    }[source]

    # *** ALL SCRAPERS NOW GUARANTEE A LIST ***
    news = news_func(ticker) if source != "finviz" else asyncio.run(news_func(ticker))

    # If for any reason news is None → treat as empty list
    news = news or []

    if not news:
        return {"vader_pos": 0, "vader_neg": 0, "finbert_pos": 0, "finbert_neg": 0}

    vader_pos, vader_neg = analyze_vader(news)
    finbert_pos, finbert_neg = analyze_finbert(news)
    return {
        "vader_pos": vader_pos,
        "vader_neg": vader_neg,
        "finbert_pos": finbert_pos,
        "finbert_neg": finbert_neg,
    }
