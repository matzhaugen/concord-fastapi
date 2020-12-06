import json
from typing import Dict, List

import numpy as np
import pandas as pd
import src.concord_helper as concord_helper
import src.data_transforms as data_transforms
import src.db as db
from fastapi import FastAPI
from pydantic import BaseModel

app = FastAPI()


class CreatePortfolioRequest(BaseModel):
    tickers: List[str]
    end_date: str


class CreatePortfolioResponse(BaseModel):
    weights: Dict[str, Dict[str, float]]
    wealth: Dict[str, float]


@app.get("/")
def world():
    return {"hello": "world"}


@app.post("/portfolio", response_model=CreatePortfolioResponse)
def create_portfolio(request: CreatePortfolioRequest):

    tickers = request.tickers
    prices = db.get_data(request.tickers, request.end_date)
    method = "concord"  # TODO :remove this hard-coding
    weights, returns, times, rebalance_dates = concord_helper.get_weights(prices, method=method)
    wealth_times, wealth_values = data_transforms.get_wealth(weights, returns, times, rebalance_dates)

    wealth_srs = pd.Series(data=np.around(wealth_values, 3), name="value", index=wealth_times)

    weights_df = pd.DataFrame(data=weights, columns=tickers, index=rebalance_dates)
    weights_df.index = weights_df.index.strftime(date_format="%Y-%m-%d")

    response = {
        "wealth": json.loads(wealth_srs.to_json(orient="index")),
        "weights": json.loads(weights_df.to_json(orient="index")),
    }
    return response
