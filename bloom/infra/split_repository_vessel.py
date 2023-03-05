from csv import writer
from logging import getLogger
from pathlib import Path
from typing import List
import zipfile
from io import BytesIO

from src.infra.repository_vessel import VesselRepository, Vessel

logger = getLogger()

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

    def load_vessel(self, vessel_IMO: int):
        logger.info(
            f"Load vessel {vessel_IMO}'s historic"
        )


class ChainedFilesIO(BytesIO):
    def __init__(self, csv_paths: List[Path]) -> None:
        self._load(csv_paths)

    def _load(self, csv_paths):
        with zipfile.ZipFile(self, 'w') as z:
        
            data = b""
            for csv_path in csv_paths:
                with open(csv_path, "rb") as fd:
                    data += fd.read()
            
            z.writestr('data.csv', data)
        
        self.seek(0)  

    def readable(self):
        return True
    
