import json
from csv import DictWriter
from logging import getLogger
from pathlib import Path

import pandas as pd

from bloom.domain.vessel import AbstractVessel, VesselPositionMarineTraffic

logger = getLogger()


class VesselRepository(AbstractVessel):
    def __init__(self) -> None:
        self.vessels_path = Path.joinpath(Path.cwd(), "data/chalutiers_pelagiques.xlsx")
        self.results_path = Path.joinpath(Path.cwd(), "data/bloom_scrap.csv")

    def load_vessel_identifiers(self) -> list[VesselPositionMarineTraffic]:
        df = pd.read_excel(self.vessels_path, engine="openpyxl")
        vessel_identifiers_list = df["IMO"].tolist()

        return [VesselPositionMarineTraffic(IMO=imo) for imo in vessel_identifiers_list]

    def save_vessels(self, vessels_list: list[VesselPositionMarineTraffic]) -> None:
        logger.info(
            f"Saving vessels positions : {[vessel.IMO for vessel in vessels_list]}",
        )
        with Path.open(self.results_path, "a") as write_obj:
            headers = vessels_list[0].__fields__.keys()
            csv_writer = DictWriter(
                write_obj,
                delimiter=";",
                lineterminator="\n",
                fieldnames=headers,
            )
            if write_obj.tell() == 0:
                csv_writer.writeheader()

            for vessel in vessels_list:
                csv_writer.writerow(json.loads(vessel.json()))
