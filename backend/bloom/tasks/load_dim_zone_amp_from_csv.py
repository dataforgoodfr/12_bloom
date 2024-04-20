from pathlib import Path
from time import perf_counter

import pandas as pd
from bloom.config import settings
from bloom.container import UseCases
from bloom.domain.zone import Zone
from bloom.infra.database.errors import DBException
from bloom.logger import logger
from pydantic import ValidationError
from shapely import wkb


def map_to_domain(row: pd.Series) -> Zone:
    isna = row.isna()

    return Zone(
        category="amp",
        sub_category=None,
        name=row["name"],
        geometry=row["geometry"],
        centroid=row["geometry"].centroid,
        json_data={k: row[k] if not isna[k] else None for k in
                   ["index", "desig_eng", "desig_type", "iucn_cat", "parent_iso", "iso3", "benificiaries"]},
    )


def run(csv_file_name: str):
    use_cases = UseCases()
    db = use_cases.db()
    zone_repository = use_cases.zone_repository()

    total = 0
    try:
        df = pd.read_csv(csv_file_name, sep=",")
        df = df.rename(columns={"Geometry": "geometry",
                                "Index": "index", "WDPAID": "wdpaid",
                                "Name": "name",
                                "DESIG_ENG": "desig_eng",
                                "DESIG_TYPE": "desig_type",
                                "IUCN_CAT": "iucn_cat",
                                "PARENT_ISO": "parent_iso",
                                "ISO3": "iso3",
                                "Benificiaries": "benificiaries"})
        df["geometry"] = df["geometry"].apply(wkb.loads)
        zones = df.apply(map_to_domain, axis=1)
        with db.session() as session:
            zones = zone_repository.batch_create_zone(session, list(zones))
            session.commit()
            total = len(zones)
            print(zones)
    except ValidationError as e:
        logger.error("Erreur de validation des données de bateau")
        logger.error(e.errors())
    except DBException:
        logger.error("Erreur d'insertion en base")
    logger.info(f"{total} bateau(x) créés")


if __name__ == "__main__":
    time_start = perf_counter()
    file_name = Path(settings.data_folder).joinpath("./zones_subset.csv")
    logger.info(f"DEBUT - Chargement des données des zones AMP depuis le fichier {file_name}")
    run(file_name)
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Chargement des données des zones AMP en {duration:.2f}s")
