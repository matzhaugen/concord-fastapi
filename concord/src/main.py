from datetime import date
from typing import Dict, List

import src.db as db
from fastapi import Depends, FastAPI
from pydantic import BaseModel
from src.service import PortfolioService

app = FastAPI()


def to_camel(string: str) -> str:
    result = "".join(word.capitalize() for word in string.split("_"))
    result = result[0].lower() + result[1:]
    return result


class PortfolioRequest(BaseModel):
    tickers: List[str]
    end_date: date

    class Config:
        schema_extra = {"example": {"tickers": ["AA", "AXP"], "endDate": "1993-01-01"}}
        alias_generator = to_camel
        allow_population_by_field_name = True


class CreatePortfolioResponse(BaseModel):
    weights: Dict[str, Dict[str, float]]
    wealth: Dict[str, float]
    BACKEND_URL = "http://localhost:8000"


@app.get("/tickers")
def tickers():
    prices = db.get_data()
    return {"tickers": prices.columns.tolist()}


@app.post("/portfolio", response_model=CreatePortfolioResponse)
def portfolio(
    request: PortfolioRequest, portfolio_service: PortfolioService = Depends()
):

    result = portfolio_service.get_portfolio(
        request.tickers, request.end_date.strftime("%Y-%m-%d")
    )

    return result
