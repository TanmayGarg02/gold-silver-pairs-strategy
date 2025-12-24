import pandas as pd
from typing import Tuple


def load_price_csv(
    filepath: str,
    price_col: str = "close",
    time_col: str = "timestamp"
) -> pd.DataFrame:


    df = pd.read_csv(filepath)
    df[time_col] = pd.to_datetime(df[time_col])
    df = df.sort_values(time_col)
    df = df[[time_col, price_col]]
    df = df.set_index(time_col)
    df = df[~df.index.duplicated(keep="first")]

    return df


def align_price_series(
    gold_df: pd.DataFrame,
    silver_df: pd.DataFrame
) -> pd.DataFrame:

    df = pd.concat(
        [gold_df.rename(columns={"close": "gold"}),
         silver_df.rename(columns={"close": "silver"})],
        axis=1
    )

    # Drop timestamps where either price is missing
    df = df.dropna()

    return df


def load_and_align_prices(
    gold_path: str,
    silver_path: str
) -> pd.DataFrame:
    
    gold = load_price_csv(gold_path)
    silver = load_price_csv(silver_path)

    prices = align_price_series(gold, silver)

    return prices
