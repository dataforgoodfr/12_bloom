import pandas as pd
import json
import numpy as np
from geopy import distance
from shapely.geometry import Point
from time import perf_counter

from bloom.container import UseCases
from bloom.infra.repositories.repository_spire_ais_data import SpireAisDataRepository
from bloom.logger import logger
from bloom.domain.spire_ais_data import SpireAisData
from bloom.domain.vessel import Vessel
from bloom.domain.vessel_position import VesselPosition
from bloom.infra.repositories.repository_task_execution import TaskExecutionRepository
from datetime import datetime, timezone


def map_ais_data_to_vessel_position(
    ais_data: SpireAisData, vessel: Vessel
) -> VesselPosition:
    return VesselPosition(
        timestamp=ais_data.position_timestamp,
        accuracy=ais_data.position_accuracy,
        collection_type=ais_data.position_collection_type,
        course=ais_data.position_course,
        heading=ais_data.position_heading,
        position=Point(ais_data.position_longitude, ais_data.position_latitude),
        latitude=ais_data.position_latitude,
        longitude=ais_data.position_longitude,
        maneuver=ais_data.position_maneuver,
        navigational_status=ais_data.position_navigational_status,
        rot=ais_data.position_rot,
        speed=ais_data.position_speed,
        vessel_id=vessel.id,
    )


def get_distance(current_position: tuple, last_position: tuple):
    if np.isnan(last_position[0]) or np.isnan(last_position[1]):
        return np.nan

    return distance.geodesic(current_position, last_position).km


def map_vessel_position_to_domain(row: pd.Series) -> VesselPosition:
    return VesselPosition(
        vessel_id=row["vessel_id"],
        timestamp=row["position_timestamp"],
        position=Point(row["position_longitude"], row["position_latitude"]),
        latitude=row["position_latitude"],
        longitude=row["position_longitude"],
        speed=row["speed"],
    )


def to_coords(row: pd.Series) -> pd.Series:
    if pd.isna(row["end_position"]) is False:
        row["longitude"] = row["end_position"].x
        row["latitude"] = row["end_position"].y

    return row


def run():
    use_cases = UseCases()
    db = use_cases.db()
    spire_repository = use_cases.spire_ais_data_repository()
    excursion_repository = use_cases.excursion_repository()
    segment_repository = use_cases.segment_repository()
    vessel_position_repository = use_cases.vessel_position_repository()
    with db.session() as session:
        point_in_time = TaskExecutionRepository.get_point_in_time(
            session, "clean_positions"
        )
        now = datetime.now(timezone.utc)
        # Step 1: load SPIRE batch: read from SpireAisData
        batch = spire_repository.get_all_data_after_date(session, point_in_time)
        logger.info(f"Réception de {len(batch)} nouvelles positions de Spire")
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
            (row["position_longitude"], row["position_latitude"]),
            (row["longitude"], row["latitude"]),
        ),
        axis=1,
    )

    # Step 6.2. Compute time in hours between last and current position
    ## If timestamp_end is NULL --> new_vessel is TRUE (record will be kept)
    ## --> fillna with anything to avoid exception
    batch.loc[batch["timestamp_end"].isna(), "timestamp_end"] = batch.loc[
        batch["timestamp_end"].isna(), "position_timestamp"
    ].copy()
    batch["timestamp_end"] = pd.to_datetime(batch["timestamp_end"])
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
    batch["speed"] *= 0.5399568  # Conversion km/h to noeuds

    # Step 7: apply to_keep flag: keep only positions WHERE:
    # - row["new_vessel"] is True, i.e. there is a new vessel_id
    # - OR speed is not close to 0, i.e. vessel moved significantly since last position
    batch["to_keep"] = (batch["new_vessel"] == True) | ~(  # detect new vessels
        (batch["excursion_closed"] == True)  # if last excursion closed
        & (batch["speed"] <= 0.01)  # and speed < 0.01: don't keep
    )

    # Step 8: filter unflagged rows to insert to DB
    vessel_position_columns = [
        "position_timestamp",
        "position_latitude",
        "position_longitude",
        "speed",
        "vessel_id",
    ]
    batch = batch.loc[batch["to_keep"] == True, vessel_position_columns].copy()

    # Step 9: insert to DataBase
    clean_positions = batch.apply(map_vessel_position_to_domain, axis=1).tolist()
    with db.session() as session:
        vessel_position_repository.batch_create_vessel_position(
            session, clean_positions
        )
        TaskExecutionRepository.set_point_in_time(session, "clean_position", now)
        session.commit()

    logger.info(f"Envoi de {len(batch)} positions à la table vessel_positions")

    return batch


if __name__ == "__main__":
    time_start = perf_counter()
    logger.info("DEBUT - Nettoyage des positions")
    run()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Nettoyage des positions en {duration:.2f}s")
