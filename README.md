# Gold–Silver Statistical Arbitrage Strategy (MCX Futures)

This project implements a statistically grounded pairs trading strategy between
MCX Gold and Silver futures. The focus is on statistical validity, robustness,
and risk awareness rather than pure return maximization.

---

## Project Overview

The strategy exploits the long-term equilibrium relationship between Gold and
Silver prices using cointegration and mean reversion principles. Trades are
generated based on statistically significant deviations of the spread and are
validated using walk-forward analysis and Monte Carlo simulations.

---

## Project Structure

```text
gold_silver_strategy/
├── data/
│   ├── fetch_data.py              # Angel One SmartAPI data fetch script
│   ├── gold.csv                   # Historical Gold futures data
│   └── silver.csv                 # Historical Silver futures data
│
├── notebooks/
│   ├── 01_data_exploration.ipynb
│   ├── 02_statistical_tests.ipynb
│   ├── 03_backtest.ipynb
│   └── 04_validation.ipynb
│
├── src/
│   ├── data_loader.py
│   ├── stats.py
│   ├── strategy.py
│   ├── backtester.py
│   ├── validation.py
│   └── monte_carlo.py
│
├── results/
│   ├── figures/                   # Saved plots and diagrams
│   └── report.pdf                 # Final project report
│
├── .env                           # API credentials (not committed)
├── .env.example                   # Template for credentials
├── .gitignore
├── requirements.txt
└── README.md

```
---

## Data Source

Historical MCX Gold and Silver futures data is sourced using the Angel One
SmartAPI historical data endpoint, as provided in the assignment instructions.
Data is stored locally in CSV format to ensure reproducibility and to avoid
repeated API calls.

API credentials are loaded securely using environment variables and are not
hardcoded in the repository.

---

## Methodology

### 1. Data Analysis
- Price visualization
- Returns distribution analysis
- Rolling correlation
- Missing data checks

### 2. Statistical Validation
- Engle–Granger cointegration test
- Hedge ratio estimation using OLS
- Spread construction
- Stationarity testing using ADF
- Mean reversion speed estimation using half-life

### 3. Strategy Logic
- Z-score normalization of the spread
- Entry threshold at ±2 standard deviations
- Exit threshold at ±0.5 standard deviations
- Positions held until partial mean reversion

### 4. Backtesting
- Realistic execution with no lookahead bias
- Transaction cost modeling
- Performance metrics: Sharpe ratio, drawdown, Calmar ratio

### 5. Validation and Risk Assessment
- Walk-forward (in-sample vs out-of-sample) testing
- Monte Carlo simulations for tail-risk estimation
- Parameter robustness checks

---

## How to Run

### Install dependencies
pip install -r requirements.txt

### Configure API credentials
Create a `.env` file in the project root using `.env.example` as a reference.

### Fetch data (once API access is active)
cd data
python fetch_data.py

### Run notebooks
Execute notebooks in the following order:
1. 01_data_exploration.ipynb
2. 02_statistical_tests.ipynb
3. 03_backtest.ipynb
4. 04_validation.ipynb

---

## Notes

- No live trading or order placement is performed.
- The project emphasizes statistical correctness and robustness.
- All analysis is fully reproducible.

---

## Author

<Tanmay Garg>
