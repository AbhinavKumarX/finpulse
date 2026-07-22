from fastapi import FastAPI, HTTPException, BackgroundTasks, Header, Depends
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import csv
from io import StringIO
from fastapi.responses import PlainTextResponse

import database
import fetcher

app = FastAPI(title="FinPulse API", version="2.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.on_event("startup")
def on_startup():
    database.init_db()


# ─────────────────────────────────────────────────────────────────────────────
# Auth Dependency
# ─────────────────────────────────────────────────────────────────────────────

def get_current_user(x_user_token: Optional[str] = Header(default=None)):
    if not x_user_token:
        raise HTTPException(status_code=401, detail="Missing X-User-Token header.")
    user = database.get_user_by_token(x_user_token)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid or expired session. Please log in again.")
    return user


# ─────────────────────────────────────────────────────────────────────────────
# Auth Endpoints
# ─────────────────────────────────────────────────────────────────────────────

class RegisterInput(BaseModel):
    username: str

class LoginInput(BaseModel):
    username: str


@app.post("/auth/register")
def register(body: RegisterInput):
    """Create a new account. Username must be unique (case-insensitive)."""
    username = body.username.strip()
    if not username or len(username) < 2:
        raise HTTPException(status_code=400, detail="Username must be at least 2 characters.")
    if len(username) > 30:
        raise HTTPException(status_code=400, detail="Username must be 30 characters or less.")
    try:
        result = database.create_user(username)
        # Kick off background fetch for the pre-allocated stocks
        return {
            "token": result["user_id"],
            "username": result["username"],
            "is_new": True,
            "message": f"Welcome, {result['username']}! Your account has been created with 20 pre-loaded stocks."
        }
    except ValueError as e:
        raise HTTPException(status_code=409, detail=str(e))


@app.post("/auth/login")
def login(body: LoginInput):
    """Login with exact username (case-sensitive)."""
    username = body.username.strip()
    try:
        result = database.login_user(username)
        return {
            "token": result["user_id"],
            "username": result["username"],
            "is_new": False,
            "message": f"Welcome back, {result['username']}!"
        }
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/auth/me")
def get_me(user=Depends(get_current_user)):
    return {"username": user["username"], "user_id": user["user_id"]}


# ─────────────────────────────────────────────────────────────────────────────
# Stock / Watchlist Endpoints (User-scoped)
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/stocks")
def get_all_stocks(user=Depends(get_current_user)):
    """Return fundamental data for all stocks in the user's watchlist."""
    return {"stocks": database.get_fundamental_data_for_user(user["user_id"])}


@app.post("/stocks/{ticker}")
def add_stock(ticker: str, background_tasks: BackgroundTasks, user=Depends(get_current_user)):
    ticker = ticker.upper()
    # Validate ticker
    try:
        fund_data = fetcher.fetch_fundamental_data(ticker)
        if not fund_data or (not fund_data.get('current_price') and not fund_data.get('name')):
            raise HTTPException(status_code=400, detail="Invalid ticker or data not available.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch data for {ticker}: {str(e)}")

    database.add_user_ticker(user["user_id"], ticker)
    database.upsert_fundamental_data(ticker, fund_data)

    def fetch_history(t):
        hist_data = fetcher.fetch_historical_prices(t)
        database.upsert_historical_prices(t, hist_data)

    background_tasks.add_task(fetch_history, ticker)
    return {"message": f"Successfully added {ticker} to your watchlist."}


@app.delete("/stocks/{ticker}")
def remove_stock(ticker: str, user=Depends(get_current_user)):
    ticker = ticker.upper()
    database.remove_user_ticker(user["user_id"], ticker)
    return {"message": f"Successfully removed {ticker} from your watchlist."}


@app.get("/stocks/{ticker}")
def get_stock(ticker: str):
    """Global stock details — no auth required."""
    ticker = ticker.upper()
    data = database.get_fundamental_data(ticker)
    if not data:
        raise HTTPException(status_code=404, detail="Stock not found in cache.")
    return data


@app.post("/stocks/{ticker}/refresh")
def refresh_stock(ticker: str, user=Depends(get_current_user)):
    ticker = ticker.upper()
    tickers = database.get_user_tickers(user["user_id"])
    if ticker not in tickers:
        raise HTTPException(status_code=404, detail="Stock not in your watchlist.")
    try:
        fund_data = fetcher.fetch_fundamental_data(ticker)
        database.upsert_fundamental_data(ticker, fund_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")
    return {"message": f"Successfully refreshed {ticker}."}


@app.get("/stocks/{ticker}/history")
def get_stock_history(ticker: str):
    """Historical prices — global cache, no auth required."""
    ticker = ticker.upper()
    history = database.get_historical_prices(ticker)
    if not history:
        raise HTTPException(status_code=404, detail="No historical data found.")
    return {"history": history}


@app.get("/stocks/{ticker}/news")
def get_stock_news(ticker: str):
    ticker = ticker.upper()
    try:
        return {"news": fetcher.fetch_stock_news(ticker)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


# ─────────────────────────────────────────────────────────────────────────────
# Portfolio Endpoints (User-scoped, DB-backed)
# ─────────────────────────────────────────────────────────────────────────────

class PortfolioHolding(BaseModel):
    ticker: str
    shares: float
    buy_price: float


@app.get("/portfolio")
def get_portfolio(user=Depends(get_current_user)):
    return {"portfolio": database.get_portfolio(user["user_id"])}


@app.post("/portfolio")
def upsert_holding(holding: PortfolioHolding, user=Depends(get_current_user)):
    database.upsert_portfolio_holding(
        user["user_id"], holding.ticker.upper(), holding.shares, holding.buy_price
    )
    return {"message": "Holding saved."}


@app.delete("/portfolio/{ticker}")
def delete_holding(ticker: str, user=Depends(get_current_user)):
    database.delete_portfolio_holding(user["user_id"], ticker.upper())
    return {"message": f"Removed {ticker} from portfolio."}


# ─────────────────────────────────────────────────────────────────────────────
# Public / Global Endpoints
# ─────────────────────────────────────────────────────────────────────────────

@app.get("/search")
def search_stock(q: str):
    return {"results": fetcher.search_ticker(q)}


@app.get("/market-indices")
def get_market_indices():
    try:
        return {"indices": fetcher.fetch_indices()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/market-summary")
def get_market_summary(user=Depends(get_current_user)):
    data = database.get_fundamental_data_for_user(user["user_id"])
    if not data:
        return {"summary": "No stocks tracked."}
    total_market_cap = sum(d.get('market_cap', 0) or 0 for d in data)
    avg_pe = sum(d.get('pe_ratio', 0) or 0 for d in data) / len(data) if data else 0
    return {
        "tracked_companies": len(data),
        "total_market_cap": total_market_cap,
        "average_pe_ratio": avg_pe,
        "top_by_market_cap": sorted(data, key=lambda x: x.get('market_cap', 0) or 0, reverse=True)[:5]
    }


@app.get("/export-report")
def export_report(user=Depends(get_current_user)):
    data = database.get_fundamental_data_for_user(user["user_id"])
    if not data:
        raise HTTPException(status_code=404, detail="No data to export.")
    output = StringIO()
    fieldnames = ["ticker", "name", "sector", "market_cap", "pe_ratio", "pb_ratio",
                  "eps", "current_price", "roe", "roce", "high_52w", "low_52w",
                  "dividend_yield", "beta", "target_price", "recommendation"]
    writer = csv.DictWriter(output, fieldnames=fieldnames, extrasaction='ignore')
    writer.writeheader()
    for row in data:
        writer.writerow(row)
    return PlainTextResponse(
        content=output.getvalue(),
        media_type="text/csv",
        headers={"Content-Disposition": "attachment; filename=finpulse_report.csv"}
    )


# ─────────────────────────────────────────────────────────────────────────────
# Background seeding — fetch data for pre-allocated stocks
# ─────────────────────────────────────────────────────────────────────────────

@app.post("/auth/seed/{user_id}")
def seed_user_stocks(user_id: str, background_tasks: BackgroundTasks):
    """Internal endpoint: triggers background fetch for a user's pre-allocated stocks."""
    tickers = database.get_user_tickers(user_id)

    def _seed(ticker_list):
        for t in ticker_list:
            try:
                fd = fetcher.fetch_fundamental_data(t)
                database.upsert_fundamental_data(t, fd)
                hd = fetcher.fetch_historical_prices(t)
                database.upsert_historical_prices(t, hd)
            except Exception:
                pass

    background_tasks.add_task(_seed, tickers)
    return {"message": f"Seeding {len(tickers)} stocks in background."}
