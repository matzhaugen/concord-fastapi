import time
from datetime import date
from typing import List, Optional

import pandas as pd
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.orm import Session
from src import schemas

from . import models


def df_to_db_input(df):
    df.index = df.index.strftime("%Y-%m-%d")
    df = df.reset_index()
    df = df.melt(id_vars=["date"], value_name="close")
    return df.to_dict("records")


def _db_output_to_df(db_result):
    df = pd.DataFrame(
        data=[(s.date, s.ticker, s.close) for s in db_result],
        columns=["date", "ticker", "close"],
    )
    df = df.pivot(columns=["ticker"], index="date", values="close")
    df.index = pd.to_datetime(df.index)
    return df


def insert_stocks_bulk(
    db: Session, stock_data: List[schemas.StockDate], overwrite=True
):

    db.bulk_insert_mappings(
        models.Stocks,
        stock_data,
    )
    db.commit()


def insert_stocks(db: Session, stock_data: List[schemas.StockDate], overwrite=True):
    start_time = time.time()
    stmt = insert(models.Stocks).values(stock_data)
    if overwrite:
        stmt = stmt.on_conflict_do_update(
            index_elements=["ticker", "date"], set_={"close": stmt.excluded.close}
        )
    else:
        stmt = stmt.on_conflict_do_nothing()
    db.connection().execute(stmt)
    print(f"Upserted {len(stock_data)} rows in {time.time() - start_time} seconds")


def retrieve_stocks(
    db: Session,
    tickers: List[str],
    end_date: Optional[date] = None,
    start_date: Optional[date] = None,
) -> pd.DataFrame:
    result = db.query(models.Stocks).filter(models.Stocks.ticker.in_(tickers))

    if end_date:
        result = result.filter(models.Stocks.date <= end_date)

    if start_date:
        result = result.filter(models.Stocks.date >= start_date)

    result = result.all()

    return _db_output_to_df(result)


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
