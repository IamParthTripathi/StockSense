<!-- Badges -->
![Python](https://img.shields.io/badge/Python-3.11-3776AB?style=flat&logo=python&logoColor=white)
![LangChain](https://img.shields.io/badge/LangChain-1.3-1C3C3C?style=flat)
![OpenAI](https://img.shields.io/badge/OpenAI-GPT--4o--mini-412991?style=flat&logo=openai&logoColor=white)
![yfinance](https://img.shields.io/badge/yfinance-0.2.54-00897B?style=flat)
![Streamlit](https://img.shields.io/badge/Streamlit-1.45-FF4B4B?style=flat&logo=streamlit&logoColor=white)
![License](https://img.shields.io/badge/License-MIT-green?style=flat)
![Status](https://img.shields.io/badge/Status-Live%20Demo-brightgreen?style=flat)

---

# 📈 StockSense — AI Financial Research Agent

> **Type a ticker. Get a complete investment brief with live data, news, and AI analysis.**

**[▶ Live Demo](https://iamparthtripathi-stocksense.hf.space/)** &nbsp;|&nbsp;
**[📹 Demo Video](#)** &nbsp;|&nbsp;
**[📄 Technical Blog Post](#)**

---

![StockSense Demo](assets/demo.gif)

---

## 🎯 Problem Statement

Individual investors and students have to manually check stock prices on one site,
financial ratios on another, and news on a third — then mentally combine it all.
StockSense automates this entire research workflow through an AI agent that
fetches all data autonomously and synthesizes it into one structured brief.

---

## ✨ Key Features

| Feature | Description |
|---------|-------------|
| 🤖 **Agentic Tool-Calling** | LLM decides which tools to call and when — not a fixed pipeline |
| 📡 **Live Price Data** | Real-time stock price, daily change, 52-week range via yfinance |
| 🏢 **Company Fundamentals** | Market cap, P/E, EPS, dividend yield, beta, sector |
| 📰 **News Sentiment** | Latest headlines → Bullish/Bearish/Neutral classification |
| 📋 **Structured Brief** | BUY/HOLD/SELL recommendation with reasoning and confidence level |
| 📉 **Interactive Chart** | 30-day price chart rendered in the UI |
| ⬇️ **Export** | Download the analysis as a text file |
| 🇮🇳 **Indian Stocks** | Supports NSE (`.NS`) and BSE (`.BO`) tickers |

---

## 🏗️ Agent Architecture (ReAct Pattern)

```
User: "Analyze Apple (AAPL)"
         │
         ▼
┌─────────────────────────────────────────────┐
│          LangChain ReAct Agent               │
│    (gemini-1.5-flash + System Prompt)   n   │
│                                             │
│  REASON: "I need price data first"          │
│     └──▶ CALL: get_stock_price("AAPL")      │
│           └──▶ yfinance API                 │
│                └──▶ "$196.45 (+1.2%)"       │
│                                             │
│  REASON: "Now I need fundamentals"          │
│     └──▶ CALL: get_company_info("AAPL")     │
│           └──▶ yfinance API                 │
│                └──▶ "Market cap: $3.0T..."  │
│                                             │
│  REASON: "Now I need latest news"           │
│     └──▶ CALL: get_latest_news("Apple")     │
│           └──▶ NewsAPI                      │
│                └──▶ "5 headlines..."        │
│                                             │
│  REASON: "I have all data, generate report" │
│     └──▶ Synthesize → Structured Brief      │
└──────────────────────────────────────────────┘
         │
         ▼
  Final Investment Brief (BUY/HOLD/SELL)
```

**Why agent over fixed pipeline?**
A pipeline always calls tools in the same order. An agent can:
- Skip news if the query is just "what's the price?"
- Call the same tool multiple times if needed
- Adapt its strategy based on intermediate results
This flexibility makes it more robust and extensible.

---

## 📊 Technical Metrics

| Metric | Result |
|--------|--------|
| Average analysis time | **15-25 seconds** |
| Tickers supported | **8,000+** (US) + Indian NSE/BSE |
| Tools available to agent | **3** (price, fundamentals, news) |
| Max agent iterations | **8** (prevents infinite loops) |
| Cost per analysis (gemini-1.5-flash) | **~$0.01 USD** |

---

## 🛠️ Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| Agent Framework | LangChain 1.3 (LCEL) | ReAct agent + tool orchestration |
| LLM | gemini-1.5-flash | Reasoning and report generation |
| Stock Data | yfinance 0.2.54 | Real-time price + fundamentals (free) |
| News Data | NewsAPI | Latest financial headlines |
| Frontend | Streamlit 1.45 | Interactive UI + chart rendering |
| Deployment | HuggingFace Spaces | Free hosting with GPU/CPU |

---

## 🚀 Run Locally

### Prerequisites
- Python 3.11+
- Google API key
- NewsAPI key (free at newsapi.org — optional)

### Setup

```bash
# 1. Clone the repo
git clone https://github.com/IamParthTripathi/stocksense.git
cd stocksense

# 2. Create virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Configure environment
cp .env.example .env
# Edit .env:
#   GOOGLE_API_KEY=your_key_here
#   NEWS_API_KEY=your_key_here  (optional)

# 5. Run
streamlit run app.py
```

### Ticker Format Guide

| Market | Format | Example |
|--------|--------|---------|
| US Stock (NYSE/NASDAQ) | `TICKER` | `AAPL`, `TSLA`, `NVDA` |
| NSE India | `TICKER.NS` | `TCS.NS`, `RELIANCE.NS` |
| BSE India | `TICKER.BO` | `TCS.BO`, `INFY.BO` |
| Crypto | `TICKER-USD` | `BTC-USD`, `ETH-USD` |

---

## 📁 Project Structure

```
stocksense/
├── app.py              # Main Streamlit UI
├── agent.py            # LangChain ReAct agent + system prompt
├── stock_tools.py      # Tool definitions (price, fundamentals, news)
├── requirements.txt    # Dependencies
├── Dockerfile          # HuggingFace Spaces config
├── .env.example        # Environment variable template
├── .gitignore
└── assets/
    └── demo.gif        # Demo animation
```

---

## 🧠 Key Technical Decisions

**Why `create_openai_tools_agent` over basic ReAct?**
OpenAI's native function-calling API is more reliable than text-based ReAct
because the tool selection is structured JSON rather than parsed text. This
eliminates a whole class of parsing errors common in basic ReAct agents.

**Why yfinance over a paid financial API?**
yfinance is free, has no rate limits for personal use, and covers 8,000+ global
tickers including Indian NSE/BSE. For a portfolio project, it's the right tool —
it demonstrates real API integration without requiring paid subscriptions.

**Why `max_iterations=8`?**
Without a cap, a buggy tool or unclear query can cause the agent to call tools
repeatedly. 8 iterations is enough for the full analysis (price + fundamentals
+ news + generation) while preventing infinite loops.

---

## 📈 Future Roadmap

- [ ] Add technical indicators (RSI, MACD, Moving averages)
- [ ] Portfolio analysis (analyze multiple stocks, suggest allocation)
- [ ] Earnings calendar integration
- [ ] Email alerts for buy/sell signals
- [ ] Fine-tuned sentiment model on financial news dataset

---

## ⚠️ Important Disclaimer

StockSense is built for **educational and portfolio demonstration purposes only**.
The analysis it produces is AI-generated and based on publicly available data.
**This is NOT financial advice.** Never make investment decisions based solely on
AI output. Always consult a qualified financial professional.

---

## 📄 License

MIT License — free to use, modify, and distribute.

---

⭐ **If StockSense helped you, please star the repo!**

*Built by [Parth Tripathi](https://linkedin.com/in/iamparthtripathi) — AI Engineer*
