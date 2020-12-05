import requests
from src.config import environment as env


class PortfolioService:
    def __init__(self):
        self.backend_url = env.backend_url

    def get_portfolio(self, tickers, end_date):

        response = requests.post(
            f"{self.backend_url}/portfolio",
            json={"tickers": tickers, "end_date": end_date},
        )

        return response.json()
