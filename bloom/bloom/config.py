import os

from pydantic import BaseSettings

class Settings(BaseSettings):
    postgres_user = os.environ.get("POSTGRES_USER")
    postgres_password = os.environ.get("POSTGRES_PASSWORD")
    postgres_hostname = os.environ.get("POSTGRES_HOSTNAME")
    postgres_port = os.environ.get("POSTGRES_PORT")
    postgres_db = os.environ.get("POSTGRES_DB")
    
    #print("db_url: ", f"postgresql://{postgres_user}:{postgres_password}@{postgres_hostname}:"
    #                    f"{postgres_port}/{postgres_db}")

    db_url = (
        "postgresql://"
        f"{postgres_user}"
        ":"
        f"{postgres_password}"
        "@"
        f"{postgres_hostname}"
        ":"
        f"{postgres_port}"
        "/"
        f"{postgres_db}"
    )

    srid: int = 4326

settings = Settings()
