from pathlib import Path
from time import perf_counter

import pandas as pd
from bloom.config import settings
from bloom.container import UseCases
from bloom.domain.vessel import Vessel
from bloom.infra.database.errors import DBException
from bloom.logger import logger
from pydantic import ValidationError


def map_to_domain(row: pd.Series) -> Vessel:
    isna = row.isna()
    return Vessel(
        mmsi=int(row["mmsi"]) if not isna["mmsi"] else None,
        ship_name=row["ship_name"],
        width=None,
        length=row["loa"],
        country_iso3=row["country_iso3"] if not isna["country_iso3"] else "XXX",
        type=row["type"],
        imo=row["IMO"] if not isna["IMO"] else None,
        cfr=row["cfr"] if not isna["cfr"] else None,
        registration_number=row["registration_number"]
        if not isna["registration_number"]
        else None,
        external_marking=row["external_marking"] if not isna["external_marking"] else None,
        ircs=row["ircs"] if not isna["ircs"] else None,
        mt_activated=row["mt_activated"].strip(),
    )


def run(csv_file_name: str) -> None:
    use_cases = UseCases()
    vessel_repository = use_cases.vessel_repository()
    db = use_cases.db()

    ports = []
    total = 0
    try:
        df = pd.read_csv(csv_file_name, sep=";")
        vessels = df.apply(map_to_domain, axis=1)
        with db.session() as session:
            ports = vessel_repository.batch_create_vessel(list(vessels), session)
            session.commit()
            total = len(ports)
    except ValidationError as e:
        logger.error("Erreur de validation des données de bateau")
        logger.error(e.errors())
    except DBException as e:
        logger.error("Erreur d'insertion en base")
    logger.info(f"{total} bateau(x) créés")


if __name__ == "__main__":
    time_start = perf_counter()
    file_name = Path(settings.data_folder).joinpath("./chalutiers_pelagiques.csv")
    logger.info(f"DEBUT - Chargement des données de bateaux depuis le fichier {file_name}")
    run(file_name)
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Chargement des données de bateaux en {duration:.2f}s")
