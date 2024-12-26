import argparse
import warnings
from datetime import datetime,timedelta, timezone
from time import perf_counter

import numpy as np
import pandas as pd
from geopy import distance
from shapely.geometry import Point

from bloom.container import UseCases
from bloom.domain.vessel_position import VesselPosition
from bloom.infra.repositories.repository_task_execution import TaskExecutionRepository
from bloom.logger import logger

warnings.filterwarnings("ignore")


# distance.distance takes pair of (lat, lon) tuples:
def get_distance(current_position: tuple, last_position: tuple):
    if np.isnan(last_position[0]) or np.isnan(last_position[1]):
        return np.nan

    return distance.geodesic(current_position, last_position).km


def map_vessel_position_to_domain(row: pd.Series) -> VesselPosition:
    return VesselPosition(
        vessel_id=row["vessel_id"],
        timestamp=row["position_timestamp"],
        accuracy=row["position_accuracy"],
        collection_type=row["position_collection_type"],
        course=row["position_course"],
        heading=row["position_heading"],
        position=Point(row["position_longitude"], row["position_latitude"]),
        latitude=row["position_latitude"],
        longitude=row["position_longitude"],
        maneuver=row["position_maneuver"],
        navigational_status=row["position_navigational_status"],
        rot=row["position_rot"],
        speed=row["speed"],
    )


def to_coords(row: pd.Series) -> pd.Series:
    if pd.isna(row["end_position"]) is False:
        row["longitude"] = row["end_position"].x
        row["latitude"] = row["end_position"].y

    return row


def run(batch_time):
    use_cases = UseCases()
    db = use_cases.db()
    spire_repository = use_cases.spire_ais_data_repository()
    excursion_repository = use_cases.excursion_repository()
    segment_repository = use_cases.segment_repository()
    vessel_position_repository = use_cases.vessel_position_repository()
    process_start=datetime.now(timezone.utc)
    point_in_time=None
    position_count=None
    with db.session() as session:
        point_in_time = TaskExecutionRepository.get_point_in_time(
            session, "clean_positions",
        )
        batch_limit = point_in_time + timedelta(days=batch_time)
        # Step 1: load SPIRE batch: read from SpireAisData
        logger.info(f"Lecture des nouvelles positions de Spire en base between {point_in_time} and {batch_limit}")
        batch = spire_repository.get_all_data_between_date(session, point_in_time, batch_limit)

        # Recherche de la date de l'enregistrement traité le plus récent.
        # Cette date est stockée comme date d'exécution du traitement ce qui permettra de repartir de cette date
        # à la prochaine execution pour traiter les enregistrements + récents
        max_created = max(batch["position_timestamp"]) if len(batch) > 0 else batch_limit
        logger.info(f"Traitement des positions entre le {point_in_time} et le {max_created}")
        position_count=len(batch)
        logger.info(f"{position_count} nouvelles positions de Spire")
        batch.dropna(
            subset=[
                "position_latitude",
                "position_longitude",
                "position_timestamp",
                "position_update_timestamp",
            ],
            inplace=True,
        )

        # Step 2: load excursion from fct_excursion where date_arrival IS NULL
        excursions = excursion_repository.get_current_excursions(session)

        # Step 3: load last_segment where last_vessel_segment == 1
        last_segment = segment_repository.get_last_vessel_id_segments(session)
        last_segment["longitude"] = None
        last_segment["latitude"] = None
        last_segment = last_segment.apply(to_coords, axis=1)

        # Step 4: merge batch with last_segment on vessel_id.
        # If column _merge == "left_only" --> this is a new vessel (keep it)
        batch = batch.merge(
            last_segment,
            how="left",
            on="vessel_id",
            suffixes=["", "_segment"],
            indicator=True,
        )
        batch.rename(columns={"_merge": "new_vessel"}, inplace=True)
        batch["new_vessel"] = batch["new_vessel"] == "left_only"

        # Step 5: merge batch with excursions
        # If column _merge == "left_only" --> the excursion is closed
        batch = batch.merge(
            excursions,
            how="left",
            on="vessel_id",
            suffixes=["", "_excursion"],
            indicator=True,
        )
        batch.rename(columns={"_merge": "excursion_closed"}, inplace=True)
        batch["excursion_closed"] = batch["excursion_closed"] == "left_only"

        # Step 6: compute speed between last and current position
        # Step 6.1. Compute distance in km between last and current position
        batch["distance_since_last_position"] = batch.apply(
            lambda row: get_distance(
                (row["position_latitude"], row["position_longitude"]),
                (row["latitude"], row["longitude"]),
            ),
            axis=1,
        )

        # Step 6.2. Compute time in hours between last and current position
        ## If timestamp_end is NULL --> new_vessel is TRUE (record will be kept)
        ## --> fillna with anything to avoid exception
        batch.loc[batch["timestamp_end"].isna(), "timestamp_end"] = batch.loc[
            batch["timestamp_end"].isna(), "position_timestamp"
        ].copy()
        batch["timestamp_end"] = pd.to_datetime(batch["timestamp_end"], utc=True)
        batch["position_timestamp"] = pd.to_datetime(batch["position_timestamp"], utc=True)
        batch["time_since_last_position"] = (
                batch["position_timestamp"] - batch["timestamp_end"]
        )
        batch["hours_since_last_position"] = (
                batch["time_since_last_position"].dt.seconds / 3600
        )

        # Step 6.3. Compute speed: speed = distance / time
        batch["speed"] = (
                batch["distance_since_last_position"] / batch["hours_since_last_position"]
        )
        batch["speed"] *= 0.5399568  # Conversion km/h to
        batch["speed"] = batch["speed"].fillna(batch["position_speed"])
        batch.replace([np.nan], [None], inplace=True)
        # Step 7: apply to_keep flag: keep only positions WHERE:
        # - row["new_vessel"] is True, i.e. there is a new vessel_id
        # - OR speed is not close to 0, i.e. vessel moved significantly since last position
        batch["to_keep"] = (batch["new_vessel"] == True) | ~(  # detect new vessels
                (batch["excursion_closed"] == True)  # if last excursion closed
                & (batch["speed"] <= 0.01)  # and speed < 0.01: don't keep
        )

        # Step 8: filter unflagged rows to insert to DB
        batch = batch.loc[batch["to_keep"] == True].copy()

        # Step 9: insert to DataBase
        clean_positions = batch.apply(map_vessel_position_to_domain, axis=1).values.tolist()
        print(f"Batch final:\n{clean_positions}")
        vessel_position_repository.batch_create_vessel_position(session, clean_positions)
        TaskExecutionRepository.set_point_in_time(session, "clean_positions", max_created)
        logger.info(f"Ecriture de {len(clean_positions)} positions dans la table vessel_positions")
        session.commit()
        if point_in_time:
            TaskExecutionRepository.set_duration(session,
                                             "clean_positions",
                                             max_created,
                                             datetime.now(timezone.utc)-process_start)
        if position_count != None:
            TaskExecutionRepository.set_position_count(session,
                                             "clean_positions",
                                             max_created,
                                             position_count)
        session.commit()


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Clean position")
    parser.add_argument(
        "-b",
        "--batch-time",
        type=int,
        help="batch size in days",
        required=False,
        default=7,
    )
    args = parser.parse_args()
    time_start = perf_counter()
    logger.info("DEBUT - Nettoyage des positions")
    run(args.batch_time)
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Nettoyage des positions en {duration:.2f}s")
