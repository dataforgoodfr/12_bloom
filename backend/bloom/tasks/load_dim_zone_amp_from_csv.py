from pathlib import Path
from time import perf_counter

import pandas as pd
from shapely import wkb

from bloom.config import settings
from bloom.container import UseCasesContainer
from bloom.domain.zone import Zone
from bloom.logger import logger

FIC_ZONE = ["french_metropolitan_mpas.csv", "fishing_coastal_waters.csv", "territorial_seas.csv"]


def map_to_domain(row: pd.Series) -> Zone:
    isna = row.isna()

    json_data = {}
    for k in ["index", "wdpaid", "desig_eng", "desig_type", "iucn_cat", "parent_iso", "iso3", "benificiaries",
              "source", "reference"]:
        try:
            value = row[k] if not isna[k] else None
            json_data[k] = value
        except:
            pass

    return Zone(
        category=row["category"],
        sub_category=row["sub_category"] if not isna["sub_category"] else None,
        name=row["name"],
        geometry=row["geometry"],
        centroid=row["geometry"].centroid,
        json_data=json_data,
    )


def run():
    use_cases = UseCasesContainer()
    db = use_cases.db()
    zone_repository = use_cases.zone_repository()

    with db.session() as session:
        for fic_csv in FIC_ZONE:
            file_name = Path(settings.data_folder).joinpath(fic_csv)
            logger.info(f"Chargement des données du fichier {file_name}")

            total = 0
            df = pd.read_csv(file_name, sep=",")
            df["geometry"] = df["geometry"].apply(wkb.loads)
            zones = df.apply(map_to_domain, axis=1)
            zones = zone_repository.batch_create_zone(session, list(zones))
            total = len(zones)
            logger.info(f"{total} zone(s) créés")
        session.commit()


if __name__ == "__main__":
    time_start = perf_counter()
    logger.info("DEBUT - Chargement des données des zones")
    run()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Chargement des données des zones en {duration:.2f}s")
