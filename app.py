import argparse
from logging import getLogger

from src.enums import ExecutionMode
from src.infra.marine_traffic_scraper import MarineTrafficVesselScraper
from src.infra.repository_vessel import VesselRepository
from src.scheduler import PeriodicScheduler
from src.usecase.ScrapVesselsFromMarineTraffic import ScrapVesselsFromMarineTraffic

SCRAP_INTERVAL = 15 * 60

logger = getLogger()


def scrap_vessels_with_marine_traffic():
    vessels_repository = VesselRepository()
    scraper = MarineTrafficVesselScraper()
    ScrapVesselsFromMarineTraffic(vessels_repository, scraper).scrap_vessels()


def main():
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
            function=scrap_vessels_with_marine_traffic, interval=SCRAP_INTERVAL
        )
        scrap_vessels_with_marine_traffic()
        while True:
            scheduler.start()
    else:
        logger.info("Starting scraping with external scheduler")
        scrap_vessels_with_marine_traffic()


if __name__ == "__main__":
    main()
