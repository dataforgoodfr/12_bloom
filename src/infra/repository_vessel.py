import os
from pathlib import Path
from typing import List
from logging import getLogger
import pandas as pd
from csv import writer

from src.domain.vessel import Vessel, AbstractVessel

logger = getLogger()


class VesselRepository(AbstractVessel):

    def __init__(self):
        self.vessels_path = Path.joinpath(Path.cwd(), "data/chalutiers_pelagiques.xlsx")
        self.results_path = Path.joinpath(Path.cwd(), "data/bloom_scrap.csv")

    def load_vessel_identifiers(self) -> List[Vessel]:

        df = pd.read_excel(self.vessels_path, engine="openpyxl")
        vessel_identifiers_list = df["IMO"].tolist()

        return [
            Vessel(IMO=imo)
            for imo in vessel_identifiers_list
        ]

    def save_vessels(self, vessels_list: List[Vessel]):
        logger.info(f"Saving vessels positions : {[vessel.IMO for vessel in vessels_list]}")
        with open(self.results_path, 'a', newline='') as write_obj:
            for vessel in vessels_list:
                csv_writer = writer(write_obj)
                csv_writer.writerow(vessel.to_list())
