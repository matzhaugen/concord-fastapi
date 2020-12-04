from fastapi.testclient import TestClient
from src.main import app
import json
import pytest

client = TestClient(app)


@pytest.mark.parametrize("method", [("concord"), ("vanilla")])
def test_portfolio(method):
    response = client.post("/portfolio/",
                           json={"tickers": ["AA", "AXP"], "method": method})

    assert float(json.loads(response.json()['wealth_data'])[-1]['value']) > 1


def test_tickers():
    response = client.get("/tickers/")

    assert len(response.json()['tickers']) > 0
