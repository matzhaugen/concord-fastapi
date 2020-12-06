import pytest
from src.config import Config
from src.db.models import User
from src.main import get_db
from src.schemas import Item, User


@pytest.fixture(scope="session")
def config():
    yield Config()


@pytest.fixture(autouse=True)
def truncate_all_tables_between_each_test(db):
    db.truncate_all()


@pytest.fixture(scope="session")
def db(config):
    yield get_db()


def test_insert_user(db):
    item = Item(title="hi", description="world", id=2, owner_id="1")
    user = User(id=1, is_active=True, items=[item])

    db.create_user(user)
    db.create_user_item(item)
    user = db.get_users()
    assert user.first().id == 1
