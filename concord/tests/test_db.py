import datetime
import time

import numpy as np
import pytest
from pandas import Series
from src.db import crud
from src.db.database import Base, SessionLocal
from src.mock_db import get_data
from src.schemas import StockDate, UserCreate


# Dependency
@pytest.fixture(scope="session")
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(autouse=True)
def truncate_all_tables_between_each_test(db):
    for table in reversed(Base.metadata.sorted_tables):
        db.execute(table.delete())


def test_insert_user(db):
    user_create = UserCreate(email="a@b.c", password="secret")

    crud.create_user(db, user_create)
    user_down = crud.get_users(db)[0]

    assert user_down.id > 0


def test_insert_stocks(db):
    data_df = get_data()
    dates = data_df.index.values.astype(datetime.date)
    data_df.index.values.astype(datetime.date)
    stock_data = []
    start_time = time.time()
    for stock_name in data_df:
        for date, price in zip(dates, data_df[stock_name]):
            stock_data.append(StockDate(ticker=stock_name, date=date, price=price))
    print(f"Created input in {time.time() - start_time} seconds")
    crud.insert_stocks(db, stock_data)

    stock = crud.retrieve_stock(db, ticker="VZ")
    srs = Series(
        index=[s.date for s in stock], data=[s.price for s in stock], name="VZ"
    )
    np.testing.assert_array_equal(srs.values, data_df["VZ"].values)
