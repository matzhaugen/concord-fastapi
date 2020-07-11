from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, validator
import numpy as np
from concord import concord

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
