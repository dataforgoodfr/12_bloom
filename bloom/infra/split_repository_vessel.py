import itertools
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
    handles paths logic and vessel related information.
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
        logger.info(
            f"Saving vessels positions : {[vessel.IMO for vessel in vessels_list]}",
        )
        paths, rows = zip(
            *[
                (self._get_vessel_csv_path(vessel), vessel.to_list())
                for vessel in vessels_list
            ],
            strict=True,
        )

        self._storage.append_rows(paths, rows)

    def load_data(
        self,
        vessel_imos: int | str | list[int | str] | None = None,
        date_strings: list[str] | str | None = None,
    ) -> DataFile:
        if date_strings:
            if not isinstance(date_strings, list):
                date_strings = [date_strings]

            dates = [
                parse_date(date_string).strftime("%Y-%m-%d")
                for date_string in date_strings
            ]
        else:
            dates = ["*"]

        if vessel_imos:
            if not isinstance(vessel_imos, list):
                vessel_imos = [vessel_imos]
        else:
            vessel_imos = ["**"]

        logger.info(f"Load data from vessels {vessel_imos}' at dates {dates}.")

        files = []
        for date_str, imo in itertools.product(dates, vessel_imos):
            files.extend(self._storage.glob(f"{imo}/{date_str}.csv"))

        if not files:
            raise DataDoesNotExistError()

        return DataFile(files)

    def load_vessel(self, vessel_imo: int | str) -> DataFile:
        logger.info(f"Load vessel {vessel_imo}'s historic")

        return self.load_data(vessel_imos=vessel_imo)

    def load_day(self, date_string: str = "today") -> DataFile:
        logger.info(f"Load {date_string}'s historic")

        return self.load_data(date_strings=date_string)


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


def get_day_file(date_string: str = "today") -> DataFile:
    """Return a file like object containing the data of a given day.

    Args:
        date_string: A string representing a day. As we use
            dateparser to parse it, it can be given under a large
            variety of way such as "today", "two days ago", "10/10/2021",
            ect...

    Returns:
        DataFile: An object that encapsulate all the data
            of this day and can be read with geo_pandas

    Raises:
        DataDoesNotExistError: Raise this error when no data are found.
    """

    return _split_vessel_repository.load_day(date_string)


def get_data_file(
    vessel_imos: int | str | list[int | str] = None,
    date_strings: list[str] | str = None,
) -> DataFile:
    """Return a file like object containing the data given filters.

    Args:
        date_strings: A string or a list of strings representing (a) day(s).
            As we use dateparser to parse it, it can be given under a large
            variety of way such as "today", "two days ago", "10/10/2021",
            ect... If none are given, all the historical data is returned.
        vessel_imos: A string or a list of strings representing the IMO
            of (a) vessel(s) to get. if none are given, the data of all
            vessels is returned.

    Returns:
        DataFile: An object that encapsulate all the data
            of this day and can be read with geo_pandas

    Raises:
        DataDoesNotExistError: Raise this error when no data are found.
    """

    return _split_vessel_repository.load_data(vessel_imos, date_strings)
