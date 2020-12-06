from pydantic import BaseSettings


class Config(BaseSettings):
    backend_url: str = "http://localhost:81"  # Default if not set in environment
    sqlalchemy_db_uri: str = (
        "postgresql://postgres:postgrespassword@postgres:5432/postgres"
    )


config = Config()
