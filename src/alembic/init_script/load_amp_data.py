import logging
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import wkb
from sqlalchemy import create_engine
from bloom.config import settings


logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

engine = create_engine(settings.db_url, echo=False)

df = pd.read_csv(
    Path(settings.data_folder).joinpath("./zones_subset.csv"),
    sep=",",
)

df = df.rename(columns={"Geometry": "geometry",
                        "Index": "index", "Wdpaid": "WDPAID",
                        "Name": "name",
                        "Desig Eng": "DESIG_ENG",
                        "Desig Type": "DESIG_TYPE",
                        "Iucn Cat": "IUCN_CAT",
                        "Parent Iso": "PARENT_ISO",
                        "Iso3": "ISO3",
                        "Beneficiaries": "BENEFICIARIES"})

df['geometry'] = df['geometry'].apply(wkb.loads)
gdf = gpd.GeoDataFrame(df, crs='epsg:4326')
gdf.head()

gdf.to_postgis("mpa_fr_with_mn", con=engine, if_exists="replace", index=False)
