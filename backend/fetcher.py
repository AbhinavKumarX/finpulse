import yfinance as yf
import pandas as pd
from typing import Dict, Any, List

def fetch_fundamental_data(ticker: str) -> Dict[str, Any]:
    stock = yf.Ticker(ticker)
    info = {}
    try:
        info = stock.info or {}
    except Exception:
        info = {}

    fast_info = {}
    try:
        fast_info = getattr(stock, "fast_info", {}) or {}
    except Exception:
        fast_info = {}

    # 5-day history fallback for price, change, volume
    hist_price = 0.0
    day_chg_pct = 0.0
    vol = 0
    try:
        h5 = stock.history(period="5d")
        if not h5.empty:
            hist_price = float(h5["Close"].iloc[-1])
            if len(h5) >= 2:
                prev_c = float(h5["Close"].iloc[-2])
                if prev_c > 0:
                    day_chg_pct = (hist_price - prev_c) / prev_c * 100
            vol = int(h5["Volume"].iloc[-1])
    except Exception:
        pass

    # Extract price with multiple fallbacks
    cp = (
        info.get("currentPrice")
        or info.get("regularMarketPrice")
        or info.get("previousClose")
        or info.get("open")
        or (fast_info.get("last_price") if hasattr(fast_info, "get") else None)
        or (fast_info.last_price if hasattr(fast_info, "last_price") else None)
        or hist_price
        or 0
    )

    mcap = (
        info.get("marketCap")
        or info.get("enterpriseValue")
        or (fast_info.get("market_cap") if hasattr(fast_info, "get") else None)
        or (fast_info.market_cap if hasattr(fast_info, "market_cap") else None)
        or 0
    )

    hi52 = (
        info.get("fiftyTwoWeekHigh")
        or (fast_info.get("year_high") if hasattr(fast_info, "get") else None)
        or (fast_info.year_high if hasattr(fast_info, "year_high") else None)
        or 0
    )

    lo52 = (
        info.get("fiftyTwoWeekLow")
        or (fast_info.get("year_low") if hasattr(fast_info, "get") else None)
        or (fast_info.year_low if hasattr(fast_info, "year_low") else None)
        or 0
    )

    chg_pct = info.get("regularMarketChangePercent") or day_chg_pct or 0

    div_y = info.get("dividendYield") or info.get("trailingAnnualDividendYield") or 0
    if div_y > 0.15:
        div_y = div_y / 100

    return {
        "name": info.get("shortName") or info.get("longName") or ticker,
        "sector": info.get("sector") or "Equity",
        "market_cap": mcap,
        "pe_ratio": info.get("trailingPE") or info.get("forwardPE") or 0,
        "eps": info.get("trailingEps") or info.get("forwardEps") or 0,
        "current_price": cp,
        "pb_ratio": info.get("priceToBook") or 0,
        "roe": info.get("returnOnEquity") or 0,
        "roce": info.get("returnOnAssets") or info.get("operatingAssets") or 0,
        "high_52w": hi52,
        "low_52w": lo52,
        "dividend_yield": div_y,
        "beta": info.get("beta") or 0,
        "target_price": info.get("targetMeanPrice") or info.get("targetLowPrice") or 0,
        "recommendation": info.get("recommendationKey") or "N/A",
        "day_change_pct": chg_pct,
        "volume": info.get("regularMarketVolume") or info.get("volume") or vol or 0,
        "avg_volume": info.get("averageVolume") or info.get("averageVolume10days") or 0,
        "currency": info.get("financialCurrency") or info.get("currency") or "INR",
    }

def fetch_historical_prices(ticker: str, period: str = "5y") -> List[Dict[str, Any]]:
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)

    if hist.empty:
        return []

    hist.reset_index(inplace=True)
    if hist['Date'].dt.tz is not None:
        hist['Date'] = hist['Date'].dt.tz_localize(None)
    hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')

    records = []
    for _, row in hist.iterrows():
        records.append({
            "date": row['Date'],
            "open": float(row.get('Open', 0) or 0),
            "high": float(row.get('High', 0) or 0),
            "low": float(row.get('Low', 0) or 0),
            "close": float(row.get('Close', 0) or 0),
            "volume": int(row.get('Volume', 0) or 0)
        })
    return records

def search_ticker(query: str) -> List[Dict[str, str]]:
    import requests
    queries = [query]
    if not query.upper().endswith('.NS') and not query.upper().endswith('.BO'):
        queries.insert(0, query + ".NS")

    results = []
    seen = set()
    headers = {'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36'}

    for q_str in queries:
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={q_str}&lang=en-US&region=IN"
        try:
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                quotes = data.get('quotes', [])
                for q in quotes:
                    if q.get('quoteType') not in ['EQUITY', 'ETF']:
                        continue
                    sym = q.get('symbol', '')
                    if not sym or sym in seen:
                        continue
                    if any(sym.endswith(s) for s in ['-RI', '-RT', '-WI', 'F']):
                        continue
                    seen.add(sym)
                    results.append({
                        'symbol': sym,
                        'shortname': q.get('shortname') or q.get('longname') or sym,
                        'exchDisp': q.get('exchDisp') or q.get('exchange') or '',
                    })
        except Exception:
            pass

    return results[:5]
