import argparse
from time import perf_counter
from datetime import timedelta, datetime, timezone
from pathlib import Path

from bloom.container import UseCases
from bloom.logger import logger


def run(window: int, output_path: str):
    use_cases = UseCases()
    spire_ais_data_repository = use_cases.spire_ais_data_repository()

    db = use_cases.db()
    with db.session() as session:
        now = datetime.now(timezone.utc)
        date_limit = now - timedelta(days=window)
        logger.info(f"Suppression des données antérieures au {date_limit}")
        df = spire_ais_data_repository.get_all_data_before_as_df(session, date_limit)
        if len(df) > 0:
            min_date = df["created_at"].min().strftime("%Y-%m-%dT%H:%M:%S")
            max_date = df["created_at"].max().strftime("%Y-%m-%dT%H:%M:%S")
            file_name = Path(output_path).joinpath(f"./spire_ais_data_{min_date}_{max_date}.parquet")
            df.to_parquet(file_name)
            logger.info(f"{len(df)} enregistrements archivés dans le fichier {file_name}")
            count = spire_ais_data_repository.delete_rows(session, list(df["id"]))
            logger.info(f"{count} enregistrements supprimés en base de données")
        else:
            logger.info("Aucune donnée à archiver")
        session.commit()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Archivage de la table spire_ais_data")
    parser.add_argument(
        "-w",
        "--history-window",
        type=int,
        help="history window in days",
        required=False,
        default=365/2,
    )
    parser.add_argument(
        "-o",
        "--output-path",
        type=str,
        help="output path",
        required=False,
        default="./",
    )
    args = parser.parse_args()
    time_start = perf_counter()
    logger.info("DEBUT - Archivage des données de la table spire_ais_data")
    run(args.history_window, args.output_path)
    time_end = perf_counter()
    duration = time_end - time_start
    logger.info(f"FIN - Archivage des données de la table spire_ais_data en {duration:.2f}s")
