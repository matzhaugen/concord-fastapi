from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, validator
import numpy as np
import pandas as pd
import requests
import time
import helper

app = FastAPI()


class PortfolioRequest(BaseModel):
    tickers: List[str]

    class Config:
        schema_extra = {
            "example": {
                "tickers": ['AA', 'AXP'],
            }
        }


@app.get("/")
def read_root():
    res = requests.get("http://concord:80/")
    return res.json()


@app.get("/tickers/")
def tickers():

    prices = helper.get_data()
    return {"tickers": prices.columns.tolist()}


@app.post("/portfolio/")
def portfolio(request: PortfolioRequest):

    prices = helper.get_data(request.tickers)
    weights, returns, times, rebalance_dates = helper.get_weights(prices)
    wealth_times, wealth_values = helper.get_wealth(weights, returns, times, rebalance_dates)

    result_ts = pd.DataFrame(
        data=np.array([np.around(wealth_values, 3), wealth_times]).T,
        columns=['value', 'date'])
    weights_data = [{'value': w, 'date': rbd} for w, rbd in zip(weights.tolist(), rebalance_dates.astype(str).tolist())]
    result = {
        'wealth_data': result_ts.to_json(orient='records'),
        'weights_data': weights_data
    }
    return result
