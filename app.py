# app.py
import streamlit as st
import pandas as pd
import asyncio
from datetime import datetime, timedelta
import os
from scraper.finviz import get_finviz_news
from scraper.googlenews import get_google_news
from scraper.yfinance import get_yfinance_news
from sentiment.vader import analyze_vader
from sentiment.finbert import analyze_finbert
from utils.async_helper import run_async_tasks

st.set_page_config(page_title="Stock News Sentiment", layout="wide")
st.title("Stock News Sentiment Analyzer")

# --- Sidebar: Source Selection ---
st.sidebar.header("News Sources")
use_finviz = st.sidebar.checkbox("Finviz", value=True)
use_google = st.sidebar.checkbox("Google News", value=True)
use_yfinance = st.sidebar.checkbox("Yahoo Finance", value=True)

sources = []
if use_finviz: sources.append("finviz")
if use_google: sources.append("google")
if use_yfinance: sources.append("yfinance")

if not sources:
    st.warning("Please select at least one news source.")
    st.stop()

# --- Input: Tickers ---
st.header("Enter Stock Tickers")
ticker_input = st.text_input(
    "Comma-separated (e.g. AAPL, TSLA, NVDA)",
    placeholder="AAPL, MSFT"
)

uploaded_file = st.file_uploader("Or upload CSV (column: 'ticker')", type=["csv"])

tickers = []
if uploaded_file:
    df = pd.read_csv(uploaded_file)
    if 'ticker' not in df.columns:
        st.error("CSV must have 'ticker' column.")
        st.stop()
    tickers = [t.strip().upper() for t in df['ticker'].dropna().unique()]
    st.success(f"Loaded {len(tickers)} tickers from file.")
else:
    if ticker_input:
        tickers = [t.strip().upper() for t in ticker_input.split(",") if t.strip()]

if not tickers:
    st.info("Enter tickers or upload a CSV to start.")
    st.stop()

tickers = list(dict.fromkeys(tickers))  # dedupe

# --- Cache Key ---
@st.cache_data(ttl=3600, show_spinner=False)  # 1 hour cache
def get_sentiment_cached(ticker, source):
    news_func = {
        "finviz": get_finviz_news,
        "google": get_google_news,
        "yfinance": get_yfinance_news,
    }[source]
    news = news_func(ticker)
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

# --- Run Analysis ---
if st.button("Analyze Sentiment", type="primary"):
    results = []
    progress_bar = st.progress(0)
    status_text = st.empty()

    total_tasks = len(tickers) * len(sources)
    completed = 0

    # Build tasks
    tasks = []
    for ticker in tickers:
        for source in sources:
            tasks.append((ticker, source))

    # Run async
    sentiment_results = run_async_tasks(
        tasks,
        lambda t: get_sentiment_cached(t[0], t[1]),
        max_concurrent=10  # Safe for Streamlit Cloud
    )

    # Aggregate per ticker
    agg = {t: {"vader_pos": 0, "vader_neg": 0, "finbert_pos": 0, "finbert_neg": 0} for t in tickers}
    for (ticker, source), res in zip(tasks, sentiment_results):
        for k in agg[ticker]:
            agg[ticker][k] += res[k]
        completed += 1
        progress_bar.progress(completed / total_tasks)
        status_text.text(f"Processed {ticker} - {source}... ({completed}/{total_tasks})")

    # Build final DF
    for ticker in tickers:
        r = agg[ticker]
        results.append({
            "Ticker": ticker,
            "VADER_Pos": r["vader_pos"],
            "VADER_Neg": r["vader_neg"],
            "FinBERT_Pos": r["finbert_pos"],
            "FinBERT_Neg": r["finbert_neg"],
        })

    df = pd.DataFrame(results)
    st.success("Analysis Complete!")
    st.dataframe(df, use_container_width=True)

    # Download
    csv = df.to_csv(index=False)
    st.download_button("Download Results", csv, "sentiment_results.csv", "text/csv")
