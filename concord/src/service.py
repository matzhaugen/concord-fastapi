import asyncio  # noqa
import io
from datetime import date, timedelta
from typing import Dict, List

import aiohttp  # noqa
import numpy as np
import pandas as pd
import requests
import ujson
from sqlalchemy.orm import Session
from src import performance_metrics
from src.config import config
from src.db import crud

ESTIMATION_HORIZON = 225
REBALANCE_INTERVAL = 30
# BACKEND_URL = f"{config.openfaas_url}/function/of-concord-fastapi"
# BACKEND_URL = f"{config.openfaas_url}/function/starlette-backend"
BACKEND_URL = f"{config.starlette_backend_url}/"


def split_by_rebalance_periods(
    df: pd.DataFrame, rebalance_dates: np.ndarray, estimation_horizon: int
):
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


def get_returns(prices: pd.DataFrame) -> pd.DataFrame:
    r = np.diff(prices, axis=0) / prices[:-1]
    r.index = prices.index[1:]
    return r


def get_rebalance_dates(
    start_date: np.datetime64, end_date: np.datetime64, rebalance_interval: int
):
    # Calculate the rebalance dates based on the realance interval (in days)

    rebalance_dates = np.arange(start_date, end_date, dtype="M8[D]")
    return rebalance_dates[::rebalance_interval]


async def call_of_concord(aio_session, url: str, data: Dict):
    async with aio_session.post(url, data=data) as resp:
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

    async def get_portfolio_async(
        self, db: Session, tickers: List[str], end_date: date
    ):

        # Fetch data
        prices = crud.retrieve_stocks(db, tickers=tickers, end_date=end_date)
        start_date = np.datetime64(prices.index[0], "D") + np.timedelta64(365, "D")
        observed_end_date = np.datetime64(prices.index[-1], "D")
        assert start_date < observed_end_date, "Not enough data to estimate portfolio"
        rebalance_dates = get_rebalance_dates(
            start_date, observed_end_date, REBALANCE_INTERVAL
        )
        chunks = split_by_rebalance_periods(prices, rebalance_dates, ESTIMATION_HORIZON)

        # call openfaas to calculate weights
        async with aiohttp.ClientSession() as aio_session:
            aws = [
                call_of_concord(aio_session, BACKEND_URL, to_bytestring(df.values))
                for df in chunks
            ]
            weights = await asyncio.gather(*aws)  # where the magic happens
        weights = [w["weights"] for w in weights]

        # calculate wealth growth
        returns = get_returns(prices)
        times = returns.index.values.astype("datetime64[D]")
        wealth_times, wealth_values = performance_metrics.get_wealth(
            np.array(weights), returns.values, times, rebalance_dates
        )

        # produce response
        wealth_srs = pd.Series(
            data=np.around(wealth_values, 3), name="value", index=wealth_times
        )

        weights_df = pd.DataFrame(data=weights, columns=tickers, index=rebalance_dates)
        weights_df.index = weights_df.index.strftime(date_format="%Y-%m-%d")

        response = {
            "wealth": ujson.loads(wealth_srs.to_json(orient="index")),
            "weights": ujson.loads(weights_df.to_json(orient="index")),
        }

        return response

    def get_portfolio_sync(
        self, db: Session, tickers: List[str], end_date: date
    ) -> Dict[str, List]:

        prices = crud.retrieve_stocks(db, tickers=tickers, end_date=end_date)
        start_date = np.datetime64(prices.index[0], "D") + np.timedelta64(365, "D")
        observed_end_date = np.datetime64(prices.index[-1], "D")
        assert start_date < observed_end_date, "Not enough data to estimate portfolio"
        rebalance_dates = get_rebalance_dates(
            start_date, observed_end_date, REBALANCE_INTERVAL
        )
        chunks = split_by_rebalance_periods(prices, rebalance_dates, ESTIMATION_HORIZON)

        weights = []
        for chunk in chunks:
            response = requests.post(
                BACKEND_URL,
                data=to_bytestring(chunk.values),
            )
            weights.append(response.json())
        weights = [w["weights"] for w in weights]
        returns = get_returns(prices)
        times = returns.index.values.astype("datetime64[D]")
        wealth_times, wealth_values = performance_metrics.get_wealth(
            np.array(weights), returns.values, times, rebalance_dates
        )

        wealth_srs = pd.Series(
            data=np.around(wealth_values, 3), name="value", index=wealth_times
        )

        weights_df = pd.DataFrame(data=weights, columns=tickers, index=rebalance_dates)
        weights_df.index = weights_df.index.strftime(date_format="%Y-%m-%d")

        final_response = {
            "wealth": ujson.loads(wealth_srs.to_json(orient="index")),
            "weights": ujson.loads(weights_df.to_json(orient="index")),
        }

        return final_response

    def get_portfolio_backend(self, tickers: List[str], end_date):
        print(self.backend_url)
        response = requests.post(
            f"{self.backend_url}/portfolio",
            json={"tickers": tickers, "end_date": end_date},
        )

        return response.json()
