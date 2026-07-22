import sqlite3
import hashlib
import random
import os
from typing import List, Dict, Any, Optional

# On HuggingFace Spaces: DB_DIR=/data (persistent volume)
# Locally: current directory
_db_dir = os.environ.get("DB_DIR", ".")
os.makedirs(_db_dir, exist_ok=True)
DB_PATH = os.path.join(_db_dir, "finpulse.db")

# 50 Nifty 50 stocks to randomly sample 20 from for new users
NIFTY_50_POOL = [
    "RELIANCE.NS", "TCS.NS", "HDFCBANK.NS", "INFY.NS", "ICICIBANK.NS",
    "HINDUNILVR.NS", "ITC.NS", "SBIN.NS", "BHARTIARTL.NS", "KOTAKBANK.NS",
    "LT.NS", "AXISBANK.NS", "ASIANPAINT.NS", "MARUTI.NS", "SUNPHARMA.NS",
    "TITAN.NS", "ULTRACEMCO.NS", "BAJFINANCE.NS", "NESTLEIND.NS", "WIPRO.NS",
    "HCLTECH.NS", "POWERGRID.NS", "NTPC.NS", "ONGC.NS", "TATAMOTORS.NS",
    "TATASTEEL.NS", "JSWSTEEL.NS", "ADANIENT.NS", "ADANIPORTS.NS", "COALINDIA.NS",
    "BPCL.NS", "TECHM.NS", "GRASIM.NS", "CIPLA.NS", "DRREDDY.NS",
    "EICHERMOT.NS", "HEROMOTOCO.NS", "BAJAJ-AUTO.NS", "BRITANNIA.NS", "DIVISLAB.NS",
    "APOLLOHOSP.NS", "BAJAJFINSV.NS", "SBILIFE.NS", "HDFCLIFE.NS", "UPL.NS",
    "TATACONSUM.NS", "HINDALCO.NS", "INDUSINDBK.NS", "M&M.NS", "LTIM.NS"
]

def get_connection():
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db():
    conn = get_connection()
    c = conn.cursor()

    # ── Users ────────────────────────────────────────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            user_id    TEXT PRIMARY KEY,
            username   TEXT NOT NULL UNIQUE,
            created_at TEXT DEFAULT (datetime('now'))
        )
    ''')

    # ── Per-user watchlist ────────────────────────────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_tickers (
            user_id  TEXT NOT NULL,
            ticker   TEXT NOT NULL,
            added_at TEXT DEFAULT (datetime('now')),
            PRIMARY KEY (user_id, ticker),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')

    # ── Per-user portfolio ────────────────────────────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS user_portfolio (
            user_id   TEXT NOT NULL,
            ticker    TEXT NOT NULL,
            shares    REAL NOT NULL,
            buy_price REAL NOT NULL,
            PRIMARY KEY (user_id, ticker),
            FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE
        )
    ''')

    # ── Global fundamental cache ─────────────────────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS fundamental_data (
            ticker           TEXT PRIMARY KEY,
            name             TEXT,
            sector           TEXT,
            market_cap       REAL,
            pe_ratio         REAL,
            eps              REAL,
            current_price    REAL,
            pb_ratio         REAL,
            roe              REAL,
            roce             REAL,
            high_52w         REAL,
            low_52w          REAL,
            dividend_yield   REAL,
            beta             REAL,
            target_price     REAL,
            recommendation   TEXT,
            day_change_pct   REAL,
            volume           INTEGER,
            avg_volume       INTEGER,
            currency         TEXT
        )
    ''')

    # ── Global historical prices cache ───────────────────────────────────────────
    c.execute('''
        CREATE TABLE IF NOT EXISTS historical_prices (
            ticker TEXT,
            date   TEXT,
            open   REAL,
            high   REAL,
            low    REAL,
            close  REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date)
        )
    ''')

    # Migration: add any missing columns to existing DBs
    _migrate(c)

    conn.commit()
    conn.close()


def _migrate(cursor):
    """Add new columns to old databases without recreating tables."""
    extra_cols = [
        ("fundamental_data", "pb_ratio", "REAL"),
        ("fundamental_data", "roe", "REAL"),
        ("fundamental_data", "roce", "REAL"),
        ("fundamental_data", "high_52w", "REAL"),
        ("fundamental_data", "low_52w", "REAL"),
        ("fundamental_data", "dividend_yield", "REAL"),
        ("fundamental_data", "beta", "REAL"),
        ("fundamental_data", "target_price", "REAL"),
        ("fundamental_data", "recommendation", "TEXT"),
        ("fundamental_data", "day_change_pct", "REAL"),
        ("fundamental_data", "volume", "INTEGER"),
        ("fundamental_data", "avg_volume", "INTEGER"),
        ("fundamental_data", "currency", "TEXT"),
    ]
    for table, col, col_type in extra_cols:
        try:
            cursor.execute(f"ALTER TABLE {table} ADD COLUMN {col} {col_type}")
        except sqlite3.OperationalError:
            pass  # column already exists


# ─────────────────────────────────────────────────────────────────────────────
# User Management
# ─────────────────────────────────────────────────────────────────────────────

def _make_user_id(username: str) -> str:
    """Derive a stable user_id from the username."""
    return hashlib.sha256(username.encode()).hexdigest()


def create_user(username: str) -> Dict[str, Any]:
    """
    Create a new user. Returns the user dict.
    Raises ValueError if username is already taken (case-insensitive check).
    """
    conn = get_connection()
    c = conn.cursor()

    # Case-insensitive uniqueness check (but store as-is)
    c.execute("SELECT username FROM users WHERE LOWER(username) = LOWER(?)", (username,))
    existing = c.fetchone()
    if existing:
        conn.close()
        raise ValueError(f"Username '{existing[0]}' is already taken. Please choose a different one.")

    user_id = _make_user_id(username)
    c.execute(
        "INSERT INTO users (user_id, username) VALUES (?, ?)",
        (user_id, username)
    )

    # Pre-allocate 20 random Nifty 50 stocks
    sample = random.sample(NIFTY_50_POOL, 20)
    for ticker in sample:
        c.execute(
            "INSERT OR IGNORE INTO user_tickers (user_id, ticker) VALUES (?, ?)",
            (user_id, ticker)
        )

    conn.commit()
    conn.close()
    return {"user_id": user_id, "username": username, "is_new": True}


def login_user(username: str) -> Dict[str, Any]:
    """
    Login an existing user by exact username (case-sensitive).
    Returns user dict or raises ValueError if not found.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, username FROM users WHERE username = ?", (username,))
    row = c.fetchone()
    conn.close()
    if not row:
        raise ValueError("Username not found. Did you mean to register?")
    return {"user_id": row[0], "username": row[1], "is_new": False}


def get_user_by_token(token: str) -> Optional[Dict[str, Any]]:
    """Look up a user by their token (= user_id = SHA-256 of username)."""
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT user_id, username FROM users WHERE user_id = ?", (token,))
    row = c.fetchone()
    conn.close()
    if not row:
        return None
    return {"user_id": row[0], "username": row[1]}


# ─────────────────────────────────────────────────────────────────────────────
# User Watchlist (Tickers)
# ─────────────────────────────────────────────────────────────────────────────

def get_user_tickers(user_id: str) -> List[str]:
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT ticker FROM user_tickers WHERE user_id = ? ORDER BY added_at", (user_id,))
    tickers = [row[0] for row in c.fetchall()]
    conn.close()
    return tickers


def add_user_ticker(user_id: str, ticker: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "INSERT OR IGNORE INTO user_tickers (user_id, ticker) VALUES (?, ?)",
        (user_id, ticker)
    )
    conn.commit()
    conn.close()


def remove_user_ticker(user_id: str, ticker: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM user_tickers WHERE user_id = ? AND ticker = ?", (user_id, ticker))
    conn.commit()
    conn.close()


# ─────────────────────────────────────────────────────────────────────────────
# Fundamental Data (global cache)
# ─────────────────────────────────────────────────────────────────────────────

FUNDAMENTAL_FIELDS = [
    "ticker", "name", "sector", "market_cap", "pe_ratio", "eps", "current_price",
    "pb_ratio", "roe", "roce", "high_52w", "low_52w",
    "dividend_yield", "beta", "target_price", "recommendation",
    "day_change_pct", "volume", "avg_volume", "currency"
]


def upsert_fundamental_data(ticker: str, data: Dict[str, Any]):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO fundamental_data (
            ticker, name, sector, market_cap, pe_ratio, eps, current_price,
            pb_ratio, roe, roce, high_52w, low_52w,
            dividend_yield, beta, target_price, recommendation,
            day_change_pct, volume, avg_volume, currency
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(ticker) DO UPDATE SET
            name=excluded.name, sector=excluded.sector,
            market_cap=excluded.market_cap, pe_ratio=excluded.pe_ratio,
            eps=excluded.eps, current_price=excluded.current_price,
            pb_ratio=excluded.pb_ratio, roe=excluded.roe, roce=excluded.roce,
            high_52w=excluded.high_52w, low_52w=excluded.low_52w,
            dividend_yield=excluded.dividend_yield, beta=excluded.beta,
            target_price=excluded.target_price, recommendation=excluded.recommendation,
            day_change_pct=excluded.day_change_pct, volume=excluded.volume,
            avg_volume=excluded.avg_volume, currency=excluded.currency
    ''', (
        ticker, data.get('name'), data.get('sector'), data.get('market_cap'),
        data.get('pe_ratio'), data.get('eps'), data.get('current_price'),
        data.get('pb_ratio'), data.get('roe'), data.get('roce'),
        data.get('high_52w'), data.get('low_52w'), data.get('dividend_yield'),
        data.get('beta'), data.get('target_price'), data.get('recommendation'),
        data.get('day_change_pct'), data.get('volume'), data.get('avg_volume'),
        data.get('currency'),
    ))
    conn.commit()
    conn.close()


def get_fundamental_data(ticker: str = None):
    conn = get_connection()
    c = conn.cursor()
    if ticker:
        c.execute("SELECT * FROM fundamental_data WHERE ticker = ?", (ticker,))
        row = c.fetchone()
        res = dict(zip([col[0] for col in c.description], row)) if row else None
    else:
        c.execute("SELECT * FROM fundamental_data")
        cols = [col[0] for col in c.description]
        res = [dict(zip(cols, row)) for row in c.fetchall()]
    conn.close()
    return res


def get_fundamental_data_for_user(user_id: str) -> List[Dict[str, Any]]:
    """Return fundamental data only for tickers in a user's watchlist."""
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        SELECT f.* FROM fundamental_data f
        INNER JOIN user_tickers ut ON f.ticker = ut.ticker
        WHERE ut.user_id = ?
        ORDER BY ut.added_at
    ''', (user_id,))
    cols = [col[0] for col in c.description]
    res = [dict(zip(cols, row)) for row in c.fetchall()]
    conn.close()
    return res


# ─────────────────────────────────────────────────────────────────────────────
# Historical Prices (global cache)
# ─────────────────────────────────────────────────────────────────────────────

def upsert_historical_prices(ticker: str, prices: List[Dict[str, Any]]):
    conn = get_connection()
    c = conn.cursor()
    for row in prices:
        c.execute('''
            INSERT INTO historical_prices (ticker, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, date) DO UPDATE SET
                open=excluded.open, high=excluded.high, low=excluded.low,
                close=excluded.close, volume=excluded.volume
        ''', (ticker, row['date'], row['open'], row['high'], row['low'],
              row['close'], row['volume']))
    conn.commit()
    conn.close()


def get_historical_prices(ticker: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT * FROM historical_prices WHERE ticker = ? ORDER BY date ASC",
        (ticker,)
    )
    cols = [col[0] for col in c.description]
    res = [dict(zip(cols, row)) for row in c.fetchall()]
    conn.close()
    return res


# ─────────────────────────────────────────────────────────────────────────────
# User Portfolio
# ─────────────────────────────────────────────────────────────────────────────

def upsert_portfolio_holding(user_id: str, ticker: str, shares: float, buy_price: float):
    conn = get_connection()
    c = conn.cursor()
    c.execute('''
        INSERT INTO user_portfolio (user_id, ticker, shares, buy_price)
        VALUES (?, ?, ?, ?)
        ON CONFLICT(user_id, ticker) DO UPDATE SET
            shares=excluded.shares, buy_price=excluded.buy_price
    ''', (user_id, ticker, shares, buy_price))
    conn.commit()
    conn.close()


def delete_portfolio_holding(user_id: str, ticker: str):
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM user_portfolio WHERE user_id = ? AND ticker = ?", (user_id, ticker))
    conn.commit()
    conn.close()


def get_portfolio(user_id: str) -> List[Dict[str, Any]]:
    conn = get_connection()
    c = conn.cursor()
    c.execute(
        "SELECT ticker, shares, buy_price FROM user_portfolio WHERE user_id = ?",
        (user_id,)
    )
    res = [{"ticker": r[0], "shares": r[1], "buy_price": r[2]} for r in c.fetchall()]
    conn.close()
    return res
