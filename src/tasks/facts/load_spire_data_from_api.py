import argparse
import json
from datetime import datetime, timezone
from pathlib import Path
from time import perf_counter

from tasks.base import BaseTask
from bloom.container import UseCases
from bloom.domain.vessel import Vessel
from bloom.infra.http.spire_api_utils import map_raw_vessels_to_domain
from bloom.logger import logger
from pydantic import ValidationError

from bloom.config import settings


class LoadSpireDataFromApi(BaseTask):

    
    def run(self,*args,**kwargs) -> None:
        use_cases = UseCases()
        spire_ais_data_repository = use_cases.spire_ais_data_repository()
        spire_traffic_usecase = use_cases.get_spire_data_usecase()
        vessel_repository = use_cases.vessel_repository()
        db = use_cases.db()

        orm_data = []
        try:
            with db.session() as session:
                vessels: list[Vessel] = vessel_repository.load_all_vessel_metadata(session)

                raw_vessels = spire_traffic_usecase.get_raw_vessels_from_spire(vessels)
                if kwargs['dump_path'] is not None:
                    try:
                        now = datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")
                        dump_file = Path(kwargs['dump_path'], f"spire_{now}").with_suffix(".json")
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
                session.commit()
        except ValidationError as e:
            logger.error("Erreur de validation des données JSON")
            logger.error(e.errors())
        except Exception as e:
            logger.error("Echec de l'appel API", exc_info=e)
        logger.info(f"{len(orm_data)} vessel data loaded")


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
    LoadSpireDataFromApi(dump_path=args.dump_path).start()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Chargement des données depuis l'API SPIRE en {duration:.2f}s")
