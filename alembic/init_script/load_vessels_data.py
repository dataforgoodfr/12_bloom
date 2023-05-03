from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

# The db url is configured with the db connexion variables declared in the db.yaml file.
db_url = "postgresql://bloom_user:bloom@postgres:5432/bloom_db"
engine = create_engine(db_url, echo=False)
df = pd.read_csv(
    Path.joinpath(Path.cwd(), "../../data/chalutiers_pelagiques.csv"),
    sep=";",
)
df.to_sql("vessels", engine, if_exists="append", index=False)
