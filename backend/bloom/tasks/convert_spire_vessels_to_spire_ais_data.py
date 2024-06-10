from time import perf_counter
from typing import Generator

from bloom.container import UseCasesContainer
from bloom.domain.spire_ais_data import SpireAisData
from bloom.infra.database.sql_model import VesselPositionSpire
from bloom.logger import logger
from geoalchemy2.shape import to_shape
from shapely import Point
from sqlalchemy.orm.session import Session

use_cases = UseCasesContainer()
vessel_repo = use_cases.vessel_repository()
spire_ais_data_repo = use_cases.spire_ais_data_repository()
db = use_cases.db()
batch_size = 1000


def map_to_ais_spire_data(vessel_position: VesselPositionSpire) -> SpireAisData:
    position: Point = to_shape(vessel_position.position)
    return SpireAisData(
        spire_update_statement=vessel_position.timestamp,
        vessel_ais_class=None,
        vessel_flag=None,
        vessel_name=vessel_position.ship_name,
        vessel_callsign=None,
        vessel_timestamp=None,
        vessel_update_timestamp=None,
        vessel_ship_type=None,
        vessel_sub_ship_type=None,
        vessel_mmsi=vessel_position.mmsi,
        vessel_imo=vessel_position.IMO,
        vessel_width=vessel_position.vessel_width,
        vessel_length=vessel_position.vessel_length,
        position_accuracy=vessel_position.accuracy,
        position_collection_type=vessel_position.position_sensors,
        position_course=vessel_position.course,
        position_heading=vessel_position.heading,
        position_latitude=position.x,
        position_longitude=position.y,
        position_maneuver=None,
        position_navigational_status=vessel_position.navigation_status,
        position_rot=vessel_position.rot,
        position_speed=vessel_position.speed,
        position_timestamp=vessel_position.last_position_time,
        position_update_timestamp=vessel_position.last_position_time,
        voyage_destination=vessel_position.voyage_destination,
        voyage_draught=vessel_position.voyage_draught,
        voyage_eta=vessel_position.voyage_draught,
        voyage_timestamp=None,
        voyage_update_timestamp=None,
    )


def batch_convert(session: Session) -> Generator[list[SpireAisData], None, None]:
    batch = []
    for vessel_position in vessel_repo.get_all_spire_vessels_position(session, batch_size):
        batch.append(map_to_ais_spire_data(vessel_position))
        if len(batch) >= batch_size:
            yield batch
            batch = []
    yield batch


def run() -> None:
    count = 0
    try:
        with db.session() as session:
            for b in batch_convert(session):
                count = count + len(b)
                spire_ais_data_repo.batch_create_ais_data(b, session)
            session.commit()
    except Exception as e:
        session.rollback()
        logger.error("Erreur lors de conversion, transaction ROLLBACK")
        logger.error(e)
    logger.info(f"{count} enregistrements convertis")


if __name__ == "__main__":
    time_start = perf_counter()
    logger.info(
        f"Conversion spire_vessel_positions -> spire_ais_data (taille des lots: {batch_size})"
    )
    run()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"Conversion spire_vessel_positions -> spire_ais_data en {duration:.2f}s")
