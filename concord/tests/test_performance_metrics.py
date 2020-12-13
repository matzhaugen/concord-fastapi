from datetime import date

import numpy as np
from src import mock_db, performance_metrics, service


def test_get_wealth():
    end_date = date(1995, 1, 1)
    rebalance_dates = np.array(
        [
            np.datetime64("1991-02-12", "D"),
            np.datetime64("1991-05-01", "D"),
        ]
    )
    prices = mock_db.get_data(tickers=["AA", "AXP"], end_date=end_date)
    returns = service.get_returns(prices)
    weights = np.array([[0.5, 0.5], [0.5, 0.5]])
    times = returns.index.values.astype("datetime64[D]")

    wealth_times, wealth_values = performance_metrics.get_wealth(weights, returns.values, times, rebalance_dates)

    assert len(wealth_values) == len(wealth_times)
