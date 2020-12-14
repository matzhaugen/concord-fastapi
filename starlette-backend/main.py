import io
from http import HTTPStatus

import numpy as np
from starlette.applications import Starlette
from starlette.responses import JSONResponse
from starlette.routing import Route

from concord import concord, robust_selection


async def homepage(request):
    return JSONResponse({"hello": "world"})


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


async def call_concord(request):
    """handle a request to the function
    Args:
        request (dict): request body
    """
    try:
        req_body = await request.body()
        prices = np.load(io.BytesIO(req_body))
        returns = to_returns(prices)
        weights, lambda_robust = robust_concord_weights(returns)
    except Exception as e:
        raise IOError(f"Something went wrong in concord: {e}")
        p = prices.shape[0]
        weights = [[1.0 / p] * p]  # equal weights
    #  The body need to be a dict so that it can be json decoded.
    res = JSONResponse({"weights": weights.tolist()})
    return res


app = Starlette(
    routes=[
        Route("/", homepage),
        Route("/", call_concord, methods=["POST"]),
    ]
)
