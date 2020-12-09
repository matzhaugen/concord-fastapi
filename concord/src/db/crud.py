import time
from datetime import date
from typing import List, Optional

from pandas import Series
from sqlalchemy.orm import Session
from src import schemas

from . import models


def insert_stocks(db: Session, stock_data: List[schemas.StockDate]):
    stock_rows = []
    start_time = time.time()
    for stock_row in stock_data:
        stock_rows.append(
            models.Stocks(
                ticker=stock_row.ticker, date=stock_row.date, price=stock_row.price
            )
        )
    print(f"Created input in {time.time() - start_time} seconds")
    start_time = time.time()
    db.add_all(stock_rows)
    print(f"Created input in {time.time() - start_time} seconds")
    db.commit()


def retrieve_stock(
    db: Session,
    ticker: str,
    date_min: Optional[date] = None,
    date_max: Optional[date] = None,
):
    return db.query(models.Stocks).filter(models.Stocks.ticker == ticker)


def get_user(db: Session, user_id: int):
    return db.query(models.User).filter(models.User.id == user_id).first()


def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()


def get_users(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.User).offset(skip).limit(limit).all()


def create_user(db: Session, user: schemas.UserCreate):
    fake_hashed_password = user.password + "notreallyhashed"
    db_user = models.User(email=user.email, hashed_password=fake_hashed_password)
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def get_items(db: Session, skip: int = 0, limit: int = 100):
    return db.query(models.Item).offset(skip).limit(limit).all()


def create_user_item(db: Session, item: schemas.ItemCreate):
    db_item = models.Item(**item.dict())
    db.add(db_item)
    db.commit()
    db.refresh(db_item)
    return db_item
