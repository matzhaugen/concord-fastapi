import asyncio
import concurrent.futures
from datetime import date
from typing import Dict, List

import aiohttp
import requests
import src.mock_db as db
from fastapi import Depends, FastAPI, HTTPException
from pydantic import BaseModel
from sqlalchemy.orm import Session
from src import schemas
from src.config import config
from src.db import crud, models
from src.db.database import SessionLocal, engine
from src.service import PortfolioService, call_of_concord

app = FastAPI()

# Dependency
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/async-hello")
async def async_hello():
    url = f"{config.openfaas_url}/function/of-concord"

    async with aiohttp.ClientSession() as aio_session:
        aws = [call_of_concord(aio_session, url, {"input": i}) for i in range(10)]
        resp_list = await asyncio.gather(*aws)  # where the magic happens
        final_resp = {f"{i}": res for i, res in enumerate(resp_list)}

    return final_resp


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
def create_item_for_user(
    user_id: int, item: schemas.ItemCreate, db: Session = Depends(get_db)
):
    return crud.create_user_item(db=db, item=item)


@app.get("/items/", response_model=List[schemas.Item])
def read_items(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    items = crud.get_items(db, skip=skip, limit=limit)
    return items


@app.get("/tickers")
def tickers():
    prices = db.get_data()
    return {"tickers": prices.columns.tolist()}


@app.post("/portfolio-sync", response_model=schemas.CreatePortfolioResponse)
def portfolio_sync(
    request: schemas.PortfolioRequest,
    portfolio_service: PortfolioService = Depends(),
    db: Session = Depends(get_db),
):

    result = portfolio_service.get_portfolio_sync(db, request.tickers, request.end_date)

    return result


@app.post("/portfolio-async", response_model=schemas.CreatePortfolioResponse)
async def portfolio_async(
    request: schemas.PortfolioRequest,
    portfolio_service: PortfolioService = Depends(),
    db: Session = Depends(get_db),
):

    result = await portfolio_service.get_portfolio_async(
        db, request.tickers, request.end_date
    )

    return result
