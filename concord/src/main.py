from typing import List, Dict
from fastapi import FastAPI
from pydantic import BaseModel
from datetime import date
import requests
import src.db as db
import src.service as service


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
        
class CreatePortfolioResponse(BaseModel):
    weights: Dict[str, Dict[str, float]]
    wealth: Dict[str, float]

@app.get("/tickers")
def tickers():
    prices = db.get_data()
    return {"tickers": prices.columns.tolist()}


@app.post("/portfolio", response_model=CreatePortfolioResponse)
def portfolio(request: PortfolioRequest):
    result = service.get_portfolio(request.tickers, request.end_date.strftime('%Y-%m-%d'))

    return result
