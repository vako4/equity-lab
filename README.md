# equity-lab

A Python toolkit for analyzing the risk-adjusted performance of US equities and constructing portfolios from screened universes. Built around a local SQLite layer so analysis is fast, reproducible, and offline-friendly.

---

## What it does

- **Pulls** historical price data from Yahoo Finance for any list of tickers
- **Stores** prices in a local SQLite database (queryable with plain SQL)
- **Computes** standard performance metrics: total return, annualized volatility, Sharpe ratio, maximum drawdown
- **Compares** individual stocks against a benchmark (e.g., VOO) and against equal-weighted portfolios
- **Reveals** correlation structure inside a basket of stocks — useful for spotting hidden concentration risk

The reference dataset throughout the demo notebooks is the "Magnificent 7" (AAPL, MSFT, GOOGL, AMZN, META, NVDA, TSLA) plus VOO as an S&P 500 benchmark, over calendar year 2025.

---

## Sample finding

Across 2025, daily-return correlations among the Mag 7 ranged from **0.42 to 0.66**, with the MSFT / META / AMZN / NVDA cluster correlating particularly tightly (0.64–0.66). An equal-weighted Mag 7 portfolio is therefore far less diversified than the seven distinct tickers suggest — a single "US mega-cap tech" factor explains most of the joint variance, and the highest-Sharpe individual name (GOOGL, Sharpe ≈ 2.0) outperformed the equal-weight portfolio on a risk-adjusted basis.

---

## Project structure

```
equity-lab/
├── data.py                    # fetch / save / load market data (yfinance + SQLite)
├── analytics.py               # pure analysis: returns, volatility, Sharpe, drawdown
├── requirements.txt
├── 01_first_look.ipynb        # initial exploration, single-stock and multi-stock charts
├── 02_sqlite_setup.ipynb      # build the local price database
├── 03_analysis_demo.ipynb     # summary statistics across the Mag 7 + VOO
└── 04_full_pipeline.ipynb     # end-to-end demo: load → analyze → output, in 5 lines
```

Data lives in `equity_lab.db` (SQLite, gitignored). Regenerate it any time by calling `refresh_database()` from `data.py`.

---

## Getting started

```bash
git clone https://github.com/vako4/equity-lab.git
cd equity-lab
pip install -r requirements.txt
```

Then in a Jupyter notebook:

```python
from data import refresh_database, load_prices
from analytics import summary_stats

TICKERS = ["AAPL", "MSFT", "GOOGL", "AMZN", "META", "NVDA", "TSLA", "VOO"]

# One-time fetch + save to local SQLite
refresh_database(TICKERS, start="2025-01-01", end="2026-01-01")

# Load and analyze
prices = load_prices(TICKERS)
summary_stats(prices).sort_values("Sharpe", ascending=False)
```

Output:

| Ticker | Total Return % | Annual Vol % | Sharpe | Max Drawdown % |
|--------|---------------:|-------------:|-------:|---------------:|
| GOOGL  | 65.88          | 32.41        | 2.03   | -29.81         |
| NVDA   | 34.88          | 49.64        | 0.70   | -36.88         |
| MSFT   | 16.39          | 24.30        | 0.67   | -20.56         |
| AAPL   | 11.99          | 32.46        | 0.37   | -30.22         |
| TSLA   | 18.57          | 63.31        | 0.29   | -48.19         |
| META   | 10.50          | 38.03        | 0.28   | -34.15         |
| AMZN   | 4.81           | 34.49        | 0.14   | -30.88         |

---

## Design notes

- **Data and analysis are kept separate.** `data.py` handles the outside world (network calls, SQLite I/O); `analytics.py` is pure math. Either layer can be swapped without touching the other.
- **SQLite is intentional.** Querying a local database with SQL is closer to real production analytics work than running everything against a remote API every time. It also makes runs reproducible across machines and over time.
- **Long format on disk, wide format in memory.** Prices are stored long (one row per `date × ticker`) because that's the natural shape for SQL; analysis pivots to wide (date index, one column per ticker) because that's the natural shape for pandas.
- **Sharpe is simplified.** Calculated as total return / annualized volatility, omitting the risk-free rate. Adequate for relative comparison; would refine for absolute claims.

---

## Limitations and intended next steps

- Data quality reflects whatever Yahoo Finance returns. Survivorship bias, restatements, and missing values are not corrected.
- The screener layer (filtering by P/E, ROE, debt/equity, etc.) is on the roadmap and not yet implemented.
- Correlation analysis and the equal-weight portfolio backtest live in notebooks rather than `analytics.py`. Both should move into the module once the API stabilizes.
- No automated tests yet; planned for the next iteration.

---

## Author

Valerian Meipariani · Data Analyst at Liberty Bank, Tbilisi · [LinkedIn](https://www.linkedin.com/in/vako-meipariani)