# FinPulse 📈

> **Indian Stock Market Monitoring & Intelligence Platform**  
> Track, analyze, and compare NSE-listed stocks with real-time market data, interactive Plotly charts, AI Copilot insights, and a per-user persistent portfolio tracker.

[![Live App](https://img.shields.io/badge/Live%20App-finpulse99.streamlit.app-brightgreen?style=for-the-badge&logo=streamlit)](https://finpulse99.streamlit.app)
[![GitHub Repo](https://img.shields.io/badge/GitHub-AbhinavKumarX%2Ffinpulse-blue?style=for-the-badge&logo=github)](https://github.com/AbhinavKumarX/finpulse)

![Python](https://img.shields.io/badge/Python-3.11+-blue) ![Streamlit](https://img.shields.io/badge/Streamlit-1.35+-red) ![FastAPI](https://img.shields.io/badge/FastAPI-0.111-green) ![SQLite](https://img.shields.io/badge/Database-SQLite-lightgrey)

---

## 📋 Deliverables & Assignment Checklist

- [x] **Public GitHub Repository**: [https://github.com/AbhinavKumarX/finpulse](https://github.com/AbhinavKumarX/finpulse) (clean commit history).
- [x] **Live Deployed Web Application**: [https://finpulse99.streamlit.app](https://finpulse99.streamlit.app) (100% functional, zero cost, no card required).
- [x] **Working Backend REST API**: FastAPI backend (`backend/main.py`) with Swagger UI docs (`/docs`).
- [x] **Comprehensive Project Report**: Available in repository as [`project_report.docx`](file:///Users/abhinavkumar/Downloads/sofi%20core%20alogolabs/project_report.docx) and [`project_report.md`](file:///Users/abhinavkumar/.gemini/antigravity/brain/34d55d5f-52d9-4923-b314-9131ba1e762e/project_report.md).
- [x] **Detailed Setup & Usage Documentation**: Complete instructions for local monolith run & decoupled API client.
- [x] **Disclosure of Frameworks & AI Tools**: Full breakdown of APIs, libraries, and AI pair programming tools used.

---

## 🌐 Deployed Application & Links

| Component | URL | Status |
|-----------|-----|--------|
| **Live Web App (Front End)** | [https://finpulse99.streamlit.app](https://finpulse99.streamlit.app) | 🟢 Live & Functional |
| **GitHub Repository** | [https://github.com/AbhinavKumarX/finpulse](https://github.com/AbhinavKumarX/finpulse) | 🟢 Public Repository |
| **Local API Swagger Docs** | `http://localhost:8000/docs` | 🟢 Local Backend Service |

---

## 🗂 Project Architecture

FinPulse implements a **dual-mode architecture** to support both production cloud deployment without financial constraints and standard decoupled client-server API evaluation:

```
finpulse/
├── streamlit_app.py     # Main Streamlit Dashboard (Production Monolith entrypoint)
├── requirements.txt     # Global dependencies for Streamlit Cloud
├── generate_report.py   # Script to build project_report.docx
├── project_report.docx  # One-page / Detailed Word Project Report
├── backend/
│   ├── main.py          # FastAPI REST API endpoints
│   ├── database.py      # SQLite ORM layer (Multi-user, Shared Caching)
│   ├── fetcher.py       # yFinance market data engine & multi-tier fallbacks
│   └── requirements.txt
├── frontend/
│   └── app.py           # Decoupled HTTP Streamlit client (communicates via REST API)
└── README.md
```

### Execution Modes:
1. **Production Monolith (`streamlit_app.py`)**: Imports `database.py` and `fetcher.py` directly in memory. Deployed on Streamlit Community Cloud for 100% free hosting with persistent SQLite database storage.
2. **Decoupled REST Architecture (`backend/main.py` + `frontend/app.py`)**: Streamlit frontend calls the FastAPI backend endpoints via HTTP requests (`X-User-Token` authentication header).

---

## 🔐 Multi-User System & Authentication

- **Claimable Username Identity**: Users register and sign in using unique usernames. No password management overhead.
- **Case-Sensitivity Rules**: Login handles are case-sensitive (`admin` ≠ `Admin`), while registration enforces case-insensitive uniqueness to prevent handle squatting.
- **Auto-Provisioned Watchlists**: On registration, new users automatically receive 20 pre-allocated random NIFTY 50 stocks.
- **Data Isolation**: Watchlists (`user_tickers`) and holdings (`user_portfolio`) are indexed by SHA-256 tokens (`user_id`), guaranteeing data separation across users.

---

## 📊 Core Features

1. **Live Market Dashboard**:
   - Live NSE prices, 52-week high/low range bar, key metrics (Market Cap, P/E, P/B, ROE, ROA, Div Yield, Beta).
   - Interactive Plotly Candlestick and Line charts with toggleable 10D, 40D, and 90D Moving Average overlays.
   - 14-period RSI technical indicator and live Yahoo Finance news feed.
2. **AI Copilot Heuristic Engine**:
   - Automated qualitative valuation summaries assessing company efficiency, P/E positioning, and analyst target upside.
3. **Stock Comparison Tool**:
   - 1-Year normalized performance index curves (base = 100).
   - Side-by-side metric bar charts (P/E, P/B, ROE, ROA), P/E vs ROE bubble chart, and sector donut chart.
4. **Stock Screener with CSV Export**:
   - Multi-metric filtering by P/E range, minimum ROE, max P/B, and minimum Market Cap. Includes 1-click CSV report export.
5. **Portfolio Tracker**:
   - Real-time tracking of buy price vs LTP, total investment, P&L per holding, percentage returns, and allocation pie charts.

---

## 🌐 Working Backend API Specification

FastAPI backend (`backend/main.py`) exposes 16 RESTful endpoints:

| Method | Endpoint | Auth Required | Description |
|--------|----------|---------------|-------------|
| `POST` | `/auth/register` | ❌ No | Create a new user account (returns `user_id` token) |
| `POST` | `/auth/login` | ❌ No | Authenticate user and receive session token |
| `GET`  | `/auth/me` | ✅ Yes | Retrieve current user profile info |
| `GET`  | `/stocks` | ✅ Yes | Get user's watchlist with fundamental data |
| `POST` | `/stocks/{ticker}` | ✅ Yes | Add a stock to user's watchlist |
| `DELETE`| `/stocks/{ticker}`| ✅ Yes | Remove a stock from user's watchlist |
| `POST` | `/stocks/{ticker}/refresh` | ✅ Yes | Force re-fetch fundamental cache |
| `GET`  | `/stocks/{ticker}/history` | ❌ No | Fetch historical price series (1W to 5Y) |
| `GET`  | `/stocks/{ticker}/news` | ❌ No | Fetch latest news articles for a stock |
| `GET`  | `/market-indices` | ❌ No | Live index ribbon data (NIFTY 50, SENSEX, etc.) |
| `GET`  | `/market-summary` | ✅ Yes | User-scoped market sentiment summary |
| `GET`  | `/portfolio` | ✅ Yes | Retrieve user's portfolio holdings |
| `POST` | `/portfolio` | ✅ Yes | Add or update a portfolio holding |
| `DELETE`| `/portfolio/{ticker}`| ✅ Yes | Remove a portfolio holding |
| `GET`  | `/export-report` | ✅ Yes | Export user watchlist metrics as CSV |
| `GET`  | `/search?q=` | ❌ No | Search NSE stocks via Yahoo Finance API |

*Authentication Header*: `X-User-Token: <user_id_hash>`

---

## 🗄 Database Design & Caching Strategy

SQLite3 schema (`backend/database.py`):

```sql
-- User Tables
users            (user_id TEXT PRIMARY KEY, username TEXT UNIQUE, created_at TIMESTAMP)
user_tickers     (user_id TEXT, ticker TEXT, added_at TIMESTAMP, PRIMARY KEY(user_id, ticker))
user_portfolio   (user_id TEXT, ticker TEXT, shares REAL, buy_price REAL, PRIMARY KEY(user_id, ticker))

-- Shared Global Caches (Avoid duplicate external API queries across users)
fundamental_data (ticker TEXT PRIMARY KEY, name, sector, market_cap, pe_ratio, current_price, roe, ...)
historical_prices(ticker TEXT, date TEXT, open, high, low, close, volume, PRIMARY KEY(ticker, date))
```

*Query Optimization*: Watchlist retrieval uses a `LEFT JOIN` (`user_tickers LEFT JOIN fundamental_data`) with `COALESCE` fallbacks, guaranteeing 100% of user stocks render immediately even if external cache update is pending.

---

## 🚀 Local Setup & Execution Instructions

### Prerequisites
- Python 3.11+ installed.

### Option A: Run Monolith Streamlit App (Recommended)
```bash
git clone https://github.com/AbhinavKumarX/finpulse.git
cd finpulse
pip install -r requirements.txt
streamlit run streamlit_app.py
```
App will open automatically at `http://localhost:8501`.

### Option B: Run Decoupled FastAPI Backend + Streamlit Client
```bash
# Terminal 1: Launch FastAPI Backend
cd backend
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# Terminal 2: Launch Streamlit Frontend Client
cd frontend
pip install -r requirements.txt
streamlit run app.py
```
- Backend API Docs: `http://localhost:8000/docs`
- Frontend Client: `http://localhost:8501`

---

## 🛠 Frameworks, External APIs, Libraries & AI Tools Used

### Frameworks & Libraries
- **Streamlit**: Core frontend web framework for reactive data presentation.
- **FastAPI & Uvicorn**: High-performance RESTful API backend framework.
- **yFinance**: Python wrapper for fetching market data and time series from Yahoo Finance.
- **Plotly Express & Graph Objects**: Interactive financial charts (Candlestick, Line, Moving Averages, RSI, Bubble, Treemap, Donut).
- **Pandas & NumPy**: Financial metric calculations, time series manipulation, and data transformation.
- **SQLite3 & hashlib**: Database engine and SHA-256 identity hashing.
- **python-docx**: Automated generation of `project_report.docx`.

### External APIs
- **Yahoo Finance REST API (`query2.finance.yahoo.com`)**: Real-time ticker search & autocomplete.
- **yFinance Data Engine**: Fundamental metrics & historical price series for NSE/BSE.

### AI Tools & Assistance
- **Google Antigravity AI (Gemini 3.6 Flash)**: Used as an AI pair programmer throughout development for architectural design, code generation, database schema optimization, multi-user authentication logic, and automated report document creation.

---

## 💡 Key Challenges Faced & Technical Solutions

1. **Cloud Deployment Without Credit Cards**:
   - *Challenge*: Platform services like Render require credit card verification for free web services, while container hosts erase local SQLite databases on restart.
   - *Solution*: Developed a Production Monolith in `streamlit_app.py` that imports backend modules directly into Streamlit Community Cloud (100% free, cardless), preserving `backend/main.py` for standalone API evaluation.
2. **Yahoo Finance Rate Limiting & Partial Data**:
   - *Challenge*: Cloud IP addresses frequently experience yFinance rate limits or empty info dictionaries, causing `0.00` price displays.
   - *Solution*: Built a 3-tier fallback engine in `fetcher.py` (`info` -> `fast_info` -> `5d history` calculations) and SQL `CASE WHEN` logic in `database.py` to preserve valid non-zero values.
3. **Streamlit Widget State Restrictions**:
   - *Challenge*: Mutating `st.session_state` for a widget key after instantiation threw `StreamlitAPIException`.
   - *Solution*: Implemented a dynamic key counter pattern (`_s_key = f"search_{search_counter}"`). Incrementing the counter safely re-instantiates the search input widget without state conflicts.

---

## ⚠️ Disclaimer

FinPulse is a student project created for the **Society of Finance and Investing (SoFI) AlgoLabs Assignment 1**. Market metrics are retrieved from Yahoo Finance via `yfinance` and may be delayed. **Not financial advice.**
