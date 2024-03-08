from datetime import datetime

from pydantic import BaseModel

from typing import Union


class Alert(BaseModel):
    ship_name: Union [ str , None]
    mmsi: int
    last_position_time: datetime
    position: str
    iucn_cat: str
    mpa_name: str
