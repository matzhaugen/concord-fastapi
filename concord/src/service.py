import asyncio  # noqa
import io
from datetime import date
from typing import List

import aiohttp  # noqa
import numpy as np
import requests
from sqlalchemy.orm import Session
from src.config import config
from src.db import crud


def split_by_rebalance_periods(df):
    return [df, df]  # mock


async def call_of_concord(aio_session, url, data):
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
        chunks = split_by_rebalance_periods(prices)
        # async with aiohttp.ClientSession() as aio_session:
        #  aws = [call_of_concord(aio_session, url, {"data": i}) for i in range(10)]
        #  resp_list = await asyncio.gather(*aws)  # where the magic happens
        #  final_resp = {f"{i}": res for i, res in enumerate(resp_list)}
        data = to_bytestring(prices.values)
        response = requests.post(
            f"{self.openfaas_url}/function/of-concord",
            data=data,
        )
        from pdb import set_trace

        set_trace()
        return response.json()

    def get_portfolio(self, tickers, end_date):
        print(self.backend_url)
        response = requests.post(
            f"{self.backend_url}/portfolio",
            json={"tickers": tickers, "end_date": end_date},
        )

        return response.json()
