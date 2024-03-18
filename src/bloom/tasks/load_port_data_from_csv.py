from pathlib import Path
from time import perf_counter

import geopandas as gpd
import pandas as pd
import pycountry
from bloom.config import settings
from bloom.container import UseCases
from bloom.domain.port import Port
from bloom.logger import logger
from pydantic import ValidationError
from shapely import wkt

port_repository = UseCases.port_repository()


def map_to_domain(row):
    iso_code = pycountry.countries.get(name=row["country"])
    iso_code = iso_code.alpha_3 if iso_code is not None else "XXX"

    try:
        row["domain"] = Port(
            name=row["port"],
            locode=row["locode"],
            url=row["url"],
            country_iso3=iso_code,
            latitude=float(row["latitude"]),
            longitude=float(row["longitude"]),
            geometry_point=row["geometry_point"],
        )
    except ValidationError as e:
        logger.warning("Données de port invalides, élément ignoré")
        logger.warning(e.errors())
        logger.warning(row)
        row["domain"] = None
    return row


def create_port(row):
    try:
        if row["domain"] is None:
            row["orm"] = None
        else:
            row["orm"] = port_repository.create_port(row["domain"])
    except Exception as e:
        logger.warning("Echec d'insertion en base", exc_info=e)
        logger.warning(row)
        row["orm"] = None
    return row


def run(csv_file_name: str) -> None:
    df = pd.read_csv(csv_file_name, sep=";")
    df["geometry_point"] = df["geometry_point"].apply(wkt.loads)
    gdf = gpd.GeoDataFrame(df, geometry="geometry_point", crs=settings.srid)
    gdf = gdf.apply(map_to_domain, axis=1)
    gdf = gdf.apply(create_port, axis=1)
    total = len(gdf["orm"])
    total_ko = len(gdf[gdf["orm"] == None])
    logger.info(f"{total - total_ko}/{total} ports(s) créés")


if __name__ == "__main__":
    time_start = perf_counter()
    file_name = Path(settings.data_folder).joinpath("./ports_rad3000_res10.csv")
    logger.info(f"Chargement des données de ports depuis le fichier {file_name}")
    run(file_name)
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"Fin du chargement des données de ports en {duration:.2f}s")
