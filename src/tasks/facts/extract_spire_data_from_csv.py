import argparse
import json
import pandas as pd
import numpy as np
from pathlib import Path
from time import perf_counter
from datetime import datetime

from bloom.container import UseCases
from bloom.domain.spire_ais_data import SpireAisData
from bloom.config import settings
from bloom.logger import logger
from pydantic import ValidationError
from tasks.base import BaseTask


class ExtractSpireDataFromCsv(BaseTask):
    def map_to_domain(self, row: pd.Series) -> SpireAisData:
        isna = row.isna()
        row=row.reindex(index=SpireAisData.__fields__.keys())
        #logger.debug(row.to_dict())
        
        try:
            logger.debug(SpireAisData(**row.to_dict()))
        except Exception as e:
                logger.debug(f"{type(e)}:{e}")
        #return SpireAisData(**row.to_dict())

    def run(self, *args, **kwargs) -> None:
        use_cases = UseCases()
        spire_ais_data_repository = use_cases.spire_ais_data_repository()
        db = use_cases.db()

        file_name = kwargs['segment_data_csv_path'] if 'segment_data_csv_path' in kwargs \
                                                  else settings.segment_data_csv_path
        logger.info(f"Loading spire data from {file_name}")
        orm_data = []
        try:
            df = pd.read_csv(file_name, sep=";")
            #df['spire_update_statement']=pd.to_datetime(df['spire_update_statement'], format='%Y-%m-%d %H:%M:%S.%f %z')
            df['spire_update_statement']=df['spire_update_statement'].apply(datetime.fromisoformat)
            df['vessel_timestamp']=df['vessel_timestamp'].apply(datetime.fromisoformat)
            df['vessel_update_timestamp']=df['vessel_update_timestamp'].apply(datetime.fromisoformat)
            df['position_timestamp']=df['position_timestamp'].apply(datetime.fromisoformat)
            df['position_update_timestamp']=df['position_update_timestamp'].apply(datetime.fromisoformat)
            df['voyage_timestamp']=df['voyage_timestamp'].apply(datetime.fromisoformat)
            df['voyage_update_timestamp']=df['voyage_update_timestamp'].apply(datetime.fromisoformat)
            df['created_at']=df['created_at'].apply(datetime.fromisoformat)
            #spire_ais_data = df.apply(self.map_to_domain, axis=1)
            #with Path(file_name).open() as csv_data, db.session() as session:
            #    raw_vessels = json.load(json_data)
            #    spire_ais_data = map_raw_vessels_to_domain(raw_vessels)
            #    orm_data = spire_ais_data_repository.batch_create_ais_data(spire_ais_data, session)
            #    session.commit()
        except ValidationError as e:
            logger.error("Erreur de validation des données CSV")
            logger.error(e.errors())
        logger.info(f"{len(orm_data)} vessel data loaded")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Load Segment data from file CSV file")
    parser.add_argument(
        "filename",
        help="Path to CSV file to load",
    )
    args = parser.parse_args()
    time_start = perf_counter()
    logger.info(f"DEBUT - Chargement des données CSV depuis le fichier {args.filename}")
    ExtractSpireDataFromCsv(segment_data_csv_path=args.filename).start()
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Chargement des données CSV en {duration:.2f}s")
