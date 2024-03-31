import argparse
import json
from pathlib import Path
from time import perf_counter

from bloom.container import UseCases
from bloom.infra.http.spire_api_utils import map_raw_vessels_to_domain
from bloom.logger import logger
from pydantic import ValidationError
from tasks.base import BaseTask


class ExtractSpireDataFromCsv(BaseTask):

    def run(self, *args, **kwargs) -> None:
        use_cases = UseCases()
        spire_ais_data_repository = use_cases.spire_ais_data_repository()
        db = use_cases.db()

        logger.info(f"Loading spire data from {kwargs['file_name']}")
        orm_data = []
        try:
            df = pd.read_csv(settings.spire_data_csv_path, sep=";")
            with Path.open(kwargs['file_name']) as json_data, db.session() as session:
                raw_vessels = json.load(json_data)
                spire_ais_data = map_raw_vessels_to_domain(raw_vessels)
                orm_data = spire_ais_data_repository.batch_create_ais_data(spire_ais_data, session)
                session.commit()
        except ValidationError as e:
            logger.error("Erreur de validation des données JSON")
            logger.error(e.errors())
        logger.info(f"{len(orm_data)} vessel data loaded")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Spire data from file CSV file")
    parser.add_argument(
        "filename",
        help="Path to CSV file to load",
    )
    args = parser.parse_args()
    time_start = perf_counter()
    logger.info(f"DEBUT - Chargement des données CSV depuis le fichier {args.filename}")
    ExtractSpireDataFromCsv(file_name=args.filename).start()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Chargement des données CSV en {duration:.2f}s")
