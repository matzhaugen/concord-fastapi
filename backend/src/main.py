from typing import List
from fastapi import FastAPI
from pydantic import BaseModel

import numpy as np
import pandas as pd
from concord import concord
import concord_helper
import data_transforms
import db

app = FastAPI()

class Item(BaseModel):
    name: str




class Input(BaseModel):
    covariance: List[List[float]]
    alpha: float

    class Config:
        schema_extra = {
            "example": {
                "covariance": [[1, 0.1], [0, 0.1]],
                "alpha": 0.2
            }
        }


class CreatePortfolioRequest(BaseModel):
    tickers: List[str]
    end_date: str


class WeightsRequest(BaseModel):
    prices: List[List[float]]
    robust: bool = True


@app.post("/weights")
def weights(request: WeightsRequest):
    returns = request.returns
    weights, lambda_min, lambda_1sd, omega_hat, mean_sparsity, \
        std_sparsity, mean_rss, std_rss = concord_helper.concord_weights(np.array(returns), request.robust)

    return {"weights": weights.tolist(),
            "omega": omega_hat.tolist(),
            "lambda_min": lambda_min,
            "lambda_1sd": lambda_1sd,
            "mean_sparsity": mean_sparsity.tolist(),
            "std_sparsity": std_sparsity.tolist(),
            "mean_rss": mean_rss.tolist(),
            "std_rss": std_rss.tolist()}

@app.post("/portfolio")
def create_portfolio(request: CreatePortfolioRequest):
    print(request)
    prices = db.get_data(request.tickers, request.end_date)
    method = "concord" # TODO :remove this hard-coding

    weights, returns, times, rebalance_dates = concord_helper.get_weights(prices, method=method)
    wealth_times, wealth_values = data_transforms.get_wealth(weights, returns, times, rebalance_dates)

    result_ts = pd.DataFrame(
        data=np.array([np.around(wealth_values, 3), wealth_times]).T,
        columns=['value', 'date'])
    weights_data = [{'values': w, 'date': rbd} for w, rbd in zip(weights.tolist(), rebalance_dates.astype(str).tolist())]
    response = {
        'wealth_data': result_ts.to_json(orient='records'),
        'weights_data': weights_data
    }
    return response


@app.post("/robustweights")
def robustweights(request: WeightsRequest):
    returns = request.returns
    weights, lambda_robust = concord_helper.robust_concord_weights(np.array(returns), request.robust)

    return {"weights": weights.tolist(),
            "lambda_robust": lambda_robust,
            }

@app.get("/")
def read_root():
    return {"Hello": "World"}


@app.get("/items/{item_id}")
def read_item(item_id: int, q: str = None):
    return {"item_id": item_id, "q": q}


@app.post("/concord/")
def regularize(input: Input):
    array = np.array(input.covariance)
    omega = concord(array, input.alpha)
    dense_omega = omega.todense()
    k = np.sum(1 / np.diag(dense_omega ** 2))
    return {"regularized": omega.todense().tolist(), "sum_diag_inverse_sq": k}
