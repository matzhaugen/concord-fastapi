import psycopg2
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from src.config import config

print(f"Connecting to {config.sql_alchemy_db_uri}.")
engine = create_engine(
    config.sql_alchemy_db_uri, paramstyle="pyformat", executemany_mode="batch"
)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# For the dirty work
def get_psycopg2_conn():
    return psycopg2.connect(
        dbname="postgres",
        user=config.db_user,
        password=config.db_password,
        host=config.db_host,
    )
