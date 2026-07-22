# FinPulse 📈

> **Indian Stock Market Intelligence & Monitoring Platform**  
> Track, analyze, and compare NSE-listed stocks with real-time market data, interactive charts, AI Copilot insights, and a per-user portfolio tracker.

[![Live App](https://img.shields.io/badge/Live%20App-finpulse99.streamlit.app-brightgreen?style=for-the-badge&logo=streamlit)](https://finpulse99.streamlit.app/?t=c6e09a4bec326fed32afa9672503b2599b7bc4c61c09f7626dbebdef3ca1cbc7)
[![GitHub Repo](https://img.shields.io/badge/GitHub-AbhinavKumarX%2Ffinpulse-blue?style=for-the-badge&logo=github)](https://github.com/AbhinavKumarX/finpulse)

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green) ![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)

---

## 🌐 Live Application

- **Production URL**: [https://finpulse99.streamlit.app](https://finpulse99.streamlit.app)
- **Demo Session Link**: [https://finpulse99.streamlit.app/?t=c6e09a4bec326fed32afa9672503b2599b7bc4c61c09f7626dbebdef3ca1cbc7](https://finpulse99.streamlit.app/?t=c6e09a4bec326fed32afa9672503b2599b7bc4c61c09f7626dbebdef3ca1cbc7)
- **GitHub Repository**: [https://github.com/AbhinavKumarX/finpulse](https://github.com/AbhinavKumarX/finpulse)

---

## 🗂 Project Architecture

```
finpulse/
├── streamlit_app.py     # Main Streamlit Dashboard (Monolith entrypoint)
├── requirements.txt     # Global dependencies for Streamlit Cloud
├── backend/
│   ├── main.py          # FastAPI REST API endpoints
│   ├── database.py      # SQLite ORM layer (Multi-user, Shared Cache)
│   ├── fetcher.py       # yFinance market data engine & fallbacks
│   └── requirements.txt
├── frontend/
│   └── app.py           # Decoupled HTTP Streamlit client
└── README.md
```

---

## 🔐 Multi-User System

FinPulse features a **username-based identity and data isolation architecture**:

- **Unique User Identity**: No passwords required. Usernames act as claimable, unique handles (derived SHA-256 tokens).
- **Case Sensitivity Rules**: Login handles are case-sensitive (`admin` ≠ `Admin`), with a case-insensitive uniqueness check to prevent impersonation.
- **Pre-Allocated Watchlists**: New users are automatically provisioned with 20 random NIFTY 50 stocks upon registration.
- **Persistent Storage**: Watchlists, fundamental data, and portfolio holdings are stored in a multi-user SQLite database that survives browser reloads.

---

## 📊 Feature Overview

1. **Market Watchlist & Detail View**:
   - Live prices, 52-week range bars, key financials (P/E, P/B, ROE, ROA, Div Yield, Beta).
   - Interactive Plotly Candlestick / Line charts with 10D, 40D, and 90D Moving Average overlays.
   - 14-period RSI technical momentum indicator and live Yahoo Finance news feed.
2. **AI Copilot Insight**:
   - Automated qualitative commentary assessing valuation, efficiency, and analyst consensus targets.
3. **Stock Comparison Tool**:
   - 1-Year normalized return performance chart (base = 100).
   - Comparative bar charts (P/E, P/B, ROE, ROA), P/E vs ROE bubble chart, and sector allocation breakdown.
4. **Interactive Screener**:
   - Multi-metric filtering by P/E range, minimum ROE, max P/B, and minimum Market Capitalization with CSV export.
5. **Portfolio Management**:
   - Real-time tracking of buy price vs LTP, total investment, P&L per holding, return percentages, and allocation pie chart.

---

## 🗄 Database Design

```sql
-- Multi-User Tables
users            (user_id TEXT PRIMARY KEY, username TEXT UNIQUE, created_at TIMESTAMP)
user_tickers     (user_id TEXT, ticker TEXT, added_at TIMESTAMP, PRIMARY KEY(user_id, ticker))
user_portfolio   (user_id TEXT, ticker TEXT, shares REAL, buy_price REAL, PRIMARY KEY(user_id, ticker))

-- Shared High-Performance Caches
fundamental_data (ticker TEXT PRIMARY KEY, name, sector, market_cap, pe_ratio, current_price, roe, ...)
historical_prices(ticker TEXT, date TEXT, open, high, low, close, volume, PRIMARY KEY(ticker, date))
```

---

## 🚀 Local Setup & Execution

### Option A: Monolith Streamlit App (Recommended)
```bash
git clone https://github.com/AbhinavKumarX/finpulse.git
cd finpulse
pip install -r requirements.txt
streamlit run streamlit_app.py
```

### Option B: FastAPI Backend + Decoupled Client
```bash
# Terminal 1: Run Backend API
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2: Run Frontend App
cd frontend
pip install -r requirements.txt
streamlit run app.py
```
FastAPI Swagger Documentation: `http://localhost:8000/docs`

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| **Language** | Python 3.11+ |
| **Frontend** | Streamlit |
| **Backend API** | FastAPI + Uvicorn |
| **Database** | SQLite |
| **Data Fetcher** | yFinance + Yahoo Finance REST API |
| **Visualization** | Plotly Express & Graph Objects |
| **Deployment** | Streamlit Community Cloud |

---

## ⚠️ Disclaimer

FinPulse is a student project created for the **Society of Finance and Investing (SoFI) AlgoLabs Assignment**. Financial metrics are fetched from Yahoo Finance via `yfinance` and may be delayed. **Not financial advice.**
