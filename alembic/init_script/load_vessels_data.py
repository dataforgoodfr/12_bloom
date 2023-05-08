import logging
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

postrges_user = os.environ.get("POSTGRES_USER")
postrges_password = os.environ.get("POSTRGES_PASSWORD")
postrges_hostname = os.environ.get("POSTGRES_HOSTNAME")
postrges_db = os.environ.get("POSTGRES_DB")

# The db url is configured with the db connexion variables declared in the db.yaml file.
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
engine = create_engine(db_url)
df = pd.read_csv(
    Path.joinpath(Path.cwd(), "../../data/chalutiers_pelagiques.csv"),
    sep=";",
    dtype={"loa": float, "IMO": str},
)

df = df.drop(columns="comment")

df.to_sql("vessels", engine, if_exists="append", index=False)
