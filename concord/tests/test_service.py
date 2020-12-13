from datetime import date, timedelta

import numpy as np
import src.mock_db as db
from src import service


def test_get_rebalance_dates():
    start_date = np.datetime64("1990-01-01")
    end_date = np.datetime64("1995-01-01")
    rebalance_interval = 30
    rebalance_dates = service.get_rebalance_dates(start_date, end_date, rebalance_interval)
    assert np.all(np.diff(rebalance_dates).astype(int) == rebalance_interval)


def test_split_by_rebalance_periods():

    end_date = np.datetime64("1995-01-01")
    rebalance_dates = np.array([np.datetime64("1991-02-12"), np.datetime64("1991-05-01")])
    prices = db.get_data(tickers=["AA", "AXP"], end_date=end_date)
    estimation_horizon = 225
    chunks = service.split_by_rebalance_periods(prices, rebalance_dates, estimation_horizon)
    for rebalance_date, chunk in zip(rebalance_dates, chunks):
        assert chunk.shape[0] == estimation_horizon
        last_obs_date = np.datetime64(chunk.index[-1], "D")
        assert last_obs_date <= rebalance_date
        assert last_obs_date > (rebalance_date - np.timedelta64(3, "D"))  # to account for wwekends
