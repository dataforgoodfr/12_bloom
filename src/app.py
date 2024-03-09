"""Bloom scrapper.

This application execute the scrapping of different vessel's positions source,
based on a list of vessel. It can run in local mode, with a custom scheduler
or scheduled outside of the app by a cronjob.
"""
import argparse
from datetime import datetime, timezone

from bloom.enums import ExecutionMode
from bloom.logger import logger
from bloom.scheduler import PeriodicScheduler
from bloom.container import UseCases

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
    spire_traffic_usecase = use_cases.get_spire_data_usecase()
    alert_usecase = use_cases.generate_alert_usecase()
    timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")

    if args.mode == ExecutionMode.LOCAL:
        logger.info("Starting scraping with internal scheduler")
        spire_traffic_usecase.save_vessels(
            spire_traffic_usecase.get_all_vessels(timestamp),
        )
        alert_usecase.generate_alerts(timestamp)
        #while True:
        #    scheduler.start()
    else:
        logger.info("Starting scraping with external scheduler")
        spire_traffic_usecase.save_vessels(
            spire_traffic_usecase.get_all_vessels(timestamp),
        )
        alert_usecase.generate_alerts(timestamp)


if __name__ == "__main__":
    main()