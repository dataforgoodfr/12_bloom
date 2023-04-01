"""Bloom scrapper.

This application execute the scrapping of different vessel's positions source,
based on a list of vessel. It can run in local mode, with a custom scheduler
or scheduled outside of the app by a cronjob.
"""
import argparse
<<<<<<< HEAD

from bloom.enums import ExecutionMode
from bloom.logger import logger
=======

from logger import logger

from bloom.enums import ExecutionMode
from bloom.scheduler import PeriodicScheduler
from container import UseCases

SCRAP_INTERVAL = 15 * 60


def main() -> None:
    parser = argparse.ArgumentParser(description="Bloom scraping application")
    parser.add_argument(
        "-m",
        "--mode",
        type=ExecutionMode,
        help="execution mode of the scraper",
        required=False,
        default=ExecutionMode.CRONTAB,
    )
    args = parser.parse_args()
    use_cases = UseCases()
    marine_traffic_usecase = use_cases.scrap_marine_data_usecase()
    if args.mode == ExecutionMode.LOCAL:
        logger.info("Starting scraping with internal scheduler")
        scheduler = PeriodicScheduler(
            function=marine_traffic_usecase.scrap_vessels,
            interval=SCRAP_INTERVAL,
        )
        marine_traffic_usecase.scrap_vessels()
        while True:
            scheduler.start()
    else:
        logger.info("Starting scraping with external scheduler")
        marine_traffic_usecase.scrap_vessels()


if __name__ == "__main__":
    main()
