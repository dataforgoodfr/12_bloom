import json
from time import perf_counter
import asyncio

from bloom.config import settings
from bloom.container import UseCases
from bloom.domain.vessel import Vessel
from bloom.infra.kpler_api_client import KplerApiClient
from bloom.infra.http.kpler_api_utils import map_raw_messages_to_domain
from bloom.infra.repositories.repository_task_execution import TaskExecutionRepository
from bloom.logger import logger
from datetime import datetime, timezone
from pathlib import Path
from pydantic import ValidationError
import argparse


class GetVesselsFromKplerUseCase:
    def __init__(self) -> None:
        self.api_client = KplerApiClient()
        self.messages_page_size = settings.messages_page_size

    async def run(self, dump_path: str):
        use_cases = UseCases()
        vessel_repository = use_cases.vessel_repository()
        kpler_ais_data_repository = use_cases.kpler_ais_data_repository()
        db = use_cases.db()
        orm_data = []

        try:
            current_datetime=None
            position_count= None

            with db.session() as session:
                currentTaskTime = TaskExecutionRepository.get_point_in_time(session, "create_kpler_ais_messages")
                if(currentTaskTime <= datetime.now(timezone.utc) - settings.api_pooling_period):
                    vessels: list[Vessel] = vessel_repository.get_vessels_list(session)
                    
                    if len(vessels) > 0:
                        current_datetime=datetime.now(timezone.utc)
                        if dump_path is None:
                            TaskExecutionRepository.set_point_in_time(session,
                                                                "create_kpler_ais_messages",
                                                                current_datetime)
                            logger.info(f"Enregistrement du début d'exécution create_kpler_ais_messages {current_datetime}")
                            session.commit()
                        try:
                            raw_messages = await self.get_latest_ais_messages(vessels)
                            position_count = len(raw_messages)
                            if dump_path is not None:
                                try:
                                    now = current_datetime.strftime("%Y-%m-%dT%H:%M:%S")
                                    dump_file = Path(dump_path, f"kpler_ais_latest__{now}").with_suffix(".json")
                                    with dump_file.open("wt") as handle:
                                        json.dump(raw_messages, handle)
                                except Exception as e:
                                    logger.warning("Echec de l'écriture de la réponse Kpler", exc_info=e)   
                            else:
                                kpler_ais_data = map_raw_messages_to_domain(raw_messages)
                                orm_data = kpler_ais_data_repository.batch_create_ais_data(
                                    kpler_ais_data,
                                    session,
                                )
                                session.commit()
                        # Vu que l'on a enregistré et commité en bdd une ligne pour signalter qu'une 
                        # instance create_kpler_ais_messages était en cours
                        # en cas d'erreur ou d'interruption volontaire, on supprime la ligne en cours
                        # cela permettra aux autres instances de se lancer
                        except (KeyboardInterrupt,Exception) as e:
                            if dump_path is None:
                                TaskExecutionRepository.remove_point_in_time(session,
                                                                "create_kpler_ais_messages",
                                                                current_datetime)
                                session.commit()
                            raise(e)
                        if dump_path is None:
                            if position_count != None:
                                TaskExecutionRepository.set_position_count(session,
                                                                "create_kpler_ais_messages",
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
        session.close()

    async def get_latest_ais_messages(self, vessels: list[Vessel]):
        pages = []
        mmsi_list = [vessel.mmsi for vessel in vessels]
        mmsi_start = 0
        mmsi_end = self.messages_page_size
        while mmsi_start <= len(mmsi_list):
            mmsi_list_string = ", ".join(map(str, mmsi_list[mmsi_start:mmsi_end]))
            page = await self.api_client.get(
                "ais-latest",
                {"filter": f"mmsi IN ({mmsi_list_string})"}
            )
            if page is not None:
                pages = pages + page['features']
            mmsi_start += self.messages_page_size + 1
            mmsi_end += self.messages_page_size + 1
        await self.api_client.close()
        return pages

async def main(dump_path: str):
    usecase = GetVesselsFromKplerUseCase()
    await usecase.run(dump_path)

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
    logger.info("DEBUT - Chargement des données JSON depuis l'API Kpler")
    asyncio.run(main(args.dump_path))
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Chargement des données depuis l'API Kpler en {duration:.2f}s")

