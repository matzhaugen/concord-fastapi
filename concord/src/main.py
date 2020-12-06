from datetime import date
from typing import Dict, List

import src.mock_db as db
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src import schemas
from src.db import crud, models
from src.db.database import SessionLocal, engine
from src.service import PortfolioService

models.Base.metadata.create_all(bind=engine)

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


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


@app.post("/users/", response_model=schemas.User)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user_by_email(db, email=user.email)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    return crud.create_user(db=db, user=user)


@app.get("/users/", response_model=List[schemas.User])
def read_users(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    users = crud.get_users(db, skip=skip, limit=limit)
    return users


@app.get("/users/{user_id}", response_model=schemas.User)
def read_user(user_id: int, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, user_id=user_id)
    if db_user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return db_user


@app.post("/users/{user_id}/items/", response_model=schemas.Item)
def create_item_for_user(user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)):
    return crud.create_user_item(db=db, item=item, user_id=user_id)


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


class CreatePortfolioResponse(BaseModel):
    weights: Dict[str, Dict[str, float]]
    wealth: Dict[str, float]


@app.get("/tickers")
def tickers():
    prices = db.get_data()
    return {"tickers": prices.columns.tolist()}


@app.post("/portfolio", response_model=CreatePortfolioResponse)
def portfolio(request: PortfolioRequest, portfolio_service: PortfolioService = Depends()):

    result = portfolio_service.get_portfolio(request.tickers, request.end_date.strftime("%Y-%m-%d"))

    return result
