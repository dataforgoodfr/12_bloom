from datetime import datetime, timezone
from time import perf_counter

from bloom.container import UseCases
from bloom.domain.spire_ais_data import SpireAisData
from bloom.domain.vessel import Vessel
from bloom.domain.vessel_data import VesselData
from bloom.domain.vessel_voyage import VesselVoyage
from bloom.infra.repositories.repository_spire_ais_data import SpireAisDataRepository
from bloom.infra.repositories.repository_task_execution import TaskExecutionRepository
from bloom.infra.repositories.repository_vessel_data import VesselDataRepository
from bloom.infra.repositories.repository_vessel_voyage import VesselVoyageRepository
from bloom.logger import logger
from tasks.base import BaseTask


class UpdateVesselDataVoyage(BaseTask):

    def map_ais_data_to_vessel_data(self, ais_data: SpireAisData, vessel: Vessel) -> VesselData:
        return VesselData(
            timestamp=ais_data.vessel_timestamp,
            ais_class=ais_data.vessel_ais_class,
            flag=ais_data.vessel_flag,
            name=ais_data.vessel_name,
            callsign=ais_data.vessel_callsign,
            ship_type=ais_data.vessel_ship_type,
            sub_ship_type=ais_data.vessel_sub_ship_type,
            mmsi=ais_data.vessel_mmsi,
            imo=ais_data.vessel_imo,
            width=ais_data.vessel_width,
            length=ais_data.vessel_length,
            vessel_id=vessel.id
        )

    def map_ais_data_to_vessel_voyage(self, ais_data: SpireAisData, vessel: Vessel) -> VesselVoyage:
        return VesselVoyage(
            timestamp=ais_data.voyage_timestamp,
            destination=ais_data.voyage_destination,
            draught=ais_data.voyage_draught,
            eta=ais_data.voyage_eta,
            vessel_id=vessel.id,
        )

    def run(self, *args, **kwargs) -> None:
        use_cases = UseCases()
        spire_ais_data_repository = use_cases.spire_ais_data_repository()
        vessel_repository = use_cases.vessel_repository()
        db = use_cases.db()
        with db.session() as session:
            point_in_time = TaskExecutionRepository.get_point_in_time(session, "update_vessel_data_voyage")
            logger.info(f"Point in time={point_in_time}")
            now = datetime.now(timezone.utc)
            nb_donnees = 0
            nb_insert_data = 0
            nb_insert_voyage = 0
            vessels = vessel_repository.load_vessel_metadata(session)
            logger.info(f"{len(vessels)} bateaux à traiter")
            # Foreach vessel
            for vessel in vessels:
                # Recheche des données AIS de chaque bateau créées depuis la dernière exécution du traitement (point in time)
                spire_datas = spire_ais_data_repository.get_all_data_by_mmsi(session, vessel.mmsi,
                                                                             SpireAisDataRepository.ORDER_BY_POSITION,
                                                                             point_in_time)
                for spire_data in spire_datas:
                    vessel_data = map_ais_data_to_vessel_data(spire_data, vessel)
                    vessel_voyage = map_ais_data_to_vessel_voyage(spire_data, vessel)
                    nb_donnees += 1
                    last_data = VesselDataRepository.get_last_vessel_data(session, vessel.id)
                    last_voyage = VesselVoyageRepository.get_last_vessel_voyage(session, vessel.id)
                    # Foreach position
                    if not last_data or vessel_data.timestamp > last_data.timestamp:
                        VesselDataRepository.create_vessel_data(session, vessel_data)
                        nb_insert_data += 1
                    if not last_voyage or vessel_voyage.timestamp > last_voyage.timestamp:
                        VesselVoyageRepository.create_vessel_voyage(session, vessel_voyage)
                        nb_insert_voyage += 1
            TaskExecutionRepository.set_point_in_time(session, "update_vessel_data_voyage", now)
            session.commit()
        logger.info(f"{nb_donnees} données SPIRE traitées")
        logger.info(f"{nb_insert_data} données statiques mises à jour")
        logger.info(f"{nb_insert_voyage} données de voyage mises à jour")


if __name__ == "__main__":
    time_start = perf_counter()
    logger.info("DEBUT - Traitement des données statiques AIS des bateaux")
    UpdateVesselDataVoyage().start()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Traitement des données statiques AIS des bateaux en {duration:.2f}s")
