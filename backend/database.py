import sqlite3
from typing import List, Dict, Any

DB_PATH = "finpulse.db"

def get_connection():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tracked_tickers (
            ticker TEXT PRIMARY KEY
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS fundamental_data (
            ticker TEXT PRIMARY KEY,
            name TEXT,
            sector TEXT,
            market_cap REAL,
            pe_ratio REAL,
            eps REAL,
            current_price REAL,
            pb_ratio REAL,
            roe REAL,
            roce REAL,
            high_52w REAL,
            low_52w REAL,
            dividend_yield REAL,
            beta REAL,
            target_price REAL,
            recommendation TEXT,
            day_change_pct REAL,
            volume INTEGER,
            avg_volume INTEGER,
            currency TEXT,
            FOREIGN KEY (ticker) REFERENCES tracked_tickers (ticker) ON DELETE CASCADE
        )
    ''')

    cursor.execute('''
        CREATE TABLE IF NOT EXISTS historical_prices (
            ticker TEXT,
            date TEXT,
            open REAL,
            high REAL,
            low REAL,
            close REAL,
            volume INTEGER,
            PRIMARY KEY (ticker, date),
            FOREIGN KEY (ticker) REFERENCES tracked_tickers (ticker) ON DELETE CASCADE
        )
    ''')

    # Migration: add any missing columns to existing databases
    new_cols = [
        ("pb_ratio", "REAL"),
        ("roe", "REAL"),
        ("roce", "REAL"),
        ("high_52w", "REAL"),
        ("low_52w", "REAL"),
        ("dividend_yield", "REAL"),
        ("beta", "REAL"),
        ("target_price", "REAL"),
        ("recommendation", "TEXT"),
        ("day_change_pct", "REAL"),
        ("volume", "INTEGER"),
        ("avg_volume", "INTEGER"),
        ("currency", "TEXT"),
    ]
    for col_name, col_type in new_cols:
        try:
            cursor.execute(f"ALTER TABLE fundamental_data ADD COLUMN {col_name} {col_type}")
        except sqlite3.OperationalError:
            pass  # Column already exists

    conn.commit()
    conn.close()

def add_ticker(ticker: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO tracked_tickers (ticker) VALUES (?)", (ticker,))
    conn.commit()
    conn.close()

def remove_ticker(ticker: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("DELETE FROM tracked_tickers WHERE ticker = ?", (ticker,))
    cursor.execute("DELETE FROM fundamental_data WHERE ticker = ?", (ticker,))
    cursor.execute("DELETE FROM historical_prices WHERE ticker = ?", (ticker,))
    conn.commit()
    conn.close()

def get_all_tickers() -> List[str]:
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT ticker FROM tracked_tickers")
    tickers = [row[0] for row in cursor.fetchall()]
    conn.close()
    return tickers

FUNDAMENTAL_FIELDS = [
    "ticker", "name", "sector", "market_cap", "pe_ratio", "eps", "current_price",
    "pb_ratio", "roe", "roce", "high_52w", "low_52w",
    "dividend_yield", "beta", "target_price", "recommendation",
    "day_change_pct", "volume", "avg_volume", "currency"
]

def upsert_fundamental_data(ticker: str, data: Dict[str, Any]):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO fundamental_data (
            ticker, name, sector, market_cap, pe_ratio, eps, current_price,
            pb_ratio, roe, roce, high_52w, low_52w,
            dividend_yield, beta, target_price, recommendation,
            day_change_pct, volume, avg_volume, currency
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(ticker) DO UPDATE SET
            name=excluded.name,
            sector=excluded.sector,
            market_cap=excluded.market_cap,
            pe_ratio=excluded.pe_ratio,
            eps=excluded.eps,
            current_price=excluded.current_price,
            pb_ratio=excluded.pb_ratio,
            roe=excluded.roe,
            roce=excluded.roce,
            high_52w=excluded.high_52w,
            low_52w=excluded.low_52w,
            dividend_yield=excluded.dividend_yield,
            beta=excluded.beta,
            target_price=excluded.target_price,
            recommendation=excluded.recommendation,
            day_change_pct=excluded.day_change_pct,
            volume=excluded.volume,
            avg_volume=excluded.avg_volume,
            currency=excluded.currency
    ''', (
        ticker,
        data.get('name'),
        data.get('sector'),
        data.get('market_cap'),
        data.get('pe_ratio'),
        data.get('eps'),
        data.get('current_price'),
        data.get('pb_ratio'),
        data.get('roe'),
        data.get('roce'),
        data.get('high_52w'),
        data.get('low_52w'),
        data.get('dividend_yield'),
        data.get('beta'),
        data.get('target_price'),
        data.get('recommendation'),
        data.get('day_change_pct'),
        data.get('volume'),
        data.get('avg_volume'),
        data.get('currency'),
    ))
    conn.commit()
    conn.close()

def upsert_historical_prices(ticker: str, prices: List[Dict[str, Any]]):
    conn = get_connection()
    cursor = conn.cursor()
    for row in prices:
        cursor.execute('''
            INSERT INTO historical_prices (ticker, date, open, high, low, close, volume)
            VALUES (?, ?, ?, ?, ?, ?, ?)
            ON CONFLICT(ticker, date) DO UPDATE SET
                open=excluded.open,
                high=excluded.high,
                low=excluded.low,
                close=excluded.close,
                volume=excluded.volume
        ''', (
            ticker,
            row['date'],
            row['open'],
            row['high'],
            row['low'],
            row['close'],
            row['volume']
        ))
    conn.commit()
    conn.close()

def get_fundamental_data(ticker: str = None):
    conn = get_connection()
    cursor = conn.cursor()
    if ticker:
        cursor.execute("SELECT * FROM fundamental_data WHERE ticker = ?", (ticker,))
        row = cursor.fetchone()
        if row:
            columns = [column[0] for column in cursor.description]
            res = dict(zip(columns, row))
        else:
            res = None
    else:
        cursor.execute("SELECT * FROM fundamental_data")
        columns = [column[0] for column in cursor.description]
        res = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return res

def get_historical_prices(ticker: str):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute(
        "SELECT * FROM historical_prices WHERE ticker = ? ORDER BY date ASC",
        (ticker,)
    )
    columns = [column[0] for column in cursor.description]
    res = [dict(zip(columns, row)) for row in cursor.fetchall()]
    conn.close()
    return res
