from tasks.base import BaseTask


import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import wkb
from sqlalchemy import create_engine
from bloom.config import settings

class LoadVesselsDataTask(BaseTask):
    def run(self):

        engine = create_engine(settings.db_url)
        df = pd.read_csv(
            Path(settings.data_folder).joinpath("./chalutiers_pelagiques.csv"),
            sep=";",
            dtype={"loa": float, "IMO": str},
        )

        df = df.drop(columns="comment")

        df.to_sql("vessels", engine, if_exists="append", index=False)


if __name__ == "__main__":
    LoadVesselsDataTask().start()