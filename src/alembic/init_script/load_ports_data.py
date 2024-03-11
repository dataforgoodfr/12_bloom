import logging
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from bloom.config import settings


logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

engine = create_engine(settings.db_url, echo=False)

df = pd.read_csv(
    Path(settings.data_folder).joinpath("./ports_rad3000_res10.csv"),
    sep=";",
)

df.to_sql("ports", engine, if_exists="append", index=False)
