from time import perf_counter

from bloom.container import UseCases
from bloom.infra.repositories.repository_spire_ais_data import SpireAisDataRepository
from bloom.logger import logger


def run():
    use_cases = UseCases()
    spire_ais_data_repository = use_cases.spire_ais_data_repository()
    vessel_repository = use_cases.vessel_repository()
    db = use_cases.db()
    with db.session() as session:
        vessels = vessel_repository.load_vessel_metadata(session)
        # Foreach vessel
        for vessel in vessels:
            spire_datas = spire_ais_data_repository.get_all_data_by_mmsi(session, vessel.mmsi,
                                                                         SpireAisDataRepository.ORDER_BY_POSITION)
            for spire_data in spire_datas:
                # Foreach position
                # TODO: A poursuivre, voir MIRO pour l'algorithme
                pass


if __name__ == "__main__":
    time_start = perf_counter()
    logger.info("DEBUT - Nettoyage des positions")
    run()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Nettoyage des positions en {duration:.2f}s")
