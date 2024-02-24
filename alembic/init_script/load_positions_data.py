import logging
import os
from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

from bloom.config import settings

engine = create_engine(settings.db_url, echo=False)

df = pd.read_csv(
    Path(os.path.dirname(__file__)).joinpath("../../data/spire_positions_subset_02022024.csv"),
    sep=","
)

df.to_sql("spire_vessel_positions", engine, if_exists="append", index=False)