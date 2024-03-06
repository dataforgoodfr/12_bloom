import logging
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine
from bloom.config import settings

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

engine = create_engine(settings.db_url)

df = pd.read_csv(
    Path(settings.data_folder).joinpath("./spire_positions_subset.csv"),
    sep=","
)

df.to_sql("spire_vessel_positions", engine, if_exists="append", index=False)
