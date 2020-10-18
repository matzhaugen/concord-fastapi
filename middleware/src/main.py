from typing import List
from fastapi import FastAPI
from pydantic import BaseModel, validator
import numpy as np
import pandas as pd
import requests
import time
import helper
import service


app = FastAPI()


class PortfolioRequest(BaseModel):
    tickers: List[str]
    method: str

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


@app.get("/tickers")
def tickers():
    prices = helper.get_data()
    return {"tickers": prices.columns.tolist()}


@app.post("/portfolio/")
def portfolio(request: PortfolioRequest):
    result = service.get_portfolio(request.tickers, request.method)

    return result
