import logging
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

from bloom.config import settings

engine = create_engine(settings.db_url)
df = pd.read_csv(
    Path(os.path.dirname(__file__)).joinpath("../../data/chalutiers_pelagiques.csv"),
    sep=";",
    dtype={"loa": float, "IMO": str},
)

df = df.drop(columns="comment")

df.to_sql("vessels", engine, if_exists="append", index=False)
