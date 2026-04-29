"""
analytics.py — core portfolio analytics functions for equity-lab.

Functions take pandas DataFrames/Series and return numeric results.
No printing, no plotting, no I/O — pure analysis.
"""

import numpy as np
import pandas as pd


def daily_returns(prices: pd.DataFrame) -> pd.DataFrame:
    """Compute daily percentage returns from a price DataFrame."""
    return prices.pct_change()


def total_return(prices: pd.Series) -> float:
    """Total return over the full period, as a decimal (0.30 = 30%)."""
    return prices.iloc[-1] / prices.iloc[0] - 1


def annual_volatility(returns: pd.Series, periods_per_year: int = 252) -> float:
    """Annualized standard deviation of returns."""
    return returns.std() * np.sqrt(periods_per_year)


def sharpe_ratio(prices: pd.Series, periods_per_year: int = 252) -> float:
    """Simplified Sharpe: total return divided by annualized volatility.
    Note: omits the risk-free rate for simplicity."""
    returns = prices.pct_change()
    return total_return(prices) / annual_volatility(returns, periods_per_year)


def max_drawdown(prices: pd.Series) -> float:
    """Largest peak-to-trough decline, as a negative decimal."""
    running_max = prices.cummax()
    drawdown = (prices - running_max) / running_max
    return drawdown.min()


def summary_stats(prices: pd.DataFrame) -> pd.DataFrame:
    """Build a full summary table of metrics for each ticker.
    
    Args:
        prices: DataFrame with date index, one column per ticker.
    
    Returns:
        DataFrame with one row per ticker, columns for each metric.
    """
    returns = daily_returns(prices)
    
    summary = pd.DataFrame({
        "Total Return %": ((prices.iloc[-1] / prices.iloc[0] - 1) * 100).round(2),
        "Annual Vol %": (returns.std() * np.sqrt(252) * 100).round(2),
        "Sharpe": (
            (prices.iloc[-1] / prices.iloc[0] - 1)
            / (returns.std() * np.sqrt(252))
        ).round(2),
        "Max Drawdown %": (prices.apply(max_drawdown) * 100).round(2),
    })
    
    return summary