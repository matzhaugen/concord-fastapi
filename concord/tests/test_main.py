import pandas as pd
from fastapi.testclient import TestClient
from src.main import app

client = TestClient(app)
ERROR_TOL = 0.01


def test_fast_portfolio():
    response = client.post("/fast-portfolio", json={"tickers": ["AA", "AXP"], "endDate": "1991-01-01"})
    body = response.json()
    assert (pd.Series(body["wealth"]) >= 0).all()
    assert (pd.DataFrame(body["weights"]).T.sum(axis=1) - 1 < ERROR_TOL).all()


def test_portfolio():
    response = client.post("/portfolio", json={"tickers": ["AA", "AXP"], "endDate": "1993-01-01"})
    body = response.json()
    assert (pd.Series(body["wealth"]) >= 0).all()
    assert (pd.DataFrame(body["weights"]).T.sum(axis=1) - 1 < ERROR_TOL).all()


def test_tickers():
    response = client.get("/tickers")

    assert len(response.json()["tickers"]) > 0
