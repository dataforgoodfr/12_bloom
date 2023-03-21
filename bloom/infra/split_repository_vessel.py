from csv import writer
from os import environ
from logging import getLogger
from pathlib import Path
from typing import List, Union, Callable, Any
from dateparser import parse as parse_date
import itertools

from bloom.infra.data_file import DataFile, DataDoesNotExistError
from bloom.infra.repository_vessel import VesselRepository, Vessel
from bloom.infra.data_storage import DataStorage

logger = getLogger()


class SplitVesselRepository(VesselRepository):
    def __init__(self):
        super().__init__()
        self.results_path = Path.joinpath(Path.cwd(), "data", "csv")
        self._storage = DataStorage()

    def _get_vessel_csv_path(self, vessel: Vessel) -> Path:
        """Returns the path where to save a vessel.

        Args:
            vessel: The vessel to save

        Returns:
            Path: The path where to save the vessel.
        """

        parsed_date = vessel.timestamp.strftime("%Y-%m")
        return Path.joinpath(Path(vessel.IMO), f"{parsed_date}.csv")

    def save_vessels(self, vessels_list: List[Vessel]) -> None:
        vessels_list = [vessel for vessel in vessels_list if vessel]
        print(f"Saving vessels positions : {[vessel.IMO for vessel in vessels_list]}")
        paths, rows = zip(
            *[
                (self._get_vessel_csv_path(vessel), vessel.to_list())
                for vessel in vessels_list
            ]
        )
        rows = [vessel.to_list() for vessel in vessels_list]

        self._storage.append_rows(paths, rows)

    def load_data(
        self,
        vessel_IMOs: Union[int, str, List[Union[int, str]]] = None,
        date_strings: Union[List[str], str] = None,
    ) -> DataFile:
        if date_strings:
            if not isinstance(date_strings, list):
                date_strings = [date_strings]

            dates = [
                parse_date(date_string).strftime("%Y-%m-%d")
                for date_string in date_strings
            ]
        else:
            dates = ["**"]

        if vessel_IMOs:
            if not isinstance(vessel_IMOs, list):
                vessel_IMOs = [vessel_IMOs]
        else:
            vessel_IMOs = ["*"]

        logger.info(f"Load data from vessels {vessel_IMOs}' at dates {dates}.")

        files = []
        for date_str, imo in itertools.product(dates, vessel_IMOs):
            files.extend(self._storage.glob(f"{imo}/{date_str}.csv"))

        if not files:
            raise DataDoesNotExistError()

        return DataFile(files)

    def load_vessel(self, vessel_IMO: Union[int, str]) -> DataFile:
        logger.info(f"Load vessel {vessel_IMO}'s historic")

        return self.load_data(vessel_IMOs=vessel_IMO)

    def load_day(self, date_string: str = "today") -> DataFile:
        logger.info(f"Load {date_string}'s historic")

        return self.load_data(date_strings=date_string)


_split_vessel_repository = SplitVesselRepository()


def get_vessel_file(vessel_IMO: Union[int, str]) -> DataFile:
    """Return a file like object containing the data of a vessel.

    Args:
        vessel_IMO: The IMO of the vessel to get.

    Returns:
        DataFile: An object that encapsulate all the data
            of this vessel and can be read with geo_pandas

    Raises:
        DataDoesNotExistError: Raise this error when no data are found.
    """

    return _split_vessel_repository.load_vessel(vessel_IMO)


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
    vessel_IMOs: Union[int, str, List[Union[int, str]]] = None,
    date_strings: Union[List[str], str] = None,
) -> DataFile:
    """Return a file like object containing the data given filters.

    Args:
        date_strings: A string or a list of strings representing (a) day(s).
            As we use dateparser to parse it, it can be given under a large
            variety of way such as "today", "two days ago", "10/10/2021",
            ect... If none are given, all the historical data is returned.
        vessel_IMOs: A string or a list of strings representing the IMO
            of (a) vessel(s) to get. if none are given, the data of all
            vessels is returned.

    Returns:
        DataFile: An object that encapsulate all the data
            of this day and can be read with geo_pandas

    Raises:
        DataDoesNotExistError: Raise this error when no data are found.
    """

    return _split_vessel_repository.load_data(vessel_IMOs, date_strings)
