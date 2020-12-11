import datetime

import numpy as np
import pandas as pd
import pytest
from src.db import crud
from src.db.database import Base, SessionLocal
from src.mock_db import get_data
from src.schemas import UserCreate

END_DATE = datetime.date(1990, 6, 1)
# Dependency
@pytest.fixture(scope="session")
def db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@pytest.fixture(scope="session")
def mock_data():
    yield get_data(end_date=END_DATE)


@pytest.fixture(autouse=True)
def truncate_all_tables_between_each_test(db):
    for table in reversed(Base.metadata.sorted_tables):
        if table.name == "stocks":
            continue
        db.execute(table.delete())


def test_insert_user(db):
    user_create = UserCreate(email="a@b.c", password="secret")

    crud.create_user(db, user_create)
    user_down = crud.get_users(db)[0]

    assert user_down.id > 0


def test_get_stocks(db, mock_data):

    tickers = ["AA", "VZ"]
    stocks_df = crud.retrieve_stocks(db, tickers=tickers, end_date=END_DATE)
    expected_df = mock_data[tickers]

    pd.testing.assert_frame_equal(expected_df, stocks_df, check_index_type=False)


@pytest.mark.parametrize("overwrite", [(False), (True)])
def test_insert_stocks(db, mock_data, overwrite):
    tickers = ["AA", "VZ"]
    subset_df = mock_data[tickers]
    subset_df.index = subset_df.index.strftime("%Y-%m-%d")
    subset_df = subset_df.reset_index()
    stock_data = subset_df.melt(id_vars=["date"], value_name="price").to_dict("records")
    crud.insert_stocks(db, stock_data, overwrite=overwrite)
    stock = crud.retrieve_stocks(db, tickers=tickers, end_date=END_DATE)
    np.testing.assert_array_equal(subset_df.set_index("date"), stock)
