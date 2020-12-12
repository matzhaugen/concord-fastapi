import io
import time

import numpy as np

from concord import concord, robust_selection


def to_returns(prices):
    return np.diff(prices, axis=0) / prices[:-1]


def get_weights_from_lambda(returns, optimal_lambda):
    omega_hat = concord(returns, optimal_lambda).todense()
    vector = np.ones((omega_hat.shape[0], 1))
    coef = 1 / np.dot(np.dot(vector.T, omega_hat), vector)
    w_eff = float(coef) * np.dot(omega_hat, vector)
    return omega_hat, w_eff


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

    return (w_eff, optimal_lambda)


def concord_weights(returns):
    weights, lambda_robust = robust_concord_weights(returns)

    return np.array(weights)


def handle(event, context):

    prices = np.load(io.BytesIO(event.body))
    returns = to_returns(prices)
    weights = concord_weights(returns)

    return {
        "statusCode": 200,
        "body": {"hello": "Hello from Concord!", "result": weights.tolist()},
    }
