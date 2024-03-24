from tasks.base import BaseTask

from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import wkb
from sqlalchemy import create_engine
from bloom.config import settings

class LoadVesselPositionsDataTask(BaseTask):
    def run(self,*args,**kwargs):
        engine = create_engine(settings.db_url)

        df = pd.read_csv(
            settings.vessel_positions_data_csv_path,
            sep=","
        )

        df.to_sql("spire_vessel_positions", engine, if_exists="append", index=False)
        

if __name__ == "__main__":
    LoadVesselPositionsDataTask().start()