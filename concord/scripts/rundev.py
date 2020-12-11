import asyncio
import time
from subprocess import Popen

import sqlalchemy
from src.config import Config, config
from src.db import models
from src.db.database import engine


def is_postgres_alive(config: Config):
    engine = sqlalchemy.create_engine(config.sql_alchemy_db_uri)
    try:
        engine.connect()
        return True
    except Exception as e:
        if "Access denied" in str(e):
            return True
        else:
            return False


def setup_schema(config):
    for i in range(10):
        if not is_postgres_alive(config):
            print("postgres server not alive yet, waiting for 1 sec...")
            time.sleep(1)

    models.Base.metadata.create_all(bind=engine)


async def migrate_db(config: Config):
    version = "head"

    for i in range(180):
        if is_postgres_alive(config):
            p = Popen(f"PYTHONPATH=. poetry run alembic upgrade {version}", shell=True)
            p.wait()
            break
        time.sleep(1)


# Ingest test data to start with
# This will be replaced with real data later
def ingest_test_data(config):
    engine = sqlalchemy.create_engine(config.sql_alchemy_db_uri)
    with engine.connect() as conn:
        with conn.begin():
            print("Ingesting test data")
            conn.execute("COPY stocks FROM '/flatData.csv' DELIMITER ',' CSV HEADER;")


if __name__ == "__main__":
    # asyncio.run(migrate_db(config))
    setup_schema(config)
    # ingest_test_data(config)
