from fastapi.testclient import TestClient

from src.main import app
import pandas as pd
import numpy as np

client = TestClient(app)


def gen_mock_data():
    mock_index = np.arange(np.datetime64('2009-01-01'), np.datetime64('2012-01-01'))
    stocks = ['AA', 'AXP', 'BA', 'BAC', 'CAT', 'CSCO', 'CVX', 'DD',
              'DIS', 'GE', 'HD', 'HPQ', 'IBM', 'INTC', 'JNJ', 'JPM', 'KO', 'MCD',
              'MMM', 'MRK', 'MSFT', 'PFE', 'PG', 'T', 'TRV', 'UTX', 'VZ', 'WMT',
              'XOM']
    # generate fake data, straight line with some small noise
    sigma = 0.01
    mu = np.arange(len(mock_index)) / len(mock_index)
    mock_values = sigma * np.random.randn(len(mock_index), len(stocks)) + mu[:, None]
    mock_df = pd.DataFrame(data=mock_values, index=mock_index, columns=stocks)
    return mock_df


mock_df = gen_mock_data()


def test_regularize():
    response = client.post("/concord/",
                           json={"covariance": [[1, 0], [0, 1]], "alpha": 0.2})
    assert response.status_code == 200
    assert set(response.json().keys()).intersection(['regularized'])


def test_weights():
    # prices = mock_df.loc[:'2009-09', ['AA', 'AXP']].to_numpy()
    prices = mock_df.loc[:'2009-09', :].to_numpy()
    returns = np.diff(prices, axis=0) / prices[:-1, :]
    response = client.post("/weights",
                           json={"returns": returns.tolist()})
    assert "weights" in response.json()
