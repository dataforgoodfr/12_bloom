import argparse
import json
from pathlib import Path
from time import perf_counter

from tasks.base import BaseTask
from bloom.container import UseCases
from bloom.infra.http.spire_api_utils import map_raw_vessels_to_domain
from bloom.logger import logger
from pydantic import ValidationError


class ComputePortGeometryBuffer(BaseTask):

    def run(self,*args,**kwargs) -> None:
        use_cases = UseCases()
        spire_ais_data_repository = use_cases.spire_ais_data_repository()
        db = use_cases.db()

        logger.info(f"Loading spire data from {kwargs['file_name']}")
        orm_data = []
        try:
            with Path(kwargs['file_name']).open() as json_data, db.session() as session:
                raw_vessels = json.load(json_data)
                spire_ais_data = map_raw_vessels_to_domain(raw_vessels)
                orm_data = spire_ais_data_repository.batch_create_ais_data(spire_ais_data, session)
                session.commit()
        except ValidationError as e:
            logger.error("Erreur de validation des données JSON")
            logger.error(e.errors())
        logger.info(f"{len(orm_data)} vessel data loaded")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Spire data from file JSON file")
    parser.add_argument(
        "filename",
        help="Path to JSON file to load",
    )
    args = parser.parse_args()
    time_start = perf_counter()
    logger.info(f"DEBUT - Chargement des données JSON depuis le fichier {args.filename}")
    ComputePortGeometryBuffer(file_name=args.filename).start()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Chargement des données JSON en {duration:.2f}s")
