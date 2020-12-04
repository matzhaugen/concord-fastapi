import requests

BACKEND_URL = "http://backend:80"


def get_portfolio(tickers, end_date):

    response = requests.post(f"{BACKEND_URL}/portfolio", 
        json={"tickers": tickers, "end_date": end_date})

    return response
