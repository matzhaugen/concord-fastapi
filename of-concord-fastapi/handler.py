import io
from http import HTTPStatus
from typing import Dict, List

import numpy as np
from fastapi import HTTPException
from pydantic import BaseModel

from concord import concord, robust_selection

FUNCTION_NAME = "templatefn"
FUNCTION_VERSION = "1.0.0"
FUNCTION_SUMMARY = "A function that does this"
FUNCTION_RESPONSE_DESC = "Definition of object returned by function"


class RequestModel(BaseModel):
    data: List


class ResponseModel(BaseModel):
    weights: List


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


def handle(req):
    """handle a request to the function
    Args:
        req (dict): request body
    """
    try:
        prices = np.array(req.data)
        returns = to_returns(prices)
        weights, lambda_robust = robust_concord_weights(returns)
    except Exception as e:
        print(f"Something went wrong in concord: {e}")
        raise HTTPException(status_code=HTTPStatus.INTERNAL_SERVER_ERROR, detail=e)
        p = prices.shape[0]
        weights = [[1.0 / p] * p]  # equal weights
    #  The body need to be a dict so that it can be json decoded.
    res = ResponseModel(weights=weights.tolist())
    return res
