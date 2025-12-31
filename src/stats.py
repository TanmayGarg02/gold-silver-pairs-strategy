import numpy as np
import pandas as pd
from typing import Dict

import statsmodels.api as sm
from statsmodels.regression.linear_model import OLS
from statsmodels.tsa.stattools import coint, adfuller


def engle_granger_test(
    gold: pd.Series,
    silver: pd.Series
) -> Dict[str, float]:

    test_stat, p_value, _ = coint(gold, silver)

    return {
        "test_statistic": test_stat,
        "p_value": p_value
    }


def estimate_hedge_ratio(
    gold: pd.Series,
    silver: pd.Series
) -> float:

    silver_const = sm.add_constant(silver)
    model = OLS(gold, silver_const).fit()

    return model.params[1]


def compute_spread(
    gold: pd.Series,
    silver: pd.Series,
    hedge_ratio: float
) -> pd.Series:

    return gold - hedge_ratio * silver


def adf_test(
    series: pd.Series
) -> Dict[str, float]:

    result = adfuller(series, autolag="AIC")

    return {
        "adf_statistic": result[0],
        "p_value": result[1]
    }


def half_life(
    spread: pd.Series
) -> float:

    spread_lag = spread.shift(1)
    delta = spread - spread_lag

    spread_lag = spread_lag.dropna()
    delta = delta.dropna()

    model = OLS(delta, sm.add_constant(spread_lag)).fit()
    beta = model.params.iloc[1]

    return -np.log(2) / beta
