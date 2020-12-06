from contextlib import contextmanager
from functools import wraps
from typing import Generator, Optional

from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker
from src.config import environment as env
from src.db.models import User


def with_session(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        database_instance = args[0]
        assert isinstance(
            database_instance, Database
        ), "This decorator must be used with the Database class"
        if kwargs.get("session") is None:
            if kwargs.get("lock") is True:
                raise ValueError("session must be passed when using 'with_for_update'")
            with database_instance.session_scope() as session:
                kwargs["session"]: Session = session
                return f(*args, **kwargs)
        return f(*args, **kwargs)

    return decorated


class _DB:
    def __init__(self, env: env):
        sql_alchemy_db_uri = env.SQLALCHEMY_DB_URI
        self.engine = create_engine(sql_alchemy_db_uri)
        self._session_maker = sessionmaker(
            autocommit=False, autoflush=False, bind=self.engine
        )

    def new_session(self) -> Session:
        return self._session_maker()

    @contextmanager
    def session_scope(self) -> Generator[Session, None, None]:
        """Provide a transactional scope around a series of operations."""
        session = self.new_session()
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


class Database(_DB):
    @with_session
    def get_user(
        self,
        id: int,
        session: Optional[Session] = None,
        lock: bool = False,
        with_for_update: bool = False,
    ) -> Optional[User]:
        query = session.query(User)
        if with_for_update:
            query = query.with_for_update(of=User)
        return query.filter_by(id=id).first()
