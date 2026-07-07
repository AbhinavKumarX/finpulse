from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Optional
import database
import fetcher
import csv
from io import StringIO
from fastapi.responses import PlainTextResponse

app = FastAPI(title="FinPulse API")

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

class TickerInput(BaseModel):
    ticker: str

@app.get("/stocks")
def get_all_stocks():
    return {"stocks": database.get_fundamental_data()}

@app.get("/search")
def search_stock(q: str):
    return {"results": fetcher.search_ticker(q)}

@app.post("/stocks/{ticker}")
def add_stock(ticker: str, background_tasks: BackgroundTasks):
    ticker = ticker.upper()
    try:
        fund_data = fetcher.fetch_fundamental_data(ticker)
        if not fund_data or (not fund_data.get('current_price') and not fund_data.get('name')):
            raise HTTPException(status_code=400, detail="Invalid ticker or data not available.")
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch data for {ticker}: {str(e)}")

    database.add_ticker(ticker)
    database.upsert_fundamental_data(ticker, fund_data)

    def fetch_history(t):
        hist_data = fetcher.fetch_historical_prices(t)
        database.upsert_historical_prices(t, hist_data)

    background_tasks.add_task(fetch_history, ticker)
    return {"message": f"Successfully added {ticker}. Historical data is fetching in the background."}

@app.post("/stocks/{ticker}/refresh")
def refresh_stock(ticker: str):
    """Force re-fetch fundamentals for a stock."""
    ticker = ticker.upper()
    data = database.get_fundamental_data(ticker)
    if not data:
        raise HTTPException(status_code=404, detail="Stock not tracked. Add it first.")
    try:
        fund_data = fetcher.fetch_fundamental_data(ticker)
        database.upsert_fundamental_data(ticker, fund_data)
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Refresh failed: {str(e)}")
    return {"message": f"Successfully refreshed {ticker}."}

@app.delete("/stocks/{ticker}")
def remove_stock(ticker: str):
    ticker = ticker.upper()
    database.remove_ticker(ticker)
    return {"message": f"Successfully removed {ticker}."}

@app.get("/stocks/{ticker}")
def get_stock(ticker: str):
    ticker = ticker.upper()
    data = database.get_fundamental_data(ticker)
    if not data:
        raise HTTPException(status_code=404, detail="Stock not found in tracked list.")
    return data

@app.get("/stocks/{ticker}/history")
def get_stock_history(ticker: str):
    ticker = ticker.upper()
    history = database.get_historical_prices(ticker)
    if not history:
        raise HTTPException(status_code=404, detail="No historical data found.")
    return {"history": history}

@app.get("/market-indices")
def get_market_indices():
    try:
        return {"indices": fetcher.fetch_indices()}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/stocks/{ticker}/news")
def get_stock_news(ticker: str):
    ticker = ticker.upper()
    try:
        return {"news": fetcher.fetch_stock_news(ticker)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/market-summary")
def get_market_summary():
    data = database.get_fundamental_data()
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
def export_report():
    data = database.get_fundamental_data()
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
