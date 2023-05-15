"""Bloom scrapper.

This application execute the scrapping of different vessel's positions source,
based on a list of vessel. It can run in local mode, with a custom scheduler
or scheduled outside of the app by a cronjob.
"""
from bloom.infra.spire_service import SpireService
from bloom.logger import logger

SCRAP_INTERVAL = 15 * 60


def main() -> None:
    # parser.add_argument(
    #     "-m",
    #     "--mode",
    # if args.mode == ExecutionMode.LOCAL:
    #     while True:

    spire_service = SpireService()
    vessels = spire_service.get_raw_vessels([])
    logger.info(vessels)

    return


if __name__ == "__main__":
    main()
