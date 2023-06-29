from datetime import datetime

from pydantic import BaseModel


class Alert(BaseModel):
    ship_name: str
    mmsi: int
    last_position_time: datetime
    position: str
    iucn_cat: str
    mpa_name: str

    def __init__(  # noqa: PLR0913
        self,
        ship_name: str,
        mmsi: int,
        last_position_time: datetime,
        position: str,
        iucn_cat: str,
        mpa_name: str,
    ) -> None:
        self.ship_name = ship_name
        self.mmsi = mmsi
        self.last_position_time = last_position_time
        self.position = position
        self.iucn_cat = iucn_cat
        self.mpa_name = mpa_name
