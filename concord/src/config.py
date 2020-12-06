from pydantic import BaseSettings


class Config(BaseSettings):
    backend_url: str = "http://localhost:81"  # Default if not set in environment
    sql_alchemy_db_uri: str = "postgresql://postgres:postgrespassword@localhost:5432/postgres"


config = Config()
