from csv import writer
from logging import getLogger
from pathlib import Path

import pandas as pd

from bloom.domain.vessel import AbstractVessel, Vessel

logger = getLogger()


class VesselRepository(AbstractVessel):
    def __init__(self) -> None:
        self.vessels_path = Path.joinpath(Path.cwd(), "data/chalutiers_pelagiques.xlsx")
        self.results_path = Path.joinpath(Path.cwd(), "data/bloom_scrap.csv")

    def load_vessel_identifiers(self) -> list[Vessel]:
        df = pd.read_excel(self.vessels_path, engine="openpyxl")
        vessel_identifiers_list = df["IMO"].tolist()

        return [Vessel(IMO=imo) for imo in vessel_identifiers_list]

    def save_vessels(self, vessels_list: list[Vessel]) -> None:
        logger.info(
            f"Saving vessels positions : {[vessel.IMO for vessel in vessels_list]}",
        )
        with Path.open(self.results_path, "a", newline="") as write_obj:
            for vessel in vessels_list:
                csv_writer = writer(write_obj)
                csv_writer.writerow(vessel.to_list())
