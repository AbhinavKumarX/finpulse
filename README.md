# FinPulse – Indian Markets Intelligence Dashboard

A Perplexity Finance-style stock research dashboard for Indian markets, built with **FastAPI** (backend) and **Streamlit** (frontend).

## Features
- 🔍 Live stock search (NSE/BSE) with add-to-watchlist
- 📊 Interactive candlestick & line charts with MA overlays (10D, 40D, 90D)
- 📈 Market index ribbon (NIFTY 50, SENSEX, NIFTY BANK, BTC-INR)
- 🤖 AI Copilot fundamental analysis card
- 📰 Live news feed per stock
- ⚖️ Multi-stock comparison with normalised performance chart
- 🔍 Screener with P/E, P/B, ROE, Market Cap filters
- 💼 Portfolio tracker with P&L and allocation donut
- 🌡️ Watchlist heatmap (treemap by market cap & % change)
- 🌙 Dark / Light mode toggle

## Quick Start (Local)

```bash
# 1. Backend
cd backend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000

# 2. Frontend (new terminal)
cd frontend
python -m venv venv && source venv/bin/activate
pip install -r requirements.txt
streamlit run app.py --server.port 8501
```

Open http://localhost:8501 — password: `admin`

## Deployment (Render / Railway / Fly.io)

See the `render.yaml` in the repo root. Both backend and frontend are configured.

## Project Structure

```
.
├── backend/
│   ├── main.py          # FastAPI application
│   ├── database.py      # SQLite helpers
│   ├── fetcher.py       # yfinance wrappers
│   └── requirements.txt
├── frontend/
│   ├── app.py           # Streamlit dashboard
│   └── requirements.txt
├── render.yaml          # Render.com deployment config
├── .gitignore
└── README.md
```

## Environment Variables

| Variable | Default | Description |
|----------|---------|-------------|
| `API_URL` | `http://localhost:8000` | Backend URL (set in frontend for deployed envs) |

## Tech Stack
- **Backend**: FastAPI, yfinance, SQLite, Uvicorn
- **Frontend**: Streamlit, Plotly, st-keyup, pandas
