import asyncio  # noqa
import io
from datetime import date, timedelta
from typing import List

import aiohttp  # noqa
import numpy as np
import pandas as pd
import requests
from sqlalchemy.orm import Session
from src import performance_metrics
from src.config import config
from src.db import crud

ESTIMATION_HORIZON = 225
REBALANCE_INTERVAL = 30


def split_by_rebalance_periods(df: pd.DataFrame, rebalance_dates: np.ndarray, estimation_horizon: int):
    # Split prices into chuncks for which to calculate portfolio weights.
    # Rebalance dates are the dates for which to rebalance the portfolio.
    # Estimation horizon are the number of observations to look back in history.
    # Note that this is greater than or equal to the number of days spanning the chunck
    date = rebalance_dates[0]
    chunks = []
    for date in rebalance_dates:
        chunk = df[:date]
        start_index = max(0, len(chunk) - estimation_horizon)
        chunks.append(chunk[start_index:])
    return chunks


def get_returns(prices):
    r = np.diff(prices, axis=0) / prices[:-1]
    r.index = prices.index[1:]
    return r


def get_rebalance_dates(start_date: np.datetime64, end_date: np.datetime64, rebalance_interval: int):
    # Calculate the rebalance dates based on the realance interval (in days)

    rebalance_dates = np.arange(start_date, end_date, dtype="M8[D]")
    return rebalance_dates[::rebalance_interval]


async def call_of_concord(aio_session, url: str, data: bytes):
    async with aio_session.post(url, json=data) as resp:
        return await resp.json()


def to_bytestring(array: np.ndarray):
    memfile = io.BytesIO()
    np.save(memfile, array)
    memfile.seek(0)
    return memfile.read()  # reset curser and read as bytestring


class PortfolioService:
    def __init__(self):
        self.backend_url = config.backend_url
        self.openfaas_url = config.openfaas_url

    def get_portfolio_fast(self, db: Session, tickers: List[str], end_date: date):
        url = f"{config.openfaas_url}/function/of-concord"

        prices = crud.retrieve_stocks(db, tickers=tickers, end_date=end_date)
        start_date = np.datetime64(prices.index[0], "D") + np.timedelta64(365, "D")
        observed_end_date = np.datetime64(prices.index[-1], "D")
        assert start_date < observed_end_date, "Not enough data to estimate portfolio"
        rebalance_dates = get_rebalance_dates(
            start_date=start_date, end_date=observed_end_date, rebalance_interval=REBALANCE_INTERVAL
        )
        chunks = split_by_rebalance_periods(prices, rebalance_dates, ESTIMATION_HORIZON)
        # async with aiohttp.ClientSession() as aio_session:
        #     aws = [call_of_concord(aio_session, url, to_bytestring(df.values)) for df in range(chunks)]
        #     weights = await asyncio.gather(*aws)  # where the magic happens

        weights = []
        for chunk in chunks:
            response = requests.post(
                url,
                data=to_bytestring(chunk.values),
            )
            weights.append(response.json()["weights"])

        returns = get_returns(prices)
        times = returns.index.values.astype("datetime64[D]")
        wealth_times, wealth_values = performance_metrics.get_wealth(np.array(weights), returns, times, rebalance_dates)

        from pdb import set_trace

        set_trace()
        return response.json()

    def get_portfolio(self, tickers: List[str], end_date):
        print(self.backend_url)
        response = requests.post(
            f"{self.backend_url}/portfolio",
            json={"tickers": tickers, "end_date": end_date},
        )

        return response.json()
