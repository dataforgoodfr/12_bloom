import warnings

import pandas as pd
from bloom.domain.position_update import PositionUpdate
from shapely.geometry import Point

from bloom.container import UseCases
from bloom.domain.vessel_position import VesselPosition
from bloom.logger import logger
from time import perf_counter

warnings.filterwarnings("ignore")

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
        speed=row["position_speed"],
    )


def map_position_update_to_domain(row: pd.Series) -> PositionUpdate:
    return PositionUpdate(
        vessel_id=row["vessel_id"], 
        point_in_time=row["position_update_timestamp"]
    )


def run():
    use_cases = UseCases()
    db = use_cases.db()
    spire_repository = use_cases.spire_ais_data_repository()
    vessel_position_repository = use_cases.vessel_position_repository()
    position_update_repository = use_cases.position_update_repository()
    position_count=None

    def __init_entity_from_dataframe__(session, entity_info: pd.Series) -> PositionUpdate:
        entity = position_update_repository.find_record_by_vessel_id(
            session, entity_info['vessel_id']
        )

        if not entity:
            entity = PositionUpdate(vessel_id=entity_info["vessel_id"])
        entity.point_in_time = entity_info["max_timestamp"]

        return entity

    with db.session() as session:

        # Récupération des données Spire en se basant sur le dernier timestamp de mise à jour de position utilisé
        data = spire_repository.get_all_data_after_position_updates_per_vessel_id(session)
        logger.info(f"{len(data)} spire data with new updated position timestamp")

        # Sélection des variables
        positions: pd.DataFrame = data[
            [
                "vessel_id",
                "spire_update_statement",
                "position_accuracy",
                "position_collection_type",
                "vessel_mmsi",
                "position_course",
                "position_heading",
                "position_latitude",
                "position_longitude",
                "position_maneuver",
                "position_navigational_status",
                "position_rot",
                "position_speed",
                "position_timestamp",
                "position_update_timestamp",
            ]
        ]

        # Filtrage des duplicats
        positions.drop_duplicates(inplace=True)
        logger.info(f"{len(positions)} positions to map")

        # Save new positions
        mapped_positions = positions.apply(
            map_vessel_position_to_domain, axis=1
        ).values.tolist()

        vessel_position_repository.batch_create_vessel_position(
            session, mapped_positions
        )
        session.flush()

        logger.info(f"{len(mapped_positions)} mapped positions")

        # Mettre à jour position_updates
        df = positions[
            ["vessel_id", "position_update_timestamp"]
        ].drop_duplicates()

        df["max_timestamp"] = df.groupby(["vessel_id"])[
            "position_update_timestamp"
        ].transform(max)

        position_update_timestamps = df[
            ["vessel_id", "max_timestamp"]
        ].drop_duplicates()

        entities = []

        for id, entity_info in position_update_timestamps.iterrows():
            entity = __init_entity_from_dataframe__(session, entity_info)
            entities.append(entity)

        position_update_repository.batch_update_position_timestamp_update(
            session, entities
        )

        # session.commit()


if __name__ == "__main__":
    time_start = perf_counter()
    logger.info("DEBUT - Nettoyage des positions")
    run()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Nettoyage des positions en {duration:.2f}s")
