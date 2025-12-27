import pandas as pd
import numpy as np
from typing import Dict, Tuple

from src.stats import (
    estimate_hedge_ratio,
    compute_spread,
    half_life
)
from src.strategy import (
    compute_zscore,
    generate_signals,
    position_from_signal
)
from src.backtester import backtest_pairs_strategy, calculate_performance_metrics


def walk_forward_split(
    prices: pd.DataFrame,
    train_ratio: float = 0.7
) -> Tuple[pd.DataFrame, pd.DataFrame]:

    split_idx = int(len(prices) * train_ratio)

    train = prices.iloc[:split_idx]
    test = prices.iloc[split_idx:]

    return train, test


def run_walk_forward(
    prices: pd.DataFrame,
    z_window: int,
    entry_z: float,
    exit_z: float,
    transaction_cost: float,
    periods_per_year: int
) -> Dict[str, Dict[str, float]]:

    train, test = walk_forward_split(prices)

    # ---- IN SAMPLE ----
    hedge_ratio = estimate_hedge_ratio(
        train["gold"], train["silver"]
    )

    spread_train = compute_spread(
        train["gold"], train["silver"], hedge_ratio
    )

    z_train = compute_zscore(spread_train, z_window)
    signal_train = generate_signals(z_train, entry_z, exit_z)
    position_train = position_from_signal(signal_train)

    bt_train = backtest_pairs_strategy(
        train, position_train, hedge_ratio, transaction_cost
    )

    metrics_train = calculate_performance_metrics(
        bt_train["strategy_return"].dropna(),
        periods_per_year
    )

    # ---- OUT OF SAMPLE ----
    spread_test = compute_spread(
        test["gold"], test["silver"], hedge_ratio
    )

    z_test = compute_zscore(spread_test, z_window)
    signal_test = generate_signals(z_test, entry_z, exit_z)
    position_test = position_from_signal(signal_test)

    bt_test = backtest_pairs_strategy(
        test, position_test, hedge_ratio, transaction_cost
    )

    metrics_test = calculate_performance_metrics(
        bt_test["strategy_return"].dropna(),
        periods_per_year
    )

    return {
        "in_sample": metrics_train,
        "out_of_sample": metrics_test
    }
