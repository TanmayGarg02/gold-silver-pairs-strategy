import pandas as pd
import numpy as np
from typing import Dict


def backtest_pairs_strategy(
    prices: pd.DataFrame,
    position: pd.Series,
    hedge_ratio: float,
    transaction_cost: float = 0.0
) -> pd.DataFrame:

    gold_ret = prices["gold"].pct_change()
    silver_ret = prices["silver"].pct_change()

    spread_return = gold_ret - hedge_ratio * silver_ret

    strategy_return = position.shift(1) * spread_return

    trades = position.diff().abs()
    strategy_return -= trades * transaction_cost

    equity_curve = (1 + strategy_return).cumprod()

    result = pd.DataFrame({
        "strategy_return": strategy_return,
        "equity_curve": equity_curve,
        "position": position
    })

    return result


def calculate_performance_metrics(
    returns: pd.Series,
    periods_per_year: int
) -> Dict[str, float]:

    total_return = (1 + returns).prod() - 1

    annualized_return = (1 + total_return) ** (
        periods_per_year / len(returns)
    ) - 1

    annualized_vol = returns.std() * np.sqrt(periods_per_year)

    sharpe_ratio = (
        annualized_return / annualized_vol
        if annualized_vol != 0 else np.nan
    )

    cumulative = (1 + returns).cumprod()
    peak = cumulative.cummax()
    drawdown = (cumulative - peak) / peak
    max_drawdown = drawdown.min()

    calmar_ratio = (
        annualized_return / abs(max_drawdown)
        if max_drawdown != 0 else np.nan
    )

    return {
        "Total Return": total_return,
        "Annualized Return": annualized_return,
        "Sharpe Ratio": sharpe_ratio,
        "Max Drawdown": max_drawdown,
        "Calmar Ratio": calmar_ratio
    }
