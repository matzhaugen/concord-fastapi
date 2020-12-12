from datetime import date
from typing import List

import requests
from sqlalchemy.orm import Session
from src.config import config
from src.db import crud


class PortfolioService:
    def __init__(self):
        self.backend_url = config.backend_url
        self.openfaas_url = config.openfaas_url

    def get_portfolio_fast(self, db: Session, tickers: List[str], end_date: date):
        stocks_df = crud.retrieve_stocks(db, tickers=tickers, end_date=end_date)

        response = requests.post(
            f"{self.openfaas_url}/portfolio",
            json={"tickers": tickers, "end_date": end_date},
        )

        return response.json()

    def get_portfolio(self, tickers, end_date):
        print(self.backend_url)
        response = requests.post(
            f"{self.backend_url}/portfolio",
            json={"tickers": tickers, "end_date": end_date},
        )

        return response.json()
