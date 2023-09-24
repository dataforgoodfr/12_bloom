from datetime import datetime

from pydantic import BaseModel


class Alert(BaseModel):
    ship_name: str | None
    mmsi: int
    last_position_time: datetime
    position: str
    iucn_cat: str
    mpa_name: str
