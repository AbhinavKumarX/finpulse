# FinPulse 📈

> **Indian Stock Market Intelligence Platform**  
> Track, analyse, and compare NSE-listed stocks with real-time market data, interactive charts, and a per-user portfolio tracker.

![Python](https://img.shields.io/badge/Python-3.11-blue) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green) ![Streamlit](https://img.shields.io/badge/Streamlit-1.35-red) ![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)

---

## 🗂 Project Architecture

```
finpulse/
├── backend/
│   ├── main.py          # FastAPI REST API
│   ├── database.py      # SQLite ORM layer (multi-user)
│   ├── fetcher.py       # yFinance data fetcher
│   └── requirements.txt
├── frontend/
│   ├── app.py           # Streamlit dashboard
│   └── requirements.txt
├── .streamlit/
│   └── config.toml      # Streamlit theme config
├── render.yaml          # Render.com deploy config (backend)
└── README.md
```

---

## 🔐 Multi-User System

FinPulse supports multiple independent users with **username-based identity**:

- Each user gets their **own isolated watchlist** (20 random Nifty 50 stocks pre-loaded)
- **Portfolio holdings are stored in the database** — persist across browser sessions
- Usernames are **case-sensitive** and **globally unique** (case-insensitive uniqueness check)
- Session persists via `localStorage` — no re-login needed until sign out

---

## 🚀 Local Development

### 1. Start the Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```

API docs available at: `http://localhost:8000/docs`

### 2. Start the Frontend

```bash
cd frontend
pip install -r requirements.txt
streamlit run app.py
```

Open: `http://localhost:8501`

---

## 🌐 API Endpoints

| Method | Endpoint | Auth | Description |
|--------|----------|------|-------------|
| `POST` | `/auth/register` | ❌ | Create a new user account |
| `POST` | `/auth/login` | ❌ | Login and receive a session token |
| `GET` | `/auth/me` | ✅ | Get current user info |
| `GET` | `/stocks` | ✅ | Get user's watchlist with fundamentals |
| `POST` | `/stocks/{ticker}` | ✅ | Add stock to user's watchlist |
| `DELETE` | `/stocks/{ticker}` | ✅ | Remove stock from watchlist |
| `POST` | `/stocks/{ticker}/refresh` | ✅ | Force re-fetch fundamentals |
| `GET` | `/stocks/{ticker}/history` | ❌ | Get historical price data |
| `GET` | `/stocks/{ticker}/news` | ❌ | Get latest news for a stock |
| `GET` | `/market-indices` | ❌ | NIFTY 50, SENSEX, NIFTY BANK, BTC |
| `GET` | `/market-summary` | ✅ | User-scoped market summary |
| `GET` | `/portfolio` | ✅ | Get user's portfolio holdings |
| `POST` | `/portfolio` | ✅ | Add/update a holding |
| `DELETE` | `/portfolio/{ticker}` | ✅ | Remove a holding |
| `GET` | `/export-report` | ✅ | Export watchlist as CSV |
| `GET` | `/search?q=` | ❌ | Search for stocks |

Auth: `X-User-Token` header (returned by `/auth/login` or `/auth/register`)

---

## 🗄 Database Design

```sql
users            -- user_id (SHA-256 hash), username, created_at
user_tickers     -- per-user watchlist (user_id, ticker)
user_portfolio   -- per-user holdings (user_id, ticker, shares, buy_price)
fundamental_data -- global shared cache of stock fundamentals
historical_prices -- global shared cache of OHLCV data
```

---

## 📊 Dashboard Features

- **Dashboard Tab**: Hero stock card, AI Copilot summary, 52W range bar, key financials, candlestick/line charts with MA overlays, RSI, news feed
- **Compare Tab**: Normalised 1Y performance, P/E & ROE bar charts, P/E vs ROE bubble chart, sector donut
- **Screener Tab**: Filter by P/E, P/B, ROE, market cap. Export to CSV
- **Portfolio Tab**: Track buy price vs LTP, P&L per holding, total return, allocation donut

---

## 🛠 Tech Stack

| Layer | Technology |
|-------|-----------|
| Language | Python 3.11 |
| Backend | FastAPI + Uvicorn |
| Frontend | Streamlit |
| Database | SQLite |
| Data | yFinance (NSE/BSE via Yahoo Finance) |
| Charts | Plotly |
| Auth | SHA-256 username hashing (no passwords) |
| Deploy (Backend) | Render.com |
| Deploy (Frontend) | Streamlit Community Cloud |
| Version Control | Git + GitHub |

---

## 📦 External Libraries & APIs

- **yFinance** — Yahoo Finance wrapper for NSE/BSE market data
- **FastAPI** — REST API framework
- **Streamlit** — Interactive dashboard framework
- **Plotly** — Interactive charts
- **st-keyup** — Real-time search input component
- **Yahoo Finance Search API** — Ticker search endpoint (`query2.finance.yahoo.com`)

---

## ⚠️ Disclaimer

FinPulse is a student project built for the SoFI AlgoLabs assignment. Data is sourced from Yahoo Finance via yFinance and may be delayed. **Not financial advice.**
