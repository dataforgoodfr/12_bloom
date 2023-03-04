"""Bloom scrapper.

This application execute the scrapping of different vessel's positions source,
based on a list of vessel. It can run in local mode, with a custom scheduler
or scheduled outside of the app by a cronjob.
"""
import argparse
from logging import getLogger

from bloom.enums import ExecutionMode
from bloom.infra.marine_traffic_scraper import MarineTrafficVesselScraper
from bloom.infra.repository_vessel import VesselRepository
from bloom.scheduler import PeriodicScheduler
from bloom.usecase.ScrapVesselsFromMarineTraffic import ScrapVesselsFromMarineTraffic

SCRAP_INTERVAL = 15 * 60

logger = getLogger()


def scrap_vessels_with_marine_traffic() -> None:
    vessels_repository = VesselRepository()
    scraper = MarineTrafficVesselScraper()
    ScrapVesselsFromMarineTraffic(vessels_repository, scraper).scrap_vessels()


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
    if args.mode == ExecutionMode.LOCAL:
        logger.info("Starting scraping with internal scheduler")
        scheduler = PeriodicScheduler(
            function=scrap_vessels_with_marine_traffic,
            interval=SCRAP_INTERVAL,
        )
        scrap_vessels_with_marine_traffic()
        while True:
            scheduler.start()
    else:
        logger.info("Starting scraping with external scheduler")
        scrap_vessels_with_marine_traffic()


if __name__ == "__main__":
    main()
