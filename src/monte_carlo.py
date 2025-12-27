import numpy as np
import pandas as pd
from typing import Dict


def monte_carlo_simulation(
    returns: pd.Series,
    num_simulations: int = 1000
) -> Dict[str, np.ndarray]:

    simulated_equity = []

    returns = returns.dropna().values

    for _ in range(num_simulations):
        sampled_returns = np.random.choice(
            returns, size=len(returns), replace=True
        )
        equity = np.cumprod(1 + sampled_returns)
        simulated_equity.append(equity)

    simulated_equity = np.array(simulated_equity)

    final_returns = simulated_equity[:, -1] - 1

    max_drawdowns = []

    for equity in simulated_equity:
        peak = np.maximum.accumulate(equity)
        drawdown = (equity - peak) / peak
        max_drawdowns.append(drawdown.min())

    return {
        "final_returns": final_returns,
        "max_drawdowns": np.array(max_drawdowns)
    }
