"""
stock_tools.py — StockSense
---------------------------
Defines the tools available to the LangChain ReAct agent.

Tools:
  1. get_stock_price   — Fetches live price, volume, and 5-day change via yfinance
  2. get_company_info  — Fetches company fundamentals (P/E, market cap, sector)
  3. get_latest_news   — Fetches recent news headlines via NewsAPI

The agent decides WHEN and HOW to use each tool based on the user's query.
This is the "agentic" part — it's not a fixed pipeline.
"""

import os
from typing import Optional

import yfinance as yf
from dotenv import load_dotenv
from langchain_core.tools import tool

load_dotenv()

NEWS_API_KEY = os.getenv("NEWS_API_KEY")


@tool
def get_stock_price(ticker: str) -> str:
    """
    Fetch current stock price, 5-day performance, volume, and 52-week range
    for a given ticker symbol (e.g. AAPL, MSFT, TSLA, RELIANCE.NS for NSE).

    Use this when you need current price data or recent stock performance.
    """
    try:
        stock = yf.Ticker(ticker.upper().strip())
        hist  = stock.history(period="5d")

        if hist.empty:
            return f"No price data found for ticker '{ticker}'. Please verify the symbol."

        current_price = hist["Close"].iloc[-1]
        open_price    = hist["Open"].iloc[0]   # 5-day open
        volume        = hist["Volume"].iloc[-1]
        high_5d       = hist["High"].max()
        low_5d        = hist["Low"].min()

        # 1-day change
        if len(hist) >= 2:
            prev_close  = hist["Close"].iloc[-2]
            day_change  = current_price - prev_close
            day_pct     = (day_change / prev_close) * 100
        else:
            day_change = day_pct = 0

        # 5-day change
        five_day_pct = ((current_price - open_price) / open_price) * 100

        # 52-week data from info
        info = stock.info
        week52_high = info.get("fiftyTwoWeekHigh", "N/A")
        week52_low  = info.get("fiftyTwoWeekLow",  "N/A")

        return (
            f"📈 {ticker.upper()} Stock Data\n"
            f"Current Price : ${current_price:.2f}\n"
            f"Day Change    : ${day_change:+.2f} ({day_pct:+.2f}%)\n"
            f"5-Day Change  : {five_day_pct:+.2f}%\n"
            f"5-Day High/Low: ${high_5d:.2f} / ${low_5d:.2f}\n"
            f"52-Week High  : ${week52_high}\n"
            f"52-Week Low   : ${week52_low}\n"
            f"Volume (today): {int(volume):,}"
        )

    except Exception as e:
        return f"Error fetching price data for {ticker}: {str(e)}"


@tool
def get_company_info(ticker: str) -> str:
    """
    Fetch company fundamentals including market cap, P/E ratio, EPS, dividend
    yield, sector, industry, and a short business description.

    Use this when you need to understand the company's financial profile
    or business model before making an analysis.
    """
    try:
        stock = yf.Ticker(ticker.upper().strip())
        info  = stock.info

        if not info or "longName" not in info:
            return f"No company information found for ticker '{ticker}'."

        # Format large numbers
        def fmt_large(val):
            if not val:
                return "N/A"
            if val >= 1e12: return f"${val/1e12:.2f}T"
            if val >= 1e9:  return f"${val/1e9:.2f}B"
            if val >= 1e6:  return f"${val/1e6:.2f}M"
            return f"${val:,.0f}"

        market_cap    = fmt_large(info.get("marketCap"))
        pe_ratio      = info.get("trailingPE",   "N/A")
        fwd_pe        = info.get("forwardPE",    "N/A")
        eps           = info.get("trailingEps",  "N/A")
        div_yield     = info.get("dividendYield", 0)
        div_yield_str = f"{div_yield*100:.2f}%" if div_yield else "No Dividend"
        beta          = info.get("beta",         "N/A")
        sector        = info.get("sector",       "N/A")
        industry      = info.get("industry",     "N/A")
        description   = info.get("longBusinessSummary", "No description available.")
        # Truncate long descriptions
        if len(description) > 500:
            description = description[:500] + "..."

        return (
            f"🏢 {info.get('longName', ticker)} ({ticker.upper()})\n"
            f"Sector        : {sector}\n"
            f"Industry      : {industry}\n"
            f"Market Cap    : {market_cap}\n"
            f"P/E Ratio     : {pe_ratio}\n"
            f"Forward P/E   : {fwd_pe}\n"
            f"EPS           : {eps}\n"
            f"Dividend Yield: {div_yield_str}\n"
            f"Beta          : {beta}\n\n"
            f"About:\n{description}"
        )

    except Exception as e:
        return f"Error fetching company info for {ticker}: {str(e)}"


@tool
def get_latest_news(query: str) -> str:
    """
    Fetch the latest financial news articles about a company, ticker, or topic.
    Returns top 5 headlines with publication date and description.

    Use this to get the latest news that might affect stock sentiment.
    Ideal for queries like 'latest news about Apple' or 'TSLA earnings news'.
    """
    if not NEWS_API_KEY:
        return (
            "NEWS_API_KEY is not set. To enable live news, add your key from "
            "newsapi.org to the .env file. The analysis will proceed without news data."
        )

    try:
        import requests

        url    = "https://newsapi.org/v2/everything"
        params = {
            "q":        query,
            "language": "en",
            "sortBy":   "publishedAt",
            "pageSize": 5,
            "apiKey":   NEWS_API_KEY,
        }

        response = requests.get(url, params=params, timeout=10)
        data     = response.json()

        if data.get("status") != "ok":
            return f"NewsAPI error: {data.get('message', 'Unknown error')}"

        articles = data.get("articles", [])
        if not articles:
            return f"No recent news found for: {query}"

        formatted = [f"📰 Latest News: {query}\n"]
        for i, article in enumerate(articles[:5], 1):
            title       = article.get("title",       "No title")
            description = article.get("description", "No description")
            source      = article.get("source", {}).get("name", "Unknown")
            published   = article.get("publishedAt", "")[:10]  # Just the date

            # Truncate long descriptions
            if description and len(description) > 200:
                description = description[:200] + "..."

            formatted.append(
                f"\n{i}. [{source}] {published}\n"
                f"   Title: {title}\n"
                f"   {description}"
            )

        return "\n".join(formatted)

    except Exception as e:
        return f"Error fetching news: {str(e)}"
