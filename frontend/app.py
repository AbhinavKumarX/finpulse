import streamlit as st
from st_keyup import st_keyup
import streamlit.components.v1 as components
import pandas as pd
import requests
import plotly.graph_objects as plgo
import plotly.express as px
from plotly.subplots import make_subplots
import os

API_URL = os.environ.get("API_URL", "http://localhost:8000")

st.set_page_config(
    page_title="FinPulse — Indian Markets",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# ─────────────────────────────────────────────────────────────────────────────
# Theme System
# ─────────────────────────────────────────────────────────────────────────────
if "theme" not in st.session_state:
    st.session_state["theme"] = "dark"

T = {
    "dark": {
        "bg": "#07090f", "card": "#0f1420", "sidebar": "#0b0f1a",
        "border": "#1a2035", "border2": "#243050",
        "text": "#e8edf5", "sub": "#8892a4", "muted": "#3d4a5c",
        "primary": "#4f8ef7", "primary_dim": "rgba(79,142,247,.12)",
        "green": "#2ecc71", "red": "#e74c3c",
        "green_dim": "rgba(46,204,113,.12)", "red_dim": "rgba(231,76,60,.12)",
        "accent": "#7c5cfc", "accent_dim": "rgba(124,92,252,.12)",
        "gold": "#f0a500",
    },
    "light": {
        "bg": "#f3f6fb", "card": "#ffffff", "sidebar": "#eaeef5",
        "border": "#dde3ef", "border2": "#c8d0e0",
        "text": "#111827", "sub": "#4b5563", "muted": "#9ca3af",
        "primary": "#2563eb", "primary_dim": "rgba(37,99,235,.08)",
        "green": "#16a34a", "red": "#dc2626",
        "green_dim": "rgba(22,163,74,.1)", "red_dim": "rgba(220,38,38,.1)",
        "accent": "#6d28d9", "accent_dim": "rgba(109,40,217,.1)",
        "gold": "#d97706",
    }
}
t = T[st.session_state["theme"]]

# ─────────────────────────────────────────────────────────────────────────────
# Global CSS
# ─────────────────────────────────────────────────────────────────────────────
st.markdown(f"""
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800;900&display=swap');
*, *::before, *::after {{ font-family: 'Inter', sans-serif !important; box-sizing: border-box; }}

.stApp, [data-testid="stAppViewContainer"],
[data-testid="stAppViewContainer"] > section > div {{ background: {t["bg"]} !important; }}
.main .block-container {{ padding: 0.75rem 1.75rem 2rem !important; max-width: 100% !important; }}

[data-testid="stSidebar"], [data-testid="stSidebarCollapsedControl"],
#MainMenu, footer, header, [data-testid="stToolbar"],
[data-testid="stDecoration"] {{ display: none !important; }}

/* ── Metrics ── */
[data-testid="stMetric"] {{
    background: {t["card"]} !important; border: 1px solid {t["border"]} !important;
    border-radius: 14px !important; padding: 16px 18px 14px !important;
    transition: border-color .2s, transform .15s !important;
}}
[data-testid="stMetric"]:hover {{
    border-color: {t["primary"]} !important; transform: translateY(-1px) !important;
}}
[data-testid="stMetricLabel"] > div {{
    font-size: 9.5px !important; font-weight: 800 !important;
    letter-spacing: .1em !important; text-transform: uppercase !important;
    color: {t["muted"]} !important;
}}
[data-testid="stMetricValue"] > div {{
    font-size: 18px !important; font-weight: 800 !important; color: {t["text"]} !important;
}}
[data-testid="stMetricDelta"] > div {{ font-size: 11px !important; }}

/* ── Tabs ── */
[data-testid="stTabs"] [role="tablist"] {{
    border-bottom: 1px solid {t["border"]} !important;
    gap: 0 !important; background: transparent !important; margin-bottom: 18px !important;
}}
[data-testid="stTabs"] button[role="tab"] {{
    background: transparent !important; color: {t["sub"]} !important;
    border: none !important; border-bottom: 2px solid transparent !important;
    border-radius: 0 !important; font-size: 12.5px !important;
    font-weight: 700 !important; padding: 10px 22px !important;
    transition: color .15s !important;
}}
[data-testid="stTabs"] button[aria-selected="true"] {{
    color: {t["primary"]} !important; border-bottom-color: {t["primary"]} !important;
}}
[data-testid="stTabs"] button:hover {{ color: {t["text"]} !important; }}

/* ── Buttons ── */
.stButton > button {{
    background: {t["card"]} !important; color: {t["text"]} !important;
    border: 1px solid {t["border"]} !important; border-radius: 9px !important;
    font-size: 11.5px !important; font-weight: 700 !important;
    padding: 5px 12px !important; width: 100% !important;
    transition: border-color .15s, background .15s !important;
}}
.stButton > button:hover {{ border-color: {t["primary"]} !important; background: {t["primary_dim"]} !important; }}

/* ── Inputs ── */
.stTextInput > label {{ display: none !important; }}
.stTextInput > div > div {{
    background: {t["card"]} !important; border: 1px solid {t["border"]} !important;
    border-radius: 10px !important;
}}
.stTextInput input {{ color: {t["text"]} !important; font-size: 14px !important; }}
.stTextInput input::placeholder {{ color: {t["muted"]} !important; }}

[data-testid="stSelectbox"] > label {{
    font-size: 10px !important; color: {t["muted"]} !important;
    font-weight: 800 !important; text-transform: uppercase !important; letter-spacing: .08em !important;
}}
[data-testid="stSelectbox"] > div > div {{
    background: {t["card"]} !important; border: 1px solid {t["border"]} !important;
    border-radius: 10px !important; color: {t["text"]} !important;
}}

[data-testid="stRadio"] > label {{ display: none !important; }}
[data-testid="stRadio"] > div {{ gap: 6px !important; }}
[data-testid="stRadio"] > div > label {{
    background: {t["card"]} !important; border: 1px solid {t["border"]} !important;
    border-radius: 8px !important; padding: 4px 14px !important;
    font-size: 11px !important; font-weight: 700 !important;
    color: {t["muted"]} !important; cursor: pointer !important;
    transition: all .15s !important;
}}
[data-testid="stRadio"] > div > label:has(input:checked) {{
    border-color: {t["primary"]} !important; color: {t["primary"]} !important;
    background: {t["primary_dim"]} !important;
}}

[data-testid="stCheckbox"] label {{
    font-size: 11px !important; color: {t["muted"]} !important; font-weight: 600 !important;
}}
[data-testid="stNumberInput"] > label, [data-testid="stSlider"] > label {{
    font-size: 10px !important; color: {t["muted"]} !important;
    text-transform: uppercase !important; letter-spacing: .08em !important; font-weight: 800 !important;
}}
[data-testid="stNumberInput"] > div > div {{
    background: {t["card"]} !important; border-color: {t["border"]} !important; border-radius: 10px !important;
}}
[data-testid="stNumberInput"] input {{ color: {t["text"]} !important; }}

[data-testid="stDataFrame"] iframe {{ border-radius: 12px !important; }}
hr {{ border-color: {t["border"]} !important; margin: 12px 0 !important; }}
[data-testid="stAlert"] {{
    background: {t["card"]} !important; border-color: {t["border"]} !important; border-radius: 12px !important;
}}
::-webkit-scrollbar {{ width: 4px; height: 4px; }}
::-webkit-scrollbar-track {{ background: transparent; }}
::-webkit-scrollbar-thumb {{ background: {t["border2"]}; border-radius: 4px; }}

/* ── Login page specifics ── */
.fp-login-wrap {{
    min-height: 100vh; display: flex; align-items: center; justify-content: center;
    background: {t["bg"]};
}}
.fp-login-card {{
    background: {t["card"]}; border: 1px solid {t["border2"]};
    border-radius: 20px; padding: 44px 40px; width: 100%; max-width: 400px;
    box-shadow: 0 24px 80px rgba(0,0,0,.3);
}}
</style>
""", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────────────────────
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
        f = float(v or 0)
        return f"{f*100:.2f}%" if f != 0 else "—"
    except: return "—"

def fmt_div_yield(v):
    try:
        f = float(v or 0)
        return f"{f*100:.2f}%" if f != 0 else "—"
    except: return "—"

def rec_text(rec):
    if not rec or rec in ("N/A", "none", "", " "): return "—"
    r = rec.lower().replace("_", " ")
    labels = {
        "strong buy": "⬆ Strong Buy", "buy": "↑ Buy",
        "hold": "→ Hold", "neutral": "→ Hold",
        "sell": "↓ Sell", "underperform": "↓ Underperform"
    }
    for k, lbl in labels.items():
        if k in r: return lbl
    return rec.replace("_", " ").title()

def psym(currency):
    return "₹" if (currency or "INR") in ("INR", "INp") else "$"

def auth_headers():
    token = st.session_state.get("token", "")
    return {"X-User-Token": token}

COLORS = [
    "#4f8ef7","#2ecc71","#f0a500","#a78bfa","#e74c3c",
    "#06b6d4","#f97316","#ec4899","#10b981","#8b5cf6"
]

# ─────────────────────────────────────────────────────────────────────────────
# Auth State Bootstrap (localStorage → session_state)
# ─────────────────────────────────────────────────────────────────────────────
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "token" not in st.session_state:
    st.session_state["token"] = ""
if "username" not in st.session_state:
    st.session_state["username"] = ""

# Restore session from localStorage token via query param
if not st.session_state["authenticated"]:
    qp = st.query_params.get("fp_token", "")
    if qp:
        user = None
        try:
            r = requests.get(f"{API_URL}/auth/me", headers={"X-User-Token": qp}, timeout=5)
            if r.ok:
                user = r.json()
        except Exception:
            pass
        if user:
            st.session_state["authenticated"] = True
            st.session_state["token"] = qp
            st.session_state["username"] = user.get("username", "")
            st.query_params.clear()
            st.rerun()
        else:
            st.query_params.clear()

# ─────────────────────────────────────────────────────────────────────────────
# LOGIN / REGISTER SCREEN
# ─────────────────────────────────────────────────────────────────────────────
if not st.session_state["authenticated"]:
    # Restore from localStorage
    components.html("""
    <script>
    const tok = localStorage.getItem('fp_token_v2');
    if (tok) {
        const u = new URL(window.parent.location.href);
        u.searchParams.set('fp_token', tok);
        window.parent.location.href = u.toString();
    }
    </script>""", height=0)

    # ── Login UI ──────────────────────────────────────────────────────────────
    _, cc, _ = st.columns([1, 1.1, 1])
    with cc:
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"""
        <div style="text-align:center;margin-bottom:28px;">
          <div style="display:inline-flex;align-items:center;gap:8px;margin-bottom:6px;">
            <span style="font-size:32px;">📈</span>
            <span style="font-size:30px;font-weight:900;letter-spacing:-1.5px;color:{t['text']};">
              Fin<span style="color:{t['primary']};">Pulse</span>
            </span>
          </div>
          <p style="color:{t['sub']};font-size:13.5px;margin:0;font-weight:500;">
            Your personal Indian market intelligence hub.
          </p>
        </div>
        """, unsafe_allow_html=True)

        if "auth_mode" not in st.session_state:
            st.session_state["auth_mode"] = "login"

        mode = st.session_state["auth_mode"]

        with st.container(border=True):
            label = "Sign In" if mode == "login" else "Create Account"
            st.markdown(f"""
            <p style="font-size:17px;font-weight:800;color:{t['text']};margin:0 0 4px;">{label}</p>
            <p style="font-size:12px;color:{t['sub']};margin:0 0 18px;">
              {"Enter your username to continue." if mode == "login" else "Pick a username. It's your permanent identity."}
            </p>
            """, unsafe_allow_html=True)

            uname = st.text_input(
                "username",
                placeholder="e.g. abhinav_trades",
                label_visibility="collapsed",
                key="auth_username_input"
            )

            if st.button(
                ("→ Sign In" if mode == "login" else "→ Create Account"),
                use_container_width=True
            ):
                uname = uname.strip()
                if not uname:
                    st.error("Please enter a username.")
                else:
                    try:
                        endpoint = "login" if mode == "login" else "register"
                        payload = {"username": uname}
                        resp = requests.post(
                            f"{API_URL}/auth/{endpoint}", json=payload, timeout=10
                        )
                        if resp.ok:
                            data = resp.json()
                            token = data["token"]
                            uname_returned = data["username"]
                            is_new = data.get("is_new", False)

                            st.session_state["authenticated"] = True
                            st.session_state["token"] = token
                            st.session_state["username"] = uname_returned

                            # Persist token in localStorage
                            components.html(
                                f"<script>localStorage.setItem('fp_token_v2', '{token}');</script>",
                                height=0
                            )

                            # If new user, kick off background seed
                            if is_new:
                                try:
                                    requests.post(
                                        f"{API_URL}/auth/seed/{token}", timeout=3
                                    )
                                except Exception:
                                    pass

                            st.rerun()
                        else:
                            err = resp.json().get("detail", "Something went wrong.")
                            if mode == "login" and "not found" in err.lower():
                                suggest = f"'{uname}' doesn't exist yet."
                                st.error(f"🔍 {suggest}")
                                st.info("💡 Switch to **Create Account** below to register this username.")
                            elif mode == "register" and "already taken" in err.lower():
                                st.error(f"🚫 {err}")
                                # Suggest alternatives
                                suggestions = [f"{uname}1", f"{uname}_v2", f"{uname}_{uname[:2]}"]
                                st.info(f"💡 Try one of these instead: **{'**, **'.join(suggestions)}**")
                            else:
                                st.error(err)
                    except requests.exceptions.ConnectionError:
                        st.error("⚠️ Cannot connect to backend. Make sure the API is running.")
                    except Exception as e:
                        st.error(f"Error: {str(e)}")

            st.markdown("<div style='height:12px'></div>", unsafe_allow_html=True)
            if mode == "login":
                st.markdown(
                    f"<p style='font-size:12px;color:{t['sub']};text-align:center;margin:0;'>"
                    "New here? ",
                    unsafe_allow_html=True
                )
                if st.button("Create a new account →", use_container_width=True, key="switch_to_reg"):
                    st.session_state["auth_mode"] = "register"
                    st.rerun()
            else:
                st.markdown(
                    f"<p style='font-size:12px;color:{t['sub']};text-align:center;margin:0;'>"
                    "Already have an account? ",
                    unsafe_allow_html=True
                )
                if st.button("← Back to Sign In", use_container_width=True, key="switch_to_login"):
                    st.session_state["auth_mode"] = "login"
                    st.rerun()

        st.markdown(f"""
        <p style="text-align:center;font-size:11px;color:{t['muted']};margin-top:20px;">
          FinPulse · Data via yFinance & NSE · Not financial advice
        </p>
        """, unsafe_allow_html=True)
    st.stop()


# ─────────────────────────────────────────────────────────────────────────────
# AUTHENTICATED APP
# ─────────────────────────────────────────────────────────────────────────────
USERNAME = st.session_state["username"]
BG = t["bg"]

# ── API helpers ───────────────────────────────────────────────────────────────
@st.cache_data(ttl=30)
def get_stocks(_token: str):
    try:
        r = requests.get(f"{API_URL}/stocks", headers={"X-User-Token": _token}, timeout=8)
        return r.json().get("stocks", []) if r.ok else []
    except: return []

def add_stock(ticker):
    try:
        r = requests.post(
            f"{API_URL}/stocks/{ticker}",
            headers=auth_headers(), timeout=15
        )
        if r.ok: st.toast(f"✓ Added {ticker} to watchlist")
        else: st.toast(f"✗ {r.json().get('detail', 'Error')}")
    except Exception as e:
        st.toast(f"Error: {e}")
    get_stocks.clear()

def remove_stock(ticker):
    try: requests.delete(f"{API_URL}/stocks/{ticker}", headers=auth_headers(), timeout=5)
    except: pass
    get_stocks.clear()

def refresh_stock(ticker):
    try: requests.post(f"{API_URL}/stocks/{ticker}/refresh", headers=auth_headers(), timeout=15)
    except: pass
    get_stocks.clear()

@st.cache_data(ttl=300)
def get_history(ticker):
    try:
        r = requests.get(f"{API_URL}/stocks/{ticker}/history", timeout=12)
        return r.json().get("history", []) if r.ok else []
    except: return []

def search_api(q):
    if not q or len(q) < 2: return []
    try:
        r = requests.get(f"{API_URL}/search", params={"q": q}, timeout=6)
        return r.json().get("results", []) if r.ok else []
    except: return []

@st.cache_data(ttl=90)
def get_indices():
    try:
        r = requests.get(f"{API_URL}/market-indices", timeout=8)
        return r.json().get("indices", []) if r.ok else []
    except: return []

@st.cache_data(ttl=600)
def get_stock_news(ticker):
    try:
        r = requests.get(f"{API_URL}/stocks/{ticker}/news", timeout=8)
        return r.json().get("news", []) if r.ok else []
    except: return []

@st.cache_data(ttl=60)
def get_portfolio_db(_token: str):
    try:
        r = requests.get(f"{API_URL}/portfolio", headers={"X-User-Token": _token}, timeout=5)
        return {h["ticker"]: {"shares": h["shares"], "buy": h["buy_price"]}
                for h in r.json().get("portfolio", [])} if r.ok else {}
    except: return {}

def save_holding_db(ticker, shares, buy):
    try:
        requests.post(f"{API_URL}/portfolio",
                      json={"ticker": ticker, "shares": shares, "buy_price": buy},
                      headers=auth_headers(), timeout=5)
    except: pass
    get_portfolio_db.clear()

def delete_holding_db(ticker):
    try:
        requests.delete(f"{API_URL}/portfolio/{ticker}", headers=auth_headers(), timeout=5)
    except: pass
    get_portfolio_db.clear()

# ── Session state init ────────────────────────────────────────────────────────
TOKEN = st.session_state["token"]
stocks = get_stocks(TOKEN)
df_stocks = pd.DataFrame(stocks) if stocks else pd.DataFrame()

if "sel_ticker" not in st.session_state:
    st.session_state["sel_ticker"] = df_stocks["ticker"].iloc[0] if not df_stocks.empty else None
if "search_input_key" not in st.session_state:
    st.session_state["search_input_key"] = ""


# ─────────────────────────────────────────────────────────────────────────────
# TOP NAVIGATION BAR
# ─────────────────────────────────────────────────────────────────────────────
h1, h2, h3, h4 = st.columns([2.2, 5.5, 2.3, 1.5])

with h1:
    st.markdown(f"""
    <div style="display:flex;align-items:center;gap:8px;padding-top:6px;">
      <span style="font-size:22px;">📈</span>
      <span style="font-size:22px;font-weight:900;letter-spacing:-1px;color:{t['text']};">
        Fin<span style="color:{t['primary']};">Pulse</span>
      </span>
      <span style="font-size:9px;color:{t['muted']};font-weight:800;letter-spacing:.08em;
                  text-transform:uppercase;margin-top:2px;">INDIA</span>
    </div>
    """, unsafe_allow_html=True)

with h2:
    q_val = st_keyup(
        "search", key="search_input_key",
        placeholder="🔍  Search stocks, indices, ETFs...",
        label_visibility="collapsed", debounce=300
    )

with h3:
    st.markdown(f"""
    <div style="display:flex;align-items:center;justify-content:flex-end;gap:10px;padding-top:4px;">
      <div style="background:{t['card']};border:1px solid {t['border']};border-radius:24px;
                  padding:5px 14px;display:flex;align-items:center;gap:8px;">
        <div style="width:26px;height:26px;border-radius:50%;background:linear-gradient(135deg,{t['primary']},{t['accent']});
                    display:flex;align-items:center;justify-content:center;
                    font-size:11px;font-weight:800;color:white;">
          {USERNAME[0].upper()}
        </div>
        <div>
          <div style="font-size:11px;font-weight:700;color:{t['text']};line-height:1.2;">
            {USERNAME}
          </div>
          <div style="font-size:9px;color:{t['muted']};font-weight:600;letter-spacing:.04em;">
            MEMBER
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

with h4:
    theme_icon = "☀️" if st.session_state["theme"] == "dark" else "🌙"
    if st.button(f"{theme_icon} Theme", use_container_width=True):
        st.session_state["theme"] = "light" if st.session_state["theme"] == "dark" else "dark"
        st.rerun()

# Search results dropdown
if q_val and len(q_val.strip()) >= 2:
    results = search_api(q_val.strip())
    if results:
        with st.container(border=True):
            st.markdown(
                f"<p style='font-size:10px;font-weight:800;letter-spacing:.08em;"
                f"color:{t['muted']};margin-bottom:8px;text-transform:uppercase;'>Search Results</p>",
                unsafe_allow_html=True
            )
            for r in results:
                sym = r["symbol"]; nm = (r.get("shortname") or sym)[:36]
                exch = r.get("exchDisp", "")
                c_inf, c_add, c_view = st.columns([6, 2, 2])
                with c_inf:
                    st.markdown(
                        f"<b style='color:{t['text']}'>{sym}</b> "
                        f"<span style='font-size:11px;color:{t['sub']};'>{nm} ({exch})</span>",
                        unsafe_allow_html=True
                    )
                with c_add:
                    if st.button("＋ Add", key=f"add_{sym}", use_container_width=True):
                        add_stock(sym)
                        st.session_state["sel_ticker"] = sym
                        st.session_state["search_input_key"] = ""
                        st.rerun()
                with c_view:
                    if st.button("View", key=f"vs_{sym}", use_container_width=True):
                        st.session_state["sel_ticker"] = sym
                        st.session_state["search_input_key"] = ""
                        st.rerun()
    else:
        st.caption("No results. Try a different ticker (e.g. RELIANCE.NS, TCS.NS)")

# ─────────────────────────────────────────────────────────────────────────────
# MARKET INDEX RIBBON
# ─────────────────────────────────────────────────────────────────────────────
st.markdown("<div style='margin:10px 0 6px;'></div>", unsafe_allow_html=True)
indices = get_indices()
if indices:
    cols = st.columns(len(indices))
    for i, idx in enumerate(indices):
        price = float(idx.get("price") or 0)
        change = float(idx.get("change") or 0)
        chg_pct = float(idx.get("change_pct") or 0)
        c_col = t["green"] if change >= 0 else t["red"]
        c_dim = t["green_dim"] if change >= 0 else t["red_dim"]
        sign = "+" if change >= 0 else ""
        with cols[i]:
            st.markdown(f"""
            <div style="background:{t['card']};border:1px solid {t['border']};border-radius:14px;
                        padding:10px 16px;text-align:center;">
              <div style="font-size:9px;color:{t['muted']};text-transform:uppercase;
                          font-weight:800;letter-spacing:.08em;margin-bottom:2px;">
                {idx.get('name','Index')}
              </div>
              <div style="font-size:17px;font-weight:800;color:{t['text']};line-height:1.2;">
                {price:,.2f}
              </div>
              <div style="font-size:11px;font-weight:700;color:{c_col};
                          background:{c_dim};border-radius:20px;
                          padding:2px 8px;display:inline-block;margin-top:2px;">
                {sign}{change:,.2f} ({sign}{chg_pct:.2f}%)
              </div>
            </div>
            """, unsafe_allow_html=True)

st.markdown("<hr>", unsafe_allow_html=True)

# ─────────────────────────────────────────────────────────────────────────────
# NIFTY SENTIMENT + WELCOME BANNER
# ─────────────────────────────────────────────────────────────────────────────
nifty_pct = 0.0
for idx in indices:
    if idx.get("symbol") == "^NSEI":
        nifty_pct = float(idx.get("change_pct") or 0); break

sentiment_label = "Upbeat Sentiment 📈" if nifty_pct >= 0 else "Cautious Sentiment 📉"
sentiment_color = t["green"] if nifty_pct >= 0 else t["red"]
nifty_dir = "bullish 🟢" if nifty_pct >= 0 else "bearish 🔴"

gainers = losers = 0
top_sect = "—"
if not df_stocks.empty:
    gainers = int((df_stocks["day_change_pct"].fillna(0) > 0).sum())
    losers  = int((df_stocks["day_change_pct"].fillna(0) < 0).sum())
    s_mode = df_stocks["sector"].dropna().mode()
    top_sect = s_mode.iloc[0] if not s_mode.empty else "—"

# ── Two-column layout ─────────────────────────────────────────────────────────
col_main, col_side = st.columns([7.2, 2.8])

with col_main:
    # Welcome + summary card
    st.markdown(f"""
    <div style="background:linear-gradient(135deg,{t['card']} 0%,{t['bg']} 100%);
                border:1px solid {t['border2']};border-radius:16px;
                padding:20px 26px;margin-bottom:18px;">
      <div style="display:flex;justify-content:space-between;align-items:flex-start;flex-wrap:wrap;gap:10px;">
        <div>
          <div style="font-size:20px;font-weight:800;color:{t['text']};margin-bottom:4px;">
            Welcome back, <span style="color:{t['primary']};">{USERNAME}</span> 👋
          </div>
          <div style="font-size:12.5px;color:{t['sub']};line-height:1.6;">
            Indian equities are showing a <strong style="color:{sentiment_color};">{nifty_dir}</strong>
            trend · NIFTY 50: <strong style="color:{sentiment_color};">{nifty_pct:+.2f}%</strong>
            {'·  Watchlist: ' + str(gainers) + ' ▲ / ' + str(losers) + ' ▼' if not df_stocks.empty else ' · Add stocks to your watchlist to get started.'}
            {'· Top Sector: <em>' + top_sect + '</em>' if top_sect != '—' else ''}
          </div>
        </div>
        <div style="text-align:right;">
          <div style="font-size:10px;font-weight:800;letter-spacing:.08em;
                      text-transform:uppercase;color:{t['muted']};margin-bottom:4px;">
            Market Sentiment
          </div>
          <div style="font-size:14px;font-weight:800;color:{sentiment_color};">
            {sentiment_label}
          </div>
          <div style="font-size:11px;color:{t['muted']};margin-top:2px;">
            {len(df_stocks)} stocks tracked
          </div>
        </div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # ── TABS ──────────────────────────────────────────────────────────────────
    tab1, tab2, tab3, tab4 = st.tabs(["📊  Dashboard", "⚖️  Compare", "🔍  Screener", "💼  Portfolio"])

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 1 — DASHBOARD
    # ══════════════════════════════════════════════════════════════════════════
    with tab1:
        if df_stocks.empty:
            st.markdown(f"""
            <div style="background:{t['card']};border:1px solid {t['border']};border-radius:16px;
                        padding:40px;text-align:center;margin-top:20px;">
              <div style="font-size:48px;margin-bottom:12px;">🔍</div>
              <div style="font-size:18px;font-weight:700;color:{t['text']};margin-bottom:8px;">
                Your watchlist is loading...
              </div>
              <div style="font-size:13px;color:{t['sub']};">
                Your pre-loaded stocks are being fetched. This may take a minute on first login.<br>
                Or use the search bar above to add a stock right now.
              </div>
            </div>
            """, unsafe_allow_html=True)
        else:
            valid_tickers = df_stocks["ticker"].tolist()
            if st.session_state.get("sel_ticker") not in valid_tickers:
                st.session_state["sel_ticker"] = valid_tickers[0]

            sel = st.session_state["sel_ticker"]
            fd  = df_stocks[df_stocks["ticker"] == sel].iloc[0]
            curr = fd.get("currency") or "INR"
            sym  = psym(curr)
            price = float(fd.get("current_price") or 0)
            chg   = float(fd.get("day_change_pct") or 0)
            hi52  = float(fd.get("high_52w") or 0)
            lo52  = float(fd.get("low_52w") or 0)
            chg_sign = "+" if chg >= 0 else ""
            chg_col  = t["green"] if chg >= 0 else t["red"]
            chg_dim  = t["green_dim"] if chg >= 0 else t["red_dim"]
            arrow    = "▲" if chg >= 0 else "▼"

            # ── Hero Stock Card ───────────────────────────────────────────────
            r_pe  = float(fd.get("pe_ratio") or 0)
            r_tgt = float(fd.get("target_price") or 0)
            r_hi  = float(fd.get("high_52w") or 0)
            r_lo  = float(fd.get("low_52w") or 0)
            upside_str = ""
            if r_tgt > 0 and price > 0:
                upside = (r_tgt - price) / price * 100
                upside_col = t["green"] if upside >= 0 else t["red"]
                upside_str = f"""
                <div style="background:{t['bg']};border:1px solid {t['border']};border-radius:10px;
                            padding:8px 14px;margin-top:10px;display:inline-block;">
                  <span style="font-size:9.5px;color:{t['muted']};font-weight:800;
                               text-transform:uppercase;letter-spacing:.07em;">Analyst Target</span><br>
                  <span style="font-size:14px;font-weight:800;color:{t['text']};">{sym}{r_tgt:,.2f}</span>
                  <span style="font-size:11px;font-weight:700;color:{upside_col};margin-left:6px;">
                    ({upside:+.1f}% upside)
                  </span>
                </div>"""

            st.markdown(f"""
            <div style="background:{t['card']};border:1px solid {t['border2']};
                        border-radius:16px;padding:22px 26px;margin-bottom:16px;">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;
                          flex-wrap:wrap;gap:16px;">
                <div>
                  <div style="font-size:9.5px;font-weight:800;letter-spacing:.1em;
                              text-transform:uppercase;color:{t['muted']};margin-bottom:4px;">
                    {fd.get('sector') or '—'}
                  </div>
                  <div style="font-size:19px;font-weight:800;color:{t['text']};margin-bottom:10px;">
                    {fd.get('name') or sel}
                    <span style="color:{t['muted']};font-size:13px;font-weight:600;">({sel})</span>
                  </div>
                  <div style="display:flex;align-items:center;gap:14px;flex-wrap:wrap;">
                    <span style="font-size:40px;font-weight:900;color:{t['text']};
                                letter-spacing:-1.5px;line-height:1;">
                      {sym}{price:,.2f}
                    </span>
                    <span style="background:{chg_dim};color:{chg_col};border-radius:24px;
                                padding:5px 14px;font-size:13px;font-weight:800;">
                      {arrow} {chg_sign}{chg:.2f}%
                    </span>
                  </div>
                  {upside_str}
                </div>
                <div style="text-align:right;">
                  <div style="font-size:9.5px;font-weight:800;letter-spacing:.08em;
                              text-transform:uppercase;color:{t['muted']};margin-bottom:6px;">
                    Analyst View
                  </div>
                  <div style="font-size:16px;font-weight:800;color:{t['text']};">
                    {rec_text(fd.get('recommendation',''))}
                  </div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── AI Copilot Card ───────────────────────────────────────────────
            r_pb  = float(fd.get("pb_ratio") or 0)
            r_roe = float(fd.get("roe") or 0) * 100
            v_str = f"trades at a P/E of {r_pe:.1f}" if r_pe > 0 else "has no trailing P/E listed"
            e_str = f"delivers an ROE of {r_roe:.1f}%" if r_roe != 0 else "has stable efficiency indicators"
            r_str = f"analyst consensus target is {sym}{r_tgt:,.2f}" if r_tgt > 0 else "no consensus target is priced in"

            st.markdown(f"""
            <div style="background:linear-gradient(135deg,{t['accent_dim']},{t['primary_dim']});
                        border:1px solid {t['border']};border-radius:14px;
                        padding:18px 22px;margin-bottom:16px;">
              <div style="display:flex;align-items:center;gap:8px;margin-bottom:10px;">
                <span style="font-size:18px;">🤖</span>
                <span style="font-size:11px;font-weight:800;letter-spacing:.07em;
                            color:{t['accent']};text-transform:uppercase;">FinPulse AI Copilot</span>
              </div>
              <div style="font-size:14px;font-weight:700;color:{t['text']};margin-bottom:8px;">
                Is {fd.get('name') or sel} a buy at {sym}{price:,.2f}?
              </div>
              <div style="font-size:12.5px;color:{t['sub']};line-height:1.65;">
                Operating in <strong>{fd.get('sector') or '—'}</strong>, this stock {v_str} and {e_str}.
                The {r_str}. It has traded between
                <strong>{sym}{r_lo:,.2f}</strong> and <strong>{sym}{r_hi:,.2f}</strong> over the past 52 weeks.
              </div>
            </div>
            """, unsafe_allow_html=True)

            # ── 52-week range bar ─────────────────────────────────────────────
            if hi52 > lo52 > 0:
                pos = max(0, min(100, (price - lo52) / (hi52 - lo52) * 100))
                bar_col = t["green"] if pos >= 50 else t["gold"] if pos >= 25 else t["red"]
                st.markdown(f"""
                <div style="background:{t['card']};border:1px solid {t['border']};
                            border-radius:14px;padding:16px 22px;margin-bottom:16px;">
                  <div style="display:flex;justify-content:space-between;margin-bottom:10px;">
                    <span style="font-size:9.5px;font-weight:800;letter-spacing:.09em;
                                text-transform:uppercase;color:{t['muted']};">52-Week Range</span>
                    <span style="font-size:11px;color:{bar_col};font-weight:700;">
                      {pos:.0f}% above 52W low
                    </span>
                  </div>
                  <div style="position:relative;background:{t['border']};border-radius:6px;height:6px;">
                    <div style="position:absolute;left:0;width:{pos}%;
                                background:linear-gradient(90deg,{t['green']},{t['primary']});
                                height:6px;border-radius:6px;"></div>
                    <div style="position:absolute;left:{pos}%;transform:translateX(-50%);
                                top:-5px;width:16px;height:16px;background:{t['text']};
                                border-radius:50%;border:2.5px solid {t['primary']};"></div>
                  </div>
                  <div style="display:flex;justify-content:space-between;margin-top:10px;">
                    <span style="font-size:12px;font-weight:700;color:{t['red']};">
                      {sym}{lo52:,.2f}
                    </span>
                    <span style="font-size:12px;font-weight:700;color:{t['green']};">
                      {sym}{hi52:,.2f}
                    </span>
                  </div>
                </div>
                """, unsafe_allow_html=True)

            # ── Key Financials ────────────────────────────────────────────────
            st.markdown(
                f"<p style='font-size:10px;font-weight:800;letter-spacing:.1em;"
                f"text-transform:uppercase;color:{t['muted']};margin:0 0 10px;'>Key Financials</p>",
                unsafe_allow_html=True
            )
            r1a, r1b, r1c, r1d = st.columns(4)
            r1a.metric("Market Cap", fmt_cr(fd.get("market_cap")))
            r1b.metric("P/E (TTM)", fmt_n(fd.get("pe_ratio")))
            r1c.metric("P/B Ratio", fmt_n(fd.get("pb_ratio")))
            r1d.metric("EPS (TTM)", fmt_price(fd.get("eps"), sym))

            r2a, r2b, r2c, r2d = st.columns(4)
            r2a.metric("ROE", fmt_pct(fd.get("roe")))
            r2b.metric("ROA", fmt_pct(fd.get("roce")))
            r2c.metric("Div Yield", fmt_div_yield(fd.get("dividend_yield")))
            r2d.metric("Beta", fmt_n(fd.get("beta"), 3))

            r3a, r3b, r3c, r3d = st.columns(4)
            vol = int(fd.get("volume") or 0); avg_vol = int(fd.get("avg_volume") or 0)
            r3a.metric("52W High", fmt_price(hi52, sym))
            r3b.metric("52W Low", fmt_price(lo52, sym))
            r3c.metric("Volume", f"{vol:,}" if vol else "—")
            r3d.metric("Avg Volume 3M", f"{avg_vol:,}" if avg_vol else "—")

            st.markdown("<hr>", unsafe_allow_html=True)

            # ── Price Chart ───────────────────────────────────────────────────
            hist = get_history(sel)
            if hist:
                df_h = pd.DataFrame(hist)
                df_h["date"] = pd.to_datetime(df_h["date"])
                df_h = df_h.ffill().fillna(0).sort_values("date").drop_duplicates("date")
                df_h["MA10"] = df_h["close"].rolling(10).mean()
                df_h["MA40"] = df_h["close"].rolling(40).mean()
                df_h["MA90"] = df_h["close"].rolling(90).mean()

                ctrl1, ctrl2 = st.columns([2.5, 4.5])
                with ctrl1:
                    ctype = st.radio("Type", ["Candlestick","Line"], index=1,
                                     horizontal=True, key=f"ctype_{sel}")
                with ctrl2:
                    trange = st.radio("Range", ["1W","1M","6M","1Y","5Y"], index=2,
                                      horizontal=True, key=f"trange_{sel}")

                ma1, ma2, ma3, _ = st.columns([1,1,1,5])
                show10 = ma1.checkbox("10D MA", key=f"ma10_{sel}")
                show40 = ma2.checkbox("40D MA", key=f"ma40_{sel}")
                show90 = ma3.checkbox("90D MA", key=f"ma90_{sel}")

                offsets = {
                    "1W": pd.Timedelta(days=7),   "1M": pd.DateOffset(months=1),
                    "6M": pd.DateOffset(months=6), "1Y": pd.DateOffset(years=1),
                    "5Y": pd.DateOffset(years=5)
                }
                end_d = df_h["date"].max()
                df_f  = df_h[df_h["date"] >= end_d - offsets[trange]].copy()

                if len(df_f) >= 2:
                    sp, ep = df_f.iloc[0]["close"], df_f.iloc[-1]["close"]
                    pct = ((ep - sp) / sp * 100) if sp else 0
                    c_p = t["green"] if pct >= 0 else t["red"]
                    st.markdown(
                        f"<div style='margin:4px 0 8px;'>"
                        f"<span style='font-size:24px;font-weight:800;color:{c_p};'>"
                        f"{'+' if pct>=0 else ''}{pct:.2f}%</span>"
                        f"<span style='font-size:12px;color:{t['sub']};margin-left:12px;'>"
                        f"{sym}{sp:,.2f} → {sym}{ep:,.2f} over {trange}</span></div>",
                        unsafe_allow_html=True
                    )

                if ctype == "Candlestick":
                    fig = make_subplots(rows=2, cols=1, shared_xaxes=True,
                                        row_heights=[0.72, 0.28], vertical_spacing=0.01)
                    fig.add_trace(plgo.Candlestick(
                        x=df_f["date"], open=df_f["open"], high=df_f["high"],
                        low=df_f["low"], close=df_f["close"], name="Price",
                        increasing_line_color=t["green"],
                        increasing_fillcolor="rgba(46,204,113,.15)",
                        decreasing_line_color=t["red"],
                        decreasing_fillcolor="rgba(231,76,60,.12)",
                    ), row=1, col=1)
                    vcols = [t["green"] if c >= o else t["red"]
                             for c, o in zip(df_f["close"], df_f["open"])]
                    fig.add_trace(plgo.Bar(
                        x=df_f["date"], y=df_f["volume"], name="Volume",
                        marker_color=vcols, opacity=0.55,
                        hovertemplate="Vol: %{y:,.0f}<extra></extra>"
                    ), row=2, col=1)
                    fig.update_layout(xaxis_rangeslider_visible=False, height=490)
                    fig.update_yaxes(tickformat=".2s", row=2, col=1,
                                     gridcolor=t["border"], tickfont=dict(color=t["sub"], size=10))
                    add_row = 1
                else:
                    y_min = df_f["close"].min() * 0.997
                    y_max = df_f["close"].max() * 1.003
                    fig = plgo.Figure()
                    fig.add_trace(plgo.Scatter(
                        x=df_f["date"], y=df_f["close"], mode="lines", name="Close",
                        line=dict(color=t["primary"], width=2.5),
                        fill="tozeroy",
                        fillcolor="rgba(79,142,247,.07)" if st.session_state["theme"]=="dark" else "rgba(37,99,235,.05)",
                        hovertemplate=f"%{{x|%d %b %Y}}<br><b>{sym}%{{y:,.2f}}</b><extra></extra>"
                    ))
                    fig.update_yaxes(range=[y_min, y_max])
                    fig.update_layout(height=400)
                    add_row = None

                ma_specs = [
                    (show10, "MA10", "10D MA", t["gold"]),
                    (show40, "MA40", "40D MA", t["primary"]),
                    (show90, "MA90", "90D MA", t["accent"]),
                ]
                for show, col_name, name, color in ma_specs:
                    if show:
                        tr = plgo.Scatter(
                            x=df_f["date"], y=df_f[col_name],
                            mode="lines", name=name,
                            line=dict(color=color, width=1.5, dash="dot")
                        )
                        if add_row: fig.add_trace(tr, row=add_row, col=1)
                        else: fig.add_trace(tr)

                fig.update_layout(
                    paper_bgcolor=BG, plot_bgcolor=BG,
                    margin=dict(l=0, r=0, t=8, b=0), hovermode="x unified",
                    legend=dict(orientation="h", y=1.04, x=1, xanchor="right",
                                bgcolor="rgba(0,0,0,0)", font=dict(size=11, color=t["sub"])),
                    xaxis=dict(gridcolor=t["border"], tickfont=dict(color=t["sub"], size=10), showline=False),
                    yaxis=dict(gridcolor=t["border"], tickfont=dict(color=t["sub"], size=10),
                               showline=False, tickprefix=sym),
                )
                st.plotly_chart(fig, use_container_width=True, key=f"chart_{sel}_{ctype}_{trange}")

                # Technical indicators
                st.markdown(
                    f"<p style='font-size:10px;font-weight:800;letter-spacing:.1em;"
                    f"text-transform:uppercase;color:{t['muted']};margin:14px 0 10px;'>"
                    "Technical Indicators</p>",
                    unsafe_allow_html=True
                )
                ti1, ti2, ti3 = st.columns(3)
                lp    = df_h.iloc[-1]["close"]
                ma50  = df_h["close"].rolling(50).mean().iloc[-1]
                ma200 = df_h["close"].rolling(200).mean().iloc[-1]
                ti1.metric("vs 50D MA",  f"{'↑ Above' if lp > ma50 else '↓ Below'}", f"MA50 = {sym}{ma50:.2f}")
                if pd.notnull(ma200) and ma200 > 0:
                    ti2.metric("vs 200D MA", f"{'↑ Above' if lp > ma200 else '↓ Below'}", f"MA200 = {sym}{ma200:.2f}")
                else:
                    ti2.metric("vs 200D MA", "—", "Insufficient data")
                delta = df_h["close"].diff()
                gain  = delta.clip(lower=0).rolling(14).mean()
                loss  = (-delta.clip(upper=0)).rolling(14).mean()
                rsi   = (100 - 100 / (1 + gain / loss)).iloc[-1]
                rsi_l = "Overbought 🔴" if rsi > 70 else ("Oversold 🟢" if rsi < 30 else "Neutral ⚪")
                ti3.metric("RSI (14)", f"{rsi:.1f}", rsi_l)
            else:
                st.info("📊 Historical data is loading. Please wait a moment and refresh.")

            # News
            news_items = get_stock_news(sel)
            if news_items:
                st.markdown("<hr>", unsafe_allow_html=True)
                st.markdown(
                    f"<p style='font-size:10px;font-weight:800;letter-spacing:.1em;"
                    f"text-transform:uppercase;color:{t['muted']};margin:14px 0 10px;'>Latest News</p>",
                    unsafe_allow_html=True
                )
                n_cols = st.columns(2)
                for i, item in enumerate(news_items):
                    title = item.get("title", ""); pub = item.get("publisher","Yahoo Finance")
                    link  = item.get("link","#")
                    with n_cols[i % 2]:
                        st.markdown(f"""
                        <a href="{link}" target="_blank" style="text-decoration:none;">
                          <div style="background:{t['card']};border:1px solid {t['border']};
                                      border-radius:12px;padding:14px 18px;margin-bottom:12px;
                                      height:100px;overflow:hidden;transition:border-color .2s;"
                               onmouseover="this.style.borderColor='{t['primary']}'"
                               onmouseout="this.style.borderColor='{t['border']}'">
                            <div style="font-size:9.5px;font-weight:800;color:{t['primary']};
                                        text-transform:uppercase;margin-bottom:5px;">{pub}</div>
                            <div style="font-size:13px;font-weight:600;color:{t['text']};
                                        line-height:1.45;">{title[:95]}{'...' if len(title)>95 else ''}</div>
                          </div>
                        </a>
                        """, unsafe_allow_html=True)

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 2 — COMPARE
    # ══════════════════════════════════════════════════════════════════════════
    with tab2:
        if df_stocks.empty:
            st.info("Add stocks to compare.")
        else:
            st.markdown(
                f"<p style='font-size:10px;font-weight:800;letter-spacing:.09em;"
                f"text-transform:uppercase;color:{t['muted']};margin:0 0 12px;'>"
                "1-Year Normalised Performance (Base = 100)</p>",
                unsafe_allow_html=True
            )
            pf = plgo.Figure()
            for i, tk in enumerate(df_stocks["ticker"].tolist()):
                h = get_history(tk)
                if not h: continue
                dh = pd.DataFrame(h)
                dh["date"] = pd.to_datetime(dh["date"])
                dh = dh[dh["date"] >= dh["date"].max() - pd.DateOffset(years=1)]
                if dh.empty or dh.iloc[0]["close"] == 0: continue
                dh["norm"] = dh["close"] / dh.iloc[0]["close"] * 100
                pf.add_trace(plgo.Scatter(
                    x=dh["date"], y=dh["norm"], mode="lines", name=tk,
                    line=dict(color=COLORS[i % len(COLORS)], width=2)
                ))
            pf.add_hline(y=100, line_dash="dot", line_color=t["border"])
            pf.update_layout(
                paper_bgcolor=BG, plot_bgcolor=BG, height=360,
                margin=dict(l=0,r=0,t=8,b=0), hovermode="x unified",
                xaxis=dict(gridcolor=t["border"], tickfont=dict(color=t["sub"], size=10)),
                yaxis=dict(gridcolor=t["border"], tickfont=dict(color=t["sub"], size=10), title="Index"),
                legend=dict(orientation="h", y=1.06, bgcolor="rgba(0,0,0,0)",
                            font=dict(color=t["sub"], size=11))
            )
            st.plotly_chart(pf, use_container_width=True, key="compare_perf")

            # Metric bar charts
            st.markdown(
                f"<p style='font-size:10px;font-weight:800;letter-spacing:.09em;"
                f"text-transform:uppercase;color:{t['muted']};margin:18px 0 12px;'>"
                "Key Metrics Comparison</p>",
                unsafe_allow_html=True
            )
            mc1, mc2 = st.columns(2)
            for i, (col, lbl, mult, sfx) in enumerate([
                ("pe_ratio","P/E Ratio",1,""), ("pb_ratio","P/B Ratio",1,""),
                ("roe","ROE",100,"%"), ("roce","ROA",100,"%")
            ]):
                vals = df_stocks[col].fillna(0) * mult
                bf = plgo.Figure(plgo.Bar(
                    x=df_stocks["ticker"], y=vals,
                    marker_color=[COLORS[j % len(COLORS)] for j in range(len(df_stocks))],
                    text=[f"{v:.1f}{sfx}" for v in vals],
                    textposition="outside", textfont=dict(size=11, color=t["text"])
                ))
                bf.update_layout(
                    title=dict(text=lbl, font=dict(size=12, color=t["sub"])),
                    paper_bgcolor=BG, plot_bgcolor=BG, height=240,
                    margin=dict(l=0,r=0,t=36,b=0), showlegend=False,
                    xaxis=dict(tickfont=dict(size=11, color=t["text"])),
                    yaxis=dict(gridcolor=t["border"], tickfont=dict(color=t["sub"], size=10),
                               rangemode="tozero")
                )
                (mc1 if i % 2 == 0 else mc2).plotly_chart(bf, use_container_width=True,
                                                             key=f"cmp_bar_{col}")

            # P/E vs ROE bubble
            st.markdown(
                f"<p style='font-size:10px;font-weight:800;letter-spacing:.09em;"
                f"text-transform:uppercase;color:{t['muted']};margin:14px 0 10px;'>"
                "P/E vs ROE (bubble size = Market Cap)</p>",
                unsafe_allow_html=True
            )
            bd = df_stocks.copy()
            bd["roe_pct"] = bd["roe"].fillna(0) * 100
            bd["sz"] = bd["market_cap"].fillna(0).clip(lower=1e10).apply(
                lambda x: max(16, min(70, x / 4e12))
            )
            bfig = plgo.Figure(plgo.Scatter(
                x=bd["pe_ratio"].fillna(0), y=bd["roe_pct"],
                mode="markers+text", text=bd["ticker"],
                textposition="top center", textfont=dict(size=11, color=t["text"]),
                marker=dict(size=bd["sz"],
                            color=[COLORS[i % len(COLORS)] for i in range(len(bd))],
                            opacity=.85, line=dict(color=BG, width=1.5)),
                hovertemplate="<b>%{text}</b><br>P/E: %{x:.1f}<br>ROE: %{y:.1f}%<extra></extra>"
            ))
            bfig.update_layout(
                paper_bgcolor=BG, plot_bgcolor=BG, height=360,
                margin=dict(l=0,r=0,t=8,b=0),
                xaxis=dict(title="P/E", gridcolor=t["border"],
                           tickfont=dict(color=t["sub"], size=10), rangemode="tozero"),
                yaxis=dict(title="ROE %", gridcolor=t["border"],
                           tickfont=dict(color=t["sub"], size=10))
            )
            st.plotly_chart(bfig, use_container_width=True, key="cmp_bubble")

            # Sector donut
            sec = df_stocks.groupby("sector").size().reset_index(name="n")
            sf = plgo.Figure(plgo.Pie(
                labels=sec["sector"], values=sec["n"], hole=.55,
                marker_colors=COLORS, textinfo="label+percent", textfont_size=12
            ))
            sf.update_layout(paper_bgcolor=BG, height=300, margin=dict(l=0,r=0,t=0,b=0), showlegend=False)
            st.plotly_chart(sf, use_container_width=True, key="cmp_sector_donut")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 3 — SCREENER
    # ══════════════════════════════════════════════════════════════════════════
    with tab3:
        if df_stocks.empty:
            st.info("Add stocks to use the screener.")
        else:
            f1, f2 = st.columns(2)
            with f1:
                pe_v = df_stocks["pe_ratio"].replace(0, float("nan")).dropna()
                pe_lo = 0.0; pe_hi = float(pe_v.max()) if not pe_v.empty else 100.0
                if pe_lo >= pe_hi: pe_hi = pe_lo + 1
                min_pe, max_pe = st.slider("P/E Range", pe_lo, pe_hi, (pe_lo, pe_hi))
                min_roe = st.slider("Min ROE (%)", 0., 50., 0., 0.5)
            with f2:
                min_mc = st.number_input("Min Market Cap (Cr ₹)", 0., step=100.)
                pb_v = df_stocks["pb_ratio"].replace(0, float("nan")).dropna()
                pb_hi = float(pb_v.max()) if not pb_v.empty else 20.0
                max_pb = st.slider("Max P/B", 0., max(pb_hi * 1.5, 20.), max(pb_hi * 1.5, 20.))

            filt = df_stocks[
                (df_stocks["pe_ratio"].fillna(0) >= min_pe) &
                (df_stocks["pe_ratio"].fillna(0) <= max_pe) &
                (df_stocks["roe"].fillna(0) * 100 >= min_roe) &
                (df_stocks["market_cap"].fillna(0) >= min_mc * 1e7) &
                (df_stocks["pb_ratio"].fillna(999) <= max_pb)
            ]
            if not filt.empty:
                d = filt[["ticker","name","sector","current_price","market_cap",
                           "pe_ratio","pb_ratio","roe","roce","dividend_yield","beta"]].copy()
                d["market_cap"]     = d["market_cap"].fillna(0) / 1e7
                d["roe"]            = d["roe"].fillna(0) * 100
                d["roce"]           = d["roce"].fillna(0) * 100
                d["dividend_yield"] = d["dividend_yield"].fillna(0) * 100
                d.columns = ["Ticker","Name","Sector","Price (₹)","MCap (Cr ₹)",
                             "P/E","P/B","ROE %","ROA %","Div Yield %","Beta"]
                d = d.round(2)
                st.dataframe(
                    d.style
                     .background_gradient(subset=["ROE %"], cmap="RdYlGn", vmin=0, vmax=30)
                     .background_gradient(subset=["P/E"], cmap="RdYlGn_r", vmin=5, vmax=50)
                     .format({"MCap (Cr ₹)": "{:,.0f}", "Price (₹)": "{:,.2f}"}),
                    use_container_width=True, hide_index=True
                )
                st.caption(f"{len(filt)} of {len(df_stocks)} stocks match the filters")
                try:
                    r = requests.get(f"{API_URL}/export-report",
                                     headers=auth_headers(), timeout=5)
                    if r.ok:
                        st.download_button("⬇ Export Watchlist CSV", data=r.content,
                                           file_name="finpulse.csv", mime="text/csv")
                except: pass
            else:
                st.info("No stocks match the current filters.")

    # ══════════════════════════════════════════════════════════════════════════
    # TAB 4 — PORTFOLIO
    # ══════════════════════════════════════════════════════════════════════════
    with tab4:
        portfolio = get_portfolio_db(TOKEN)

        if not df_stocks.empty:
            a1, a2, a3 = st.columns([2.5, 1.2, 1.3])
            pt  = a1.selectbox("Stock", df_stocks["ticker"].tolist(), key="pt")
            ps  = a2.number_input("Shares", min_value=1, step=1, key="ps")
            pbp = a3.number_input("Buy Price (₹)", min_value=0.01, step=0.01, key="pbp")
            if st.button("Add / Update Holding", use_container_width=True):
                save_holding_db(pt, float(ps), float(pbp))
                portfolio = get_portfolio_db(TOKEN)
                st.toast(f"✓ Saved {pt} holding")
                st.rerun()

        if portfolio:
            rows, t_inv, t_cur = [], 0, 0
            for tk, info in portfolio.items():
                row = df_stocks[df_stocks["ticker"] == tk] if not df_stocks.empty else pd.DataFrame()
                cp  = float(row["current_price"].values[0]) if not row.empty else 0.0
                sh, bp = info["shares"], info["buy"]
                inv = sh * bp; cur = sh * cp
                pnl = cur - inv
                pp  = (cp - bp) / bp * 100 if bp else 0
                t_inv += inv; t_cur += cur
                rows.append({
                    "Ticker": tk, "Shares": sh, "Buy (₹)": bp,
                    "LTP (₹)": round(cp, 2), "Invested (₹)": round(inv, 2),
                    "Current (₹)": round(cur, 2), "P&L (₹)": round(pnl, 2), "P&L %": round(pp, 2)
                })

            if rows:
                tp = t_cur - t_inv
                tpp = tp / t_inv * 100 if t_inv else 0
                sg = "+" if tp >= 0 else ""
                p1, p2, p3, p4 = st.columns(4)
                p1.metric("Invested",      f"₹{t_inv:,.2f}")
                p2.metric("Current Value", f"₹{t_cur:,.2f}")
                p3.metric("Total P&L",     f"{sg}₹{tp:,.2f}")
                p4.metric("Total Return",  f"{sg}{tpp:.2f}%")

                st.markdown("---")
                dh = pd.DataFrame(rows)
                st.dataframe(
                    dh.style.map(
                        lambda v: f"color:{t['green']}" if isinstance(v,(int,float)) and v>0
                                  else (f"color:{t['red']}" if isinstance(v,(int,float)) and v<0 else ""),
                        subset=["P&L (₹)", "P&L %"]
                    ),
                    use_container_width=True, hide_index=True
                )

                st.markdown(
                    f"<p style='font-size:10px;font-weight:800;letter-spacing:.1em;"
                    f"text-transform:uppercase;color:{t['muted']};margin:16px 0 8px;'>"
                    "Portfolio Allocation</p>", unsafe_allow_html=True
                )
                af = plgo.Figure(plgo.Pie(
                    labels=[r["Ticker"] for r in rows],
                    values=[r["Current (₹)"] for r in rows],
                    hole=.55, marker_colors=COLORS[:len(rows)],
                    textinfo="label+percent", textfont_size=12
                ))
                af.update_layout(paper_bgcolor=BG, height=300,
                                  margin=dict(l=0,r=0,t=8,b=0), showlegend=False)
                st.plotly_chart(af, use_container_width=True, key="port_alloc")

                rm = st.selectbox("Remove holding", ["— select —"] + [r["Ticker"] for r in rows])
                if rm != "— select —" and st.button("✕ Remove"):
                    delete_holding_db(rm)
                    st.rerun()
        else:
            st.markdown(f"""
            <div style="background:{t['card']};border:1px solid {t['border']};
                        border-radius:14px;padding:32px;text-align:center;margin-top:16px;">
              <div style="font-size:36px;margin-bottom:10px;">💼</div>
              <div style="font-size:15px;font-weight:700;color:{t['text']};margin-bottom:6px;">
                No holdings yet
              </div>
              <div style="font-size:12.5px;color:{t['sub']};">
                Add a stock from your watchlist above to start tracking P&L.
              </div>
            </div>
            """, unsafe_allow_html=True)


# ─────────────────────────────────────────────────────────────────────────────
# SIDEBAR / WATCHLIST PANEL
# ─────────────────────────────────────────────────────────────────────────────
with col_side:
    st.markdown(
        f"<p style='color:{t['primary']};font-size:10px;font-weight:800;"
        f"letter-spacing:.1em;margin:0 0 12px;text-transform:uppercase;'>"
        f"📋 Your Watchlist</p>",
        unsafe_allow_html=True
    )

    if not df_stocks.empty:
        for _, row in df_stocks.iterrows():
            tk    = row["ticker"]
            price = float(row.get("current_price") or 0)
            chg   = float(row.get("day_change_pct") or 0)
            nm    = (row.get("name") or tk)[:22]
            sym_s = psym(row.get("currency"))
            is_sel = (st.session_state.get("sel_ticker") == tk)
            c_chg = t["green"] if chg >= 0 else t["red"]
            chg_s = f"{'+'if chg>=0 else ''}{chg:.2f}%"
            bdr   = t["primary"] if is_sel else t["border"]
            bg    = t["primary_dim"] if is_sel else t["card"]

            st.markdown(f"""
            <div style="background:{bg};border:1px solid {bdr};border-radius:12px;
                        padding:10px 14px;margin-bottom:6px;transition:all .15s;">
              <div style="display:flex;justify-content:space-between;align-items:flex-start;">
                <div>
                  <div style="font-size:13px;font-weight:800;color:{t['text']};">{tk}</div>
                  <div style="font-size:10px;color:{t['muted']};margin-top:1px;">{nm}</div>
                </div>
                <div style="text-align:right;">
                  <div style="font-size:13px;font-weight:700;color:{t['text']};">{sym_s}{price:,.2f}</div>
                  <div style="font-size:11px;font-weight:700;color:{c_chg};">{chg_s}</div>
                </div>
              </div>
            </div>
            """, unsafe_allow_html=True)

            bc, dc = st.columns([2.5, 1.5])
            if bc.button("View →", key=f"sel_{tk}", use_container_width=True):
                st.session_state["sel_ticker"] = tk
                st.rerun()
            if dc.button("✕", key=f"del_{tk}", use_container_width=True):
                remove_stock(tk)
                if st.session_state.get("sel_ticker") == tk:
                    st.session_state["sel_ticker"] = None
                st.rerun()
    else:
        st.caption("Nothing tracked yet — stocks loading or add via search.")

    # Heatmap treemap
    if not df_stocks.empty:
        st.markdown("<hr>", unsafe_allow_html=True)
        st.markdown(
            f"<p style='font-size:10px;font-weight:800;letter-spacing:.09em;"
            f"text-transform:uppercase;color:{t['muted']};margin:12px 0 8px;'>"
            "Performance Heatmap</p>",
            unsafe_allow_html=True
        )
        hd = df_stocks.copy()
        hd["sector"]         = hd["sector"].fillna("Unknown")
        hd["day_change_pct"] = hd["day_change_pct"].fillna(0)
        hd["market_cap"]     = hd["market_cap"].fillna(1e9).clip(lower=1e9)
        try:
            fig_map = px.treemap(
                hd, path=[px.Constant("Watchlist"), "sector", "ticker"],
                values="market_cap", color="day_change_pct",
                color_continuous_scale="RdYlGn", color_continuous_midpoint=0,
                custom_data=["current_price", "day_change_pct"]
            )
            fig_map.update_traces(
                hovertemplate="<b>%{label}</b><br>₹%{customdata[0]:,.2f}<br>%{customdata[1]:+.2f}%<extra></extra>"
            )
            fig_map.update_layout(
                paper_bgcolor=BG, plot_bgcolor=BG, height=230,
                margin=dict(l=0,r=0,t=0,b=0), coloraxis_showscale=False
            )
            st.plotly_chart(fig_map, use_container_width=True,
                            config={"displayModeBar": False}, key="sidebar_heatmap")
        except Exception as e:
            st.caption(f"Heatmap unavailable: {e}")

    # Action buttons
    st.markdown("<hr>", unsafe_allow_html=True)
    cs, co = st.columns(2)
    if cs.button("↺ Sync All", use_container_width=True):
        if not df_stocks.empty:
            for tk in df_stocks["ticker"]:
                refresh_stock(tk)
        get_stocks.clear()
        st.rerun()
    if co.button("⎋ Sign Out", use_container_width=True):
        st.session_state["authenticated"] = False
        st.session_state["token"] = ""
        st.session_state["username"] = ""
        components.html("<script>localStorage.removeItem('fp_token_v2');</script>", height=0)
        st.rerun()
