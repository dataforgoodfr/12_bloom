"""Bloom scrapper.

This application execute the scrapping of different vessel's positions source,
based on a list of vessel. It can run in local mode, with a custom scheduler
or scheduled outside of the app by a cronjob.
"""
from bloom.logger import logger
from container import UseCases

SCRAP_INTERVAL = 15 * 60


def main() -> None:
    # parser.add_argument(
    #     "-m",
    #     "--mode",
    # if args.mode == ExecutionMode.LOCAL:
    #     while True:

    use_cases = UseCases()
    spire_traffic_usecase = use_cases.get_spire_data_usecase()
    vessels = spire_traffic_usecase.get_all_vessels()
    spire_traffic_usecase.save_vessels(vessels)
    logger.info(vessels)

    return


if __name__ == "__main__":
    main()
