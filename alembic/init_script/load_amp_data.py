import logging
import os
from pathlib import Path

import geopandas as gpd
import pandas as pd
from shapely import wkb
from sqlalchemy import create_engine

logging.basicConfig()
logging.getLogger("sqlalchemy.engine").setLevel(logging.INFO)

postgres_user = os.environ.get("POSTGRES_USER")
postgres_password = os.environ.get("POSTGRES_PASSWORD")
postgres_hostname = os.environ.get("POSTGRES_HOSTNAME")
postgres_db = os.environ.get("POSTGRES_DB")
postgres_port = os.environ.get("POSTGRES_PORT")


# The db url is configured with the db connexion variables declared in the db.yaml file.
db_url = (
    "postgresql://"
    + postgres_user
    + ":"
    + postgres_password
    + "@"
    + postgres_hostname
    + ":"
    + postgres_port
    + "/"
    + postgres_db
)

engine = create_engine(db_url, echo=False)

df = pd.read_csv(
    Path.joinpath(Path.cwd(), "data/zones_subset_02022024.csv"),
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