from time import perf_counter

from bloom.container import UseCases
from bloom.infra.repositories.repository_spire_ais_data import SpireAisDataRepository
from bloom.logger import logger
from bloom.domain.spire_ais_data import SpireAisData
from bloom.domain.vessel import Vessel
from bloom.domain.vessel_position import VesselPosition
from shapely import Point
from bloom.infra.repositories.repository_task_execution import TaskExecutionRepository
from datetime import datetime, timezone


def map_ais_data_to_vessel_position(ais_data: SpireAisData, vessel: Vessel) -> VesselPosition:
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
        vessel_id=vessel.id
    )


def run():
    use_cases = UseCases()
    spire_ais_data_repository = use_cases.spire_ais_data_repository()
    vessel_repository = use_cases.vessel_repository()
    port_repository = use_cases.port_repository()
    vessel_position_repository = use_cases.vessel_position_repository()
    db = use_cases.db()
    with db.session() as session:
        point_in_time = TaskExecutionRepository.get_point_in_time(session, "clean_positions")
        logger.info(f"Point in time={point_in_time}")
        now = datetime.now(timezone.utc)
        nb_donnees = 0
        nb_au_port = 0
        nb_pas_au_port = 0
        vessels = vessel_repository.load_vessel_metadata(session)
        logger.info(f"{len(vessels)} bateaux à traiter")
        # Foreach vessel
        for vessel in vessels:
            # Recheche des données AIS de chaque bateau créées depuis la dernière exécution du traitement (point in time)
            spire_datas = spire_ais_data_repository.get_all_data_by_mmsi(session, vessel.mmsi,
                                                                         SpireAisDataRepository.ORDER_BY_POSITION,
                                                                         point_in_time)
            for spire_data in spire_datas:
                nb_donnees += 1
                # Foreach position
                position = Point(spire_data.position_longitude, spire_data.position_latitude)
                port = port_repository.find_port_by_position_in_port_buffer(session, position)
                if not port:
                    vessel_position = map_ais_data_to_vessel_position(spire_data, vessel)
                    vessel_position_repository.create_vessel_position(session, vessel_position)
                    nb_pas_au_port += 1
                else:
                    nb_au_port += 1
                # TODO: A poursuivre, voir MIRO pour l'algorithme
                pass
        TaskExecutionRepository.set_point_in_time(session, "clean_positions", now)
        session.commit()
    logger.info(f"{nb_donnees} données SPIRE traitées")
    logger.info(f"{nb_au_port} données ignorées pour des bateaux au port")
    logger.info(f"{nb_pas_au_port} données importées dans vessel_positions")


if __name__ == "__main__":
    time_start = perf_counter()
    logger.info("DEBUT - Nettoyage des positions")
    run()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Nettoyage des positions en {duration:.2f}s")
