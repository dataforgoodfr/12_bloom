import datetime
from logging import getLogger
from pathlib import Path

from dateparser import parse as parse_date

from bloom.infra.data_file import DataDoesNotExistError, DataFile
from bloom.infra.data_storage import DataStorage
from bloom.infra.repository_vessel import Vessel, VesselRepository

logger = getLogger()


class SplitVesselRepository(VesselRepository):
    """This class handle vessel data.

    It augments VesselRepository by using split data files. It
    handles paths logic, including vessel imos and dates.
    It uses DataStorage to actually save and loads data.

    """

    def __init__(self) -> None:
        super().__init__()
        self._storage = DataStorage()

    def _get_vessel_csv_path(self, vessel: Vessel) -> Path:
        """Returns the path where to save a vessel.

        Args:
            vessel: The vessel to save

        Returns:
            Path: The path where to save the vessel.
        """

        parsed_date = vessel.timestamp.strftime("%Y-%m")

        # This logic is used in the method DataStorage._clean_outdated_cache.
        # Take care if you change the way the path is build here.
        return Path.joinpath(Path(vessel.IMO), f"{parsed_date}.csv")

    def save_vessels(self, vessels_list: list[Vessel]) -> None:
        vessels_list = [vessel for vessel in vessels_list if vessel]
        paths = [self._get_vessel_csv_path(vessel) for vessel in vessels_list]

        logger.info(
            f"Saving vessels positions : {[vessel.IMO for vessel in vessels_list]}",
        )

        self._storage.append_elements(paths, vessels_list)

    def load_data(
        self,
        vessel_imos: int | str | list[int | str] | None = None,
        since_date_string: str | None = None,
        until_date_string: str | None = None,
    ) -> DataFile:
        since_date = parse_date(since_date_string or "1970")
        since_date_month_string = since_date.strftime("%Y-%m")

        until_date = (
            parse_date(
                until_date_string,
            )
            if until_date_string
            else datetime.datetime.now()
        )
        until_date_month_string = until_date and until_date.strftime("%Y-%m")

        if vessel_imos:
            if not isinstance(vessel_imos, list):
                vessel_imos = [vessel_imos]
        else:
            vessel_imos = ["[^/]+"]
        vessel_imos = "|".join(map(str, vessel_imos))

        files = []
        for file_path in self._storage.glob(f"{vessel_imos}/[^\\.]+\\.csv"):
            if since_date_month_string <= file_path.stem <= until_date_month_string:
                files.append(str(file_path))

        if not files:
            raise DataDoesNotExistError()

        if since_date_string or until_date_string:
            return DataFile(
                files,
                filter_=lambda elt: since_date
                <= datetime.datetime.strptime(
                    elt["timestamp"],
                    "%Y-%m-%d %H:%M:%S+00:00",
                )
                <= until_date,
            )

        return DataFile(files)

    def load_vessel(self, vessel_imo: int | str) -> DataFile:
        logger.info(f"Load vessel {vessel_imo}'s historic")

        return self.load_data(vessel_imos=vessel_imo)

    def load_period(
        self,
        since_date_string: str | None,
        until_date_string: str | None,
    ) -> DataFile:
        logger.info(
            f"Load since {since_date_string} until {until_date_string} 's historic",
        )

        return self.load_data(
            since_date_string=since_date_string,
            until_date_string=until_date_string,
        )


_split_vessel_repository = SplitVesselRepository()


def get_vessel_file(vessel_imo: int | str) -> DataFile:
    """Return a file like object containing the data of a vessel.

    Args:
        vessel_imo: The IMO of the vessel to get.

    Returns:
        DataFile: An object that encapsulate all the data
            of this vessel and can be read with geo_pandas

    Raises:
        DataDoesNotExistError: Raise this error when no data are found.
    """

    return _split_vessel_repository.load_vessel(vessel_imo)


def get_period_file(
    since_date_string: str | None = "24 hours ago",
    until_date_string: str | None = None,
) -> DataFile:
    """Return a file like object containing the data of a given day.

    Args:
        since_date_string: A string representing the start of a period. As we use
            dateparser to parse it, it can be given under a large
            variety of way such as "today", "two days ago", "10/10/2021",
            ect... If none are given it will be 24 hours ago.
        until_date_string: A string representing the end of a period. If none is given
            the end of the period will be the time of this function call.

    Returns:
        DataFile: An object that encapsulate all the data
            of this day and can be read with geo_pandas

    Raises:
        DataDoesNotExistError: Raise this error when no data are found.
    """

    return _split_vessel_repository.load_period(since_date_string, until_date_string)


def get_data_file(
    vessel_imos: int | str | list[int | str] = None,
    since_date_string: str | None = None,
    until_date_string: str | None = None,
) -> DataFile:
    """Return a file like object containing the data given filters.

    Args:
        since_date_string: A string representing the start of a period. As we use
            dateparser to parse it, it can be given under a large
            variety of way such as "today", "two days ago", "10/10/2021",
            ect...
        until_date_string: A string representing the end of a period.
        vessel_imos: A string or a list of strings representing the IMO
            of (a) vessel(s) to get. if none are given, the data of all
            vessels is returned.

    Returns:
        DataFile: An object that encapsulate all the data
            of this day and can be read with geo_pandas

    Raises:
        DataDoesNotExistError: Raise this error when no data are found.
    """

    return _split_vessel_repository.load_data(
        vessel_imos,
        since_date_string,
        until_date_string,
    )
