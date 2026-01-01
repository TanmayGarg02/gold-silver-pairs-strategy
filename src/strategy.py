import pandas as pd
import numpy as np
from typing import Tuple


# Compute rolling Z-score of the spread
def compute_zscore(
    spread: pd.Series,
    window: int
) -> pd.Series:

    rolling_mean = spread.rolling(window=window).mean()
    rolling_std = spread.rolling(window=window).std()

    zscore = (spread - rolling_mean) / rolling_std
    return zscore


# Generate entry and exit signals based on Z-score thresholds
def generate_signals(
    zscore: pd.Series,
    entry_threshold: float,
    exit_threshold: float,
    max_z: float = 3.0
) -> pd.Series:

    signal = pd.Series(index=zscore.index, data=0)

    # Entry signals
    signal[zscore > entry_threshold] = -1
    signal[zscore < -entry_threshold] = 1

    # Exit on mean reversion
    signal[abs(zscore) < exit_threshold] = 0

    # Stop loss on extreme divergence
    signal[abs(zscore) > max_z] = 0

    return signal

# Convert signals into persistent positions
def position_from_signal(
    signal: pd.Series
) -> pd.Series:

    position = signal.replace(to_replace=0, method="ffill")
    position = position.fillna(0)

    return position



def apply_capped_volatility_scaling(
    position: pd.Series,
    spread: pd.Series,
    vol_window: int,
    min_scale: float = 0.5,
    max_scale: float = 1.5
) -> pd.Series:

    spread_vol = spread.rolling(vol_window).std()
    target_vol = spread_vol.median()

    scale = target_vol / spread_vol
    scale = scale.clip(lower=min_scale, upper=max_scale)

    scaled_position = position * scale
    return scaled_position.fillna(0)

