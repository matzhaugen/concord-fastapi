from pydantic import BaseSettings


class Config(BaseSettings):
    # The defaults are used when running testing with pytest.
    # In the docker-compose file there are other values used to match dns lookup
    # And k8 manifests have different values to both of these.
    backend_url: str = "http://localhost:81"  # Default if not set in environment
    sql_alchemy_db_uri: str = "postgresql+psycopg2://postgres:postgrespassword@localhost:5432/postgres"
    openfaas_url: str = "http://localhost:5001"


config = Config()
