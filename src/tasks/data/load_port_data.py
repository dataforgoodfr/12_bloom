from tasks.base import BaseTask


import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import wkb
from sqlalchemy import create_engine
from bloom.config import settings

class LoadPortDataTask(BaseTask):
    def run(self,*args,**kwargs):
        engine = create_engine(settings.db_url, echo=False)

        df = pd.read_csv(
            settings.port_polygon_data_csv_path,
            sep=";",
        )

        df.to_sql("ports", engine, if_exists="append", index=False)
        
if __name__ == "__main__":
    LoadPortDataTask().start()