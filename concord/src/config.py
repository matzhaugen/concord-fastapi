from pydantic import BaseSettings


class Environment(BaseSettings):
    backend_url: str = "http://localhost:81"  # Default if not set in environment


environment = Environment()
