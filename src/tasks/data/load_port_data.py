from tasks.base import BaseTask


import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import wkb
from sqlalchemy import create_engine
from bloom.config import settings

class LoadPortDataTask(BaseTask):
    def run(self):
        engine = create_engine(settings.db_url, echo=False)

        df = pd.read_csv(
            Path(settings.data_folder).joinpath("./ports_rad3000_res10.csv"),
            sep=";",
        )

        df.to_sql("ports", engine, if_exists="append", index=False)
        
if __name__ == "__main__":
    LoadPortDataTask().start()