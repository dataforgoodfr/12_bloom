from pathlib import Path
from time import perf_counter

import pandas as pd
from bloom.config import settings
from bloom.container import UseCases
from bloom.domain.spire_ais_data import SpireAisData
from bloom.infra.database.errors import DBException
from bloom.logger import logger
from pydantic import ValidationError
from shapely import wkb
import numpy as np


def map_to_domain(row: pd.Series) -> SpireAisData:
    isna = row.isna()

    return SpireAisData(
        spire_update_statement=row['spire_update_statement'],
        vessel_ais_class=row['vessel_ais_class'],
        vessel_flag=row['vessel_flag'],
        vessel_name=row['vessel_name'],
        vessel_callsign=row['vessel_callsign'],
        vessel_timestamp=row['vessel_timestamp'],
        vessel_update_timestamp=row['vessel_update_timestamp'],
        vessel_ship_type=row['vessel_ship_type'],
        vessel_sub_ship_type=row['vessel_sub_ship_type'],
        vessel_mmsi=row['vessel_mmsi'],
        vessel_imo=row['vessel_imo'],
        vessel_width=row['vessel_width'],
        vessel_length=row['vessel_length'],
        position_accuracy=row['position_accuracy'],
        position_collection_type=row['position_collection_type'],
        position_course=row['position_course'],
        position_heading=row['position_heading'],
        position_latitude=row['position_latitude'],
        position_longitude=row['position_longitude'],
        position_maneuver=row['position_maneuver'],
        position_navigational_status=row['position_navigational_status'],
        position_rot=row['position_rot'],
        position_speed=row['position_speed'],
        position_timestamp=row['position_timestamp'],
        position_update_timestamp=row['position_update_timestamp'],
        voyage_destination=row['voyage_destination'],
        voyage_draught=row['voyage_draught'],
        voyage_eta=row['voyage_eta'],
        voyage_timestamp=row['voyage_timestamp'],
        voyage_update_timestamp=row['voyage_update_timestamp'],
        created_at=row['created_at'],
        )


def run(csv_file_name: str):
    use_cases = UseCases()
    db = use_cases.db()
    spire_ais_data_repository = use_cases.spire_ais_data_repository()

    total = 0
    try:
        df = pd.read_csv(csv_file_name, sep=";")
        df = df.rename(columns={})
        df=df.replace(np.NaN,None)
        spire_ais_data = df.apply(map_to_domain, axis=1)
        with db.session() as session:
            spire_ais_data = spire_ais_data_repository.batch_create_ais_data(session=session, ais_list=list(spire_ais_data))
            session.commit()
            total = len(spire_ais_data)
            #print(spire_ais_data)
    except ValidationError as e:
        logger.error("Erreur de validation des données de bateau")
        logger.error(e.errors())
    except DBException:
        logger.error("Erreur d'insertion en base")
    logger.info(f"{total} ais data créés")


if __name__ == "__main__":
    time_start = perf_counter()
    file_name = Path(settings.data_folder).joinpath("./spire_positions_subset.csv")
    logger.info(f"DEBUT - Chargement des données AIS Spire depuis le fichier {file_name}")
    run(file_name)
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Chargement des données AIS Spire en {duration:.2f}s")
