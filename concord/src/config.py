from pydantic import BaseSettings


class Environment(BaseSettings):
    backend_url: str = "http://localhost:8000"


environment = Environment()
