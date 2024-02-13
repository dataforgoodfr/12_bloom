import logging
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

postgres_user = os.environ.get("POSTGRES_USER")
postgres_password = os.environ.get("POSTGRES_PASSWORD")
postgres_hostname = os.environ.get("POSTGRES_HOSTNAME")
postgres_db = os.environ.get("POSTGRES_DB")
postgres_port = os.environ.get("POSTGRES_PORT")

# The db url is configured with the db connexion variables declared in the db.yaml file.
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
engine = create_engine(db_url)
df = pd.read_csv(
    Path.joinpath(Path.cwd(), "spire_positions_subset_02022024.csv"),
    sep=","
)

df.to_sql("spire_vessel_positions", engine, if_exists="append", index=False)