import os

from pydantic import BaseSettings


class Settings(BaseSettings):

    postrges_user = os.environ.get("POSTGRES_USER")
    postrges_password = os.environ.get("POSTRGES_PASSWORD")
    postrges_hostname = os.environ.get("POSTGRES_HOSTNAME")
    postrges_db = os.environ.get("POSTGRES_DB")

    db_url = (
        "postgresql://"
        + postrges_user
        + ":"
        + postrges_password
        + "@"
        + postrges_hostname
        + ":5432/"
        + postrges_db
    )

    srid: int = 4236


settings = Settings()
