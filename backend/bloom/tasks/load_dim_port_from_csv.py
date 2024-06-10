from pathlib import Path
from time import perf_counter

import geopandas as gpd
import pandas as pd
import pycountry
from bloom.config import settings
from bloom.container import UseCasesContainer
from bloom.domain.port import Port
from bloom.infra.database.errors import DBException
from bloom.logger import logger
from pydantic import ValidationError
from shapely import wkt


def map_to_domain(row) -> Port:
    iso_code = pycountry.countries.get(name=row["country"])
    iso_code = iso_code.alpha_3 if iso_code is not None else "XXX"

    return Port(
        name=row["port"],
        locode=row["locode"],
        url=row["url"],
        country_iso3=iso_code,
        latitude=float(row["latitude"]),
        longitude=float(row["longitude"]),
        geometry_point=row["geometry_point"],
    )


def run(csv_file_name: str) -> None:
    use_cases = UseCasesContainer()
    port_repository = use_cases.port_repository()
    db = use_cases.db()

    ports = []
    total = 0
    try:
        df = pd.read_csv(csv_file_name, sep=";")
        df["geometry_point"] = df["geometry_point"].apply(wkt.loads)
        gdf = gpd.GeoDataFrame(df, geometry="geometry_point", crs=settings.srid)
        ports = gdf.apply(map_to_domain, axis=1)
        with db.session() as session:
            ports = port_repository.batch_create_port(session, list(ports))
            session.commit()
            total = len(ports)
    except ValidationError as e:
        logger.error("Erreur de validation des données de port")
        logger.error(e.errors())
    except DBException as e:
        logger.error("Erreur d'insertion en base")
    logger.info(f"{total} ports(s) créés")


if __name__ == "__main__":
    time_start = perf_counter()
    file_name = Path(settings.data_folder).joinpath("./ports.csv")
    logger.info(f"DEBUT - Chargement des données de ports depuis le fichier {file_name}")
    run(file_name)
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Chargement des données de ports en {duration:.2f}s")
