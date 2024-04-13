from pathlib import Path
from time import perf_counter

import json
import pandas as pd
from datetime import datetime
from shapely.geometry import Point
from bloom.config import settings
from bloom.container import UseCases
from bloom.infra.database.errors import DBException
from bloom.logger import logger
from bloom.domain.spire_ais_data import SpireAisData
from bloom.domain.excursion import Excursion
from bloom.domain.segment import Segment
from bloom.domain.vessel_position import VesselPosition
from pydantic import ValidationError

def map_spire_to_domain(row) -> SpireAisData:
    return SpireAisData(
        id=row["id"],
        spire_update_statement=row["spire_update_statement"],
        vessel_ais_class=None,
        vessel_flag=None,
        vessel_name=None,
        vessel_callsign=None,
        vessel_timestamp=None,
        vessel_update_timestamp=None,
        vessel_ship_type=None,
        vessel_sub_ship_type=None,
        vessel_mmsi=row["vessel_mmsi"],
        vessel_imo=None,
        vessel_width=None,
        vessel_length=None,
        position_accuracy=None,
        position_collection_type=None,
        position_course=None,
        position_heading=None,
        position_latitude=row["position_latitude"],
        position_longitude=row["position_longitude"],
        position_maneuver=None,
        position_navigational_status=None,
        position_rot=None,
        position_speed=None,
        position_timestamp=row["position_timestamp"],
        position_update_timestamp=row["position_update_timestamp"],
        voyage_destination=None,
        voyage_draught=None,
        voyage_eta=None,
        voyage_timestamp=None,
        voyage_update_timestamp=None,
        created_at=None,
    )

def map_excursion_to_domain(row) -> Excursion:
    return Excursion(
        id=row["id"],
        vessel_id=row["vessel_id"],
        departure_port_id=None,
        departure_at=None,
        # FIXME: missing in test data excursions.csv
        departure_position_id=row["departure_position_id"],
        arrival_port_id=None,
        arrival_at=None if pd.isna(row["arrival_at"]) else row["arrival_at"],
        arrival_position_id=row["departure_position_id"],  # FIXME: cannot be None
        excursion_duration=None,
        total_time_at_sea=None,
        total_time_in_amp=None,
        total_time_in_territorial_waters=None,
        total_time_in_costal_waters=None,
        total_time_fishing=None,
        total_time_fishing_in_amp=None,
        total_time_fishing_in_territorial_waters=None,
        total_time_fishing_in_costal_waters=None,
        total_time_extincting_amp=None,
        created_at=None,
        updated_at=None,
    )

def map_segment_to_domain(row) -> Segment:
    return Segment(
        id=None,
        excursion_id=row["excursion_id"],
        timestamp_start=None,
        timestamp_end=row["timestamp_end"],
        segment_duration=None,
        start_position_id=row["start_position_id"],
        end_position_id=row["end_position_id"],
        heading=None,
        distance=None,
        average_speed=None,
        type=None,
        in_amp_zone=None,
        in_territorial_waters=None,
        in_costal_waters=None,
        last_vessel_segment=row["last_vessel_segment"],
        created_at=None,
        updated_at=None,
    )

def generate_vessel_positions(df_segment: pd.DataFrame, now: datetime):
    end_positions = []
    df_segment["start_position_id"] = list(range(1, len(df_segment) + 1))
    df_segment["end_position_id"] = list(range(1, len(df_segment) + 1))
    for i, (_, row) in enumerate(df_segment.iterrows()):
        vp = VesselPosition(
            id=i + 1,
            vessel_id=row["vessel_id"],
            timestamp=now,
            position=Point(row["end_position"][1], row["end_position"][0]),
            latitude=row["end_position"][0],
            longitude=row["end_position"][1],
        )
        end_positions.append(vp)

    return df_segment, end_positions

def run(excursion_csv_filename: str, segment_csv_filename: str, spire_csv_filename: str) -> None:
    use_cases = UseCases()
    excursion_repository = use_cases.excursion_repository()
    vessel_position_repository = use_cases.vessel_position_repository()
    segment_repository = use_cases.segment_repository()
    spire_repository = use_cases.spire_ais_data_repository()
    db = use_cases.db()

    total = 0
    try:
        now = datetime.now()
        df_excursions = pd.read_csv(excursion_csv_filename)
        df_excursions["departure_position_id"] = list(range(1, len(df_excursions) + 1))
        df_segment = pd.read_csv(segment_csv_filename)
        df_segment["end_position"] = df_segment["end_position"].apply(json.loads)
        df_segment = df_segment.merge(df_excursions, left_on="excursion_id", right_on="id")
        df_spire_ais_data = pd.read_csv(spire_csv_filename)
        df_segment, end_positions = generate_vessel_positions(df_segment, now)
        excursions = df_excursions.apply(map_excursion_to_domain, axis=1)
        segments = df_segment.apply(map_segment_to_domain, axis=1)
        spire_ais_data = df_spire_ais_data.apply(map_spire_to_domain, axis=1)

        with db.session() as session:
            spire_repository.batch_create_ais_data(spire_ais_data, session)
            session.commit()
        
        with db.session() as session:
            end_positions = vessel_position_repository.batch_create_vessel_position(
                session, end_positions
            )
            session.commit()
        
        with db.session() as session:
            excursions = excursion_repository.batch_create_excursion(
                session, list(excursions)
            )
            total = len(excursions)
            session.commit()
        
        with db.session() as session:
            segments = segment_repository.batch_create_segment(
                session, list(segments)
            )
            session.commit()

    except ValidationError as e:
        logger.error("Erreur de validation des données d'excursions")
        logger.error(e.errors())
    except DBException as e:
        logger.error("Erreur d'insertion en base")
    logger.info(f"{total} excursion(s) créés")


if __name__ == "__main__":
    time_start = perf_counter()
    excursions_fp = Path(settings.data_folder).joinpath("./excursions.csv")
    spire_fp = Path(settings.data_folder).joinpath("./batch.csv")
    segment_fp = Path(settings.data_folder).joinpath("./last_segment.csv")
    logger.info(
        f"DEBUT - Chargement des données d'excursions' depuis le fichier {excursions_fp}"
    )
    run(excursions_fp, segment_fp, spire_fp)
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Chargement des données de ports en {duration:.2f}s")
