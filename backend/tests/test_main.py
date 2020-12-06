import numpy as np
import pandas as pd
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)
ERROR_TOL = 0.01


def test_portfolio():
    response = client.post("/portfolio", json={"tickers": ["AA", "AXP"], "end_date": "1993-01-01"})
    body = response.json()
    assert (pd.Series(body["wealth"]) >= 0).all()
    assert (pd.DataFrame(body["weights"]).T.sum(axis=1) - 1 < ERROR_TOL).all()


def gen_mock_data():
    mock_index = np.arange(np.datetime64("2009-01-01"), np.datetime64("2012-01-01"))
    stocks = [
        "AA",
        "AXP",
        "BA",
        "BAC",
        "CAT",
        "CSCO",
        "CVX",
        "DD",
        "DIS",
        "GE",
        "HD",
        "HPQ",
        "IBM",
        "INTC",
        "JNJ",
        "JPM",
        "KO",
        "MCD",
        "MMM",
        "MRK",
        "MSFT",
        "PFE",
        "PG",
        "T",
        "TRV",
        "UTX",
        "VZ",
        "WMT",
        "XOM",
    ]
    # generate fake data, straight line with some small noise
    sigma = 0.01
    mu = np.arange(len(mock_index)) / len(mock_index)
    mock_values = sigma * np.random.randn(len(mock_index), len(stocks)) + mu[:, None]
    mock_df = pd.DataFrame(data=mock_values, index=mock_index, columns=stocks)
    return mock_df


mock_df = gen_mock_data()
