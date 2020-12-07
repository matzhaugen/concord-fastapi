import pytest
from src.db import crud
from src.db.database import Base, SessionLocal
from src.mock_db import get_data
from src.schemas import UserCreate


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
    from pdb import set_trace

    set_trace()
    crud.create_stock()
    pass
