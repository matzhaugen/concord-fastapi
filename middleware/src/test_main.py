from fastapi.testclient import TestClient
from src.main import app
import json

client = TestClient(app)


def test_portfolio():
    response = client.post("/portfolio/",
                           json={"tickers": ["AA", "AXP"]})

    assert float(json.loads(response.json()['wealth_data'])[-1]['value']) > 1


def test_tickers():
    response = client.get("/tickers/")

    assert len(response.json()['tickers']) > 0
