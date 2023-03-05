from csv import writer
from logging import getLogger
from pathlib import Path
from typing import List, Union
import zipfile
from dateparser import parse as parse_date
import itertools

from io import BytesIO

from src.infra.repository_vessel import VesselRepository, Vessel

logger = getLogger()


class DataDoesNotExist(Exception):
    "Error triggered when no data match a filter"


class ChainedFilesIO(BytesIO):
    def __init__(self, csv_paths: List[Path], zip_data: bool = True) -> None:
        # Geopandas use fiona to load files.
        # fiona only handles zip when fed with bytes.
        if zip_data:
            self._load_zip(csv_paths)
        else:
            self._load_plain(csv_paths)

        self.seek(0)

    def _load_plain(self, csv_paths):
        for csv_path in csv_paths:
            with open(csv_path, "rb") as fd:
                self.write(fd.read())
            
    def _load_zip(self, csv_paths):
        with zipfile.ZipFile(self, 'w') as z:
            data = b""
            for csv_path in csv_paths:
                with open(csv_path, "rb") as fd:
                    data += fd.read()
            
            z.writestr('data.csv', data)
        

    def readable(self):
        return True
    

class SplitVesselRepository(VesselRepository):
    def __init__(self):
        super().__init__()
        self.results_path = Path.joinpath(Path.cwd(), "data", "csv")

    def _get_vessel_csv_path(self, vessel: Vessel) -> Path:
        """Returns the path where to save a vessel.
        
        Args:
            vessel: The vessel to save
        
        Returns:
            Path: The path where to save the vessel.
        """

        parsed_date = vessel.timestamp.strftime('%Y-%m-%d')
        file_path = Path.joinpath(self.results_path, parsed_date, f"{vessel.IMO}.csv")
        file_path.parent.mkdir(parents=True, exist_ok=True)

        return file_path
    
    def save_vessels(self, vessels_list: List[Vessel]):
        logger.info(
            f"Saving vessels positions : {[vessel.IMO for vessel in vessels_list]}"
        )

        for vessel in vessels_list:
            file_path = self._get_vessel_csv_path(vessel)

            with open(file_path, "a", newline="") as write_obj:
                csv_writer = writer(write_obj)
                csv_writer.writerow(vessel.to_list())

    def load_data(
        self, 
        vessels_IMO: Union[int, str, List[Union[int, str]]] = None, 
        dates_string: Union[List[str], str] = None
    ) -> ChainedFilesIO:
        if dates_string:
            if not isinstance(dates_string, list):
                dates_string = [dates_string]

            dates = [
                parse_date(date_string).strftime('%Y-%m-%d') 
                for date_string in dates_string
            ]
        else:
            dates = ["**"]
        
        if vessels_IMO:
            if not isinstance(vessels_IMO, list):
                vessels_IMO = [vessels_IMO]
        else:
            vessels_IMO = "*"
            
        logger.info(
            f"Load data from vessels {vessels_IMO}' at dates {dates} ."
        )
        
        files = []
        for date_str, IMO in itertools.product(dates, vessels_IMO):
            files.extend(self.results_path.glob(f'{date_str}/{IMO}.csv'))
        
        if not files:
            raise DataDoesNotExist("No data has been found with the given filters.")
    
        return ChainedFilesIO(files)
    
    def load_vessel(self, vessel_IMO: Union[int, str]) -> ChainedFilesIO:
        logger.info(
            f"Load vessel {vessel_IMO}'s historic"
        )

        return self.load_data(vessels_IMO=vessel_IMO)
    
    def load_day(self, date_string: str = "today") -> ChainedFilesIO:
        logger.info(
            f"Load {date_string}'s historic"
        )

        return self.load_data(dates_string=date_string)