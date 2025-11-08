# --------------------------------------------------------------
# app.py  –  FULLY WORKING VERSION
# --------------------------------------------------------------
import streamlit as st                 # <-- MUST BE FIRST!
import pandas as pd
import asyncio
from datetime import timedelta
import os

# --- Import our modules -------------------------------------------------
from scraper.finviz import get_finviz_news
from scraper.googlenews import get_google_news
from scraper.yfinance import get_yfinance_news
from sentiment.vader import analyze_vader
from sentiment.finbert import analyze_finbert
from utils.async_helper import run_async_tasks

# -------------------------- Streamlit UI -------------------------------
st.set_page_config(page_title="Stock News Sentiment", layout="wide")
st.title("Stock News Sentiment Analyzer")

# --- Sidebar: Source Selection ---
st.sidebar.header("News Sources")
use_finviz   = st.sidebar.checkbox("Finviz", value=True)
use_google   = st.sidebar.checkbox("Google News", value=True)
use_yfinance = st.sidebar.checkbox("Yahoo Finance", value=True)

sources = []
if use_finviz:   sources.append("finviz")
if use_google:   sources.append("google")
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

tickers = list(dict.fromkeys(tickers))   # dedupe

# -------------------------- CACHING ------------------------------------
@st.cache_data(ttl=3600, show_spinner=False)   # 1-hour cache
def get_sentiment_cached(ticker: str, source: str):
    # Choose scraper
    scraper = {
        "finviz":   get_finviz_news,
        "google":   get_google_news,
        "yfinance": get_yfinance_news,
    }[source]

    # ---- Run scraper -------------------------------------------------
    if source == "finviz":                     # async scraper
        news = asyncio.run(scraper(ticker))
    else:                                      # sync scrapers
        news = scraper(ticker)

    # Guarantee a list (defensive)
    news = news or []

    if not news:
        return {"vader_pos":0, "vader_neg":0, "finbert_pos":0, "finbert_neg":0}

    vader_pos, vader_neg = analyze_vader(news)
    finbert_pos, finbert_neg = analyze_finbert(news)

    return {
        "vader_pos": vader_pos,
        "vader_neg": vader_neg,
        "finbert_pos": finbert_pos,
        "finbert_neg": finbert_neg,
    }

# -------------------------- RUN ANALYSIS -------------------------------
if st.button("Analyze Sentiment", type="primary"):
    tasks = [(t, s) for t in tickers for s in sources]

    progress_bar = st.progress(0)
    status_text  = st.empty()

    # ---- Async execution with limited concurrency --------------------
    results = run_async_tasks(
        task_args=tasks,
        task_func=lambda pair: get_sentiment_cached(pair[0], pair[1]),
        max_concurrent=8
    )

    # ---- Aggregate per ticker ---------------------------------------
    agg = {t: {"vader_pos":0, "vader_neg":0, "finbert_pos":0, "finbert_neg":0}
           for t in tickers}

    for (ticker, src), res in zip(tasks, results):
        for k in agg[ticker]:
            agg[ticker][k] += res[k]

        # Update UI
        idx = tasks.index((ticker, src)) + 1
        progress_bar.progress(idx / len(tasks))
        status_text.text(f"{ticker} – {src} … ({idx}/{len(tasks)})")

    # ---- Build final DataFrame --------------------------------------
    rows = []
    for t in tickers:
        r = agg[t]
        rows.append({
            "Ticker": t,
            "VADER_Pos": r["vader_pos"],
            "VADER_Neg": r["vader_neg"],
            "FinBERT_Pos": r["finbert_pos"],
            "FinBERT_Neg": r["finbert_neg"],
        })

    df = pd.DataFrame(rows)
    st.success("Analysis complete!")
    st.dataframe(df, use_container_width=True)

    csv = df.to_csv(index=False).encode()
    st.download_button(
        "Download CSV",
        data=csv,
        file_name="sentiment_results.csv",
        mime="text/csv"
    )
