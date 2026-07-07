import yfinance as yf
import pandas as pd
from typing import Dict, Any, List

def fetch_fundamental_data(ticker: str) -> Dict[str, Any]:
    stock = yf.Ticker(ticker)
    info = stock.info
    
    # Normalize dividend yield (Indian stock yield is often returned as percentage e.g. 0.46 for 0.46%)
    div_y = info.get("dividendYield") or info.get("trailingAnnualDividendYield") or 0
    if div_y > 0.15:
        div_y = div_y / 100
        
    return {
        "name": info.get("shortName") or info.get("longName") or ticker,
        "sector": info.get("sector") or "Unknown",
        "market_cap": info.get("marketCap") or info.get("enterpriseValue") or 0,
        "pe_ratio": info.get("trailingPE") or info.get("forwardPE") or 0,
        "eps": info.get("trailingEps") or info.get("forwardEps") or 0,
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice") or 0,
        "pb_ratio": info.get("priceToBook") or 0,
        "roe": info.get("returnOnEquity") or 0,      # Return on Equity
        "roce": info.get("returnOnAssets") or info.get("operatingAssets") or 0,     # Return on Assets
        "high_52w": info.get("fiftyTwoWeekHigh") or 0,
        "low_52w": info.get("fiftyTwoWeekLow") or 0,
        "dividend_yield": div_y,
        "beta": info.get("beta") or 0,
        "target_price": info.get("targetMeanPrice") or info.get("targetLowPrice") or 0,
        "recommendation": info.get("recommendationKey") or "N/A",
        "day_change_pct": info.get("regularMarketChangePercent") or 0,
        "volume": info.get("regularMarketVolume") or info.get("volume") or 0,
        "avg_volume": info.get("averageVolume") or info.get("averageVolume10days") or 0,
        "currency": info.get("financialCurrency") or info.get("currency") or "INR",
    }


def fetch_historical_prices(ticker: str, period: str = "5y") -> List[Dict[str, Any]]:
    stock = yf.Ticker(ticker)
    hist = stock.history(period=period)

    if hist.empty:
        return []

    hist.reset_index(inplace=True)
    # yfinance can return timezone-aware datetimes, ensure we strip it for SQLite
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
    # Prioritize NSE for this Indian stock app
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
                    # Filter: only real equity/ETF, skip futures, warrants, rights
                    if q.get('quoteType') not in ['EQUITY', 'ETF']:
                        continue
                    sym = q.get('symbol', '')
                    if not sym or sym in seen:
                        continue
                    # Skip tickers with suffixes like -RI, -RT (rights/warrants)
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

def fetch_indices() -> List[Dict[str, Any]]:
    indices = {
        "^NSEI": "NIFTY 50",
        "^BSESN": "SENSEX",
        "^NSEBANK": "NIFTY BANK",
        "BTC-INR": "Bitcoin (INR)"
    }
    results = []
    for ticker, display_name in indices.items():
        try:
            stock = yf.Ticker(ticker)
            info = stock.info
            price = info.get("currentPrice") or info.get("regularMarketPrice") or 0
            change = info.get("regularMarketChange") or 0
            change_pct = info.get("regularMarketChangePercent") or 0
            # If regularMarketChangePercent is in decimal (e.g. 0.0065), or percent (0.65)
            # yfinance returns it as percent (e.g. 0.6571), but sometimes decimal.
            # Usually regularMarketChangePercent is percent, e.g. 0.6571 means 0.65%.
            results.append({
                "symbol": ticker,
                "name": display_name,
                "price": price,
                "change": change,
                "change_pct": change_pct
            })
        except Exception:
            pass
    return results

def fetch_stock_news(ticker: str) -> List[Dict[str, Any]]:
    try:
        stock = yf.Ticker(ticker)
        raw_news = stock.news or []
        parsed = []
        for item in raw_news:
            # yfinance news can have a "content" field in newer versions
            content = item.get("content", item)
            title = content.get("title")
            pub_date = content.get("pubDate") or content.get("providerPublishTime")
            link = content.get("canonicalUrl", {}).get("url") or content.get("clickThroughUrl", {}).get("url") or content.get("link")
            provider = content.get("provider", {}).get("displayName") or content.get("publisher") or "Yahoo Finance"
            
            if title and link:
                parsed.append({
                    "title": title,
                    "publisher": provider,
                    "link": link,
                    "date": pub_date
                })
        return parsed[:6]
    except Exception:
        return []

