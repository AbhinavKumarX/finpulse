import os, sqlite3, json
import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.graph_objects as plgo
import plotly.express as px
from plotly.subplots import make_subplots
import yfinance as yf
import requests as _req

st.set_page_config(
    page_title="FinPulse – Indian Markets",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─── Theme ────────────────────────────────────────────────────────────────────
if 'theme' not in st.session_state:
    st.session_state['theme'] = 'dark'

def toggle_theme():
    st.session_state['theme'] = 'light' if st.session_state['theme'] == 'dark' else 'dark'

themes = {
    'dark': {
        'bg': '#090d16', 'card_bg': '#111827', 'border': '#1c2333',
        'text_main': '#f1f5f9', 'text_sub': '#9ca3af', 'text_muted': '#4b5563',
        'primary': '#3b82f6', 'hover_bg': '#0f172a', 'green': '#22c55e', 'red': '#ef4444'
    },
    'light': {
        'bg': '#f8fafc', 'card_bg': '#ffffff', 'border': '#e2e8f0',
        'text_main': '#0f172a', 'text_sub': '#475569', 'text_muted': '#94a3b8',
        'primary': '#2563eb', 'hover_bg': '#f1f5f9', 'green': '#16a34a', 'red': '#dc2626'
    }
}
t = themes[st.session_state['theme']]
BG = t['bg']

st.markdown(f'''
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*, *::before, *::after {{ font-family: 'Inter', sans-serif !important; box-sizing: border-box; }}
.stApp {{ background: {t["bg"]} !important; }}
[data-testid="stAppViewContainer"] {{ background: {t["bg"]} !important; }}
[data-testid="stAppViewContainer"] > section > div {{ background: {t["bg"]} !important; }}
.main .block-container {{ padding: 1rem 2rem 2rem !important; max-width: 100% !important; }}
[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
#MainMenu, footer, header, [data-testid="stToolbar"], [data-testid="stDecoration"] {{ display: none !important; }}
[data-testid="stMetric"] {{
    background: {t["card_bg"]} !important; border: 1px solid {t["border"]} !important;
    border-radius: 12px !important; padding: 16px 18px 14px !important; transition: border-color .2s !important;
}}
[data-testid="stMetric"]:hover {{ border-color: {t["primary"]} !important; }}
[data-testid="stMetricLabel"] > div {{
    font-size: 10px !important; font-weight: 700 !important;
    letter-spacing: .08em !important; text-transform: uppercase !important; color: {t["text_muted"]} !important;
}}
[data-testid="stMetricValue"] > div {{ font-size: 19px !important; font-weight: 800 !important; color: {t["text_main"]} !important; }}
[data-testid="stTabs"] [role="tablist"] {{
    border-bottom: 1px solid {t["border"]} !important; gap: 0 !important;
    background: transparent !important; margin-bottom: 15px !important;
}}
[data-testid="stTabs"] button[role="tab"] {{
    background: transparent !important; color: {t["text_sub"]} !important;
    border: none !important; border-bottom: 2px solid transparent !important;
    border-radius: 0 !important; font-size: 13px !important; font-weight: 600 !important; padding: 8px 20px !important;
}}
[data-testid="stTabs"] button[aria-selected="true"] {{ color: {t["primary"]} !important; border-bottom-color: {t["primary"]} !important; }}
[data-testid="stTabs"] button:hover {{ color: {t["text_main"]} !important; }}
.stButton > button {{
    background: {t["card_bg"]} !important; color: {t["text_main"]} !important;
    border: 1px solid {t["border"]} !important; border-radius: 8px !important;
    font-size: 11px !important; font-weight: 600 !important; padding: 4px 10px !important; width: 100% !important;
}}
.stButton > button:hover {{ border-color: {t["primary"]} !important; }}
.stTextInput > label {{ display: none !important; }}
.stTextInput > div > div {{
    background: {t["card_bg"]} !important; border: 1px solid {t["border"]} !important; border-radius: 9px !important;
}}
.stTextInput input {{ color: {t["text_main"]} !important; font-size: 13px !important; }}
.stTextInput input::placeholder {{ color: {t["text_muted"]} !important; }}
[data-testid="stRadio"] > label {{ display: none !important; }}
[data-testid="stRadio"] > div {{ gap: 4px !important; }}
[data-testid="stRadio"] > div > label {{
    background: {t["card_bg"]} !important; border: 1px solid {t["border"]} !important;
    border-radius: 8px !important; padding: 4px 12px !important;
    font-size: 11px !important; font-weight: 600 !important; color: {t["text_muted"]} !important; cursor: pointer !important;
}}
[data-testid="stRadio"] > div > label:has(input:checked) {{
    border-color: {t["primary"]} !important; color: {t["primary"]} !important; background: {t["bg"]} !important;
}}
[data-testid="stCheckbox"] label {{ font-size: 11px !important; color: {t["text_muted"]} !important; }}
[data-testid="stSelectbox"] > div > div {{
    background: {t["card_bg"]} !important; border: 1px solid {t["border"]} !important;
    border-radius: 9px !important; color: {t["text_main"]} !important;
}}
[data-testid="stNumberInput"] > div > div {{
    background: {t["card_bg"]} !important; border-color: {t["border"]} !important; border-radius: 9px !important;
}}
[data-testid="stNumberInput"] input {{ color: {t["text_main"]} !important; }}
hr {{ border-color: {t["border"]} !important; margin: 10px 0 !important; }}
[data-testid="stAlert"] {{
    background: {t["card_bg"]} !important; border-color: {t["border"]} !important; border-radius: 10px !important;
}}
::-webkit-scrollbar {{ width: 5px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {t["border"]}; border-radius: 4px; }}
</style>
''', unsafe_allow_html=True)


# ─── SQLite DB (local persistence) ───────────────────────────────────────────
DB_PATH = os.path.join(os.path.dirname(__file__), "finpulse.db")

def _conn():
    c = sqlite3.connect(DB_PATH, check_same_thread=False)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    with _conn() as c:
        c.execute("""CREATE TABLE IF NOT EXISTS tickers (
            ticker TEXT PRIMARY KEY, added_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS fundamentals (
            ticker TEXT PRIMARY KEY, data JSON, updated_at DATETIME DEFAULT CURRENT_TIMESTAMP)""")
        c.execute("""CREATE TABLE IF NOT EXISTS history (
            ticker TEXT, date TEXT, open REAL, high REAL, low REAL, close REAL, volume INTEGER,
            PRIMARY KEY (ticker, date))""")

init_db()

def db_get_tickers():
    with _conn() as c:
        return [r['ticker'] for r in c.execute("SELECT ticker FROM tickers ORDER BY added_at").fetchall()]

def db_add_ticker(ticker):
    with _conn() as c:
        c.execute("INSERT OR IGNORE INTO tickers (ticker) VALUES (?)", (ticker,))

def db_remove_ticker(ticker):
    with _conn() as c:
        c.execute("DELETE FROM tickers WHERE ticker=?", (ticker,))
        c.execute("DELETE FROM fundamentals WHERE ticker=?", (ticker,))
        c.execute("DELETE FROM history WHERE ticker=?", (ticker,))

def db_upsert_fundamentals(ticker, data):
    with _conn() as c:
        c.execute("""INSERT INTO fundamentals (ticker, data, updated_at)
                     VALUES (?,?, CURRENT_TIMESTAMP)
                     ON CONFLICT(ticker) DO UPDATE SET data=excluded.data, updated_at=CURRENT_TIMESTAMP""",
                  (ticker, json.dumps(data)))

def db_get_fundamentals(ticker=None):
    with _conn() as c:
        if ticker:
            row = c.execute("SELECT data FROM fundamentals WHERE ticker=?", (ticker,)).fetchone()
            return json.loads(row['data']) if row else None
        rows = c.execute("SELECT data FROM fundamentals").fetchall()
        return [json.loads(r['data']) for r in rows]

def db_upsert_history(ticker, records):
    with _conn() as c:
        c.executemany("""INSERT OR REPLACE INTO history (ticker,date,open,high,low,close,volume)
                         VALUES (:ticker,:date,:open,:high,:low,:close,:volume)""",
                      [{**r, 'ticker': ticker} for r in records])

def db_get_history(ticker):
    with _conn() as c:
        rows = c.execute("SELECT date,open,high,low,close,volume FROM history WHERE ticker=? ORDER BY date",
                         (ticker,)).fetchall()
        return [dict(r) for r in rows]


# ─── yfinance helpers ─────────────────────────────────────────────────────────
def _fetch_fundamentals(ticker):
    info = yf.Ticker(ticker).info
    div_y = info.get("dividendYield") or info.get("trailingAnnualDividendYield") or 0
    if div_y > 0.15:
        div_y /= 100
    return {
        "ticker": ticker,
        "name": info.get("shortName") or info.get("longName") or ticker,
        "sector": info.get("sector") or "Unknown",
        "market_cap": info.get("marketCap") or 0,
        "pe_ratio": info.get("trailingPE") or info.get("forwardPE") or 0,
        "eps": info.get("trailingEps") or 0,
        "current_price": info.get("currentPrice") or info.get("regularMarketPrice") or 0,
        "pb_ratio": info.get("priceToBook") or 0,
        "roe": info.get("returnOnEquity") or 0,
        "roce": info.get("returnOnAssets") or 0,
        "high_52w": info.get("fiftyTwoWeekHigh") or 0,
        "low_52w": info.get("fiftyTwoWeekLow") or 0,
        "dividend_yield": div_y,
        "beta": info.get("beta") or 0,
        "target_price": info.get("targetMeanPrice") or 0,
        "recommendation": info.get("recommendationKey") or "N/A",
        "day_change_pct": info.get("regularMarketChangePercent") or 0,
        "volume": info.get("regularMarketVolume") or 0,
        "avg_volume": info.get("averageVolume") or 0,
        "currency": info.get("financialCurrency") or info.get("currency") or "INR",
    }

def _fetch_history(ticker):
    hist = yf.Ticker(ticker).history(period="5y")
    if hist.empty: return []
    hist.reset_index(inplace=True)
    if hist['Date'].dt.tz is not None:
        hist['Date'] = hist['Date'].dt.tz_localize(None)
    hist['Date'] = hist['Date'].dt.strftime('%Y-%m-%d')
    return [{"date": r['Date'], "open": float(r.get('Open',0) or 0),
             "high": float(r.get('High',0) or 0), "low": float(r.get('Low',0) or 0),
             "close": float(r.get('Close',0) or 0), "volume": int(r.get('Volume',0) or 0)}
            for _, r in hist.iterrows()]

def _fetch_indices():
    INDICES = {"^NSEI":"NIFTY 50","^BSESN":"SENSEX","^NSEBANK":"NIFTY BANK","BTC-INR":"Bitcoin (INR)"}
    results = []
    for sym, name in INDICES.items():
        try:
            info = yf.Ticker(sym).info
            results.append({"symbol": sym, "name": name,
                            "price": info.get("currentPrice") or info.get("regularMarketPrice") or 0,
                            "change": info.get("regularMarketChange") or 0,
                            "change_pct": info.get("regularMarketChangePercent") or 0})
        except: pass
    return results

def _fetch_news(ticker):
    try:
        raw = yf.Ticker(ticker).news or []
        out = []
        for item in raw:
            c = item.get("content", item)
            title = c.get("title")
            link  = (c.get("canonicalUrl") or {}).get("url") or (c.get("clickThroughUrl") or {}).get("url") or c.get("link")
            pub   = (c.get("provider") or {}).get("displayName") or c.get("publisher") or "Yahoo Finance"
            if title and link:
                out.append({"title": title, "publisher": pub, "link": link})
        return out[:6]
    except: return []

def _search(q):
    if not q or len(q) < 2: return []
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        url = f"https://query2.finance.yahoo.com/v1/finance/search?q={q}.NS&lang=en-US&region=IN"
        res = _req.get(url, headers=headers, timeout=5)
        quotes = res.json().get('quotes', []) if res.ok else []
        out, seen = [], set()
        for q2 in quotes:
            if q2.get('quoteType') not in ['EQUITY','ETF']: continue
            sym = q2.get('symbol','')
            if not sym or sym in seen: continue
            seen.add(sym)
            out.append({'symbol': sym,
                        'shortname': q2.get('shortname') or q2.get('longname') or sym,
                        'exchDisp': q2.get('exchDisp') or ''})
        return out[:5]
    except: return []


# ─── Cached wrappers ──────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_stocks():
    tickers = db_get_tickers()
    rows = []
    for tk in tickers:
        d = db_get_fundamentals(tk)
        if d: rows.append(d)
    return rows

@st.cache_data(ttl=300)
def get_history(ticker):
    rows = db_get_history(ticker)
    if not rows:
        rows = _fetch_history(ticker)
        if rows: db_upsert_history(ticker, rows)
    return rows

@st.cache_data(ttl=60)
def get_indices():
    return _fetch_indices()

@st.cache_data(ttl=600)
def get_news(ticker):
    return _fetch_news(ticker)

def add_stock(ticker):
    ticker = ticker.upper()
    try:
        with st.spinner(f"Fetching {ticker}…"):
            fd = _fetch_fundamentals(ticker)
            if not fd.get('current_price') and not fd.get('name'):
                st.toast(f"✗ Could not find data for {ticker}")
                return
            db_add_ticker(ticker)
            db_upsert_fundamentals(ticker, fd)
            # Fetch history in background via session state flag
            st.session_state[f'needs_history_{ticker}'] = True
        get_stocks.clear()
        st.toast(f"✓ Added {ticker}")
    except Exception as e:
        st.toast(f"✗ Error: {e}")

def remove_stock(ticker):
    db_remove_ticker(ticker)
    get_stocks.clear()
    get_history.clear()

def refresh_stock(ticker):
    try:
        fd = _fetch_fundamentals(ticker)
        db_upsert_fundamentals(ticker, fd)
        hist = _fetch_history(ticker)
        if hist: db_upsert_history(ticker, hist)
    except: pass
    get_stocks.clear()
    get_history.clear()


# ─── Helpers ──────────────────────────────────────────────────────────────────
def fmt_cr(v):
    try:
        v = float(v or 0)
        if v <= 0: return "—"
        cr = v / 1e7
        return f"₹{cr/1e5:.2f}L Cr" if cr >= 1e5 else f"₹{cr:,.0f} Cr"
    except: return "—"

def fmt_n(v, dp=2):
    try:
        f = float(v or 0); return f"{f:,.{dp}f}" if f != 0 else "—"
    except: return "—"

def fmt_price(v, sym="₹"):
    try:
        f = float(v or 0); return f"{sym}{f:,.2f}" if f != 0 else "—"
    except: return "—"

def fmt_pct(v):
    try:
        f = float(v or 0); return f"{f*100:.2f}%" if f != 0 else "—"
    except: return "—"

def fmt_div(v):
    try:
        f = float(v or 0); return f"{f*100:.2f}%" if f != 0 else "—"
    except: return "—"

def rec_text(rec):
    if not rec or rec in ("N/A","none",""," "): return "—"
    r = rec.lower().replace("_"," ")
    for k,lbl in {"strong buy":"⬆ Strong Buy","buy":"↑ Buy","hold":"→ Hold",
                  "neutral":"→ Hold","sell":"↓ Sell","underperform":"↓ Underperform"}.items():
        if k in r: return lbl
    return rec.replace("_"," ").title()

def psym(c): return "₹" if (c or "INR") in ("INR","INp") else "$"

COLORS = ['#3b82f6','#22c55e','#f59e0b','#a78bfa','#ef4444','#06b6d4','#f97316','#ec4899']


# ─── Auth ─────────────────────────────────────────────────────────────────────
if 'authenticated' not in st.session_state:
    st.session_state['authenticated'] = False

if not st.session_state['authenticated']:
    if st.query_params.get("auth") == "ok":
        st.session_state['authenticated'] = True
        st.query_params.clear()
        st.rerun()

if not st.session_state['authenticated']:
    components.html("""<script>
    if (localStorage.getItem('fp_auth') === '1') {
        const u = new URL(window.parent.location.href);
        u.searchParams.set('auth','ok');
        window.parent.location.href = u.toString();
    }
    </script>""", height=0)
    _, cc, _ = st.columns([1, 1.2, 1])
    with cc:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:8px;">
          <span style="font-size:28px;font-weight:800;color:{t['text_main']};letter-spacing:-1px;">
            Fin<span style="color:{t['primary']};">Pulse</span></span>
          <p style="color:{t['text_muted']};font-size:13px;margin:6px 0 0;">Indian Markets Intelligence</p>
        </div>""", unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown(f"<p style='font-weight:600;font-size:15px;color:{t['text_main']};margin:0 0 12px;'>Sign in</p>", unsafe_allow_html=True)
            pw = st.text_input("pw", type="password", placeholder="Enter password", label_visibility="collapsed")
            if st.button("Continue →", use_container_width=True):
                if pw == "admin":
                    st.session_state['authenticated'] = True
                    components.html("<script>localStorage.setItem('fp_auth','1');</script>", height=0)
                    st.rerun()
                else:
                    st.error("Wrong password")
            st.caption("Password: admin")
    st.stop()


# ─── Fetch pending history in background ─────────────────────────────────────
for key in list(st.session_state.keys()):
    if key.startswith('needs_history_') and st.session_state[key]:
        tk = key.replace('needs_history_','')
        hist = _fetch_history(tk)
        if hist: db_upsert_history(tk, hist)
        st.session_state[key] = False
        get_history.clear()


# ─── Load data ────────────────────────────────────────────────────────────────
stocks    = get_stocks()
df_stocks = pd.DataFrame(stocks) if stocks else pd.DataFrame()

if 'sel_ticker' not in st.session_state:
    st.session_state['sel_ticker'] = df_stocks['ticker'].iloc[0] if not df_stocks.empty else None
if 'search_q' not in st.session_state:
    st.session_state['search_q'] = ""


# ─── Header ───────────────────────────────────────────────────────────────────
h1, h2, h3 = st.columns([2.5, 6, 2.5])
with h1:
    st.markdown(f"""<div style="padding-top:4px;">
      <span style="font-size:24px;font-weight:800;color:{t['primary']};letter-spacing:-1px;">
        Fin<span style="color:{t['text_main']};">Pulse</span></span>
      <span style="font-size:10px;color:{t['text_muted']};margin-left:8px;font-weight:700;
                  letter-spacing:0.05em;text-transform:uppercase;">India</span>
    </div>""", unsafe_allow_html=True)

with h2:
    search_q = st.text_input("search", placeholder="🔍  Search and add stocks — e.g. RELIANCE, TCS, INFY...",
                             label_visibility="collapsed", key="search_q_input")

with h3:
    theme_icon = "🌞 Light Mode" if st.session_state['theme'] == 'dark' else "🌙 Dark Mode"
    if st.button(theme_icon, use_container_width=True):
        toggle_theme(); st.rerun()

# Search results dropdown
if search_q and len(search_q.strip()) >= 2:
    results = _search(search_q.strip())
    if results:
        with st.container(border=True):
            st.markdown(f"<p style='font-size:10px;font-weight:800;letter-spacing:0.07em;color:{t['text_muted']};margin-bottom:8px;'>SEARCH RESULTS — click Add to track</p>", unsafe_allow_html=True)
            for r in results:
                sym = r['symbol']; nm = (r.get('shortname') or sym)[:32]; exch = r.get('exchDisp','')
                ci, ca, cv = st.columns([6, 2, 2])
                with ci:
                    st.markdown(f"**{sym}** · <span style='font-size:11.5px;color:{t['text_sub']};'>{nm} ({exch})</span>", unsafe_allow_html=True)
                with ca:
                    if st.button("Add ＋", key=f"add_{sym}", use_container_width=True):
                        add_stock(sym); st.session_state['sel_ticker'] = sym; st.rerun()
                with cv:
                    if st.button("View 👁", key=f"view_{sym}", use_container_width=True):
                        st.session_state['sel_ticker'] = sym; st.rerun()
    else:
        st.caption("No results. Try adding .NS suffix e.g. RELIANCE.NS")

st.markdown("<div style='margin-bottom:12px;'></div>", unsafe_allow_html=True)

# ─── Market index ribbon ──────────────────────────────────────────────────────
indices = get_indices()
if indices:
    cols = st.columns(len(indices))
    for i, idx in enumerate(indices):
        price = float(idx.get('price') or 0)
        change = float(idx.get('change') or 0)
        chg_pct = float(idx.get('change_pct') or 0)
        c_color = t['green'] if change >= 0 else t['red']
        sign = "+" if change >= 0 else ""
        with cols[i]:
            st.markdown(f"""
            <div style="background:{t['card_bg']};border:1px solid {t['border']};border-radius:12px;padding:10px 14px;text-align:center;">
                <div style="font-size:10px;color:{t['text_muted']};text-transform:uppercase;font-weight:700;letter-spacing:0.06em;">{idx.get('name')}</div>
                <div style="font-size:16px;font-weight:800;color:{t['text_main']};margin:2px 0;">{price:,.2f}</div>
                <div style="font-size:11px;font-weight:700;color:{c_color};">{sign}{change:,.2f} ({sign}{chg_pct:.2f}%)</div>
            </div>""", unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# Sentiment
nifty_pct = next((float(i.get('change_pct') or 0) for i in indices if i.get('symbol') == '^NSEI'), 0.0)
s_label = "Upbeat Sentiment" if nifty_pct >= 0 else "Cautious Sentiment"
s_color = t['green'] if nifty_pct >= 0 else t['red']
s_bars  = "████████" if nifty_pct >= 0 else "░░░░░░░░"

# ─── Main layout ──────────────────────────────────────────────────────────────
col_main, col_sidebar = st.columns([7.2, 2.8])

with col_main:
    # Market summary card
    nifty_dir = "bullish" if nifty_pct >= 0 else "bearish"
    m_text = f"<strong>Market Outlook</strong>: Indian equities show a <strong>{nifty_dir}</strong> trend. NIFTY 50 moved <strong>{nifty_pct:+.2f}%</strong> today."
    if not df_stocks.empty:
        gainers = int((df_stocks['day_change_pct'].fillna(0) > 0).sum())
        losers  = int((df_stocks['day_change_pct'].fillna(0) < 0).sum())
        m_text += f"<br><br><strong>Watchlist</strong>: {gainers} stocks advanced · {losers} declined."
    else:
        m_text += "<br><br><strong>Watchlist</strong>: No stocks tracked yet. Search above to add stocks."
    st.markdown(f"""
    <div style="background:{t['card_bg']};border:1px solid {t['border']};border-radius:12px;padding:18px 22px;margin-bottom:15px;line-height:1.5;">
        <div style="display:flex;justify-content:space-between;margin-bottom:10px;font-size:11.5px;font-weight:700;">
            <span style="color:{t['primary']};text-transform:uppercase;letter-spacing:0.05em;">📝 Market Intelligence</span>
            <span style="color:{s_color};font-weight:800;">{s_bars} {s_label}</span>
        </div>
        <div style="font-size:12.5px;color:{t['text_sub']};">{m_text}</div>
    </div>""", unsafe_allow_html=True)

    tab1, tab2, tab3, tab4 = st.tabs(["📊  Dashboard", "⚖️  Compare", "🔍  Screener", "💼  Portfolio"])

    # ══ TAB 1 — DASHBOARD ══════════════════════════════════════════════════════
    with tab1:
        if df_stocks.empty:
            st.info("👆 Use the search bar above to add stocks to your watchlist.")
        else:
            valid = df_stocks['ticker'].tolist()
            if st.session_state.get('sel_ticker') not in valid:
                st.session_state['sel_ticker'] = valid[0]
            sel  = st.session_state['sel_ticker']
            fd   = df_stocks[df_stocks['ticker'] == sel].iloc[0]
            sym  = psym(fd.get('currency'))
            price = float(fd.get('current_price') or 0)
            chg   = float(fd.get('day_change_pct') or 0)
            hi52  = float(fd.get('high_52w') or 0)
            lo52  = float(fd.get('low_52w') or 0)
            chg_col = t['green'] if chg >= 0 else t['red']
            arrow   = "▲" if chg >= 0 else "▼"
            chg_sign = "+" if chg >= 0 else ""
            chg_bg  = 'rgba(34,197,94,.1)' if chg >= 0 else 'rgba(239,68,68,.1)'
            chg_bdr = 'rgba(34,197,94,.2)' if chg >= 0 else 'rgba(239,68,68,.2)'

            # Hero card
            st.markdown(f"""
            <div style="background:{t['card_bg']};border:1px solid {t['border']};border-radius:14px;padding:20px 24px;margin-bottom:15px;">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:12px;">
                <div>
                  <div style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:{t['text_muted']};">{fd.get('sector') or '—'}</div>
                  <div style="font-size:18px;font-weight:700;color:{t['text_main']};margin:4px 0 10px;">{fd.get('name') or sel} <span style="color:{t['text_muted']};font-size:14px;">({sel})</span></div>
                  <div style="display:flex;align-items:center;gap:12px;">
                    <span style="font-size:38px;font-weight:800;color:{t['text_main']};letter-spacing:-1.2px;line-height:1;">{sym}{price:,.2f}</span>
                    <span style="background:{chg_bg};color:{chg_col};border:1px solid {chg_bdr};border-radius:20px;padding:4px 12px;font-size:12.5px;font-weight:700;">{arrow} {chg_sign}{chg:.2f}%</span>
                  </div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:9.5px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:{t['text_muted']};margin-bottom:6px;">Analyst Recommendation</div>
                  <div style="font-size:15px;font-weight:700;color:{t['text_main']};">{rec_text(fd.get('recommendation',''))}</div>
                  <div style="font-size:11.5px;color:{t['text_sub']};margin-top:4px;">Target: {fmt_price(fd.get('target_price'), sym)}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)

            # AI Copilot
            r_pe = float(fd.get('pe_ratio') or 0); r_roe = float(fd.get('roe') or 0) * 100
            r_tgt = float(fd.get('target_price') or 0); r_hi = float(fd.get('high_52w') or 0); r_lo = float(fd.get('low_52w') or 0)
            st.markdown(f"""
            <div style="background:{t['card_bg']};border:1px solid {t['border']};border-radius:12px;padding:18px 22px;margin-bottom:15px;line-height:1.5;">
                <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                    <span style="font-size:16px;">🤖</span>
                    <span style="font-size:12px;font-weight:800;letter-spacing:0.05em;color:{t['primary']};text-transform:uppercase;">FinPulse AI Copilot</span>
                </div>
                <div style="font-size:13.5px;font-weight:700;color:{t['text_main']};margin-bottom:8px;">Is {fd.get('name') or sel} a buy at {sym}{price:,.2f}?</div>
                <div style="font-size:12.5px;color:{t['text_sub']};">
                    <strong>Analysis:</strong> Operating in <strong>{fd.get('sector') or '—'}</strong> sector.
                    {"P/E of "+str(round(r_pe,1)) if r_pe>0 else "No trailing P/E listed"} ·
                    {"ROE of "+str(round(r_roe,1))+"%" if r_roe!=0 else "ROE stable"} ·
                    {"Target " + sym + f"{r_tgt:,.2f}" if r_tgt>0 else "No analyst target"} ·
                    52W range: {sym}{r_lo:,.2f} – {sym}{r_hi:,.2f}
                </div>
            </div>""", unsafe_allow_html=True)

            # 52W bar
            if hi52 > lo52 > 0:
                pos = max(0, min(100, (price - lo52) / (hi52 - lo52) * 100))
                st.markdown(f"""
                <div style="background:{t['card_bg']};border:1px solid {t['border']};border-radius:12px;padding:14px 20px;margin-bottom:15px;">
                  <div style="display:flex;justify-content:space-between;margin-bottom:8px;">
                    <span style="font-size:10px;font-weight:700;letter-spacing:.08em;text-transform:uppercase;color:{t['text_muted']};">52-Week Range</span>
                    <span style="font-size:11px;color:{t['text_sub']};">{pos:.0f}% above 52W low</span>
                  </div>
                  <div style="position:relative;background:{t['border']};border-radius:4px;height:5px;">
                    <div style="position:absolute;left:0;width:{pos}%;background:linear-gradient(90deg,{t['green']},{t['primary']});height:5px;border-radius:4px;"></div>
                    <div style="position:absolute;left:{pos}%;transform:translateX(-50%);top:-5px;width:14px;height:14px;background:{t['text_main']};border-radius:50%;border:2px solid {t['primary']};"></div>
                  </div>
                  <div style="display:flex;justify-content:space-between;margin-top:8px;">
                    <span style="font-size:11px;font-weight:600;color:{t['red']};">{sym}{lo52:,.2f}</span>
                    <span style="font-size:11px;font-weight:600;color:{t['green']};">{sym}{hi52:,.2f}</span>
                  </div>
                </div>""", unsafe_allow_html=True)

            # Metrics
            st.markdown(f"<p style='font-size:10px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:{t['text_muted']};margin:0 0 10px;'>Key Financials</p>", unsafe_allow_html=True)
            r1a,r1b,r1c,r1d = st.columns(4)
            r1a.metric("Market Cap", fmt_cr(fd.get('market_cap')))
            r1b.metric("P/E Ratio",  fmt_n(fd.get('pe_ratio')))
            r1c.metric("P/B Ratio",  fmt_n(fd.get('pb_ratio')))
            r1d.metric("EPS (TTM)",  fmt_price(fd.get('eps'), sym))

            r2a,r2b,r2c,r2d = st.columns(4)
            r2a.metric("ROE",           fmt_pct(fd.get('roe')))
            r2b.metric("ROA",           fmt_pct(fd.get('roce')))
            r2c.metric("Div Yield",     fmt_div(fd.get('dividend_yield')))
            r2d.metric("Beta",          fmt_n(fd.get('beta'), 3))

            r3a,r3b,r3c,r3d = st.columns(4)
            vol = int(fd.get('volume') or 0); avg_vol = int(fd.get('avg_volume') or 0)
            r3a.metric("52W High",      fmt_price(hi52, sym))
            r3b.metric("52W Low",       fmt_price(lo52, sym))
            r3c.metric("Volume",        f"{vol:,}" if vol else "—")
            r3d.metric("Avg Vol 3M",    f"{avg_vol:,}" if avg_vol else "—")

            st.markdown("<hr>", unsafe_allow_html=True)

            # Chart
            hist = get_history(sel)
            if hist:
                df_h = pd.DataFrame(hist)
                df_h['date'] = pd.to_datetime(df_h['date'])
                df_h = df_h.ffill().fillna(0).sort_values('date').drop_duplicates('date')
                df_h['MA10'] = df_h['close'].rolling(10).mean()
                df_h['MA40'] = df_h['close'].rolling(40).mean()
                df_h['MA90'] = df_h['close'].rolling(90).mean()

                ctrl1, ctrl2 = st.columns([2.5, 4.5])
                with ctrl1:
                    ctype = st.radio("Type", ["Candlestick","Line"], index=1, horizontal=True, key=f"ctype_{sel}")
                with ctrl2:
                    trange = st.radio("Range", ["1W","1M","6M","1Y","5Y"], index=2, horizontal=True, key=f"trange_{sel}")

                ma1,ma2,ma3,_ = st.columns([1,1,1,5])
                show10 = ma1.checkbox("10D MA", key=f"ma10_{sel}")
                show40 = ma2.checkbox("40D MA", key=f"ma40_{sel}")
                show90 = ma3.checkbox("90D MA", key=f"ma90_{sel}")

                offsets = {"1W": pd.Timedelta(days=7), "1M": pd.DateOffset(months=1),
                           "6M": pd.DateOffset(months=6), "1Y": pd.DateOffset(years=1),
                           "5Y": pd.DateOffset(years=5)}
                df_f = df_h[df_h['date'] >= df_h['date'].max() - offsets[trange]].copy()

                if len(df_f) >= 2:
                    sp, ep = df_f.iloc[0]['close'], df_f.iloc[-1]['close']
                    pct = ((ep-sp)/sp*100) if sp else 0
                    c_p = t['green'] if pct >= 0 else t['red']
                    st.markdown(f"<div style='margin:4px 0 8px;'>"
                                f"<span style='font-size:22px;font-weight:700;color:{c_p};'>{'+' if pct>=0 else ''}{pct:.2f}%</span>"
                                f"<span style='font-size:12px;color:{t['text_sub']};margin-left:10px;'>{sym}{sp:,.2f} → {sym}{ep:,.2f} over {trange}</span>"
                                f"</div>", unsafe_allow_html=True)

                if ctype == "Candlestick":
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                        row_heights=[0.72, 0.28], vertical_spacing=0.01)
                    fig.add_trace(plgo.Candlestick(
                        x=df_f['date'], open=df_f['open'], high=df_f['high'],
                        low=df_f['low'], close=df_f['close'], name='Price',
                        increasing_line_color=t['green'], increasing_fillcolor='rgba(34,197,94,.15)',
                        decreasing_line_color=t['red'],   decreasing_fillcolor='rgba(239,68,68,.12)',
                    ), row=1, col=1)
                    vcols = [t['green'] if c >= o else t['red'] for c,o in zip(df_f['close'], df_f['open'])]
                    fig.add_trace(plgo.Bar(x=df_f['date'], y=df_f['volume'], name='Volume',
                                           marker_color=vcols, opacity=0.6,
                                           hovertemplate='Vol: %{y:,.0f}<extra></extra>'), row=2, col=1)
                    fig.update_layout(xaxis_rangeslider_visible=False, height=480)
                    fig.update_yaxes(tickformat='.2s', row=2, col=1,
                                     gridcolor=t['border'], tickfont=dict(color=t['text_sub'], size=10))
                    add_row = 1
                else:
                    y_min = df_f['close'].min() * 0.997; y_max = df_f['close'].max() * 1.003
                    fig = plgo.Figure()
                    fig.add_trace(plgo.Scatter(
                        x=df_f['date'], y=df_f['close'], mode='lines', name='Close',
                        line=dict(color=t['primary'], width=2.5),
                        fill='tozeroy',
                        fillcolor='rgba(59,130,246,.08)' if st.session_state['theme']=='dark' else 'rgba(37,99,235,.06)',
                        hovertemplate=f'%{{x|%d %b %Y}}<br><b>{sym}%{{y:,.2f}}</b><extra></extra>'
                    ))
                    fig.update_yaxes(range=[y_min, y_max])
                    fig.update_layout(height=390)
                    add_row = None

                for show, col_name, name, color in [
                    (show10,'MA10','10D MA','#f59e0b'),
                    (show40,'MA40','40D MA',t['primary']),
                    (show90,'MA90','90D MA','#a78bfa')
                ]:
                    if show:
                        tr = plgo.Scatter(x=df_f['date'], y=df_f[col_name], mode='lines', name=name,
                                          line=dict(color=color, width=1.5, dash='dot'))
                        fig.add_trace(tr, row=add_row, col=1) if add_row else fig.add_trace(tr)

                fig.update_layout(
                    paper_bgcolor=BG, plot_bgcolor=BG, margin=dict(l=0,r=0,t=8,b=0),
                    hovermode='x unified',
                    legend=dict(orientation='h', y=1.04, x=1, xanchor='right',
                                bgcolor='rgba(0,0,0,0)', font=dict(size=11, color=t['text_sub'])),
                    xaxis=dict(gridcolor=t['border'], tickfont=dict(color=t['text_sub'], size=10), showline=False),
                    yaxis=dict(gridcolor=t['border'], tickfont=dict(color=t['text_sub'], size=10),
                               showline=False, tickprefix=sym),
                )
                st.plotly_chart(fig, use_container_width=True,
                                key=f"main_chart_{sel}_{ctype}_{trange}_{show10}_{show40}_{show90}")

                # Technical indicators
                st.markdown(f"<p style='font-size:10px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:{t['text_muted']};margin:12px 0 10px;'>Technical Indicators</p>", unsafe_allow_html=True)
                ti1,ti2,ti3 = st.columns(3)
                lp    = df_h.iloc[-1]['close']
                ma50  = df_h['close'].rolling(50).mean().iloc[-1]
                ma200 = df_h['close'].rolling(200).mean().iloc[-1]
                ti1.metric("vs 50D MA",  f"{'↑ Above' if lp>ma50 else '↓ Below'}", f"MA50={sym}{ma50:.2f}")
                ti2.metric("vs 200D MA", f"{'↑ Above' if lp>ma200 else '↓ Below'}" if pd.notnull(ma200) and ma200>0 else "—",
                           f"MA200={sym}{ma200:.2f}" if pd.notnull(ma200) and ma200>0 else "Insufficient data")
                delta = df_h['close'].diff(); gain = delta.clip(lower=0).rolling(14).mean()
                loss  = (-delta.clip(upper=0)).rolling(14).mean()
                rsi   = (100 - 100/(1+gain/loss)).iloc[-1]
                ti3.metric("RSI (14)", f"{rsi:.1f}", "Overbought" if rsi>70 else ("Oversold" if rsi<30 else "Neutral"))
            else:
                st.info("📊 Historical data is being fetched. Refresh in a moment.")

            # News
            news = get_news(sel)
            if news:
                st.markdown(f"<hr><p style='font-size:10px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:{t['text_muted']};margin:16px 0 10px;'>Latest News</p>", unsafe_allow_html=True)
                n_cols = st.columns(2)
                for i, item in enumerate(news):
                    with n_cols[i % 2]:
                        st.markdown(f"""<a href="{item.get('link','#')}" target="_blank" style="text-decoration:none;">
                            <div style="background:{t['card_bg']};border:1px solid {t['border']};border-radius:10px;padding:12px 16px;margin-bottom:12px;height:105px;overflow:hidden;">
                                <div style="font-size:10px;font-weight:700;color:{t['primary']};text-transform:uppercase;margin-bottom:4px;">{item.get('publisher','')}</div>
                                <div style="font-size:13px;font-weight:600;color:{t['text_main']};line-height:1.4;">{item.get('title','')[:90]}{'...' if len(item.get('title',''))>90 else ''}</div>
                            </div></a>""", unsafe_allow_html=True)

    # ══ TAB 2 — COMPARE ════════════════════════════════════════════════════════
    with tab2:
        if df_stocks.empty:
            st.info("Add stocks to compare.")
        else:
            st.markdown(f"<p style='font-size:10px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:{t['text_muted']};margin:0 0 10px;'>1-Year Normalized Performance (Base=100)</p>", unsafe_allow_html=True)
            pf = plgo.Figure()
            for i, tk in enumerate(df_stocks['ticker'].tolist()):
                h = get_history(tk)
                if not h: continue
                dh = pd.DataFrame(h); dh['date'] = pd.to_datetime(dh['date'])
                dh = dh[dh['date'] >= dh['date'].max() - pd.DateOffset(years=1)]
                if dh.empty or dh.iloc[0]['close'] == 0: continue
                dh['norm'] = dh['close'] / dh.iloc[0]['close'] * 100
                pf.add_trace(plgo.Scatter(x=dh['date'], y=dh['norm'], mode='lines', name=tk,
                                           line=dict(color=COLORS[i%len(COLORS)], width=2)))
            pf.add_hline(y=100, line_dash='dot', line_color=t['border'])
            pf.update_layout(paper_bgcolor=BG, plot_bgcolor=BG, height=360,
                              margin=dict(l=0,r=0,t=8,b=0), hovermode='x unified',
                              xaxis=dict(gridcolor=t['border'], tickfont=dict(color=t['text_sub'],size=10)),
                              yaxis=dict(gridcolor=t['border'], tickfont=dict(color=t['text_sub'],size=10), title='Index'),
                              legend=dict(orientation='h', y=1.06, bgcolor='rgba(0,0,0,0)', font=dict(color=t['text_sub'],size=11)))
            st.plotly_chart(pf, use_container_width=True, key="compare_perf")

            mc1, mc2 = st.columns(2)
            for i,(col,lbl,mult,sfx) in enumerate([('pe_ratio','P/E',1,''),('pb_ratio','P/B',1,''),('roe','ROE',100,'%'),('roce','ROA',100,'%')]):
                vals = df_stocks[col].fillna(0)*mult
                bf = plgo.Figure(plgo.Bar(x=df_stocks['ticker'], y=vals,
                    marker_color=[COLORS[j%len(COLORS)] for j in range(len(df_stocks))],
                    text=[f"{v:.1f}{sfx}" for v in vals], textposition='outside',
                    textfont=dict(size=11,color=t['text_main'])))
                bf.update_layout(title=dict(text=lbl,font=dict(size=12,color=t['text_sub'])),
                    paper_bgcolor=BG, plot_bgcolor=BG, height=240,
                    margin=dict(l=0,r=0,t=36,b=0), showlegend=False,
                    xaxis=dict(tickfont=dict(size=11,color=t['text_main'])),
                    yaxis=dict(gridcolor=t['border'], tickfont=dict(color=t['text_sub'],size=10), rangemode='tozero'))
                (mc1 if i%2==0 else mc2).plotly_chart(bf, use_container_width=True, key=f"cbar_{col}")

            sec = df_stocks.groupby('sector').size().reset_index(name='n')
            sf  = plgo.Figure(plgo.Pie(labels=sec['sector'], values=sec['n'], hole=.55,
                                        marker_colors=COLORS, textinfo='label+percent', textfont_size=12))
            sf.update_layout(paper_bgcolor=BG, height=300, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
            st.plotly_chart(sf, use_container_width=True, key="sector_donut")

    # ══ TAB 3 — SCREENER ═══════════════════════════════════════════════════════
    with tab3:
        if df_stocks.empty:
            st.info("Add stocks to use the screener.")
        else:
            f1, f2 = st.columns(2)
            with f1:
                pe_v = df_stocks['pe_ratio'].replace(0, float('nan')).dropna()
                pe_lo = 0.0; pe_hi = float(pe_v.max()) if not pe_v.empty else 100.0
                if pe_lo >= pe_hi: pe_hi = pe_lo + 1
                min_pe, max_pe = st.slider("P/E Range", pe_lo, pe_hi, (pe_lo, pe_hi))
                min_roe = st.slider("Min ROE (%)", 0., 50., 0., 0.5)
            with f2:
                min_mc = st.number_input("Min Market Cap (Cr ₹)", 0., step=100.)
                pb_v   = df_stocks['pb_ratio'].replace(0, float('nan')).dropna()
                pb_hi  = float(pb_v.max()) if not pb_v.empty else 20.0
                max_pb = st.slider("Max P/B", 0., max(pb_hi*1.5, 20.), max(pb_hi*1.5, 20.))

            filt = df_stocks[
                (df_stocks['pe_ratio'].fillna(0) >= min_pe) &
                (df_stocks['pe_ratio'].fillna(0) <= max_pe) &
                (df_stocks['roe'].fillna(0)*100 >= min_roe) &
                (df_stocks['market_cap'].fillna(0) >= min_mc*1e7) &
                (df_stocks['pb_ratio'].fillna(999) <= max_pb)]

            if not filt.empty:
                d = filt[['ticker','name','sector','current_price','market_cap','pe_ratio','pb_ratio','roe','roce','dividend_yield','beta']].copy()
                d['market_cap']     = d['market_cap'].fillna(0)/1e7
                d['roe']            = d['roe'].fillna(0)*100
                d['roce']           = d['roce'].fillna(0)*100
                d['dividend_yield'] = d['dividend_yield'].fillna(0)*100
                d.columns = ['Ticker','Name','Sector','Price (₹)','MCap (Cr ₹)','P/E','P/B','ROE %','ROA %','Div %','Beta']
                st.dataframe(
                    d.round(2).style
                     .background_gradient(subset=['ROE %'], cmap='RdYlGn', vmin=0, vmax=30)
                     .background_gradient(subset=['P/E'],   cmap='RdYlGn_r', vmin=5, vmax=50)
                     .format({'MCap (Cr ₹)':'{:,.0f}','Price (₹)':'{:,.2f}'}),
                    use_container_width=True, hide_index=True)
                st.caption(f"{len(filt)} of {len(df_stocks)} stocks match")
                csv = d.to_csv(index=False)
                st.download_button("⬇ Export CSV", data=csv, file_name="finpulse_screener.csv", mime="text/csv")
            else:
                st.info("No stocks match the current filters.")

    # ══ TAB 4 — PORTFOLIO ══════════════════════════════════════════════════════
    with tab4:
        if 'portfolio' not in st.session_state:
            st.session_state['portfolio'] = {}
        if not df_stocks.empty:
            a1,a2,a3 = st.columns([2,1,1])
            pt  = a1.selectbox("Stock", df_stocks['ticker'].tolist(), key='pt')
            ps  = a2.number_input("Shares", min_value=1, step=1, key='ps')
            pbp = a3.number_input("Buy Price (₹)", min_value=0.01, step=0.01, key='pbp')
            if st.button("Add / Update Holding", use_container_width=True):
                st.session_state['portfolio'][pt] = {'shares': ps, 'buy': pbp}
                st.toast(f"Updated {pt}")

            if st.session_state['portfolio']:
                rows, t_inv, t_cur = [], 0, 0
                for t_key, info in list(st.session_state['portfolio'].items()):
                    row = df_stocks[df_stocks['ticker']==t_key]
                    if row.empty: continue
                    cp = float(row['current_price'].values[0] or 0)
                    sh, bp = info['shares'], info['buy']
                    inv = sh*bp; cur = sh*cp; pnl = cur-inv
                    pp  = (cp-bp)/bp*100 if bp else 0
                    t_inv += inv; t_cur += cur
                    rows.append({"Ticker":t_key,"Shares":sh,"Buy (₹)":bp,"LTP (₹)":round(cp,2),
                                 "Invested":round(inv,2),"Current":round(cur,2),
                                 "P&L (₹)":round(pnl,2),"P&L %":round(pp,2)})
                if rows:
                    tp = t_cur-t_inv; tpp = tp/t_inv*100 if t_inv else 0; sg = "+" if tp>=0 else ""
                    p1,p2,p3,p4 = st.columns(4)
                    p1.metric("Invested",      f"₹{t_inv:,.2f}")
                    p2.metric("Current Value", f"₹{t_cur:,.2f}")
                    p3.metric("Total P&L",     f"{sg}₹{tp:,.2f}")
                    p4.metric("Total Return",  f"{sg}{tpp:.2f}%")
                    st.markdown("---")
                    dh2 = pd.DataFrame(rows)
                    st.dataframe(dh2.style.map(
                        lambda v: f"color:{t['green']}" if isinstance(v,(int,float)) and v>0
                                  else (f"color:{t['red']}" if isinstance(v,(int,float)) and v<0 else ''),
                        subset=['P&L (₹)','P&L %']), use_container_width=True, hide_index=True)
                    af = plgo.Figure(plgo.Pie(labels=[r['Ticker'] for r in rows], values=[r['Current'] for r in rows],
                        hole=.55, marker_colors=COLORS[:len(rows)], textinfo='label+percent', textfont_size=12))
                    af.update_layout(paper_bgcolor=BG, height=300, margin=dict(l=0,r=0,t=8,b=0), showlegend=False)
                    st.plotly_chart(af, use_container_width=True, key="port_donut")
                    rm = st.selectbox("Remove holding", ["— select —"]+[r['Ticker'] for r in rows])
                    if rm != "— select —" and st.button("Remove"):
                        del st.session_state['portfolio'][rm]; st.rerun()
        else:
            st.info("Add stocks to your watchlist first.")


# ─── Sidebar / Watchlist ──────────────────────────────────────────────────────
with col_sidebar:
    st.markdown(f"<p style='color:{t['primary']};font-size:11px;font-weight:800;letter-spacing:.09em;margin:0 0 12px;text-transform:uppercase;'>Your Watchlist</p>", unsafe_allow_html=True)

    if not df_stocks.empty:
        for _, row in df_stocks.iterrows():
            tk = row['ticker']; price_s = float(row.get('current_price') or 0)
            chg_s = float(row.get('day_change_pct') or 0); nm = (row.get('name') or tk)[:24]
            sym_s = psym(row.get('currency')); is_sel = (st.session_state.get('sel_ticker') == tk)
            c_chg = t['green'] if chg_s >= 0 else t['red']
            chg_str = f"{'+'if chg_s>=0 else ''}{chg_s:.2f}%"
            bdr = t['primary'] if is_sel else t['border']; bg = t['hover_bg'] if is_sel else t['card_bg']
            st.markdown(f"""
            <div style="background:{bg};border:1px solid {bdr};border-radius:10px;padding:10px 12px;margin-bottom:6px;">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                  <div style="font-size:13px;font-weight:700;color:{t['text_main']};">{tk}</div>
                  <div style="font-size:10.5px;color:{t['text_muted']};margin-top:2px;">{nm}</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:13px;font-weight:600;color:{t['text_main']};">{sym_s}{price_s:,.2f}</div>
                  <div style="font-size:11px;font-weight:600;color:{c_chg};">{chg_str}</div>
                </div>
              </div>
            </div>""", unsafe_allow_html=True)
            bc, dc = st.columns([2.5, 1.5])
            if bc.button("View →", key=f"sel_{tk}", use_container_width=True):
                st.session_state['sel_ticker'] = tk; st.rerun()
            if dc.button("Remove ✕", key=f"del_{tk}", use_container_width=True):
                remove_stock(tk)
                if st.session_state.get('sel_ticker') == tk: st.session_state['sel_ticker'] = None
                st.rerun()
    else:
        st.caption("Nothing tracked yet. Search above to add stocks.")

    # Heatmap
    if not df_stocks.empty:
        st.markdown(f"<hr><p style='font-size:10px;font-weight:800;letter-spacing:.09em;text-transform:uppercase;color:{t['text_muted']};margin:16px 0 8px;'>Performance Heatmap</p>", unsafe_allow_html=True)
        try:
            hd = df_stocks.copy()
            hd['sector']         = hd['sector'].fillna('Unknown')
            hd['day_change_pct'] = hd['day_change_pct'].fillna(0)
            hd['market_cap']     = hd['market_cap'].fillna(1e9).clip(lower=1e9)
            fig_map = px.treemap(hd, path=[px.Constant("Watchlist"),'sector','ticker'],
                                 values='market_cap', color='day_change_pct',
                                 color_continuous_scale='RdYlGn', color_continuous_midpoint=0,
                                 custom_data=['current_price','day_change_pct'])
            fig_map.update_traces(hovertemplate='<b>%{label}</b><br>₹%{customdata[0]:,.2f}<br>%{customdata[1]:+.2f}%<extra></extra>')
            fig_map.update_layout(paper_bgcolor=BG, height=220,
                                   margin=dict(l=0,r=0,t=0,b=0), coloraxis_showscale=False)
            st.plotly_chart(fig_map, use_container_width=True,
                            config={'displayModeBar': False}, key="heatmap")
        except Exception as e:
            st.caption(f"Heatmap unavailable: {e}")

    st.markdown("<hr>", unsafe_allow_html=True)
    cs, co = st.columns(2)
    if cs.button("↺ Sync All", use_container_width=True):
        for tk in df_stocks['ticker']:
            refresh_stock(tk)
        st.rerun()
    if co.button("Sign out", use_container_width=True):
        st.session_state['authenticated'] = False
        components.html("<script>localStorage.removeItem('fp_auth');</script>", height=0)
        st.rerun()
