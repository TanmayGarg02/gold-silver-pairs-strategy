import pandas as pd
import numpy as np
from typing import Tuple


def compute_zscore(
    spread: pd.Series,
    window: int
) -> pd.Series:

    rolling_mean = spread.rolling(window=window).mean()
    rolling_std = spread.rolling(window=window).std()

    zscore = (spread - rolling_mean) / rolling_std
    return zscore


def generate_signals(
    zscore: pd.Series,
    entry_threshold: float,
    exit_threshold: float
) -> pd.Series:

    signal = pd.Series(index=zscore.index, data=0)

    signal[zscore > entry_threshold] = -1   # short spread
    signal[zscore < -entry_threshold] = 1   # long spread

    signal[abs(zscore) < exit_threshold] = 0

    return signal


def position_from_signal(
    signal: pd.Series
) -> pd.Series:

    position = signal.replace(to_replace=0, method="ffill")
    position = position.fillna(0)

    return position
