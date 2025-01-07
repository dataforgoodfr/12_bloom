import argparse
import json
from datetime import datetime, timezone, timedelta
from pathlib import Path
from time import perf_counter

from bloom.container import UseCases
from bloom.domain.vessel import Vessel
from bloom.infra.http.spire_api_utils import map_raw_vessels_to_domain
from bloom.logger import logger
from pydantic import ValidationError
from bloom.infra.repositories.repository_task_execution import TaskExecutionRepository
from bloom.config import settings


def run(dump_path: str) -> None:
    use_cases = UseCases()
    spire_ais_data_repository = use_cases.spire_ais_data_repository()
    spire_traffic_usecase = use_cases.get_spire_data_usecase()
    vessel_repository = use_cases.vessel_repository()
    db = use_cases.db()

    orm_data = []
    try:
        process_start=datetime.now(timezone.utc)
        current_datetime=None
        position_count= None
        with db.session() as session:
            currentTaskTime=TaskExecutionRepository.get_point_in_time(session,"load_spire_data_from_api")
            if(currentTaskTime <= datetime.now(timezone.utc) - settings.api_pooling_period):
                vessels: list[Vessel] = vessel_repository.get_vessels_list(session)
                if len(vessels) > 0:
                    current_datetime=datetime.now(timezone.utc)
                    TaskExecutionRepository.set_point_in_time(session,
                                                        "load_spire_data_from_api",
                                                        current_datetime)
                    logger.info(f"Enregistrement du début d'exécution load_spire_data_from_api {current_datetime}")
                    # Afin de séquencer plusieurs tâche load_spire_data_from_api qui pourraient
                    # être lancée en parallèle sur différentes machines, on enregistre le point_in_time
                    # dès le début de la tâche afin que les autres instances détectent qu'une instance
                    # est déjà en cours d'exécution
                    # Pour ça, on est obligé de commiter en base dès le début afin
                    # d'éviter que d'autres instances ne se lancent pendant le traitement 
                    # de la première instance
                    session.commit()
                    try:
                        raw_vessels = spire_traffic_usecase.get_raw_vessels_from_spire(vessels)
                        position_count=len(raw_vessels)
                        if dump_path is not None:
                            try:
                                now =current_datetime.strftime("%Y-%m-%dT%H:%M:%S")
                                dump_file = Path(args.dump_path, f"spire_{now}").with_suffix(".json")
                                with dump_file.open("wt") as handle:
                                    json.dump(raw_vessels, handle)
                            except Exception as e:
                                logger.warning("Echec de l'écriture de la réponse Spire", exc_info=e)
                        else:
                            spire_ais_data = map_raw_vessels_to_domain(raw_vessels)
                            orm_data = spire_ais_data_repository.batch_create_ais_data(
                                spire_ais_data,
                                session,
                            )
                    # Vu que l'on a enregistré et commité en bdd une ligne pour signalter qu'une 
                    # instance load_spire_data_from_api était en cours
                    # en cas d'erreur ou d'interruption volontaire, on supprime la ligne en cours
                    # cela permettra aux autres instances de se lancer
                    except (KeyboardInterrupt,Exception) as e:
                        TaskExecutionRepository.remove_point_in_time(session,
                                                        "load_spire_data_from_api",
                                                        current_datetime)
                        session.commit()
                        raise(e)
                    session.commit()
                    if current_datetime != None:
                        TaskExecutionRepository.set_duration(session,
                                                            "load_spire_data_from_api",
                                                            current_datetime,
                                                            datetime.now(timezone.utc)-process_start)
                    if position_count != None:
                        TaskExecutionRepository.set_position_count(session,
                                                        "load_spire_data_from_api",
                                                        current_datetime,
                                                        position_count)
                    session.commit()
            else:
                logger.info(f'Le temps écoulé depuis le dernier chargement est inférieur à la période d\'interrogation {settings.api_pooling_period}')
            
    except ValidationError as e:
        logger.error("Erreur de validation des données JSON")
        logger.error(e.errors())
        raise e
    except Exception as e:
        logger.error("Echec de l'appel API", exc_info=e)
        raise e
    logger.info(f"{len(orm_data)} données chargées")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Bloom scraping application")
    parser.add_argument(
        "-d",
        "--dump-path",
        help="Répertoire de destination des dump",
        required=False,
        default=None,
    )
    args = parser.parse_args()
    time_start = perf_counter()
    logger.info("DEBUT - Chargement des données JSON depuis l'API SPIRE")
    run(args.dump_path)
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Chargement des données depuis l'API SPIRE en {duration:.2f}s")
