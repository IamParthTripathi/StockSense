"""
app.py — StockSense
-------------------
AI-Powered Financial Research Agent with Live Data.
Uses LangChain ReAct agent with tool-calling to:
  - Fetch live stock prices via yfinance
  - Fetch company fundamentals via yfinance
  - Fetch latest news via NewsAPI
  - Generate a structured investment brief

Run locally: streamlit run app.py
"""

import streamlit as st
from agent import analyze_stock

# ─────────────────────────────────────────────
# Page configuration
# ─────────────────────────────────────────────
st.set_page_config(
    page_title="StockSense — AI Financial Analyst",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ─────────────────────────────────────────────
# Custom CSS
# ─────────────────────────────────────────────
st.markdown("""
<style>
    .main-title { font-size: 2.4rem; font-weight: 800; color: #1a7f37; }
    .subtitle   { font-size: 1rem; color: #666; margin-bottom: 1.5rem; }
    .disclaimer {
        background: #fff3cd;
        border: 1px solid #ffc107;
        border-radius: 6px;
        padding: 10px 14px;
        font-size: 0.85rem;
        color: #856404;
        margin: 12px 0;
    }
    .tool-badge {
        display: inline-block;
        background: #e6f4ea;
        color: #1a7f37;
        border: 1px solid #34a853;
        border-radius: 12px;
        padding: 2px 10px;
        font-size: 0.78rem;
        margin: 2px;
    }
    .report-box {
        background: #f8f9fa;
        border: 1px solid #dee2e6;
        border-radius: 8px;
        padding: 20px;
        font-family: monospace;
        white-space: pre-wrap;
        line-height: 1.6;
    }
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────
# Header
# ─────────────────────────────────────────────
st.markdown('<p class="main-title">📈 StockSense</p>', unsafe_allow_html=True)
st.markdown(
    '<p class="subtitle">AI Financial Research Agent · Live Price Data · News Sentiment · Investment Brief</p>',
    unsafe_allow_html=True,
)

st.markdown("""
<div class="disclaimer">
⚠️ <strong>Disclaimer:</strong> StockSense is for <strong>educational and demonstration purposes only</strong>.
This is NOT financial advice. Always consult a qualified financial advisor before making investment decisions.
</div>
""", unsafe_allow_html=True)

st.divider()

# ─────────────────────────────────────────────
# Sidebar — Quick Stock Examples
# ─────────────────────────────────────────────
with st.sidebar:
    st.header("📌 Quick Examples")
    st.caption("Click to auto-fill the form")

    examples = [
        ("Apple",     "AAPL"),
        ("Microsoft", "MSFT"),
        ("Tesla",     "TSLA"),
        ("NVIDIA",    "NVDA"),
        ("Google",    "GOOGL"),
        ("Amazon",    "AMZN"),
        ("Meta",      "META"),
        ("Infosys",   "INFY"),   # Indian stock, NSE listed
        ("TCS",       "TCS.NS"), # NSE symbol format
        ("Reliance",  "RELIANCE.NS"),
    ]

    for company_ex, ticker_ex in examples:
        if st.button(f"{company_ex} ({ticker_ex})", use_container_width=True):
            st.session_state["company_input"] = company_ex
            st.session_state["ticker_input"]  = ticker_ex
            st.rerun()

    st.divider()
    st.markdown("""
    **How StockSense works:**
    
    1. LangChain ReAct agent receives your request
    2. Agent REASONS which tools to call
    3. Calls `get_stock_price` → live price
    4. Calls `get_company_info` → fundamentals
    5. Calls `get_latest_news` → headlines
    6. Synthesizes all data into a structured brief
    
    **Ticker format tips:**
    - US stocks: `AAPL`, `MSFT`
    - NSE (India): `TCS.NS`, `RELIANCE.NS`
    - BSE (India): `TCS.BO`
    """)

# ─────────────────────────────────────────────
# Input Form
# ─────────────────────────────────────────────
col1, col2 = st.columns([2, 1], gap="medium")

with col1:
    company = st.text_input(
        "Company Name",
        value=st.session_state.get("company_input", ""),
        placeholder="e.g. Apple",
        key="company_input",
    )

with col2:
    ticker = st.text_input(
        "Ticker Symbol",
        value=st.session_state.get("ticker_input", ""),
        placeholder="e.g. AAPL",
        key="ticker_input",
    )

can_analyze = bool(company.strip()) and bool(ticker.strip())

analyze_btn = st.button(
    "🔍 Analyze Stock",
    type="primary",
    disabled=not can_analyze,
    use_container_width=False,
)

if not can_analyze and not analyze_btn:
    st.caption("Enter a company name and ticker symbol to run analysis.")

# ─────────────────────────────────────────────
# Analysis Section
# ─────────────────────────────────────────────
if analyze_btn and can_analyze:
    ticker_clean  = ticker.strip().upper()
    company_clean = company.strip()

    st.divider()
    st.subheader(f"🔄 Analyzing {company_clean} ({ticker_clean})...")

    # Show what the agent is doing
    status = st.empty()
    status.markdown(f"""
    🤖 **AI Agent is working...**
    - 📡 Fetching live stock price for `{ticker_clean}`
    - 🏢 Retrieving company fundamentals
    - 📰 Searching latest news headlines
    - 📊 Generating investment brief...
    """)

    with st.spinner(f"Running analysis for {company_clean} (~15-25 seconds)..."):
        results = analyze_stock(company_clean, ticker_clean)

    status.empty()

    # ── Error handling ──
    if results.get("error"):
        st.error(f"""
❌ Analysis failed: {results['error']}

**Common causes:**
- Invalid ticker symbol (try `AAPL` not `apple`)
- For Indian stocks: use `TCS.NS` (NSE) or `TCS.BO` (BSE) format
- Network timeout — please try again
        """)
        st.stop()

    st.success(f"✅ Analysis complete for {company_clean}!")

    # Show which tools were called
    tools_used = results.get("tools_used", [])
    if tools_used:
        tool_labels = {
            "get_stock_price":  "📈 Live Price Data",
            "get_company_info": "🏢 Company Fundamentals",
            "get_latest_news":  "📰 Latest News",
        }
        tools_html = " ".join([
            f'<span class="tool-badge">{tool_labels.get(t, t)}</span>'
            for t in tools_used
        ])
        st.markdown(f"**Tools used by agent:** {tools_html}", unsafe_allow_html=True)

    st.divider()

    # Display the report
    st.subheader("📊 Investment Analysis Report")
    st.markdown(results["report"])

    # Download button
    st.download_button(
        label="⬇️ Download Report (.txt)",
        data=results["report"],
        file_name=f"stocksense_{ticker_clean}_analysis.txt",
        mime="text/plain",
    )

    # Historical chart
    st.divider()
    st.subheader(f"📉 {ticker_clean} — 30-Day Price Chart")

    try:
        import yfinance as yf
        import pandas as pd

        stock_data = yf.Ticker(ticker_clean).history(period="1mo")
        if not stock_data.empty:
            chart_df = stock_data[["Close"]].rename(columns={"Close": f"{ticker_clean} Price ($)"})
            st.line_chart(chart_df)
        else:
            st.caption("Could not load chart data for this ticker.")
    except Exception as chart_err:
        st.caption(f"Chart unavailable: {str(chart_err)}")

# ─────────────────────────────────────────────
# Landing state — show capabilities
# ─────────────────────────────────────────────
if not analyze_btn:
    st.divider()
    st.subheader("🧠 What StockSense Analyzes")

    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown("""
**📈 Live Market Data**
- Current stock price (real-time)
- Daily and 5-day price change
- Volume and 52-week range
- Powered by Yahoo Finance API (free)
        """)
    with col2:
        st.markdown("""
**🏢 Company Fundamentals**
- Market capitalization
- P/E ratio (trailing + forward)
- EPS, dividend yield, beta
- Sector and industry classification
        """)
    with col3:
        st.markdown("""
**📰 News Sentiment**
- Latest 5 news headlines
- Sentiment classification (Bullish/Bearish/Neutral)
- Key catalysts identified
- Risk factors highlighted
        """)
