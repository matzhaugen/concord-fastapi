from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, validator
import numpy as np
from concord import concord
import concord_helper

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


class WeightsRequest(BaseModel):
    returns: List[List[float]]
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
