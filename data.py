"""
data.py — fetch market data and read/write it to SQLite.

External world (yfinance, sqlite) lives here.
Analytics code in analytics.py never touches the network or disk.
"""

import sqlite3
import pandas as pd
import yfinance as yf


DB_PATH = "equity_lab.db"


def fetch_prices(tickers: list[str], start: str, end: str) -> pd.DataFrame:
    """Pull daily prices from Yahoo Finance for a list of tickers.
    
    Args:
        tickers: e.g. ["AAPL", "MSFT", "VOO"]
        start: ISO date string, e.g. "2025-01-01"
        end: ISO date string, exclusive, e.g. "2026-01-01"
    
    Returns:
        Long-format DataFrame with columns:
        date, ticker, open, high, low, close, volume
    """
    raw = yf.download(tickers, start=start, end=end, progress=False)
    
    # Reshape from wide multi-index to long format
    long = raw.stack(level=1, future_stack=True).reset_index()
    long.columns = ["Date", "Ticker", "Close", "High", "Low", "Open", "Volume"]
    long = long[["Date", "Ticker", "Open", "High", "Low", "Close", "Volume"]]
    
    return long


def save_prices(prices: pd.DataFrame, db_path: str = DB_PATH) -> int:
    """Write a long-format prices DataFrame to SQLite.
    
    Returns:
        Number of rows written.
    """
    conn = sqlite3.connect(db_path)
    prices.to_sql("prices", conn, if_exists="replace", index=False)
    conn.close()
    return len(prices)


def load_prices(
    tickers: list[str] | None = None,
    db_path: str = DB_PATH,
) -> pd.DataFrame:
    """Load prices from SQLite in wide format (date index, ticker columns).
    
    Args:
        tickers: optional filter; if None, returns all tickers in the DB.
    
    Returns:
        Wide DataFrame with date index and one column per ticker (close prices).
    """
    conn = sqlite3.connect(db_path)
    
    if tickers is None:
        query = "SELECT date, ticker, close FROM prices ORDER BY date"
        long = pd.read_sql(query, conn, parse_dates=["Date"])
    else:
        # Parameterized query — safe against SQL injection, good habit even here
        placeholders = ",".join("?" for _ in tickers)
        query = f"SELECT date, ticker, close FROM prices WHERE ticker IN ({placeholders}) ORDER BY date"
        long = pd.read_sql(query, conn, params=tickers, parse_dates=["Date"])
    
    conn.close()
    
    # Pivot from long (date, ticker, close) to wide (date index, ticker columns)
    wide = long.pivot(index="Date", columns="Ticker", values="Close")
    return wide


def refresh_database(tickers: list[str], start: str, end: str, db_path: str = DB_PATH) -> int:
    """Convenience: fetch and save in one call. Returns rows written."""
    prices = fetch_prices(tickers, start, end)
    return save_prices(prices, db_path)


query = "SELECT date, ticker, close FROM prices ORDER BY date"
long = pd.read_sql(query, conn, parse_dates=["Date"])
long.head()