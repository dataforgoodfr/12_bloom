import os

from pydantic import BaseSettings


class Settings(BaseSettings):

    postgres_user = os.environ.get("POSTGRES_USER")
    postgres_password = os.environ.get("POSTGRES_PASSWORD")
    postgres_hostname = os.environ.get("POSTGRES_HOSTNAME")
    postgres_db = os.environ.get("POSTGRES_DB")
    postgres_port = os.environ.get("POSTGRES_PORT")

    db_url = (
        "postgresql://"
        + postgres_user
        + ":"
        + postgres_password
        + "@"
        + postgres_hostname
        + ":"
        + postgres_port
        + "/"
        + postgres_db
    )

    srid: int = 4236


settings = Settings()
