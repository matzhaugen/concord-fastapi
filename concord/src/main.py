from typing import List
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
import requests
import db
import service


app = FastAPI()

def to_camel(string: str) -> str:
    result = ''.join(word.capitalize() for word in string.split('_'))
    result = result[0].lower() + result[1:]
    return result

class PortfolioRequest(BaseModel):
    tickers: List[str]
    end_date: date

    class Config:
        schema_extra = {
            "example": {
                "tickers": ['AA', 'AXP'],
            }
        }
        alias_generator = to_camel
        allow_population_by_field_name = True
        

@app.get("/")
def read_root():
    res = requests.get("http://backend:80/")
    return res.json()


@app.get("/tickers")
def tickers():
    prices = db.get_data()
    return {"tickers": prices.columns.tolist()}


@app.post("/portfolio")
def portfolio(request: PortfolioRequest):
    result = service.get_portfolio(request.tickers, request.end_date.strftime('%Y-%m-%d'))

    return result.json()
