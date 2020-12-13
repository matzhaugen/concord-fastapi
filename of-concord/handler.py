import io
import time
from http import HTTPStatus

import numpy as np

from concord import concord, robust_selection


def to_returns(prices):
    return np.diff(prices, axis=0) / prices[:-1]


def get_weights_from_lambda(returns, optimal_lambda):
    omega_hat = concord(returns, optimal_lambda).todense()
    vector = np.ones((omega_hat.shape[0], 1))
    coef = 1 / np.dot(np.dot(vector.T, omega_hat), vector)
    w_eff = float(coef) * np.dot(omega_hat, vector)
    return omega_hat, np.array(w_eff).ravel()


def robust_concord_weights(returns, coef_mu=1):
    """Cross-validate to find the best penalty and then compute the
    weights

    Parameters
    ----------
    returns -- Matrix of returns
    """
    # compute returns

    optimal_lambda = robust_selection(returns)
    omega_hat, w_eff = get_weights_from_lambda(returns, optimal_lambda)

    return w_eff, optimal_lambda


def handle(event, context):

    try:
        prices = np.load(io.BytesIO(event.body))
        returns = to_returns(prices)
        weights, lambda_robust = robust_concord_weights(returns)
        status_code = HTTPStatus.OK
    except Exception as e:
        print(f"Something went wrong in concord: {e}")
        status_code = HTTPStatus.INTERNAL_SERVER_ERROR
        p = prices.shape[0]
        weights = [[1.0 / p] * p]  # equal weights
    return {
        "statusCode": status_code,
        "body": {"weights": weights.tolist()},
    }
